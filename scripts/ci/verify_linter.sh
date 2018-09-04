#!/usr/bin/env bash
set -x

# Install CLI & Dev Tools
echo "Installing azure-cli-dev-tools and azure-cli..."
pip install --pre azure-cli --extra-index-url https://azurecliprod.blob.core.windows.net/edge
pip install -e "git+https://github.com/Azure/azure-cli@dev#egg=azure-cli-dev-tools&subdirectory=tools" -q
echo "Installed."

# check for index updates
public_index=$(az extension list-available -d)
index_file=$(cat ./src/index.json)

python ./scripts/ci/index_changes.py "$index_file" "$public_index"

azdev cli-lint --ci
echo "OK. Completed Linting"
