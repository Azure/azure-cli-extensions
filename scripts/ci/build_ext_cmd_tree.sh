#!/usr/bin/env bash

changed_content=$(git --no-pager diff --diff-filter=ACMRT HEAD~$AZURE_EXTENSION_COMMIT_NUM -- src/index.json)
if [[ -z "$changed_content" ]]; then
    echo "index.json not modified. End task."
    exit 0
fi

pip install azure-cli-core azure-cli requests
pip install azure-storage-blob==1.5.0
echo "Listing Available Extensions:"
az extension list-available -otable

# turn off telemetry as it crowds output
export AZURE_CORE_COLLECT_TELEMETRY=False

# wait for the index.json to be synced in storage account
# Remove this when we can support using customized index.json
sleep 360

output=$(az extension list-available --query [].name -otsv)
# azure-cli-iot-ext is the deprecated old versions of the renamed azure-iot extension
blocklist=("azure-cli-iot-ext")

rm -f ~/.azure/extCmdTreeToUpload.json

filter_exts=""
for ext in $output; do
    ext=${ext%$'\r'}   # Remove a trailing newline when running on Windows.
    if [[ " ${blocklist[@]} " =~ " ${ext} " ]]; then
        continue
    fi
    filter_exts="${filter_exts} ${ext}"
    echo "Adding extension:" $ext
    az extension add -n $ext
    if [ $? != 0 ]
    then
        echo "Failed to load:" $ext
        exit 1
    fi
done

python $(cd $(dirname $0); pwd)/update_ext_cmd_tree.py $filter_exts
