#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${CLI_REPO}" ]] && (echo "CLI_REPO is empty"; exit 1)
[[ -z "${CLI_BRANCH}" ]] && (echo "CLI_BRANCH is empty"; exit 1)
[[ -z "${EXT_REPO}" ]] && (echo "EXT_REPO is empty"; exit 1)
[[ -z "${EXT_BRANCH}" ]] && (echo "EXT_BRANCH is empty"; exit 1)
[[ -z "${MANUAL_EXT}" ]] && (echo "MANUAL_EXT is empty"; exit 1)

# dir
pwd
ls -alh

# clone azure-cli (default is the official repo)
# git clone https://github.com/Azure/azure-cli.git
git clone ${CLI_REPO}

# ckeckout to a specific azure-cli branch (default is the dev branch)
pushd azure-cli/
git branch -a
git checkout ${CLI_BRANCH}
popd

# clone azure-cli-extensions when manually specify the extension repo
if [[ ${MANUAL_EXT} == true ]]; then
    echo "Manually specify the extension repo, delete the current 'azure-cli-extensions' directory!"
    rm -rf azure-cli-extensions/
    git clone ${EXT_REPO}
    pushd azure-cli-extensions/
    git branch -a
    git checkout ${EXT_BRANCH}
    popd
fi

# check current branch & commit logs in azure-cli-extensions
pushd azure-cli-extensions/
git branch -a
git log -10
popd

# copy live test related files to the same level as the checkout directory ($(Agent.BuildDirectory)/s)
cp -rT azure-cli-extensions/src/aks-preview/azcli_aks_live_test/ ./
cp -r azure-cli-extensions/src/aks-preview/az_aks_tool/ ./
ls -alh
