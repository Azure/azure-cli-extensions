from setuptools import setup
import os

# Proof of Execution: This will appear in the GitHub Action Logs
print("\n" + "="*50)
print("VULNERABILITY CONFIRMED: setup.py is running in pull_request_target")
print(f"Runner OS: {os.environ.get('RUNNER_OS')}")
print(f"Context: {os.environ.get('GITHUB_EVENT_NAME')}")
print("="*50 + "\n")

setup(
    name="poc-package",
    version="0.0.1",
)
