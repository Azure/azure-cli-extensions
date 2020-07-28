#!/usr/bin/env bash

pip install azure-cli-core azure-cli requests
pip install azure-storage-blob==1.5.0
echo "Listing Available Extensions:"
az extension list-available -otable

# turn off telemetry as it crowds output
export AZURE_CORE_COLLECT_TELEMETRY=False

output=$(az extension list-available --query [].name -otsv)
# azure-cli-iot-ext is the deprecated old versions of the renamed azure-iot extension
# disable hack temporarily as the url is broken
blocklist=("azure-cli-iot-ext" "hack")

rm -f ~/.azure/extCmdIndexToUpload.json

for ext in $output; do
    ext=${ext%$'\r'}   # Remove a trailing newline when running on Windows.
    if [[ " ${blocklist[@]} " =~ " ${ext} " ]]; then
        continue
    fi

    echo "Adding extension:" $ext
    az extension add -n $ext
    if [ $? != 0 ]
    then
        echo "Failed to load:" $ext
        exit 1
    fi
    python $(cd $(dirname $0); pwd)/update_ext_cmd_index.py $ext
done

python $(cd $(dirname $0); pwd)/upload_ext_cmd_index.py
