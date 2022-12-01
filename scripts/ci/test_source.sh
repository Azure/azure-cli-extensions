#!/usr/bin/env bash
set -ex

# Install CLI & CLI testsdk
echo "Installing azure-cli-testsdk, azure-cli-core, azure-cli from source code"
git clone https://github.com/Azure/azure-cli --depth 1
find azure-cli/src/ -name setup.py -type f | xargs -I {} dirname {} | grep -v azure-cli-testsdk | xargs -I {} pip install --editable {} --no-deps
pip install --editable azure-cli/src/azure-cli-testsdk
pip install -r azure-cli/src/azure-cli/requirements.py3.$(uname).txt
echo "Installed."

pip list -v
az --version

python ./scripts/ci/test_source.py -v

echo "OK. Completed tests."
