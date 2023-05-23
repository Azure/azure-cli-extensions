import json

from azext_load.tests.latest.helper import create_test, delete_test
from azure.cli.testsdk import JMESPathCheck, ScenarioTest


class LoadScenario(ScenarioTest):
    load_test_resource = "hbisht-cli-testing"
    resource_group = "hbisht-rg"
    test_id = "sampletest1"
    #
    load_test_config_file = r"C:\\Users\\hbisht\\Desktop\\config.yaml"
    test_plan = r"C:\\Users\\hbisht\\Desktop\\LoadTest2.jmx"
    app_component_id = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss"
    app_component_type = r"Microsoft.Compute/virtualMachineScaleSets"
    metric_id = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU"
    metric_name = r"Percentage_CPU"
    metric_namespace = r"microsoft.compute/virtualmachinescalesets"
    aggregation = r"Average"

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
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "download-test-case-1507-2608",
                "path": ".",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
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

        response = self.cmd(
            "az load test download-files "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--path {path}"
        )
        # assert "Files belonging to test".casefold() in response.output.casefold()

        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    # creating test with config file
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

        # creating test with config file and no arguments
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--load-test-config-file {load_test_config_file} "
            "--test-plan {test_plan} "
            "--engine-instances {engine_instances} "
            "--wait ",
            checks=checks,
        ).get_output_in_json()

        # additional arguments should be ignored by the command
        assert response.get("loadTestConfiguration", {}).get(
            "engineInstances", None
        ) != int(self.kwargs["engine_instances"])

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
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "update-test-case-1507-2608",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
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

    def testcase_load_app_components(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "app-component-test-case-1507-2608",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
                "app_component_id": LoadScenario.app_component_id,
                "app_component_name": "my-app-component",
                "app_component_type": LoadScenario.app_component_type,
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
        # Adding an app component to the load test
        response = self.cmd(
            "az load test app-components add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-name {app_component_name} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the app component was added by making use of the list command

        list_of_app_components = self.cmd(
            "az load test app-components list "
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
            "az load test app-components remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-id {app_component_id} "
            "--yes"
        )

        list_of_app_components = self.cmd(
            "az load test app-components list "
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

    def testcase_load_server_metrics(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadScenario.load_test_resource,
                "resource_group": LoadScenario.resource_group,
                "test_id": "server-metrics-test-case-1507-2608",
                "load_test_config_file": LoadScenario.load_test_config_file,
                "test_plan": LoadScenario.test_plan,
                "metric_id": LoadScenario.metric_id,
                "metric_name": LoadScenario.metric_name,
                "metric_namespace": LoadScenario.metric_namespace,
                "aggregation": LoadScenario.aggregation,
                "app_component_id": LoadScenario.app_component_id,
                "app_component_name": "my-app-component",
                "app_component_type": LoadScenario.app_component_type,
            }
        )
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
        ]

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
            "az load test app-components add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-name {app_component_name} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the app component was added by making use of the list command

        list_of_app_components = self.cmd(
            "az load test app-components list "
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
            "az load test server-metrics add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-id '{metric_id}' "
            "--metric-name {metric_name} "
            "--metric-namespace {metric_namespace} "
            "--aggregation {aggregation} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the server metrics was added by making use of the list command

        list_of_server_metrics = self.cmd(
            "az load test server-metrics list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert list_of_server_metrics.get("metrics", {}).get(self.kwargs["metric_id"])
        # assert self.kwargs["metric_id"] == list_of_server_metrics.get("metrics",{}).get(self.kwargs["metric_id"], {}).get("id")

        # Remove server metrics
        self.cmd(
            "az load test server-metrics remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-id '{metric_id}' "
            "--yes"
        )

        list_of_server_metrics = self.cmd(
            "az load test server-metrics list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not list_of_app_components.get("metrics", {}).get(
            self.kwargs["metric_id"]
        )

        # Delete the load test
        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
        )


##TO-DO update download-files/file command subgroup test case according to new changes
