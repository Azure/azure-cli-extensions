#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${WIKI_LINK}" ]] && (echo "WIKI_LINK is empty"; exit 1)
[[ -z "${AKS_PREVIEW_BASE_DIR}" ]] && (echo "AKS_PREVIEW_BASE_DIR is empty"; exit 1)

# activate virtualenv
source azEnv/bin/activate

# setup aks-preview
./scripts/setup_venv.sh setup-akspreview

# unit test & coverage report
azext_aks_preview_unit_test_failed=""
pushd ${AKS_PREVIEW_BASE_DIR}
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
mkdir -p reports/ && cp ${AKS_PREVIEW_BASE_DIR}/coverage_azext_aks_preview.json reports/

if [[ ${azext_aks_preview_unit_test_failed} == "true" ]]; then
    echo "Unit test failed!"
    echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
    exit 1
fi
