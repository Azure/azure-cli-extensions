#!/bin/bash

set -eux
pwd

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

# Ensure that the command index is updated by calling a specific command in aks-preview, so that all the commands defined in aks-preview are loaded correctly
# Otherwise, cold boot execution of azdev test may use the api version adopted by the acs command group in azure-cli (which may diverge from the api version used in current aks-preview)
retry_count=0
while ! az aks command invoke --help && [[ $retry_count < 3 ]]
do
    retry_count=`expr $retry_count + 1`
    echo $retry_count"th retry to install aks-preview..." 
    azdev extension add aks-preview --debug
    az extension list --debug
    azdev extension list --debug | grep "aks-preview" -C 5
    deactivate
    source azEnv/bin/activate
done

# unit test & coverage report
# azcli_aks_live_test
azcli_aks_live_test_unit_test_result=""
pushd azure-cli-extensions/src/aks-preview/azcli_aks_live_test/
# clean existing coverage report
(coverage combine || true) && (coverage erase || true)
if ! coverage run --source=. --omit=*/tests/* -p -m unittest discover; then
    azcli_aks_live_test_unit_test_result="error"
fi
# currently no test written in pytest format under 'azcli_aks_live_test/'
# coverage run --source=. --omit=*/tests/* -p -m pytest
coverage combine && coverage json -o coverage_azcli_aks_live_test.json
coverage report -m
popd
cp azure-cli-extensions/src/aks-preview/azcli_aks_live_test/coverage_azcli_aks_live_test.json reports/

# azext_aks_preview
azext_aks_preview_unit_test_result=""
pushd azure-cli-extensions/src/aks-preview/azext_aks_preview
# clean existing coverage report
(coverage combine || true) && (coverage erase || true)
# currently test using module 'unittest' is the same as module 'pytest', and test using 'pytest' is just recording test
if ! coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -p -m unittest discover || coverage run --source=. --omit=*/vendored_sdks/*,*/tests/* -p -m pytest; then
    azext_aks_preview_unit_test_result="error"
fi
coverage combine && coverage json -o coverage_azext_aks_preview.json
coverage report -m
popd
cp azure-cli-extensions/src/aks-preview/azext_aks_preview/coverage_azext_aks_preview.json reports/

if [[ $azcli_aks_live_test_unit_test_result == "error" || $azext_aks_preview_unit_test_result == "error" ]]; then
    echo "Unit test failed!"
    exit 1
fi

# prepare run flags
run_flags="-em ext_matrix_default.json --no-exitfirst --discover --report-path ./ --reruns 3 --capture=sys"
# parallel
if [ $PARALLELISM -ge 2 ]; then
    run_flags+=" -n $PARALLELISM"
else
    run_flags+=" -s"
fi
# ext filter
if [[ -n $EXT_TEST_FILTER ]]; then
    run_flags+=" -ef $EXT_TEST_FILTER"
fi
# ext extra coverage
if [[ $EXT_TEST_COVERAGE ]]; then
    run_flags+=" -ec $EXT_TEST_COVERAGE"
fi

# recording test
if [[ $TEST_MODE == "record" || $TEST_MODE == "all" ]]; then
    echo "Test in record mode!"
    run_flags+=" --json-report-file=ext_report.json"
    run_flags+=" --xml-file=ext_result.xml"
    echo "run flags: ${run_flags}"
    echo ${run_flags} | xargs python -u az_aks_tool/main.py
    cp ext_report.json ext_result.xml reports/
fi

# live test
if [[ $TEST_MODE == "live" || $TEST_MODE == "all" ]]; then
    echo "Test in live mode!"
    az login --service-principal -u $AZCLI_ALT_CLIENT_ID -p $AZCLI_ALT_CLIENT_SECRET -t $TENANT_ID
    az account set -s $AZCLI_ALT_SUBSCRIPTION_ID
    az account show
    run_flags+=" -l --json-report-file=ext_live_report.json"
    run_flags+=" --xml-file=ext_live_result.xml"
    echo "run flags: ${run_flags}"
    echo ${run_flags} | xargs python -u az_aks_tool/main.py 
    cp ext_live_report.json ext_live_result.xml reports/
fi
