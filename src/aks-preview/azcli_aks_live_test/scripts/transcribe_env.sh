#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
# from variable group
# client id, secret and tenant id of sp 'azcli-aks-live-test'
[[ -z "${AZCLI_ALT_CLIENT_ID}" ]] && (echo "AZCLI_ALT_CLIENT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_SUBSCRIPTION_ID}" ]] && (echo "AZCLI_ALT_SUBSCRIPTION_ID is empty"; exit 1)
[[ -z "${TENANT_ID}" ]] && (echo "TENANT_ID is empty"; exit 1)
# basic ubuntu image with python3 pre-installed, hosted on some container registry
[[ -z "${IMAGE_PREFIX}" ]] && (echo "IMAGE_PREFIX is empty"; exit 1)
[[ -z "${IMAGE_NAME}" ]] && (echo "IMAGE_NAME is empty"; exit 1)
[[ -z "${IMAGE_TAG}" ]] && (echo "IMAGE_TAG is empty"; exit 1)
# specify the version of python3
[[ -z "${PYTHON_VERSION}" ]] && (echo "PYTHON_VERSION is empty"; exit 1)

# from azure devops
[[ -z "${BUILD_REASON}" ]] && (echo "BUILD_REASON is empty")
[[ -z "${SYSTEM_PULLREQUEST_TARGETBRANCH}" ]] && (echo "SYSTEM_PULLREQUEST_TARGETBRANCH is empty")

# custom
[[ -z "${TEST_LOCATION}" ]] && (echo "TEST_LOCATION is empty"; exit 1)
[[ -z "${COVERAGE}" ]] && (echo "COVERAGE is empty"; exit 1)
[[ -z "${TEST_MODE}" ]] && (echo "TEST_MODE is empty"; exit 1)
[[ -z "${PARALLELISM}" ]] && (echo "PARALLELISM is empty"; exit 1)
[[ -z "${TEST_CASES}" ]] && (echo "TEST_CASES is empty")
[[ -z "${CLI_TEST_MATRIX}" ]] && (echo "CLI_TEST_MATRIX is empty")
[[ -z "${CLI_TEST_FILTER}" ]] && (echo "CLI_TEST_FILTER is empty")
[[ -z "${CLI_TEST_COVERAGE}" ]] && (echo "CLI_TEST_COVERAGE is empty")
[[ -z "${EXT_TEST_MATRIX}" ]] && (echo "EXT_TEST_MATRIX is empty")
[[ -z "${EXT_TEST_FILTER}" ]] && (echo "EXT_TEST_FILTER is empty")
[[ -z "${EXT_TEST_COVERAGE}" ]] && (echo "EXT_TEST_COVERAGE is empty")
[[ -z "${CLI_REPO}" ]] && (echo "CLI_REPO is empty"; exit 1)
[[ -z "${CLI_BRANCH}" ]] && (echo "CLI_BRANCH is empty"; exit 1)
[[ -z "${EXT_REPO}" ]] && (echo "EXT_REPO is empty"; exit 1)
[[ -z "${EXT_BRANCH}" ]] && (echo "EXT_BRANCH is empty"; exit 1)
[[ -z "${BACKWARD_COMPATIBILITY_TEST}" ]] && (echo "BACKWARD_COMPATIBILITY_TEST is empty")
# base directories for acs, aks-preview and live test
[[ -z "${ACS_BASE_DIR}" ]] && (echo "ACS_BASE_DIR is empty"; exit 1)
[[ -z "${AKS_PREVIEW_BASE_DIR}" ]] && (echo "AKS_PREVIEW_BASE_DIR is empty"; exit 1)
[[ -z "${LIVE_TEST_BASE_DIR}" ]] && (echo "LIVE_TEST_BASE_DIR is empty"; exit 1)

# clear
cat /dev/null > env.list

# tenant, sub, client
echo "TENANT_ID=${TENANT_ID}" >> env.list
echo "AZCLI_ALT_SUBSCRIPTION_ID=${AZCLI_ALT_SUBSCRIPTION_ID}" >> env.list
echo "AZCLI_ALT_CLIENT_ID=${AZCLI_ALT_CLIENT_ID}" >> env.list

# image
echo "IMAGE_PREFIX=${IMAGE_PREFIX}" >> env.list
echo "IMAGE_NAME=${IMAGE_NAME}" >> env.list
echo "IMAGE_TAG=${IMAGE_TAG}" >> env.list

# predefined variables 
echo "BUILD_REASON=${BUILD_REASON}" >> env.list
echo "SYSTEM_PULLREQUEST_TARGETBRANCH=${SYSTEM_PULLREQUEST_TARGETBRANCH}" >> env.list

# python version
echo "PYTHON_VERSION=${PYTHON_VERSION}" >> env.list

# base directories
echo "ACS_BASE_DIR=${ACS_BASE_DIR}" >> env.list
echo "AKS_PREVIEW_BASE_DIR=${AKS_PREVIEW_BASE_DIR}" >> env.list
echo "LIVE_TEST_BASE_DIR=${LIVE_TEST_BASE_DIR}" >> env.list

# azdev env
echo "AZURE_CLI_TEST_DEV_SP_NAME=${AZCLI_ALT_CLIENT_ID}" >> env.list
echo "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION=${TEST_LOCATION}" >> env.list

# test
echo "COVERAGE=${COVERAGE}" >> env.list
echo "TEST_MODE=${TEST_MODE}" >> env.list
echo "PARALLELISM=${PARALLELISM}" >> env.list
echo "TEST_CASES=${TEST_CASES}" >> env.list
echo "CLI_TEST_MATRIX=${CLI_TEST_MATRIX}" >> env.list
echo "CLI_TEST_FILTER=${CLI_TEST_FILTER}" >> env.list
echo "CLI_TEST_COVERAGE=${CLI_TEST_COVERAGE}" >> env.list
echo "EXT_TEST_MATRIX=${EXT_TEST_MATRIX}" >> env.list
echo "EXT_TEST_FILTER=${EXT_TEST_FILTER}" >> env.list
echo "EXT_TEST_COVERAGE=${EXT_TEST_COVERAGE}" >> env.list

# repo
echo "CLI_REPO=${CLI_REPO}" >> env.list
echo "CLI_BRANCH=${CLI_BRANCH}" >> env.list
echo "EXT_REPO=${EXT_REPO}" >> env.list
echo "EXT_BRANCH=${EXT_BRANCH}" >> env.list

# backward compatibility
echo "BACKWARD_COMPATIBILITY_TEST=${BACKWARD_COMPATIBILITY_TEST}" >> env.list