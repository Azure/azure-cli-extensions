#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
# take the first arg as test mode
mode=${1:-"cli"}
[[ -z "${WIKI_LINK}" ]] && (echo "WIKI_LINK is empty"; exit 1)
[[ -z "${ACS_BASE_DIR}" ]] && (echo "ACS_BASE_DIR is empty"; exit 1)
[[ -z "${AKS_PREVIEW_BASE_DIR}" ]] && (echo "AKS_PREVIEW_BASE_DIR is empty"; exit 1)
[[ -z "${IGNORE_EXIT_CODE}" ]] && (echo "IGNORE_EXIT_CODE is empty")
[[ -z "${CLI_COVERAGE_CONFIG}" ]] && (echo "CLI_COVERAGE_CONFIG is empty")
[[ -z "${EXT_COVERAGE_CONFIG}" ]] && (echo "EXT_COVERAGE_CONFIG is empty")

# activate virtualenv
source azEnv/bin/activate

# config aks-preview
source ./scripts/setup_venv.sh
removeAKSPreview
if [[ ${mode} == "ext" ]]; then
    setupAKSPreview
    igniteAKSPreview
fi

# check mode
if [[ ${mode} == "cli" ]]; then
    UT_BASE_DIR=${ACS_BASE_DIR}
elif [[ ${mode} == "ext" ]]; then
    UT_BASE_DIR=${AKS_PREVIEW_BASE_DIR}
else
    echo "Unsupported coverage mode, please choose \"cli\" or \"ext\""
    exit 1
fi

# unit test & coverage report
pushd ${UT_BASE_DIR}

# clean existing coverage report
(coverage combine || true) && (coverage erase || true)

# perform unit test with module 'unittest'
test_result=0
coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -m pytest tests/latest/ || test_result=$?

# generate coverage report
coverage combine || true
coverage report -m
coverage json -o coverage.json
popd

# copy coverage report
mkdir -p reports/ && cp ${UT_BASE_DIR}/coverage.json reports/

# prepare running options
# unit test result
options="--unit-test-result ${test_result} --coverage-report ${UT_BASE_DIR}/coverage.json"
# ignore exit code
if [[ -n ${IGNORE_EXIT_CODE} ]]; then
    options+=" --ignore-exit-code"
fi
if [[ ${mode} == "cli" && -n ${CLI_COVERAGE_CONFIG} ]]; then
    options+=" --coverage-config ./configs/${CLI_COVERAGE_CONFIG}"
fi
if [[ ${mode} == "ext" && -n ${EXT_COVERAGE_CONFIG} ]]; then
    options+=" --coverage-config ./configs/${EXT_COVERAGE_CONFIG}"
fi

combined_result=0
azaks-cov ${options} || combined_result=$?
echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
exit ${combined_result}
