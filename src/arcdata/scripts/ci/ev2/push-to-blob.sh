#!/bin/bash

#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
#------------------------------------------------------------------------------

# Description:
#
# This script publishes the arcdata azure-cli-extension whl to production blob
# storage. It assumes that the wheel hase been copied into a folder structure
# as such:
#
#       .
#       ├── arcdata-{CLI_VERSION}-py2.py3-none-any.whl   # The whl to upload
#       └── push-to-blob.sh                              # This script
#       
#
set -e

export scriptPath=$(dirname "$0")
pushd ${scriptPath}
arcdata_ext=(`ls arcdata*.whl`)

echo
echo "------------------------------------------------------------"
echo "Files: ${scriptPath}"
echo "------------------------------------------------------------"
ls -R
echo "Release wheel to upload: '${arcdata_ext[*]}'"
echo "------------------------------------------------------------"
echo

# Check to see if whl is already published and error out
curl https://raw.githubusercontent.com/Azure/azure-cli-extensions/main/src/index.json -o public-index.json
if grep -R "${arcdata_ext[*]}" "public-index.json"
then
  echo "ERROR: ${arcdata_ext[*]} already published!"
  exit 1
fi

az --version
az login --identity
az storage blob upload \
    --auth-mode login \
    --overwrite true \
    --account-name azurearcdatacli \
    --container-name '$web' \
    --file ${arcdata_ext[*]}

echo
echo "Wheel published: https://azurearcdatacli.z13.web.core.windows.net/${arcdata_ext[*]}"
echo
echo "Done."
echo

popd