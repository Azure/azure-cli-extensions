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
[[ -z "${EXT_TEST_MATRIX}" ]] && (echo "EXT_TEST_MATRIX is empty")
[[ -z "${EXT_TEST_FILTER}" ]] && (echo "EXT_TEST_FILTER is empty")
[[ -z "${EXT_TEST_COVERAGE}" ]] && (echo "EXT_TEST_COVERAGE is empty")

# activate virtualenv
source azEnv/bin/activate

# setup aks-preview
./scripts/setup_venv.sh setup-akspreview

# login before the recording test to avoid the newly added test case does not include a corresponding
# recording file and fall back to live mode, otherwise it will prompt `az login`.
az login --service-principal -u "${AZCLI_ALT_CLIENT_ID}" -p "${AZCLI_ALT_CLIENT_SECRET}" -t "${TENANT_ID}"
az account set -s "${AZCLI_ALT_SUBSCRIPTION_ID}"
az account show

# prepare running options
# base options
base_options="-e --no-exitfirst --report-path ./reports --reruns 3 --capture=sys"
# parallel
if [[ ${PARALLELISM} -ge 2 ]]; then
    base_options+=" -j ${PARALLELISM}"
else
    base_options+=" -s"
fi

# filter options
filter_options=""
# ext matrix
if [[ -n ${EXT_TEST_MATRIX} ]]; then
    filter_options+=" -em ./configs/${EXT_TEST_MATRIX}"
fi
# ext extra filter
if [[ -n ${EXT_TEST_FILTER} ]]; then
    filter_options+=" -ef ${EXT_TEST_FILTER}"
fi
# ext extra coverage
if [[ -n ${EXT_TEST_COVERAGE} ]]; then
    filter_options+=" -ec ${EXT_TEST_COVERAGE}"
fi

# recording test
if [[ ${TEST_MODE} == "recording" || ${TEST_MODE} == "all" ]]; then
    echo "Test in recording mode!"
    coverage_options=" -ec test_aks_commands.AzureKubernetesServiceScenarioTest"
    recording_options="${base_options}${coverage_options}"
    recording_options+=" --json-report-file=ext_recording_report.json"
    recording_options+=" --xml-file=ext_recording_result.xml"
    echo "Recording test options: ${recording_options}"
    test_result=0
    azaks ${recording_options} || test_result=$?
    if [[ ${test_result} -ne 0 ]]; then
        echo "Recording test failed!"
        echo "Please refer to this wiki (https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/156735/AZCLI-AKS-Live-Unit-Test-Pipeline) for troubleshooting guidelines."
        exit ${test_result}
    else
        echo -e "Recording test passed!\n\n"
    fi
fi

# live test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live mode!"
    live_options="${base_options}${filter_options}"
    live_options+=" -l --json-report-file=ext_live_report.json"
    live_options+=" --xml-file=ext_live_result.xml"
    echo "Live test options: ${live_options}"
    test_result=0
    azaks ${live_options} || test_result=$?
    if [[ ${test_result} -ne 0 ]]; then
        echo "Live test failed!"
        echo "Please refer to this wiki (https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/156735/AZCLI-AKS-Live-Unit-Test-Pipeline) for troubleshooting guidelines."
        exit ${test_result}
    else
        echo -e "Live test passed!\n\n"
    fi
fi

# live-replay test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live-replay mode!"
    live_replay_options="${base_options}${filter_options}"
    live_replay_options+=" --json-report-file=ext_live_replay_report.json"
    live_replay_options+=" --xml-file=ext_live_replay_result.xml"
    echo "Live-replay test options: ${live_replay_options}"
    test_result=0
    azaks ${live_replay_options} || test_result=$?
    if [[ ${test_result} -ne 0 ]]; then
        echo "Live-replay test failed!"
        echo "Please refer to this wiki (https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/156735/AZCLI-AKS-Live-Unit-Test-Pipeline) for troubleshooting guidelines."
        exit ${test_result}
    else
        echo -e "Live-replay test passed!\n\n"
    fi
fi
