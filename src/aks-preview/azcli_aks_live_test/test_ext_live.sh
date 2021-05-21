#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${TENANT_ID}" ]] && (echo "TENANT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_SUBSCRIPTION_ID}" ]] && (echo "AZCLI_ALT_SUBSCRIPTION_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_CLIENT_ID}" ]] && (echo "AZCLI_ALT_CLIENT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_CLIENT_SECRET}" ]] && (echo "AZCLI_ALT_CLIENT_SECRET is empty"; exit 1)
[[ -z "${TEST_MODE}" ]] && (echo "TEST_MODE is empty"; exit 1)
[[ -z "${PARALLELISM}" ]] && (echo "PARALLELISM is empty"; exit 1)
[[ -z "${TEST_CASES}" ]] && (echo "TEST_CASES is empty")
[[ -z "${EXT_TEST_MATRIX}" ]] && (echo "EXT_TEST_MATRIX is empty")
[[ -z "${EXT_TEST_FILTER}" ]] && (echo "EXT_TEST_FILTER is empty")
[[ -z "${EXT_TEST_COVERAGE}" ]] && (echo "EXT_TEST_COVERAGE is empty")

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

# prepare run flags
run_flags="-e -em ext_matrix_default.json --no-exitfirst --report-path ./reports --reruns 3 --capture=sys"
# parallel
if [ ${PARALLELISM} -ge 2 ]; then
    run_flags+=" -j ${PARALLELISM}"
else
    run_flags+=" -s"
fi
# test cases
if [[ -n ${TEST_CASES} ]]; then
    run_flags+=" -t ${TEST_CASES}"
fi
# ext matrix
if [[ -n ${EXT_TEST_MATRIX} ]]; then
    run_flags+=" -em ${EXT_TEST_MATRIX}"
fi
# ext extra filter
if [[ -n ${EXT_TEST_FILTER} ]]; then
    run_flags+=" -ef ${EXT_TEST_FILTER}"
fi
# ext extra coverage
if [[ -n ${EXT_TEST_COVERAGE} ]]; then
    run_flags+=" -ec ${EXT_TEST_COVERAGE}"
fi

# recording test
if [[ ${TEST_MODE} == "record" || ${TEST_MODE} == "all" ]]; then
    echo "Test in record mode!"
    run_flags+=" --json-report-file=ext_report.json"
    run_flags+=" --xml-file=ext_result.xml"
    echo "run flags: ${run_flags}"
    echo "${run_flags}" | xargs python -u az_aks_tool/main.py
fi

# live test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live mode!"
    az login --service-principal -u ${AZCLI_ALT_CLIENT_ID} -p ${AZCLI_ALT_CLIENT_SECRET} -t ${TENANT_ID}
    az account set -s ${AZCLI_ALT_SUBSCRIPTION_ID}
    az account show
    run_flags+=" -l --json-report-file=ext_live_report.json"
    run_flags+=" --xml-file=ext_live_result.xml"
    echo "run flags: ${run_flags}"
    echo "${run_flags}" | xargs python -u az_aks_tool/main.py 
fi
