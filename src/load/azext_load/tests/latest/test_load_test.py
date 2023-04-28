from azure.cli.testsdk import (
    ScenarioTest,
    JMESPathCheck,
)


class LoadScenario(ScenarioTest):
    load_test_resource = "hbisht-cli-testing"
    resource_group = "hbisht-rg"
    test_id = "sampletest1"

    # test case for 'az load test list' command
    def testcase_load_test_list(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
            }
        )

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert len(list_of_tests) > 0
        assert "fake_test_id" not in [test["testId"] for test in list_of_tests]

    # test case for 'az load test show' command
    def testcase_load_test_show(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": LoadScenario.test_id,
            }
        )

        checks = [
            JMESPathCheck("testId", LoadScenario.test_id),
            JMESPathCheck("loadTestConfiguration.engineInstances", 1),
        ]

        test_details = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            checks=checks,
        ).get_output_in_json()

        assert test_details.get("testId", None) == LoadScenario.test_id
