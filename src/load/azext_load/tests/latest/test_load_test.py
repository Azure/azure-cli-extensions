from azure.cli.testsdk import (
    ScenarioTest,
    JMESPathCheck,
)

import json


class LoadScenario(ScenarioTest):
    load_test_resource = "hbisht-cli-testing"
    resource_group = "hbisht-rg"
    test_id = "sampletest1"
    #
    load_test_config_file = "C:\\\\Users\\\\hbisht\\\\Desktop\\\\config.yaml"
    test_plan = "C:\\\\Users\\\\hbisht\\\\Desktop\\\\LoadTest2.jmx"

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

    def testcase_load_test_delete(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "delete-test-case-1507-2608",
                "load_test_config_file": "C:\\\\Users\\\\hbisht\\\\Desktop\\\\config.yaml",
            }
        )
        
        self.cmd("az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--load-test-config-file {load_test_config_file} "
        )
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]

        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes"
        )

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in list_of_tests]

    def testcase_load_test_download_files(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "download-test-case-1507-2608",
                "path": "C:\\\\Users\\\\hbisht\\\\Desktop\\\\test\\\\",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
            }
        )
        self.cmd("az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--load-test-config-file {load_test_config_file} "
                "--test-plan {test_plan}"
        )
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]

        response = self.cmd(
            "az load test download-files "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--path {path}"
        )
        assert "Files belonging to test".casefold() in response.output.casefold()

        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes"
        )

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in list_of_tests]

    def testcase_load_test_create(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "create-test-case-1507-2608",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
            }
        )

        #creating test with config file and no arguments
        response = self.cmd("az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--load-test-config-file {load_test_config_file} "
                "--test-plan {test_plan}"
        ).get_output_in_json()

        assert response.get("testId", None) == self.kwargs["test_id"]

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]

        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes"
        )

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in list_of_tests]
        #
    
    def testcase_load_test_update(self):
        self.kwargs.update(
        {
            "load_test_resource": LoadScenario.load_test_resource,
            "resource_group": LoadScenario.resource_group,
            "test_id": "update-test-case-1507-2608",
            "load_test_config_file": LoadScenario.load_test_config_file,
            "test_plan": LoadScenario.test_plan,
        }
        )

        # Create a new load test
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--load-test-config-file {load_test_config_file} "
            "--test-plan {test_plan}"
        )

        # Update the load test
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instances 11 "
        ).get_output_in_json()

        # Verify that the load test was updated
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]
        assert response.get("engineCount", None) == 11

        # Delete the load test
        self.cmd(
            "az load test delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes"
        )

        # Verify that the load test was deleted
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in list_of_tests]
