#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# const
acs_base_dir="azure-cli/src/azure-cli/azure/cli/command_modules/acs"

# activate virtualenv
source azEnv/bin/activate

# remove aks-preview
source ./scripts/setup_venv.sh
removeAKSPreview

# unit test & coverage report
acs_unit_test_failed=""
pushd ${acs_base_dir}
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
mkdir -p reports/ && cp ${acs_base_dir}/coverage_acs.json reports/

if [[ ${acs_unit_test_failed} == "true" ]]; then
    echo "Unit test failed!"
    exit 1
fi
