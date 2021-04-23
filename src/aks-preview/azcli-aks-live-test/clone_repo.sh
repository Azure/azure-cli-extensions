#!/bin/bash

set -eux
pwd

# clone azure-cli (default is the official repo)
# git clone https://github.com/Azure/azure-cli.git
git clone $CLI_REPO

# ckeckout to a specific azure-cli branch (default is the dev branch)
pushd azure-cli/
git branch -a
git checkout $CLI_BRANCH
popd

# clone azure-cli-extensions when manually specify the extension repo
if [[ $MANUAL_EXT == true && -n $EXT_REPO && -n $EXT_BRANCH ]]; then
    echo "Manually specify the extension repo, delete the current 'azure-cli-extensions' directory!"
    rm -rf azure-cli-extensions/
    git clone $EXT_REPO
    pushd azure-cli-extensions/
    git checkout $EXT_BRANCH
    popd
fi

# check current branch & commit logs in azure-cli-extensions
pushd azure-cli-extensions/
git branch -a
git log -10
popd

# move live test related files to the same level as the checkout directory ($(Agent.BuildDirectory)/s)
mv azure-cli-extensions/src/aks-preview/azcli-aks-live-test/* ./
ls -alh
