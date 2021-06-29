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

# prepare run flags
run_flags="-c --no-exitfirst --report-path ./reports --reruns 3 --capture=sys"
# parallel
if [[ ${PARALLELISM} -ge 2 ]]; then
    run_flags+=" -j ${PARALLELISM}"
else
    run_flags+=" -s"
fi
# cli matrix
if [[ -n ${CLI_TEST_MATRIX} ]]; then
    run_flags+=" -cm ./configs/${CLI_TEST_MATRIX}"
fi
# cli extra filter
if [[ -n ${CLI_TEST_FILTER} ]]; then
    run_flags+=" -cf ${CLI_TEST_FILTER}"
fi
# cli extra coverage
if [[ -n ${CLI_TEST_COVERAGE} ]]; then
    run_flags+=" -cc ${CLI_TEST_COVERAGE}"
fi

# recording test
if [[ ${TEST_MODE} == "record" || ${TEST_MODE} == "all" ]]; then
    echo "Test in record mode!"
    run_flags+=" --json-report-file=cli_report.json"
    run_flags+=" --xml-file=cli_result.xml"
    echo "run flags: ${run_flags}"
    azaks ${run_flags}
fi

# live test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live mode!"
    az login --service-principal -u "${AZCLI_ALT_CLIENT_ID}" -p "${AZCLI_ALT_CLIENT_SECRET}" -t "${TENANT_ID}"
    az account set -s "${AZCLI_ALT_SUBSCRIPTION_ID}"
    az account show
    run_flags+=" -l --json-report-file=cli_live_report.json"
    run_flags+=" --xml-file=cli_live_result.xml"
    echo "run flags: ${run_flags}"
    azaks ${run_flags}
fi
