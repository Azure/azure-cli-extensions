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
[[ -z "${CLI_TEST_MATRIX}" ]] && (echo "CLI_TEST_MATRIX is empty")
[[ -z "${CLI_TEST_FILTER}" ]] && (echo "CLI_TEST_FILTER is empty")
[[ -z "${CLI_TEST_COVERAGE}" ]] && (echo "CLI_TEST_COVERAGE is empty")

# activate virtualenv
source azEnv/bin/activate

# remove aks-preview
source ./scripts/setup_venv.sh
removeAKSPreview

# prepare running options
# base options
base_options="-c --no-exitfirst --report-path ./reports --reruns 3 --capture=sys"
# parallel
if [[ ${PARALLELISM} -ge 2 ]]; then
    base_options+=" -j ${PARALLELISM}"
else
    base_options+=" -s"
fi

# filter options
filter_options=""
# cli matrix
if [[ -n ${CLI_TEST_MATRIX} ]]; then
    filter_options+=" -cm ./configs/${CLI_TEST_MATRIX}"
fi
# cli extra filter
if [[ -n ${CLI_TEST_FILTER} ]]; then
    filter_options+=" -cf ${CLI_TEST_FILTER}"
fi
# cli extra coverage
if [[ -n ${CLI_TEST_COVERAGE} ]]; then
    filter_options+=" -cc ${CLI_TEST_COVERAGE}"
fi

# recording test
if [[ ${TEST_MODE} == "record" || ${TEST_MODE} == "all" ]]; then
    echo "Test in recording mode!"
    coverage_options=" -cc test_aks_commands.AzureKubernetesServiceScenarioTest"
    recording_options="${base_options}${coverage_options}"
    recording_options+=" --json-report-file=cli_recording_report.json"
    recording_options+=" --xml-file=cli_recording_result.xml"
    echo "recording options: ${recording_options}"
    azaks ${recording_options}
fi

# live test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live mode!"
    az login --service-principal -u "${AZCLI_ALT_CLIENT_ID}" -p "${AZCLI_ALT_CLIENT_SECRET}" -t "${TENANT_ID}"
    az account set -s "${AZCLI_ALT_SUBSCRIPTION_ID}"
    az account show
    live_options="${base_options}${filter_options}"
    live_options+=" -l --json-report-file=cli_live_report.json"
    live_options+=" --xml-file=cli_live_result.xml"
    echo "live options: ${live_options}"
    azaks ${live_options}
fi

# re-recording test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in re-recording mode(after live test)!"
    re_recording_options="${base_options}${filter_options}"
    re_recording_options+=" --json-report-file=cli_re_recording_report.json"
    re_recording_options+=" --xml-file=cli_re_recording_result.xml"
    echo "re-recording options: ${re_recording_options}"
    azaks ${re_recording_options}
fi
