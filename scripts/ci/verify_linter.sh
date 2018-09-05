#!/usr/bin/env bash
set -ex

# Install CLI & Dev Tools
echo "Installing azure-cli-dev-tools and azure-cli..."
pip install --pre azure-cli --extra-index-url https://azurecliprod.blob.core.windows.net/edge
pip install -e "git+https://github.com/Azure/azure-cli@dev#egg=azure-cli-dev-tools&subdirectory=tools" -q
echo "Installed."
az --version
set +x

# check for index updates
modified_extensions=$(python ./scripts/ci/index_changes.py)
echo "Found the following modified extensions:"
echo "$modified_extensions"

# run linter on each modified extension
for ext in $modified_extensions; do
    echo
    echo "Adding extension:" $ext
    az extension add -n $ext
    echo "Running linter on extension:" $ext
    azdev cli-lint --ci --extensions $ext
    az extension remove -n $ext
    echo $ext "extension has been removed."
done

echo "OK. Completed Linting"
