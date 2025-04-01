# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.helper import delete_test
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)
from knack.log import get_logger

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-app-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-app-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}


class LoadTestScenarioAppComponents(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioAppComponents, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_app_components(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_APP_COMPONENTS,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]

        self.cmd(
            "az load test create "
            '--load-test-config-file "{load_test_config_file}" '
            "--test-id {test_id} "
            "--test-type {test_type} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=checks,
        ).get_output_in_json()
        
        app_components_response = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=[]
        ).get_output_in_json()
        server_metric_response = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=[]
        ).get_output_in_json()

        app_components = app_components_response.get("components", {})
        server_metrics = server_metric_response.get("metrics", {})
        assert len(app_components.values()) == 2
        # Ensure at least 2 metrics are returned, default can be of any number, but we patch 2 metrics by our self.
        assert len(server_metrics.values()) >= 2

        for items in app_components.values():
            if items.get("resourceName") == "sample-app-comp1":
                assert items.get("kind") == "app"
                assert items.get("resourceType") == "Microsoft.Web/serverfarms"
                assert items.get("resourceGroup") == "sample-rg"
                assert items.get("resourceId") == "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/Microsoft.Web/serverfarms/sample-app-comp1"
                assert items.get("subscriptionId") == "00000000-0000-0000-0000-000000000000"
            else:
                assert items.get("resourceType") == "Microsoft.Web/serverfarms"
                assert items.get("resourceGroup") == "sample-rg"
                assert items.get("resourceId") == "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/sample-rg/providers/Microsoft.Web/serverfarms/sample-app-comp2"
                assert items.get("subscriptionId") == "00000000-0000-0000-0000-000000000000"
        
        for items in server_metrics.values():
            if items.get("name") == "ServiceApiHit":
                assert items.get("aggregation") == "Count"
                assert items.get("metricNamespace") == "microsoft.keyvault/vaults"
                assert items.get("resourceType") == "Microsoft.Web/serverfarms"
            elif items.get("name") == "ServiceApiLatency":
                assert items.get("name") == "ServiceApiLatency"
                assert items.get("aggregation") == "Average"
                assert items.get("resourceType") == "Microsoft.Web/serverfarms"
                assert items.get("metricNamespace") == "Microsoft.Web/serverfarms"

        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_APP_COMPONENTS2,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]

        self.cmd(
            "az load test update "
            '--load-test-config-file "{load_test_config_file}" '
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=checks,
        ).get_output_in_json()
        
        app_components_response = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=[]
        ).get_output_in_json()
        server_metric_response = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=[]
        ).get_output_in_json()

        app_components = app_components_response.get("components", {})
        server_metrics = server_metric_response.get("metrics", {})
        assert len(app_components.values()) == 1
        # Ensure at least 2 metrics are returned, default can be of any number, but we patch 2 metrics by our self.
        assert len(server_metrics.values()) == 2

        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_APP_COMPONENTS_INVALID,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]

        try:
            self.cmd(
                "az load test update "
                '--load-test-config-file "{load_test_config_file}" '
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group}",
                checks=checks,
            )
        except Exception as e:
            assert "App component name is not a valid resource id" in str(e)

        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_SERVER_METRICS_INVALID,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]

        try:
            self.cmd(
                "az load test update "
                '--load-test-config-file "{load_test_config_file}" '
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group}",
                checks=checks,
            )
        except Exception as e:
            assert "Server metric name and aggregation are required" in str(e)

        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_SERVER_METRICS_INVALID2,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]

        try:
            self.cmd(
                "az load test update "
                '--load-test-config-file "{load_test_config_file}" '
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group}",
                checks=checks,
            )
        except Exception as e:
            assert "Server metric name and aggregation are required" in str(e)