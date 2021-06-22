#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# dir
pwd
ls -alh

# activate virtualenv
source azEnv/bin/activate

# remove extension
echo "Remove existing aks-preview extension (if any)"
if az extension remove --name aks-preview || azdev extension remove aks-preview; then
    deactivate
    source azEnv/bin/activate
fi

# install latest extension
echo "Install the latest aks-preview extension and re-activate the virtualenv"
azdev extension add aks-preview
az extension list
azdev extension list | grep "aks-preview" -C 5
deactivate
source azEnv/bin/activate

# use a fake command to force trigger the command index update of azure-cli, in order to load aks-preview commands
# otherwise, cold boot execution of azdev test / pytest would only use commands in the acs module
az aks fake-command --debug || true

# unit test & coverage report
# az_aks_tool
az_aks_tool_unit_test_result=""
pushd azure-cli-extensions/src/aks-preview/az_aks_tool/
# clean existing coverage report
(coverage combine || true) && (coverage erase || true)
if ! coverage run --source=. --omit=*/tests/* -p -m unittest discover; then
    az_aks_tool_unit_test_result="error"
fi
# currently no test written in pytest format under 'az_aks_tool/'
# coverage run --source=. --omit=*/tests/* -p -m pytest
coverage combine && coverage json -o coverage_az_aks_tool.json
coverage report -m
popd
cp azure-cli-extensions/src/aks-preview/az_aks_tool/coverage_az_aks_tool.json reports/

# azext_aks_preview
azext_aks_preview_unit_test_result=""
pushd azure-cli-extensions/src/aks-preview/azext_aks_preview
# clean existing coverage report
(coverage combine || true) && (coverage erase || true)
# currently test using module 'unittest' is the same as module 'pytest', and test using 'pytest' is just recording test
if ! coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -p -m unittest discover || ! coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -p -m pytest; then
    azext_aks_preview_unit_test_result="error"
fi
coverage combine && coverage json -o coverage_azext_aks_preview.json
coverage report -m
popd
cp azure-cli-extensions/src/aks-preview/azext_aks_preview/coverage_azext_aks_preview.json reports/

if [[ ${az_aks_tool_unit_test_result} == "error" || ${azext_aks_preview_unit_test_result} == "error" ]]; then
    echo "Unit test failed!"
    exit 1
fi
