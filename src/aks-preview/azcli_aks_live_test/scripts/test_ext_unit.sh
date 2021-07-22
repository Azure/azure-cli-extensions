#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# const
aks_preview_base_dir="azure-cli-extensions/src/aks-preview/azext_aks_preview"

# activate virtualenv
source azEnv/bin/activate

# setup aks-preview
./scripts/setup_venv.sh setup-akspreview

# unit test & coverage report
azext_aks_preview_unit_test_failed=""
pushd ${aks_preview_base_dir}
# clean existing coverage report
(coverage combine || true) && (coverage erase || true)
# perform unit test with module 'unittest'
# since recording test (performed in test_ext_live.sh) is based on module 'pytest', so skip here
# coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -p -m pytest
if ! coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -p -m unittest discover; then
    azext_aks_preview_unit_test_failed="true"
fi
# generate & copy coverage report
coverage combine
coverage report -m
coverage json -o coverage_azext_aks_preview.json
popd
mkdir -p reports/ && cp ${aks_preview_base_dir}/coverage_azext_aks_preview.json reports/

if [[ ${azext_aks_preview_unit_test_failed} == "true" ]]; then
    echo "Unit test failed!"
    exit 1
fi
