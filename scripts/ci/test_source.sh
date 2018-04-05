#!/usr/bin/env bash
set -ex

# Install CLI & CLI testsdk
echo "Installing azure-cli-testsdk and azure-cli..."
pip install --pre azure-cli --extra-index-url https://azurecliprod.blob.core.windows.net/edge
pip install "git+https://github.com/Azure/azure-cli@dev#egg=azure-cli-testsdk&subdirectory=src/azure-cli-testsdk" -q
echo "Installed."

python ./scripts/ci/test_source.py -v

echo "OK. Completed tests."
