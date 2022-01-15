#!/usr/bin/env bash

# bash options
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# check var
[[ -z "${WIKI_LINK}" ]] && (echo "WIKI_LINK is empty"; exit 1)
[[ -z "${TENANT_ID}" ]] && (echo "TENANT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_SUBSCRIPTION_ID}" ]] && (echo "AZCLI_ALT_SUBSCRIPTION_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_CLIENT_ID}" ]] && (echo "AZCLI_ALT_CLIENT_ID is empty"; exit 1)
[[ -z "${AZCLI_ALT_CLIENT_SECRET}" ]] && (echo "AZCLI_ALT_CLIENT_SECRET is empty"; exit 1)
[[ -z "${IGNORE_EXIT_CODE}" ]] && (echo "IGNORE_EXIT_CODE is empty")
[[ -z "${TEST_MODE}" ]] && (echo "TEST_MODE is empty"; exit 1)
[[ -z "${PARALLELISM}" ]] && (echo "PARALLELISM is empty")
[[ -z "${RERUNS}" ]] && (echo "RERUNS is empty")
[[ -z "${NON_BOXED}" ]] && (echo "NON_BOXED is empty")
[[ -z "${LOG_LEVEL}" ]] && (echo "LOG_LEVEL is empty")
[[ -z "${CAPTURE}" ]] && (echo "CAPTURE is empty")
[[ -z "${NO_EXIT_FIRST}" ]] && (echo "NO_EXIT_FIRST is empty")
[[ -z "${LAST_FAILED}" ]] && (echo "LAST_FAILED is empty")
[[ -z "${CLI_TEST_MATRIX}" ]] && (echo "CLI_TEST_MATRIX is empty")
[[ -z "${CLI_TEST_FILTER}" ]] && (echo "CLI_TEST_FILTER is empty")
[[ -z "${CLI_TEST_COVERAGE}" ]] && (echo "CLI_TEST_COVERAGE is empty")
[[ -z "${ENABLE_SELECTION}" ]] && (echo "ENABLE_SELECTION is empty")
[[ -z "${SELECTION_MODE}" ]] && (echo "SELECTION_MODE is empty")
[[ -z "${SELECTION_COUNT}" ]] && (echo "SELECTION_COUNT is empty")
[[ -z "${UNFIX_RANDOM_SEED}" ]] && (echo "UNFIX_RANDOM_SEED is empty")

# activate virtualenv
source azEnv/bin/activate

# remove aks-preview
source ./scripts/setup_venv.sh
removeAKSPreview

# login before the recording test to avoid the newly added test case does not include a corresponding
# recording file and fall back to live mode, otherwise it will prompt `az login`.
az login --service-principal -u "${AZCLI_ALT_CLIENT_ID}" -p "${AZCLI_ALT_CLIENT_SECRET}" -t "${TENANT_ID}"
az account set -s "${AZCLI_ALT_SUBSCRIPTION_ID}"
az account show

# prepare running options
# pytest options
pytest_options="-c --report-path ./reports"
# parallel
if [[ -n ${PARALLELISM} ]]; then
    pytest_options+=" -j ${PARALLELISM}"
else
    pytest_options+=" -s"
fi
# reruns
if [[ -n ${RERUNS} ]]; then
    pytest_options+=" --reruns ${RERUNS}"
fi
# non boxed
if [[ -n ${NON_BOXED} ]]; then
    pytest_options+=" --non-boxed"
fi
# log level
if [[ -n ${LOG_LEVEL} ]]; then
    pytest_options+=" --log-level ${LOG_LEVEL}"
fi
# capture
if [[ -n ${CAPTURE} ]]; then
    pytest_options+=" --capture ${CAPTURE}"
fi
# no exit first
if [[ -n ${NO_EXIT_FIRST} ]]; then
    pytest_options+=" --no-exitfirst"
fi
# last failed
if [[ -n ${LAST_FAILED} ]]; then
    pytest_options+=" --last-failed"
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

# case selection
selection_options=""
# enable selection
if [[ -n ${ENABLE_SELECTION} ]]; then
    selection_options+=" --enable-selection"
fi
# selection mode
if [[ -n ${SELECTION_MODE} ]]; then
    selection_options+=" --selection-mode ${SELECTION_MODE}"
fi
# selection count
if [[ -n ${SELECTION_COUNT} ]]; then
    selection_options+=" --selection-count ${SELECTION_COUNT}"
fi
# unfix random seed
if [[ -n ${UNFIX_RANDOM_SEED} ]]; then
    selection_options+=" --unfix-random-seed"
fi

# recording test
if [[ ${TEST_MODE} == "recording" || ${TEST_MODE} == "all" ]]; then
    echo "Test in recording mode!"
    coverage_options=" -cc test_aks_commands.AzureKubernetesServiceScenarioTest"
    recording_options="${pytest_options}${coverage_options}${selection_options}"
    recording_options+=" --json-report-file=cli_recording_report.json"
    recording_options+=" --xml-file=cli_recording_result.xml"
    echo "Recording test options: ${recording_options}"
    test_result=0
    azaks ${recording_options} || test_result=$?
    if [[ ${test_result} -ne 0 ]]; then
        echo "Recording test failed!"
        echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
        if [[ -z ${IGNORE_EXIT_CODE} ]]; then
            exit ${test_result}
        fi
    else
        echo -e "Recording test passed!\n\n"
    fi
fi

# live test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live mode!"
    live_options="${pytest_options}${filter_options}${selection_options}"
    live_options+=" -l --json-report-file=cli_live_report.json"
    live_options+=" --xml-file=cli_live_result.xml"
    echo "Live test options: ${live_options}"
    test_result=0
    azaks ${live_options} || test_result=$?
    if [[ ${test_result} -ne 0 ]]; then
        echo "Live test failed!"
        echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
        if [[ -z ${IGNORE_EXIT_CODE} ]]; then
            exit ${test_result}
        fi
    else
        echo -e "Live test passed!\n\n"
    fi
fi

# live-replay test
if [[ ${TEST_MODE} == "live" || ${TEST_MODE} == "all" ]]; then
    echo "Test in live-replay mode!"
    live_replay_options="${pytest_options}${filter_options}${selection_options}"
    live_replay_options+=" --json-report-file=cli_live_replay_report.json"
    live_replay_options+=" --xml-file=cli_live_replay_result.xml"
    echo "Live-replay test options: ${live_replay_options}"
    test_result=0
    azaks ${live_replay_options} || test_result=$?
    if [[ ${test_result} -ne 0 ]]; then
        echo "Live-replay test failed!"
        echo "Please refer to this wiki (${WIKI_LINK}) for troubleshooting guidelines."
        if [[ -z ${IGNORE_EXIT_CODE} ]]; then
            exit ${test_result}
        fi
    else
        echo -e "Live-replay test passed!\n\n"
    fi
fi
