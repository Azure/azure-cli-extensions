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
    load_test_config_file = r"C:\\Users\\hbisht\\Desktop\\config.yaml"
    test_plan = r"C:\\Users\\hbisht\\Desktop\\LoadTest2.jmx"

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

    #creating test with config file
    def testcase_load_test_create(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "create-test-case-1507-2608",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
                "engine_instances": "49",
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
        ]

        #creating test with config file and no arguments
        response = self.cmd("az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--load-test-config-file {load_test_config_file} "
                "--test-plan {test_plan} "
                "--engine-instances {engine_instances} ",
                checks=checks,
        ).get_output_in_json()

        #additional arguments should be ignored by the command
        assert response.get("loadTestConfiguration", {}).get("engineInstances", None) != int(self.kwargs["engine_instances"])

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
    
    def test_load_test_create_with_args(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "create-with-args-test-case-1507-2608",
                "display_name": "My Load Test",
                "test_description": "This is a load test created with arguments",
                "test_plan": LoadScenario.test_plan,
                "engine_instances": "1",
                "env": "a=2 b=3",
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.engineInstances", 1),
            JMESPathCheck("environmentVariables.a", 2),
            JMESPathCheck("environmentVariables.b", 3), 
        ]

        # Create a new load test with arguments
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--display-name '{display_name}' "
            "--test-description '{test_description}' "
            "--test-plan {test_plan} "
            "--engine-instances {engine_instances} "
            "--env {env}",
            checks=checks,
        ).get_output_in_json()

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]

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

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
        ]

        # Create a new load test
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--load-test-config-file {load_test_config_file} "
            "--test-plan {test_plan}",
            checks=checks,
        )

        # Update the load test
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instances 11 ",
            checks=checks,
        ).get_output_in_json()

        # Verify that the load test was updated
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]
        assert response.get("loadTestConfiguration", {}).get("engineInstances", None) == 11

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
