#!/usr/bin/env bash
set -ex

# Install CLI & Dev Tools
echo "Installing azure-cli..."
pip install --pre azure-cli --extra-index-url https://azurecliprod.blob.core.windows.net/edge
echo "Installed."
az --version
set +x

# check for index updates
modified_extensions=$(python ./scripts/ci/index_changes.py)
echo "Found the following modified extension entries:"
echo "$modified_extensions"

# run linter on each modified extension entry
while read line; do
    if [ -z "$line" ]; then
        continue
    fi
    part_array=($line)
    ext=${part_array[0]}
    source=${part_array[1]}
    echo
    echo "New index entries detected for extension:" $ext
    echo "Adding latest entry from source:" $source
    set +e
    az extension add -s $source -y
    if [ $? != 0 ]; then
        continue
    fi
    set -e
    echo "Load all commands"
    az self-test
    echo "Running linter"
    azdev linter $ext
    az extension remove -n $ext
    echo $ext "extension has been removed."
done <<< "$modified_extensions"

echo "OK. Completed Verification of Modified Extensions."
