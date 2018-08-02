#!/usr/bin/env bash
set -x

# Install CLI & CLI testsdk
echo "Installing azure-cli-dev-tools and azure-cli..."
pip install --pre azure-cli --extra-index-url https://azurecliprod.blob.core.windows.net/edge
pip install -e "git+https://github.com/Azure/azure-cli@dev#egg=azure-cli-dev-tools&subdirectory=tools" -q
echo "Installed."

azdev cli-lint --ci
echo "OK. Completed tests."
