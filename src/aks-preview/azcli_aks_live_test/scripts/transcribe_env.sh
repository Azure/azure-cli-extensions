#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
# azure devops
[[ -z "${BUILD_REASON}" ]] && (echo "BUILD_REASON is empty")
[[ -z "${SYSTEM_PULLREQUEST_TARGETBRANCH}" ]] && (echo "SYSTEM_PULLREQUEST_TARGETBRANCH is empty")

# client id, secret and tenant id of sp 'azcli-aks-live-test' (from variable group "azcli-aks-tool")
[[ -z "${AZCLI_ALT_CLIENT_ID}" ]] && (echo "AZCLI_ALT_CLIENT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_SUBSCRIPTION_ID}" ]] && (echo "AZCLI_ALT_SUBSCRIPTION_ID is empty"; exit 1)
[[ -z "${TENANT_ID}" ]] && (echo "TENANT_ID is empty"; exit 1)

# basic ubuntu image with python3 pre-installed, hosted on some container registry (from variable group "azcli-aks-tool")
[[ -z "${IMAGE_PREFIX}" ]] && (echo "IMAGE_PREFIX is empty"; exit 1)
[[ -z "${IMAGE_NAME}" ]] && (echo "IMAGE_NAME is empty"; exit 1)
[[ -z "${IMAGE_TAG}" ]] && (echo "IMAGE_TAG is empty"; exit 1)

# specify the version of python3
[[ -z "${PYTHON_VERSION}" ]] && (echo "PYTHON_VERSION is empty"; exit 1)

# tsg/wiki link
[[ -z "${WIKI_LINK}" ]] && (echo "WIKI_LINK is empty"; exit 1)

# pytest options
[[ -z "${PARALLELISM}" ]] && (echo "PARALLELISM is empty")
[[ -z "${RERUNS}" ]] && (echo "RERUNS is empty")
[[ -z "${NON_BOXED}" ]] && (echo "NON_BOXED is empty")
[[ -z "${LOG_LEVEL}" ]] && (echo "LOG_LEVEL is empty")
[[ -z "${CAPTURE}" ]] && (echo "CAPTURE is empty")
[[ -z "${NO_EXIT_FIRST}" ]] && (echo "NO_EXIT_FIRST is empty")
[[ -z "${LAST_FAILED}" ]] && (echo "LAST_FAILED is empty")

# custom
[[ -z "${IGNORE_EXIT_CODE}" ]] && (echo "IGNORE_EXIT_CODE is empty")
[[ -z "${TEST_LOCATION}" ]] && (echo "TEST_LOCATION is empty"; exit 1)
[[ -z "${COVERAGE}" ]] && (echo "COVERAGE is empty"; exit 1)
[[ -z "${TEST_MODE}" ]] && (echo "TEST_MODE is empty"; exit 1)
[[ -z "${CLI_TEST_MATRIX}" ]] && (echo "CLI_TEST_MATRIX is empty")
[[ -z "${CLI_TEST_FILTER}" ]] && (echo "CLI_TEST_FILTER is empty")
[[ -z "${CLI_TEST_COVERAGE}" ]] && (echo "CLI_TEST_COVERAGE is empty")
[[ -z "${EXT_TEST_MATRIX}" ]] && (echo "EXT_TEST_MATRIX is empty")
[[ -z "${EXT_TEST_FILTER}" ]] && (echo "EXT_TEST_FILTER is empty")
[[ -z "${EXT_TEST_COVERAGE}" ]] && (echo "EXT_TEST_COVERAGE is empty")
[[ -z "${ENABLE_SELECTION}" ]] && (echo "ENABLE_SELECTION is empty")
[[ -z "${SELECTION_MODE}" ]] && (echo "SELECTION_MODE is empty")
[[ -z "${SELECTION_COUNT}" ]] && (echo "SELECTION_COUNT is empty")
[[ -z "${UNFIX_RANDOM_SEED}" ]] && (echo "UNFIX_RANDOM_SEED is empty")
[[ -z "${CLI_COVERAGE_CONFIG}" ]] && (echo "CLI_COVERAGE_CONFIG is empty")
[[ -z "${EXT_COVERAGE_CONFIG}" ]] && (echo "EXT_COVERAGE_CONFIG is empty")
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

# azure devops
echo "BUILD_REASON=${BUILD_REASON}" >> env.list
echo "SYSTEM_PULLREQUEST_TARGETBRANCH=${SYSTEM_PULLREQUEST_TARGETBRANCH}" >> env.list

# tenant, sub, client
echo "TENANT_ID=${TENANT_ID}" >> env.list
echo "AZCLI_ALT_SUBSCRIPTION_ID=${AZCLI_ALT_SUBSCRIPTION_ID}" >> env.list
echo "AZCLI_ALT_CLIENT_ID=${AZCLI_ALT_CLIENT_ID}" >> env.list

# image
echo "IMAGE_PREFIX=${IMAGE_PREFIX}" >> env.list
echo "IMAGE_NAME=${IMAGE_NAME}" >> env.list
echo "IMAGE_TAG=${IMAGE_TAG}" >> env.list

# python version
echo "PYTHON_VERSION=${PYTHON_VERSION}" >> env.list

# tsg/wiki link
echo "WIKI_LINK=${WIKI_LINK}" >> env.list

# pytest options
echo "PARALLELISM=${PARALLELISM}" >> env.list
echo "RERUNS=${RERUNS}" >> env.list
echo "NON_BOXED=${NON_BOXED}" >> env.list
echo "LOG_LEVEL=${LOG_LEVEL}" >> env.list
echo "CAPTURE=${CAPTURE}" >> env.list
echo "NO_EXIT_FIRST=${NO_EXIT_FIRST}" >> env.list
echo "LAST_FAILED=${LAST_FAILED}" >> env.list

# custom - azdev env
echo "AZURE_CLI_TEST_DEV_SP_NAME=${AZCLI_ALT_CLIENT_ID}" >> env.list
echo "AZURE_CLI_TEST_DEV_RESOURCE_GROUP_LOCATION=${TEST_LOCATION}" >> env.list

# custom - az-aks-tool
echo "IGNORE_EXIT_CODE=${IGNORE_EXIT_CODE}" >> env.list
# live test
echo "COVERAGE=${COVERAGE}" >> env.list
echo "TEST_MODE=${TEST_MODE}" >> env.list
echo "CLI_TEST_MATRIX=${CLI_TEST_MATRIX}" >> env.list
echo "CLI_TEST_FILTER=${CLI_TEST_FILTER}" >> env.list
echo "CLI_TEST_COVERAGE=${CLI_TEST_COVERAGE}" >> env.list
echo "EXT_TEST_MATRIX=${EXT_TEST_MATRIX}" >> env.list
echo "EXT_TEST_FILTER=${EXT_TEST_FILTER}" >> env.list
echo "EXT_TEST_COVERAGE=${EXT_TEST_COVERAGE}" >> env.list
echo "ENABLE_SELECTION=${ENABLE_SELECTION}" >> env.list
echo "SELECTION_MODE=${SELECTION_MODE}" >> env.list
echo "SELECTION_COUNT=${SELECTION_COUNT}" >> env.list
echo "UNFIX_RANDOM_SEED=${UNFIX_RANDOM_SEED}" >> env.list
# unit test
echo "CLI_COVERAGE_CONFIG=${CLI_COVERAGE_CONFIG}" >> env.list
echo "EXT_COVERAGE_CONFIG=${EXT_COVERAGE_CONFIG}" >> env.list

# custom - repo
echo "CLI_REPO=${CLI_REPO}" >> env.list
echo "CLI_BRANCH=${CLI_BRANCH}" >> env.list
echo "EXT_REPO=${EXT_REPO}" >> env.list
echo "EXT_BRANCH=${EXT_BRANCH}" >> env.list

# custom - backward compatibility
echo "BACKWARD_COMPATIBILITY_TEST=${BACKWARD_COMPATIBILITY_TEST}" >> env.list

# base directories
echo "ACS_BASE_DIR=${ACS_BASE_DIR}" >> env.list
echo "AKS_PREVIEW_BASE_DIR=${AKS_PREVIEW_BASE_DIR}" >> env.list
echo "LIVE_TEST_BASE_DIR=${LIVE_TEST_BASE_DIR}" >> env.list
