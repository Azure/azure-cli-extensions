#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${TENANT_ID}" ]] && (echo "TENANT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_SUBSCRIPTION_ID}" ]] && (echo "AZCLI_ALT_SUBSCRIPTION_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_CLIENT_ID}" ]] && (echo "AZCLI_ALT_CLIENT_ID is empty"; exit 1)
[[ -z "${TEST_LOCATION}" ]] && (echo "TEST_LOCATION is empty"; exit 1)
[[ -z "${BUILD_REASON}" ]] && (echo "BUILD_REASON is empty")
[[ -z "${SYSTEM_PULLREQUEST_TARGETBRANCH}" ]] && (echo "SYSTEM_PULLREQUEST_TARGETBRANCH is empty")
[[ -z "${COVERAGE}" ]] && (echo "COVERAGE is empty"; exit 1)
[[ -z "${TEST_MODE}" ]] && (echo "TEST_MODE is empty"; exit 1)
[[ -z "${PARALLELISM}" ]] && (echo "PARALLELISM is empty"; exit 1)
[[ -z "${TEST_CASES}" ]] && (echo "TEST_CASES is empty")
[[ -z "${EXT_TEST_MATRIX}" ]] && (echo "EXT_TEST_MATRIX is empty")
[[ -z "${EXT_TEST_FILTER}" ]] && (echo "EXT_TEST_FILTER is empty")
[[ -z "${EXT_TEST_COVERAGE}" ]] && (echo "EXT_TEST_COVERAGE is empty")
[[ -z "${CLI_REPO}" ]] && (echo "CLI_REPO is empty"; exit 1)
[[ -z "${CLI_BRANCH}" ]] && (echo "CLI_BRANCH is empty"; exit 1)
[[ -z "${EXT_REPO}" ]] && (echo "EXT_REPO is empty"; exit 1)
[[ -z "${EXT_BRANCH}" ]] && (echo "EXT_BRANCH is empty"; exit 1)
[[ -z "${MANUAL_EXT}" ]] && (echo "MANUAL_EXT is empty"; exit 1)
[[ -z "${IMAGE_PREFIX}" ]] && (echo "IMAGE_PREFIX is empty"; exit 1)
[[ -z "${IMAGE_NAME}" ]] && (echo "IMAGE_NAME is empty"; exit 1)
[[ -z "${IMAGE_TAG}" ]] && (echo "IMAGE_TAG is empty"; exit 1)
[[ -z "${PYTHON_VERSION}" ]] && (echo "PYTHON_VERSION is empty")

# clear
cat /dev/null > env.list

# tenant, sub, client
echo "TENANT_ID=${TENANT_ID}" >> env.list
echo "AZCLI_ALT_SUBSCRIPTION_ID=${AZCLI_ALT_SUBSCRIPTION_ID}" >> env.list
echo "AZCLI_ALT_CLIENT_ID=${AZCLI_ALT_CLIENT_ID}" >> env.list

# azdev env
echo "AZURE_CLI_TEST_DEV_SP_NAME=${AZCLI_ALT_CLIENT_ID}" >> env.list
echo "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION=${TEST_LOCATION}" >> env.list

# predefined variables 
echo "BUILD_REASON=${BUILD_REASON}" >> env.list
echo "SYSTEM_PULLREQUEST_TARGETBRANCH=${SYSTEM_PULLREQUEST_TARGETBRANCH}" >> env.list

# test
echo "COVERAGE=${COVERAGE}" >> env.list
echo "TEST_MODE=${TEST_MODE}" >> env.list
echo "PARALLELISM=${PARALLELISM}" >> env.list
echo "TEST_CASES=${TEST_CASES}" >> env.list
echo "EXT_TEST_MATRIX=${EXT_TEST_MATRIX}" >> env.list
echo "EXT_TEST_FILTER=${EXT_TEST_FILTER}" >> env.list
echo "EXT_TEST_COVERAGE=${EXT_TEST_COVERAGE}" >> env.list

# repo
echo "CLI_REPO=${CLI_REPO}" >> env.list
echo "CLI_BRANCH=${CLI_BRANCH}" >> env.list
echo "EXT_REPO=${EXT_REPO}" >> env.list
echo "EXT_BRANCH=${EXT_BRANCH}" >> env.list
echo "MANUAL_EXT=${MANUAL_EXT}" >> env.list

# image
echo "IMAGE_PREFIX=${IMAGE_PREFIX}" >> env.list
echo "IMAGE_NAME=${IMAGE_NAME}" >> env.list
echo "IMAGE_TAG=${IMAGE_TAG}" >> env.list

# misc
echo "PYTHON_VERSION=${PYTHON_VERSION}" >> env.list
