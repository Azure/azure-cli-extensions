#!/usr/bin/env bash
set -ex

# Install CLI & CLI testsdk
echo "Installing azure-cli-testsdk, azure-cli-core, azure-cli from source code"
git clone https://github.com/Azure/azure-cli --depth 1
# Because the new version has breaking change, so bump to 1.21.1
pip install azure-core==1.21.1
pip install -e azure-cli/src/azure-cli-testsdk
pip install -e azure-cli/src/azure-cli-core
pip install -e azure-cli/src/azure-cli
echo "Installed."

pip list -v
az --version

python ./scripts/ci/test_source.py -v

echo "OK. Completed tests."
