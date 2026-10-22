#!/usr/bin/env bash

changed_content=$(git --no-pager diff --diff-filter=ACMRT HEAD~$AZURE_EXTENSION_COMMIT_NUM -- src/index.json)
if [[ -z "$changed_content" ]]; then
    echo "index.json not modified. End task."
    exit 0
fi

echo "Listing Available Extensions:"
az extension list-available -otable

# turn off telemetry as it crowds output
export AZURE_CORE_COLLECT_TELEMETRY=False

# use index.json in master branch
export AZURE_EXTENSION_INDEX_URL=https://raw.githubusercontent.com/Azure/azure-cli-extensions/master/src/index.json

output=$(az extension list-available --query [].name -otsv)
# azure-cli-ml is replaced by ml
# disable alias which relies on Jinja2 2.10
# disable rdbms-connect and deploy-to-azure which cause cmd tree build failures
blocklist=("azure-cli-ml" "alias" "rdbms-connect" "deploy-to-azure")

rm -f ~/.azure/extCmdTreeToUpload.json

filter_exts=""
for ext in $output; do
    ext=${ext%$'\r'}   # Remove a trailing newline when running on Windows.
    if [[ " ${blocklist[@]} " =~ " ${ext} " ]]; then
        continue
    fi
    filter_exts="${filter_exts} ${ext}"
    echo "Adding extension:" $ext
    az extension add --upgrade -n $ext
    if [ $? != 0 ]
    then
        echo "Failed to load:" $ext
        exit 1
    fi
done

# Preserve the CLI environment from azdev setup; the legacy storage SDK pin
# causes pip to downgrade the CLI below current extensions' minimum version.
# regex is needed by arcdata.
python -m pip install requests regex
python $(cd $(dirname $0); pwd)/update_ext_cmd_tree.py $filter_exts
