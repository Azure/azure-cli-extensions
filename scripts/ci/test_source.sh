#!/usr/bin/env bash
set -ex

# Install CLI & CLI testsdk
echo "Installing azure-cli-testsdk and azure-cli..."

# Update the git commit or branch when we need a new version of azure-cli-testsdk
pip install "git+https://github.com/Azure/azure-cli@dev#egg=azure-cli-testsdk&subdirectory=src/azure-cli-testsdk" -q
pip install knack==0.3.1 -q
echo "Installed."

python ./scripts/ci/test_source.py -v

echo "OK. Completed tests."
