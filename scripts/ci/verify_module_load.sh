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
echo "Found the following modified extension entries:"
echo "$modified_extensions"

# add each modified extension entry.
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
done <<< "$modified_extensions"

exit_code=0
msg="OK. All modules loaded successfuly."

# verify that all modules are loaded properly.
echo
echo "Loading all modules..."

set +e
azdev verify load-all
if [ $? != 0 ]
then
    exit_code=1
    msg="A module load was unsuccessful."
fi

# remove the added extensions
while read line; do
    if [ -z "$line" ]; then
        continue
    fi
    part_array=($line)
    ext=${part_array[0]}
    az extension remove -n $ext
    echo $ext "extension has been removed."
done <<< "$modified_extensions"

echo $msg
exit $exit_code

