from azure.cli.testsdk import (
    ScenarioTest,
    JMESPathCheck,
)

from azext_load.tests.latest.helper import (
    create_test,
    delete_test,
)
from azext_load.tests.latest.constants import (
    LoadTestConstants,
)
import json, time

from azext_load.tests.latest.helper import create_test, delete_test
from azure.cli.testsdk import JMESPathCheck, ScenarioTest


class LoadTestScenario(ScenarioTest):
    # test case for 'az load test list' command

    # creating test with config file
    def testcase_load_test_create(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        # creating test with config file and no arguments
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--load-test-config-file {load_test_config_file} "
            "--wait ",
        ).get_output_in_json()

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

        assert self.kwargs["test_id"] not in [
            test.get("testId") for test in list_of_tests
        ]

    def testcase_load_test_list(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.LIST_TEST_ID,
            }
        )
        create_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            test_plan=LoadTestConstants.TEST_PLAN,
        )

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert len(list_of_tests) > 0
        assert "fake_test_id" not in [test["testId"] for test in list_of_tests]
        assert self.kwargs["test_id"] in [test["testId"] for test in list_of_tests]

        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    # test case for 'az load test show' command
    def testcase_load_test_show(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.SHOW_TEST_ID,
            }
        )

        create_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            test_plan=LoadTestConstants.TEST_PLAN,
        )

        test_details = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert test_details.get("testId", None) == LoadTestConstants.SHOW_TEST_ID

        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    def testcase_load_test_delete(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.DELETE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        create_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=self.kwargs["load_test_config_file"],
        )
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]
        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [
            test.get("testId") for test in list_of_tests
        ]

    def testcase_load_test_download_files(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.DOWNLOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "path": ".",                                    #download temp directory
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )
        create_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=self.kwargs["load_test_config_file"],
            test_plan=self.kwargs["test_plan"],
        )

        self.cmd(
            "az load test download-files "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--path {path}"
        )
        
        #TO-DO checks for download

        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    def test_load_test_create_with_args(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.CREATE_WITH_ARGS_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "display_name": "Create_with_args_test",
                "test_description": "This is a load test created with arguments",
                "test_plan": LoadTestConstants.TEST_PLAN,
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
            "--env {env} "
            "--wait ",
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

        assert self.kwargs["test_id"] not in [
            test.get("testId") for test in list_of_tests
        ]

    def testcase_load_test_update(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.UPDATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )

        # Create a new load test
        create_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            load_test_config_file=self.kwargs["load_test_config_file"],
            test_plan=self.kwargs["test_plan"],
        )

        # Update the load test
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instances 11 ",
        ).get_output_in_json()

        # Verify that the load test was updated
        list_of_tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in list_of_tests]
        assert (
            response.get("loadTestConfiguration", {}).get("engineInstances", None) == 11
        )

        # Delete the load test
        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
        )

    def testcase_load_test_app_component(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestConstants.RESOURCE_GROUP,
                "test_id": LoadTestConstants.APP_COMPONENT_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
                "app_component_id": LoadTestConstants.APP_COMPONENT_ID,
                "app_component_name": LoadTestConstants.APP_COMPONENT_NAME,
                "app_component_type": LoadTestConstants.APP_COMPONENT_TYPE,
            }
        )

        # Create a new load test
        create_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            load_test_config_file=self.kwargs["load_test_config_file"],
            test_plan=self.kwargs["test_plan"],
        )
        time.sleep(10)
        # assuming the app component is already created
        # Adding an app component to the load test
        response = self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-name {app_component_name} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the app component was added by making use of the list command

        list_of_app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert list_of_app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert self.kwargs["app_component_id"] == list_of_app_components.get(
            "components", {}
        ).get(self.kwargs["app_component_id"]).get("resourceId")

        # Remove app component
        self.cmd(
            "az load test app-component remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-id {app_component_id} "
            "--yes"
        )

        list_of_app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not list_of_app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )

        # Delete the load test
        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
        )

    def testcase_load_test_server_metric(self):
        self.kwargs.update(
        {
            "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
            "resource_group": LoadTestConstants.RESOURCE_GROUP,
            "test_id": LoadTestConstants.SERVER_METRIC_TEST_ID,
            "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            "test_plan": LoadTestConstants.TEST_PLAN,
            "app_component_id": LoadTestConstants.APP_COMPONENT_ID,
            "app_component_name": LoadTestConstants.APP_COMPONENT_NAME,
            "app_component_type": LoadTestConstants.APP_COMPONENT_TYPE,
            "server_metric_id": LoadTestConstants.SERVER_METRIC_ID,
            "server_metric_name": LoadTestConstants.SERVER_METRIC_NAME,
            "server_metric_namespace": LoadTestConstants.SERVER_METRIC_NAMESPACE,
            "aggregation": LoadTestConstants.AGGREGATION,
            "app_component_id": LoadTestConstants.APP_COMPONENT_ID,
            "app_component_name": LoadTestConstants.APP_COMPONENT_NAME,
            "app_component_type": LoadTestConstants.APP_COMPONENT_TYPE,
        }
        )

        # Create a new load test
        create_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            load_test_config_file=self.kwargs["load_test_config_file"],
            test_plan=self.kwargs["test_plan"],
        )

        # assuming the app component is already created
        self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-name {app_component_name} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the app component was added by making use of the list command

        list_of_app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert list_of_app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        #        assert self.kwargs["app_component_id"] == list_of_app_components.get("components",{}).get(self.kwargs["app_component_id"]).get("resourceId")

        # Adding an server metrics to the load test
        self.cmd(
            "az load test server-metric add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-id {server_metric_id} "
            "--metric-name {server_metric_name} "
            "--metric-namespace {server_metric_namespace} "
            "--aggregation {aggregation} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the server metrics was added by making use of the list command

        list_of_server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert list_of_server_metrics.get("metrics", {}).get(self.kwargs["server_metric_id"][1:-1])
        #assert self.kwargs["metric_id"] == list_of_server_metrics.get("metrics",{}).get(self.kwargs["metric_id"], {}).get("id")

        # Remove server metrics
        self.cmd(
            "az load test server-metric remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-id {server_metric_id} "
            "--yes"
        )

        list_of_server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not list_of_app_components.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

        # Delete the load test
        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
        )

    def testcase_load_test_file(self):
        self.kwargs.update(
        {
            "load_test_resource": LoadTestConstants.LOAD_TEST_RESOURCE,
            "resource_group": LoadTestConstants.RESOURCE_GROUP,
            "test_id": LoadTestConstants.FILE_TEST_ID,
            "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            "test_plan": LoadTestConstants.TEST_PLAN,
            "download_path": ".",
            "file_name": LoadTestConstants.FILE_NAME,            
        }
        )

        # Create a new load test
        create_test(self, test_id=self.kwargs["test_id"], load_test_resource=self.kwargs["load_test_resource"], resource_group=self.kwargs["resource_group"], load_test_config_file=self.kwargs["load_test_config_file"], test_plan=self.kwargs["test_plan"])

        #delete jmx file
        self.cmd(
            "az load test file delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-name {file_name} "
            "--yes"
        )

        #list file and confirm
        list_of_files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] not in [file["fileName"] for file in list_of_files]

        #upload new jmx file
        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--path {test_plan} "
            "--wait"
        )

        #list file and confirm
        list_of_files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] in [file["fileName"] for file in list_of_files]
        
        #download this file 
        self.cmd(
            "az load test file download "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-name {file_name} "
            "--path {download_path} "
        )
        
        delete_test(self, test_id=self.kwargs["test_id"], load_test_resource=self.kwargs["load_test_resource"], resource_group=self.kwargs["resource_group"])
