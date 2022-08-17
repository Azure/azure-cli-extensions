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
[[ -z "${BUILD_REASON}" ]] && (echo "BUILD_REASON is empty"; exit 1)
[[ -z "${LIVE_TEST_BASE_DIR}" ]] && (echo "LIVE_TEST_BASE_DIR is empty"; exit 1)

# clone azure-cli (default is the official repo)
git clone "${CLI_REPO}"

# ckeckout to a specific azure-cli branch (default is the dev branch)
pushd azure-cli/
git branch -a
git checkout "${CLI_BRANCH}"
popd

# clone azure-cli-extensions when manually trigger the pipeline
if [[ ${BUILD_REASON} == "Manual" ]]; then
    echo "Manually trigger the pipeline, delete the current 'azure-cli-extensions' directory!"
    rm -rf azure-cli-extensions/
    git clone "${EXT_REPO}"
    pushd azure-cli-extensions/
    git branch -a
    git checkout "${EXT_BRANCH}"
    popd
fi

# check current branch & commit logs in azure-cli-extensions
pushd azure-cli-extensions/
git branch -a
git log -10
popd

# copy live test related files to the same level as the checkout directory ($(Agent.BuildDirectory)/s)
cp -rT "${LIVE_TEST_BASE_DIR}" ./
ls -alh
