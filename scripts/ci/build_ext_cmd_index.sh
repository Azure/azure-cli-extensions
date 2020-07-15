#!/usr/bin/env bash

echo "Listing Available Extensions:"
az extension list-available -otable

# turn off telemetry as it crowds output
export AZURE_CORE_COLLECT_TELEMETRY=False

output=$(az extension list-available --query [].name -otsv)
blocklist=("azure-cli-iot-ext")  # azure-cli-iot-ext is the deprecated old versions of the renamed azure-iot extension
exit_code=0

for ext in $output; do
    ext=${ext%$'\r'}   # Remove a trailing newline when running on Windows.
    if [[ " ${blocklist[@]} " =~ " ${ext} " ]]; then
        continue
    fi

    echo "Adding extension:" $ext
    az extension add -n $ext
    if [ $? != 0 ]
    then
        exit_code=1
        echo "Failed to load:" $ext
    fi
    python $(cd $(dirname $0); pwd)/update_ext_cmd_index.py $ext
done

exit $exit_code
