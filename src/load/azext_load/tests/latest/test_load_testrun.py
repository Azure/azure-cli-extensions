import json
import time

from azext_load.tests.latest.helper import (
    create_test,
    create_test_run,
    delete_test,
    delete_test_run,
)
from azure.cli.testsdk import JMESPathCheck, ScenarioTest


class LoadTestRunScenario(ScenarioTest):
    load_test_resource = "hbisht-cli-testing"
    resource_group = "hbisht-rg"
    test_id = "sampletest1"
    test_id_long = "14fc47b6-fc59-4a1f-91d2-0678944ff121"
    test_run_id_const = "4008685a-79ab-4007-b559-11cf9051c06f"
    test_run_id = "1507-2608-"
    load_test_config_file = r"C:\\Users\\hbisht\\Desktop\\config.yaml"
    test_plan = r"C:\\Users\\hbisht\\Desktop\\LoadTest2.jmx"
    app_component_id = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss"
    app_component_type = "Microsoft.Compute/virtualMachineScaleSets"
    server_metric_id = r"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/hbisht-rg/providers/Microsoft.Compute/virtualMachineScaleSets/hbisht-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU"
    server_metric_name = "Percentage_CPU"
    server_metric_namespace = "microsoft.compute/virtualmachinescalesets"
    metric_name = "VirtualUsers"
    metric_namespace = "LoadTestRunMetrics"
    metric_dimension_name = "RequestName"
    metric_dimension_value = "Homepage"
    metric_filters_all = "*"
    metric_filters_value_all = f"{metric_dimension_name}=*"
    metric_filters_value_specific = f"{metric_dimension_name}={metric_dimension_value}"
    aggregation = "Average"

    def testcase_load_test_run_list(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id,
                "test_run_id": LoadTestRunScenario.test_run_id_const,
            }
        )

        list_of_test_run = self.cmd(
            "az load test-run list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id}"
        ).get_output_in_json()

        assert len(list_of_test_run) > 0
        assert self.kwargs["test_run_id"] in [
            test["testRunId"] for test in list_of_test_run
        ]
        assert "fake_test_run_id" not in [
            test["testRunId"] for test in list_of_test_run
        ]

    def testcase_load_test_run_show(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id,
                "test_run_id": LoadTestRunScenario.test_run_id_const,
            }
        )

        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}"
        ).get_output_in_json()

        assert test_run["testRunId"] == self.kwargs["test_run_id"]

    def testcase_load_test_run_create(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "create_test_run",
                "test_run_id": LoadTestRunScenario.test_run_id + "create_test_run",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )
        create_test(
            self,
            test_plan=self.kwargs["test_plan"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=self.kwargs["load_test_config_file"],
        )
        test_run_id = create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )
        delete_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_run_id=test_run_id,
        )
        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    def testcase_load_test_run_delete(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "delete_test_run",
                "test_run_id": LoadTestRunScenario.test_run_id + "delete_test_run",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )
        create_test(
            self,
            test_plan=self.kwargs["test_plan"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=self.kwargs["load_test_config_file"],
        )
        test_run_id = create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )
        delete_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_run_id=test_run_id,
        )
        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    def testcase_load_test_run_update(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "update_test_run",
                "test_run_id": LoadTestRunScenario.test_run_id + "update_test_run",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )

        create_test(
            self,
            test_plan=self.kwargs["test_plan"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=self.kwargs["load_test_config_file"],
        )
        test_run_id = create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )
        time.sleep(10)
        test_run = self.cmd(
            "az load test-run update "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            f"--test-run-id {test_run_id} "
            "--description 'Udated test run description' "
        ).get_output_in_json()

        assert test_run["description"] == "Udated test run description"

        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            f"--test-run-id {test_run_id}"
        ).get_output_in_json()

        assert test_run["description"] == "Udated test run description"

        delete_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_run_id=test_run_id,
        )
        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    def testcase_load_test_run_download_files(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "download_test_run_files",
                "test_run_id": LoadTestRunScenario.test_run_id + "download_files",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
            }
        )

        create_test(
            self,
            test_plan=self.kwargs["test_plan"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            load_test_config_file=self.kwargs["load_test_config_file"],
        )
        test_run_id = create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )

        self.cmd(
            "az load test-run download-files "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            f"--test-run-id {test_run_id} "
            "--path . "
            "--input "
            "--log "
        )

        delete_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_run_id=test_run_id,
        )
        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

    def testcase_load_app_components(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "app-components",
                "test_run_id": LoadTestRunScenario.test_run_id
                + "app-components-testrun",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
                "app_component_id": LoadTestRunScenario.app_component_id,
                "app_component_name": "my-app-component",
                "app_component_type": LoadTestRunScenario.app_component_type,
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
        create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )
        # assuming the app component is already created
        # Adding an app component to the load test
        response = self.cmd(
            "az load test-run app-components add "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-name {app_component_name} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the app component was added by making use of the list command

        list_of_app_components = self.cmd(
            "az load test-run app-components list "
            "--test-run-id {test_run_id} "
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
            "az load test-run app-components remove "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-id {app_component_id} "
            "--yes"
        )

        list_of_app_components = self.cmd(
            "az load test-run app-components list "
            "--test-run-id {test_run_id} "
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

    def testcase_load_test_run_server_metrics(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "server-metrics",
                "test_run_id": LoadTestRunScenario.test_run_id
                + "server-metrics-testrun",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
                "metric_id": LoadTestRunScenario.server_metric_id,
                "metric_name": LoadTestRunScenario.server_metric_name,
                "metric_namespace": LoadTestRunScenario.server_metric_namespace,
                "aggregation": LoadTestRunScenario.aggregation,
                "app_component_id": LoadTestRunScenario.app_component_id,
                "app_component_name": "my-app-component",
                "app_component_type": LoadTestRunScenario.app_component_type,
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
        create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )
        # assuming the app component is already created
        response = self.cmd(
            "az load test-run app-components add "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--app-component-name {app_component_name} "
            "--app-component-type {app_component_type} "
            "--app-component-id {app_component_id} ",
        ).get_output_in_json()

        # Verify that the app component was added by making use of the list command

        list_of_app_components = self.cmd(
            "az load test-run app-components list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert list_of_app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert self.kwargs["app_component_id"] == list_of_app_components.get(
            "components", {}
        ).get(self.kwargs["app_component_id"]).get("resourceId")

        # Adding an server metrics to the load test
        self.cmd(
            "az load test-run server-metrics add "
            "--test-run-id {test_run_id} "
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
            "az load test-run server-metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert list_of_server_metrics.get("metrics", {}).get(self.kwargs["metric_id"])
        # assert self.kwargs["metric_id"] == list_of_server_metrics.get("metrics",{}).get(self.kwargs["metric_id"], {}).get("id")

        # Remove server metrics
        self.cmd(
            "az load test-run server-metrics remove "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-id '{metric_id}' "
            "--yes"
        )

        list_of_server_metrics = self.cmd(
            "az load test-run server-metrics list "
            "--test-run-id {test_run_id} "
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

    def testcase_load_test_run_metrics(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id + "metrics",
                "test_run_id": LoadTestRunScenario.test_run_id + "metrics-testrun",
                "load_test_config_file": LoadTestRunScenario.load_test_config_file,
                "test_plan": LoadTestRunScenario.test_plan,
                "metric_name": LoadTestRunScenario.metric_name,
                "metric_namespace": LoadTestRunScenario.metric_namespace,
                "metric_dimension_value": LoadTestRunScenario.metric_dimension_value,
                "metric_filters_all": LoadTestRunScenario.metric_filters_all,
                "metric_filters_dimension_all": LoadTestRunScenario.metric_filters_value_all,
                "metric_filters_dimension_specific": LoadTestRunScenario.metric_filters_value,
                "aggregation": LoadTestRunScenario.aggregation,
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
        create_test_run(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
            test_run_id=self.kwargs["test_run_id"],
        )

        # Verify metrics for the test run with no additional parameters

        metrics_no_additional_parameters = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            "--metric-namespace {metric_namespace} ",
        ).get_output_in_json()

        assert len(metrics_no_additional_parameters) > 0
        assert self.kwargs["metric_name"] in metrics_no_additional_parameters

        # Verify metrics for the test run with metric name

        metrics_with_name = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            "--metric-namespace {metric_namespace} ",
            "--metric-name {metric_name} ",
        ).get_output_in_json()

        assert "data" in metrics_with_name
        assert len(metrics_with_name["data"]) > 0

        # Verify metrics for the test run with metric name and all dimensions and all values

        metrics_with_filters_all = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            "--metric-namespace {metric_namespace} ",
            "--metric-name {metric_name} ",
            "--dimension-filters {metric_filters_all} ",
        ).get_output_in_json()

        assert len(metrics_with_filters_all) > 0
        dimensions_list = [
            dimension
            for metric in metrics_with_filters_all
            for dimension in metric["dimensionValues"]
        ]
        assert self.kwargs["metric_dimension_name"] in set(
            [dimension["name"] for dimension in dimensions_list]
        )
        assert self.kwargs["metric_dimension_value"] in [
            dimension["value"] for dimension in dimensions_list
        ]

        # Verify metrics for the test run with metric name and specific dimension and all values

        metrics_with_filters_dimension_all = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            "--metric-namespace {metric_namespace} ",
            "--metric-name {metric_name} ",
            "--dimension-filters {metric_filters_dimension_all} ",
        ).get_output_in_json()

        assert len(metrics_with_filters_dimension_all) > 0
        dimensions_list = [
            dimension
            for metric in metrics_with_filters_dimension_all
            for dimension in metric["dimensionValues"]
        ]
        assert self.kwargs["metric_dimension_name"] in set(
            [dimension["name"] for dimension in dimensions_list]
        )
        assert self.kwargs["metric_dimension_value"] in [
            dimension["value"] for dimension in dimensions_list
        ]

        # Verify metrics for the test run with metric name and specific dimension and values

        metrics_with_filters_dimension_specific = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            "--metric-namespace {metric_namespace} ",
            "--metric-name {metric_name} ",
            "--dimension-filters {metric_filters_dimension_specific} ",
        ).get_output_in_json()

        assert len(metrics_with_filters_dimension_specific) > 0
        dimensions_list = [
            dimension
            for metric in metrics_with_filters_dimension_specific
            for dimension in metric["dimensionValues"]
        ]
        assert self.kwargs["metric_dimension_name"] in set(
            [dimension["name"] for dimension in dimensions_list]
        )
        assert self.kwargs["metric_dimension_value"] in [
            dimension["value"] for dimension in dimensions_list
        ]

        # Delete the load test
        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
        )


"""
    def testcase_load_test_run_stop(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunScenario.load_test_resource,
                "resource_group": LoadTestRunScenario.resource_group,
                "test_id": LoadTestRunScenario.test_id,
                "test_run_id": LoadTestRunScenario.test_run_id + "stop",
            }
        )

        self.cmd(
            "az load test-run create "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id} "
            "--no-wait "
        )

        #assert test_run["testRunId"] is not None

        self.cmd(
            "az load test-run stop "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}"
        )

        
        """
