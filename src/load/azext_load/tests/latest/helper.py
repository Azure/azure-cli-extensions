# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict

from azext_load.tests.latest.constants import LoadConstants
from azure.cli.testsdk import JMESPathCheck


def create_test(
    ScenarioTest,
    load_test_resource=None,
    resource_group=None,
    test_id=None,
    load_test_config_file=None,
    test_plan=None,
    is_long=False,
    no_wait=False,
):
    if not load_test_resource:
        load_test_resource = ScenarioTest.kwargs["load_test_resource"]
    if not resource_group:
        resource_group = ScenarioTest.kwargs["resource_group"]
    if not test_id:
        test_id = ScenarioTest.kwargs["test_id"]
    if not load_test_config_file:
        load_test_config_file = ScenarioTest.kwargs["load_test_config_file"]

    template = (
        "az load test create "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-id {test_id} "
        f'--load-test-config-file "{load_test_config_file}"'
    )

    duration = LoadConstants.ENV_VAR_DURATION_SHORT
    if is_long:
        duration = LoadConstants.ENV_VAR_DURATION_LONG
    template += f" --env {LoadConstants.ENV_VAR_DURATION_NAME}={duration}"

    if test_plan:
        template += f' --test-plan "{test_plan}"'

    if no_wait:
        template += " --no-wait"

    ScenarioTest.cmd(
        template, checks=[JMESPathCheck("testId", ScenarioTest.kwargs["test_id"])]
    )

    tests = ScenarioTest.cmd(
        "az load test list "
        "--load-test-resource {load_test_resource} "
        "--resource-group {resource_group}"
    ).get_output_in_json()

    assert ScenarioTest.kwargs["test_id"] in [test.get("testId") for test in tests]


def create_test_run(
    ScenarioTest,
    load_test_resource=None,
    resource_group=None,
    test_id=None,
    test_run_id=None,
):
    if not load_test_resource:
        load_test_resource = ScenarioTest.kwargs["load_test_resource"]
    if not resource_group:
        resource_group = ScenarioTest.kwargs["resource_group"]
    if not test_id:
        test_id = ScenarioTest.kwargs["test_id"]
    if not test_run_id:
        test_run_id = ScenarioTest.kwargs["test_run_id"]

    test_run = ScenarioTest.cmd(
        "az load test-run create "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-id {test_id} "
        f"--test-run-id {test_run_id} ",
        checks=[JMESPathCheck("testRunId", ScenarioTest.kwargs["test_run_id"])],
    ).get_output_in_json()

    test_runs = ScenarioTest.cmd(
        "az load test-run list "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-id {test_id}"
    ).get_output_in_json()

    assert test_run["testRunId"] in [run.get("testRunId") for run in test_runs]


def delete_test_run(
    ScenarioTest, load_test_resource=None, resource_group=None, test_run_id=None
):
    if not load_test_resource:
        load_test_resource = ScenarioTest.kwargs["load_test_resource"]
    if not resource_group:
        resource_group = ScenarioTest.kwargs["resource_group"]
    if not test_run_id:
        test_run_id = ScenarioTest.kwargs["test_run_id"]
    test_id = ScenarioTest.kwargs["test_id"]

    ScenarioTest.cmd(
        "az load test-run delete "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-run-id {test_run_id} "
        f"--yes"
    )

    test_runs = ScenarioTest.cmd(
        "az load test-run list "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-id {test_id} "
    ).get_output_in_json()

    assert test_run_id not in [run.get("testRunId") for run in test_runs]


def delete_test(
    ScenarioTest, load_test_resource=None, resource_group=None, test_id=None
):
    if not load_test_resource:
        load_test_resource = ScenarioTest.kwargs["load_test_resource"]
    if not resource_group:
        resource_group = ScenarioTest.kwargs["resource_group"]
    if not test_id:
        test_id = ScenarioTest.kwargs["test_id"]

    ScenarioTest.cmd(
        "az load test delete "
        f"--test-id {test_id} "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--yes"
    )

    tests = ScenarioTest.cmd(
        "az load test list "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group}"
    ).get_output_in_json()

    assert test_id not in [test.get("testId") for test in tests]
