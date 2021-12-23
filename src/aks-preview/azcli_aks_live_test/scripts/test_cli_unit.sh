#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${WIKI_LINK}" ]] && (echo "WIKI_LINK is empty"; exit 1)
[[ -z "${ACS_BASE_DIR}" ]] && (echo "ACS_BASE_DIR is empty"; exit 1)
[[ -z "${IGNORE_EXIT_CODE}" ]] && (echo "IGNORE_EXIT_CODE is empty")
[[ -z "${CLI_COVERAGE_CONFIG}" ]] && (echo "CLI_COVERAGE_CONFIG is empty")

# activate virtualenv
source azEnv/bin/activate

# remove aks-preview
source ./scripts/setup_venv.sh
removeAKSPreview

# unit test & coverage report
pushd ${ACS_BASE_DIR}

# clean existing coverage report
(coverage combine || true) && (coverage erase || true)

# perform unit test with module 'unittest'
test_result=0
coverage run --source=. --omit=*/tests/* -m pytest tests/latest/ || test_result=$?

# generate coverage report
coverage combine || true
coverage report -m
coverage json -o coverage_acs.json
popd

# copy coverage report
mkdir -p reports/ && cp ${ACS_BASE_DIR}/coverage_acs.json reports/

# prepare running options
# unit test result
options="--unit-test-result ${test_result} --coverage-report ${ACS_BASE_DIR}/coverage_acs.json"
# ignore exit code
if [[ -n ${IGNORE_EXIT_CODE} ]]; then
    options+=" --ignore-exit-code"
fi
if [[ -n ${CLI_COVERAGE_CONFIG} ]]; then
    options+=" --coverage-config ./configs/${CLI_COVERAGE_CONFIG}"
fi

combined_result=0
azaks-cov ${options} || combined_result=$?
echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
exit ${combined_result}
