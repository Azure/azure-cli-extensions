from azure.cli.testsdk import JMESPathCheck


def create_test(
    ScenarioTest,
    test_id,
    resource_group,
    load_test_resource,
    load_test_config_file,
    test_plan=None,
):
    checks = [
        JMESPathCheck("testId", test_id),
    ]
    if test_plan:
        ScenarioTest.cmd(
            "az load test create "
            f"--test-id {test_id} "
            f"--load-test-resource {load_test_resource} "
            f"--resource-group {resource_group} "
            f"--load-test-config-file {load_test_config_file} "
            f"--test-plan {test_plan} "
            "--wait",
            checks=checks,
        )
    else:
        ScenarioTest.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--load-test-config-file {load_test_config_file} "
        )

    list_of_tests = ScenarioTest.cmd(
        "az load test list "
        "--load-test-resource {load_test_resource} "
        "--resource-group {resource_group}"
    ).get_output_in_json()

    assert ScenarioTest.kwargs["test_id"] in [
        test.get("testId") for test in list_of_tests
    ]


def create_test_run(
    ScenarioTest, test_id, test_run_id, resource_group, load_test_resource
):
    test_run = ScenarioTest.cmd(
        f"az load test-run create "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-id {test_id} "
        f"--test-run-id {test_run_id} "
        f"--wait"
    ).get_output_in_json()

    assert test_run.get("testRunId") is not None

    list_of_test_run = ScenarioTest.cmd(
        f"az load test-run list "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-id {test_id}"
    ).get_output_in_json()

    assert len(list_of_test_run) > 0
    assert test_run.get("testRunId") in [
        test.get("testRunId") for test in list_of_test_run
    ]
    return test_run.get("testRunId")
    # assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]


def delete_test_run(ScenarioTest, test_run_id, resource_group, load_test_resource):
    ScenarioTest.cmd(
        f"az load test-run delete "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--test-run-id {test_run_id} "
        f"--yes"
    )


def delete_test(ScenarioTest, test_id, resource_group, load_test_resource):
    ScenarioTest.cmd(
        "az load test delete "
        f"--test-id {test_id} "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group} "
        f"--yes"
    )

    list_of_tests = ScenarioTest.cmd(
        "az load test list "
        f"--load-test-resource {load_test_resource} "
        f"--resource-group {resource_group}"
    ).get_output_in_json()

    assert test_id not in [test.get("testId") for test in list_of_tests]
