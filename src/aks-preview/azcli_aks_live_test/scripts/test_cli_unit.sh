#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${WIKI_LINK}" ]] && (echo "WIKI_LINK is empty"; exit 1)
[[ -z "${ACS_BASE_DIR}" ]] && (echo "ACS_BASE_DIR is empty"; exit 1)

# activate virtualenv
source azEnv/bin/activate

# remove aks-preview
source ./scripts/setup_venv.sh
removeAKSPreview

# unit test & coverage report
acs_unit_test_failed=""
pushd ${ACS_BASE_DIR}
# clean existing coverage report
(coverage combine || true) && (coverage erase || true)
# perform unit test with module 'unittest'
# since recording test (performed in test_cli_live.sh) is based on module 'pytest', so skip here
# coverage run --source=. --omit=*/tests/* -p -m pytest
if ! coverage run --source=. --omit=*/tests/* -p -m unittest discover; then
    acs_unit_test_failed="true"
fi
# generate & copy coverage report
coverage combine
coverage report -m
coverage json -o coverage_acs.json
popd
mkdir -p reports/ && cp ${ACS_BASE_DIR}/coverage_acs.json reports/

if [[ ${acs_unit_test_failed} == "true" ]]; then
    echo "Unit test failed!"
    echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
    exit 1
fi
