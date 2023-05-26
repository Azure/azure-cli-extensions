import time

from azext_load.tests.latest.helper import (
    create_test,
    create_test_run,
    delete_test,
    delete_test_run,
)
from azext_load.tests.latest.constants import (
    LoadTestRunConstants,
)
from azure.cli.testsdk import JMESPathCheck, ScenarioTest


class LoadTestRunScenario(ScenarioTest):

    def testcase_load_test_run_stop(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.STOP_TEST_ID,
                "test_run_id": LoadTestRunConstants.STOP_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            load_test_config_file=self.kwargs["load_test_config_file"],
            test_plan=self.kwargs["test_plan"], is_long=True,
        )

        test_run = self.cmd(
            "az load test-run create "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id} "
            "--test-run-id {test_run_id} "
        ).get_output_in_json()
        
        assert test_run["testRunId"] == self.kwargs["test_run_id"]

        while test_run["status"] not in ["RUNNING", "DONE", "FAILED", "CANCELLED"]:
            time.sleep(5)
            test_run = self.cmd(
                "az load test-run show "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-run-id {test_run_id} "  
            ).get_output_in_json()

        test_run = self.cmd(
            "az load test-run stop "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id} "
            "--yes"
        ).get_output_in_json()

        while test_run["status"] not in ["CANCELLED", "DONE", "FAILED"]:
            time.sleep(5)
            test_run = self.cmd(
                "az load test-run show "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-run-id {test_run_id} "  
            ).get_output_in_json()
        
        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id} "  
        ).get_output_in_json()
        
        assert test_run["status"] == "CANCELLED"

        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"]
        )


    def testcase_load_test_run_list(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.LIST_TEST_ID,
                "test_run_id": LoadTestRunConstants.LIST_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,

            }
        )

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
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_run_id=self.kwargs["test_run_id"],
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

        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"]
        )

    def testcase_load_test_run_show(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.SHOW_TEST_ID,
                "test_run_id": LoadTestRunConstants.SHOW_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )
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
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_run_id=self.kwargs["test_run_id"],
        )

        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}"
        ).get_output_in_json()

        assert test_run["testRunId"] == self.kwargs["test_run_id"]
        
        delete_test(
            self,
            test_id=self.kwargs["test_id"],
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"]
        )

    def testcase_load_test_run_create(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.CREATE_TEST_ID,
                "test_run_id": LoadTestRunConstants.CREATE_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )
        try :
            create_test(
                self,
                test_plan=self.kwargs["test_plan"],
                load_test_resource=self.kwargs["load_test_resource"],
                resource_group=self.kwargs["resource_group"],
                test_id=self.kwargs["test_id"],
                load_test_config_file=self.kwargs["load_test_config_file"],
            )
            create_test_run(
                self,
                load_test_resource=self.kwargs["load_test_resource"],
                resource_group=self.kwargs["resource_group"],
                test_id=self.kwargs["test_id"],
                test_run_id=self.kwargs["test_run_id"],
            )
        finally:
            try:
                delete_test(
                    self,
                    load_test_resource=self.kwargs["load_test_resource"],
                    resource_group=self.kwargs["resource_group"],
                    test_id=self.kwargs["test_id"],
                )
            except:
                pass

    def testcase_load_test_run_delete(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.DELETE_TEST_ID,
                "test_run_id": LoadTestRunConstants.DELETE_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )
        try :
            create_test(
                self,
                test_plan=self.kwargs["test_plan"],
                load_test_resource=self.kwargs["load_test_resource"],
                resource_group=self.kwargs["resource_group"],
                test_id=self.kwargs["test_id"],
                load_test_config_file=self.kwargs["load_test_config_file"],
            )
            create_test_run(
                self,
                load_test_resource=self.kwargs["load_test_resource"],
                resource_group=self.kwargs["resource_group"],
                test_id=self.kwargs["test_id"],
                test_run_id=self.kwargs["test_run_id"],
            )
        finally:
            try:
                delete_test(
                    self,
                    load_test_resource=self.kwargs["load_test_resource"],
                    resource_group=self.kwargs["resource_group"],
                    test_id=self.kwargs["test_id"],
                )
            except:
                pass

    def testcase_load_test_run_update(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.UPDATE_TEST_ID,
                "test_run_id": LoadTestRunConstants.UPDATE_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )
        try :
            create_test(
                self,
                test_plan=self.kwargs["test_plan"],
                load_test_resource=self.kwargs["load_test_resource"],
                resource_group=self.kwargs["resource_group"],
                test_id=self.kwargs["test_id"],
                load_test_config_file=self.kwargs["load_test_config_file"],
            )
            create_test_run(
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
                "--test-run-id {test_run_id} "
                "--description 'Udated test run description' "
            ).get_output_in_json()

            assert test_run["description"] == "Udated test run description"

            test_run = self.cmd(
                "az load test-run show "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-run-id {test_run_id}"
            ).get_output_in_json()

            assert test_run["description"] == "Udated test run description"
        finally:
            try:
                delete_test(
                    self,
                    load_test_resource=self.kwargs["load_test_resource"],
                    resource_group=self.kwargs["resource_group"],
                    test_id=self.kwargs["test_id"],
                )
            except:
                pass

    def testcase_load_test_run_download_files(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.DOWNLOAD_TEST_ID,
                "test_run_id": LoadTestRunConstants.DOWNLOAD_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )
        try:
            create_test(
                self,
                test_plan=self.kwargs["test_plan"],
                load_test_resource=self.kwargs["load_test_resource"],
                resource_group=self.kwargs["resource_group"],
                test_id=self.kwargs["test_id"],
                load_test_config_file=self.kwargs["load_test_config_file"],
            )
            create_test_run(
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
                "--test-run-id {test_run_id} "
                "--path . "
                "--input "
                "--log "
            )

        finally:
            try:
                delete_test(
                    self,
                    load_test_resource=self.kwargs["load_test_resource"],
                    resource_group=self.kwargs["resource_group"],
                    test_id=self.kwargs["test_id"],
                )
            except:
                pass

    def testcase_load_app_component(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.APP_COMPONENT_TEST_ID,
                "test_run_id": LoadTestRunConstants.APP_COMPONENT_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
                "app_component_id": LoadTestRunConstants.APP_COMPONENT_ID,
                "app_component_name": LoadTestRunConstants.APP_COMPONENT_NAME,
                "app_component_type": LoadTestRunConstants.APP_COMPONENT_TYPE,
            }
        )

        try:
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
                "az load test-run app-component add "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--app-component-name {app_component_name} "
                "--app-component-type {app_component_type} "
                "--app-component-id {app_component_id} ",
            ).get_output_in_json()

            # Verify that the app component was added by making use of the list command

            list_of_app_components = self.cmd(
                "az load test-run app-component list "
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
                "az load test-run app-component remove "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--app-component-id {app_component_id} "
                "--yes"
            )

            list_of_app_components = self.cmd(
                "az load test-run app-component list "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
            ).get_output_in_json()

            assert not list_of_app_components.get("components", {}).get(
                self.kwargs["app_component_id"]
            )
        finally:
        # Delete the load test
            try:
                delete_test(
                    self,
                    test_id=self.kwargs["test_id"],
                    load_test_resource=self.kwargs["load_test_resource"],
                    resource_group=self.kwargs["resource_group"],
                )
            except:
                pass

    def testcase_load_test_run_server_metric(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.SERVER_METRIC_TEST_ID,
                "test_run_id": LoadTestRunConstants.SERVER_METRIC_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
                "server_metric_id": LoadTestRunConstants.SERVER_METRIC_ID,
                "server_metric_name": LoadTestRunConstants.SERVER_METRIC_NAME,
                "server_metric_namespace": LoadTestRunConstants.SERVER_METRIC_NAMESPACE,
                "aggregation": LoadTestRunConstants.AGGREGATION,
                "app_component_id": LoadTestRunConstants.APP_COMPONENT_ID,
                "app_component_name": LoadTestRunConstants.APP_COMPONENT_NAME,
                "app_component_type": LoadTestRunConstants.APP_COMPONENT_TYPE,
            }
        )
        try:
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
                "az load test-run app-component add "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--app-component-name {app_component_name} "
                "--app-component-type {app_component_type} "
                "--app-component-id {app_component_id} ",
            ).get_output_in_json()

            # Verify that the app component was added by making use of the list command

            list_of_app_components = self.cmd(
                "az load test-run app-component list "
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
                "az load test-run server-metric add "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--metric-id '{server_metric_id}' "
                "--metric-name {server_metric_name} "
                "--metric-namespace {server_metric_namespace} "
                "--aggregation {aggregation} "
                "--app-component-type {app_component_type} "
                "--app-component-id {app_component_id} ",
            ).get_output_in_json()

            # Verify that the server metrics was added by making use of the list command

            list_of_server_metrics = self.cmd(
                "az load test-run server-metric list "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
            ).get_output_in_json()
            assert list_of_server_metrics.get("metrics", {}).get(self.kwargs["metric_id"])
            # assert self.kwargs["metric_id"] == list_of_server_metrics.get("metrics",{}).get(self.kwargs["metric_id"], {}).get("id")

            # Remove server metrics
            self.cmd(
                "az load test-run server-metric remove "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--metric-id '{metric_id}' "
                "--yes"
            )

            list_of_server_metrics = self.cmd(
                "az load test-run server-metric list "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
            ).get_output_in_json()

            assert not list_of_app_components.get("metrics", {}).get(
                self.kwargs["metric_id"]
            )
        finally:
            # Delete the load test
            try:
                delete_test(
                    self,
                    test_id=self.kwargs["test_id"],
                    load_test_resource=self.kwargs["load_test_resource"],
                    resource_group=self.kwargs["resource_group"],
                )
            except:
                pass
    """
    def testcase_load_test_run_metrics(self):
        self.kwargs.update(
            {
                "load_test_resource": LoadTestRunConstants.LOAD_TEST_RESOURCE,
                "resource_group": LoadTestRunConstants.RESOURCE_GROUP,
                "test_id": LoadTestRunConstants.METRIC_TEST_ID,
                "test_run_id": LoadTestRunConstants.METRIC_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
                "metric_name": LoadTestRunConstants.METRIC_NAME,
                "metric_namespace": LoadTestRunConstants.METRIC_NAMESPACE,
                "metric_dimension_value": LoadTestRunConstants.METRIC_DIMENSION_VALUE,
                "metric_filters_all": LoadTestRunConstants.METRIC_FILTERS_ALL,
                "metric_filters_dimension_all": LoadTestRunConstants.METRIC_FILTERS_VALUE_ALL,
                "metric_filters_dimension_specific": LoadTestRunConstants.METRIC_FILTERS_VALUE_SPECIFIC,
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
            "--resource-group {resource_group} "
            "--metric-namespace {metric_namespace} ",
        ).get_output_in_json()

        assert len(metrics_no_additional_parameters) > 0
        assert self.kwargs["metric_name"] in metrics_no_additional_parameters

        # Verify metrics for the test run with metric name

        metrics_with_name = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-namespace {metric_namespace} "
            "--metric-name {metric_name} ",
        ).get_output_in_json()

        assert "data" in metrics_with_name
        assert len(metrics_with_name["data"]) > 0

        # Verify metrics for the test run with metric name and all dimensions and all values

        metrics_with_filters_all = self.cmd(
            "az load test-run metrics list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--metric-namespace {metric_namespace} "
            "--metric-name {metric_name} "
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
            "--resource-group {resource_group} "
            "--metric-namespace {metric_namespace} "
            "--metric-name {metric_name} "
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
            "--resource-group {resource_group} "
            "--metric-namespace {metric_namespace} "
            "--metric-name {metric_name} "
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