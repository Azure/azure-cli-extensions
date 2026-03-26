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
    "name_prefix": "clitest-pf-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-pf-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}


class LoadTestScenarioPassFailCriteria(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioPassFailCriteria, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_failure_criteria(self, rg, load):
        self.kwargs.update(
            identity_type=LoadTestConstants.ENGINE_REFERENCE_TYPE_USERASSIGNED,
            user_assigned={LoadTestConstants.LOAD_TEST_METRICS_MI: {}}
        )
        response = self.cmd(
            "az load update "
            "--name {load_test_resource} "
            "--resource-group {resource_group} "
            "--identity-type {identity_type} "
            '--user-assigned "{user_assigned}" '
        ).get_output_in_json()
        # Create a Locust based Azure Load Test
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_CRITERIA_OLD_MODEL,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]

        response = self.cmd(
            "az load test create "
            '--load-test-config-file "{load_test_config_file}" '
            "--test-id {test_id} "
            "--test-type {test_type} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=checks,
        ).get_output_in_json()
        pass_fail_metric = response.get("passFailCriteria", {}).get(
            "passFailMetrics", {}
        )
        pass_fail_server_metric = response.get("passFailCriteria", {}).get(
            "passFailServerMetrics", {}
        )
        assert len(pass_fail_metric.values()) == 3
        assert len(pass_fail_server_metric.values()) == 0

        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_CRITERIA,
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            '--load-test-config-file "{load_test_config_file}" '
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=checks,
        ).get_output_in_json()
        pass_fail_metric = response.get("passFailCriteria", {}).get(
            "passFailMetrics", {}
        )
        pass_fail_server_metric = response.get("passFailCriteria", {}).get(
            "passFailServerMetrics", {}
        )

        assert len(pass_fail_metric.values()) == 4
        assert len(pass_fail_server_metric.values()) == 0

        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_SERVER_CRITERIA,
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            '--load-test-config-file "{load_test_config_file}" '
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}",
            checks=checks,
        ).get_output_in_json()
        pass_fail_metric = response.get("passFailCriteria", {}).get(
            "passFailMetrics", {}
        )
        pass_fail_server_metric = response.get("passFailCriteria", {}).get(
            "passFailServerMetrics", {}
        )

        assert len(pass_fail_metric.values()) == 0
        assert len(pass_fail_server_metric.values()) == 2

        for items in pass_fail_server_metric.values():
            if items.get("metricName") == "CpuPercentage":
                assert items.get("aggregation") == "Maximum"
                assert items.get("condition") == '>'
                assert items.get("metricNamespace") == "Microsoft.Web/serverfarms"
                assert abs(items.get("value") - 0.0) < LoadTestConstants.FLOAT_TOLERANCE
            else:
                assert items.get("metricName") == "MemoryPercentage"
                assert items.get("aggregation") == "Average"
                assert items.get("condition") == '<'
                assert items.get("metricNamespace") == "microsoft.web/serverfarms"
                assert abs(items.get("value") - 100.0) < LoadTestConstants.FLOAT_TOLERANCE
        
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOCUST_LOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_CRITERIA_COMPLETE,
                "test_type": "JMX"
            }
        )
        checks = [
            JMESPathCheck("kind", "JMX"),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            '--load-test-config-file "{load_test_config_file}" '
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
            checks=checks,
        ).get_output_in_json()
        pass_fail_metric = response.get("passFailCriteria", {}).get(
            "passFailMetrics", {}
        )
        pass_fail_server_metric = response.get("passFailCriteria", {}).get(
            "passFailServerMetrics", {}
        )

        assert len(pass_fail_metric.values()) == 3
        assert len(pass_fail_server_metric.values()) == 2

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
        assert len(server_metrics.values()) == 3

        # Invalid: test plan is locust but test type is not locust
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_CRITERIA_INVALID,
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                '--load-test-config-file "{load_test_config_file}" '
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid failure criteria for server metrics" in str(e)
        
        # Invalid: test plan is locust but test type is not locust
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_CRITERIA_INVALID3,
            }
        )

        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                '--load-test-config-file "{load_test_config_file}" '
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid failure criteria for server metrics" in str(e)
        
        # Invalid: test plan is locust but test type is not locust
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PF_CRITERIA_INVALID2,
            }
        )

        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                '--load-test-config-file "{load_test_config_file}" '
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid failure criteria for server metrics" in str(e)