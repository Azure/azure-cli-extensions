# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import time

from azext_load.tests.latest.constants import LoadTestRunConstants
from azext_load.tests.latest.helper import (
    create_test,
    create_test_run,
    delete_test,
    delete_test_run,
)
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    ScenarioTest,
    create_random_name,
    live_only,
)

rg_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}
sa_params = {
    "name_prefix": "clitestload",
    "location": "eastus",
    "key": "storage_account",
    "parameter_name": "storage_account",
    "resource_group_parameter_name": "rg",
    "length": 20,
}


class LoadTestRunScenario(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestRunScenario, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @live_only()
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_stop(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.STOP_TEST_ID,
                "test_run_id": LoadTestRunConstants.STOP_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(self, is_long=True)
        self.cmd(
            "az load test-run create "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id} "
            "--test-run-id {test_run_id} "
            "--no-wait",
        )

        #waiting for test to start
        if self.is_live:
            time.sleep(20)

        test_run = self.cmd(
            "az load test-run stop "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id} "
            "--yes"
        ).get_output_in_json()

        if self.is_live:
            time.sleep(20)

        test_run = self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id} ",
        ).get_output_in_json()

        assert test_run.get("status") in ["CANCELLING", "FAILED", "CANCELLED"]
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_list(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.LIST_TEST_ID,
                "test_run_id": LoadTestRunConstants.LIST_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(self)
        create_test_run(self)

        test_runs = self.cmd(
            "az load test-run list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id}"
        ).get_output_in_json()

        assert len(test_runs) > 0
        test_run_ids = [run.get("testRunId") for run in test_runs]
        assert self.kwargs["test_run_id"] in test_run_ids
        assert "fake_test_run_id" not in test_run_ids

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_show(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.SHOW_TEST_ID,
                "test_run_id": LoadTestRunConstants.SHOW_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )
        create_test(self)

        create_test_run(self)

        self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}",
            checks=[JMESPathCheck("testRunId", self.kwargs["test_run_id"])],
        ).get_output_in_json()

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_create(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.CREATE_TEST_ID,
                "test_run_id": LoadTestRunConstants.CREATE_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
                "description": LoadTestRunConstants.DESCRIPTION,
                "display_name": LoadTestRunConstants.DISPLAY_NAME,
            }
        )
        create_test(self)
        
        checks = [
            JMESPathCheck("testRunId", self.kwargs["test_run_id"]),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("environmentVariables.rps", "11"),
        ]
        self.cmd(
            "az load test-run create "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-id {test_id} "
            "--test-run-id {test_run_id} "
            "--env rps=11 "
            "--description {description} "
            "--display-name {display_name} ",
            checks=checks,
        )

        # 3. Get the test run and confirm
        self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}",
            checks=[JMESPathCheck("testRunId", self.kwargs["test_run_id"])],
        ).get_output_in_json()

        # Invalid cases for test run
        # 1. Create a test run with already existing test run id
        try:
            self.cmd(
                "az load test-run create "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-id {test_id} "
                "--test-run-id {test_run_id} "
                "--env rps=11 "
            )
        except Exception as e:
            assert "Test run with given test run ID : " in str(e)
            assert "already exist" in str(e) 
        
        # 2. Create a test run with invalid test run id
        self.kwargs.update(
            {
                "invalid_test_run_id": LoadTestRunConstants.INVALID_TEST_RUN_ID,
            }
        )
        try:
            self.cmd(
                "az load test-run create "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-id {test_id} "
                "--test-run-id {invalid_test_run_id} "
            )
        except Exception as e:
            assert "Invalid test-run-id value" in str(e)
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_delete(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.DELETE_TEST_ID,
                "test_run_id": LoadTestRunConstants.DELETE_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(self)
        create_test_run(self)
        delete_test_run(self)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_update(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.UPDATE_TEST_ID,
                "test_run_id": LoadTestRunConstants.UPDATE_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
                "new_description": "Updated test run description",
            }
        )

        create_test(self)
        create_test_run(self)
        if self.is_live:
            time.sleep(20)
        self.cmd(
            "az load test-run update "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id} "
            "--description '{new_description}' ",
            checks=[JMESPathCheck("description", self.kwargs["new_description"])],
        ).get_output_in_json()

        self.cmd(
            "az load test-run show "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id}",
            checks=[JMESPathCheck("description", self.kwargs["new_description"])],
        ).get_output_in_json()

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_download_files(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.DOWNLOAD_TEST_ID,
                "test_run_id": LoadTestRunConstants.DOWNLOAD_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(self)
        create_test_run(self)

        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"path": temp_dir})

            self.cmd(
                "az load test-run download-files "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-run-id {test_run_id} "
                '--path "{path}" '
                "--input "
                "--log "
                "--result ",
            )

            files_in_dir = [
                f
                for f in os.listdir(temp_dir)
                if os.path.isfile(os.path.join(temp_dir, f))
            ]
            exts = [os.path.splitext(f)[1].casefold() for f in files_in_dir]

            assert len(files_in_dir) >= 3
            assert all([ext in exts for ext in [".yaml", ".zip", ".jmx"]])

            # download files in a new directory using force argument
            temp_new_dir = temp_dir + r"/new"
            self.kwargs.update({"path": temp_new_dir})
            self.cmd(
                "az load test-run download-files "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--test-run-id {test_run_id} "
                '--path "{path}" '
                "--input "
                "--log "
                "--result "
                "--force",
            )

            files_in_dir = [
                f
                for f in os.listdir(temp_new_dir)
                if os.path.isfile(os.path.join(temp_new_dir, f))
            ]
            exts = [os.path.splitext(f)[1].casefold() for f in files_in_dir]

            assert len(files_in_dir) >= 3
            assert all([ext in exts for ext in [".yaml", ".zip", ".jmx"]])

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_app_component(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.APP_COMPONENT_TEST_ID,
                "test_run_id": LoadTestRunConstants.APP_COMPONENT_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(self)
        create_test_run(self)
        if self.is_live:
            time.sleep(10)

        # GET STORAGE ACCOUNT ID
        result = self.cmd(
            "az storage account show --name {storage_account} --resource-group {resource_group}"
        ).get_output_in_json()
        storage_account_id = result["id"]
        storage_account_name = result["name"]
        storage_account_type = result["type"]
        storage_account_kind = result["kind"]

        self.kwargs.update(
            {
                "app_component_id": storage_account_id,
                "app_component_name": storage_account_name,
                "app_component_type": storage_account_type,
                "app_component_kind": storage_account_kind,
            }
        )
        self.cmd(
            "az load test-run app-component add "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" '
            '--app-component-kind "{app_component_kind}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test-run app-component list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        self.cmd(
            "az load test-run app-component remove "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-id "{app_component_id}" '
            "--yes"
        )

        app_components = self.cmd(
            "az load test-run app-component list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )

        #Invalid cases for app component
        # 1. Create a test run with invalid App Component Id
        self.kwargs.update(
            {
                "invalid_app_component_id": LoadTestRunConstants.INVALID_APP_COMPONENT_ID,
                "app_component_name": LoadTestRunConstants.APP_COMPONENT_NAME,
                "app_component_type": LoadTestRunConstants.APP_COMPONENT_TYPE,
            }
        )
        try:
            self.cmd(
                "az load test-run app-component add "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--app-component-name "{app_component_name}" '
                '--app-component-type "{app_component_type}" '
                '--app-component-id "{invalid_app_component_id}" ',
            )
        except Exception as e:
            assert "app-component-id is not a valid Azure Resource ID:" in str(e)

        # 2. AppComponent type and ID mismatch
        self.kwargs.update(
            {
                "app_component_id": LoadTestRunConstants.APP_COMPONENT_ID,
                "app_component_name": LoadTestRunConstants.APP_COMPONENT_NAME,
                "invalid_app_component_type": LoadTestRunConstants.INVALID_APP_COMPONENT_TYPE,
            }
        )
        try:
            self.cmd(
                "az load test-run app-component add "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--app-component-name "{app_component_name}" '
                '--app-component-type "{invalid_app_component_type}" '
                '--app-component-id "{app_component_id}" ',
            )
        except Exception as e:
            assert "Type of app-component-id and app-component-type mismatch: " in str(
                e
            )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_run_server_metric(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.SERVER_METRIC_TEST_ID,
                "test_run_id": LoadTestRunConstants.SERVER_METRIC_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
            }
        )

        create_test(self)
        create_test_run(self)
        # GET STORAGE ACCOUNT ID
        result = self.cmd(
            "az storage account show --name {storage_account} --resource-group {resource_group}"
        ).get_output_in_json()
        storage_account_id = result["id"]
        storage_account_name = result["name"]
        storage_account_type = result["type"]
        storage_account_kind = result["kind"]

        self.kwargs.update(
            {
                "app_component_id": storage_account_id,
                "app_component_name": storage_account_name,
                "app_component_type": storage_account_type,
                "app_component_kind": storage_account_kind,
            }
        )
        self.cmd(
            "az load test-run app-component add "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" '
            '--app-component-kind "{app_component_kind}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test-run app-component list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        self.kwargs.update(
            {
                "server_metric_id": LoadTestRunConstants.SERVER_METRIC_ID.format(
                    storage_account_id
                ),
                "server_metric_name": LoadTestRunConstants.SERVER_METRIC_NAME,
                "server_metric_namespace": LoadTestRunConstants.SERVER_METRIC_NAMESPACE,
                "aggregation": LoadTestRunConstants.AGGREGATION,
            }
        )
        self.cmd(
            "az load test-run server-metric add "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            '--metric-name " {server_metric_name}" '
            '--metric-namespace "{server_metric_namespace}" '
            "--aggregation {aggregation} "
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" ',
        ).get_output_in_json()

        server_metrics = self.cmd(
            "az load test-run server-metric list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        server_metric = server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

        # 8. Remove SM & list SM
        assert server_metric is not None
        # assert self.kwargs[
        #    "server_metric_id"
        # ] == server_metric.get("id")

        self.cmd(
            "az load test-run server-metric remove "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            "--yes"
        )

        server_metrics = self.cmd(
            "az load test-run server-metric list "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

        # Invalid server metrics
        self.kwargs.update(
            {
                "app_component_id": LoadTestRunConstants.APP_COMPONENT_ID,
                "app_component_name": LoadTestRunConstants.APP_COMPONENT_NAME,
                "invalid_server_metric_id": LoadTestRunConstants.INVALID_SERVER_METRIC_ID,
                "server_metric_name": LoadTestRunConstants.SERVER_METRIC_NAME,
                "server_metric_namespace": LoadTestRunConstants.SERVER_METRIC_NAMESPACE,
                "aggregation": LoadTestRunConstants.AGGREGATION,
            }
        )
        try:
            self.cmd(
                "az load test-run server-metric add "
                "--test-run-id {test_run_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--metric-name "{server_metric_name}" '
                '--metric-namespace "{server_metric_namespace}" '
                '--metric-id "{invalid_server_metric_id}" '
                '--aggregation "{aggregation}" '
                '--app-component-type "{app_component_type}" '
                '--app-component-id "{app_component_id}" ',
            )
        except Exception as e:
            assert "metric-id is not a valid Azure Resource ID:" in str(e)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_run_metrics(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestRunConstants.METRIC_TEST_ID,
                "test_run_id": LoadTestRunConstants.METRIC_TEST_RUN_ID,
                "load_test_config_file": LoadTestRunConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestRunConstants.TEST_PLAN,
                "metric_name": LoadTestRunConstants.METRIC_NAME,
                "metric_namespace": LoadTestRunConstants.METRIC_NAMESPACE,
                "metric_dimension_name": LoadTestRunConstants.METRIC_DIMENSION_NAME,
                "metric_dimension_value": LoadTestRunConstants.METRIC_DIMENSION_VALUE,
                "metric_filters_all": LoadTestRunConstants.METRIC_FILTERS_ALL,
                "metric_filters_dimension_all": LoadTestRunConstants.METRIC_FILTERS_VALUE_ALL,
                "metric_filters_dimension_specific": LoadTestRunConstants.METRIC_FILTERS_VALUE_SPECIFIC,
            }
        )

        create_test(self, is_long=True)
        create_test_run(self)

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

        assert len(metrics_with_name) > 0
        assert "data" in metrics_with_name[0]
        assert len(metrics_with_name[0]["data"]) > 0

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
            '--dimension-filters "{metric_filters_dimension_specific}" ',
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