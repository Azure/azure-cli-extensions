# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azext_load.tests.latest.constants import LoadTestConstants, LoadTestRunConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azext_load.tests.latest.helper import (
    create_test,
    create_test_run,
)
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    live_only,
)
from unittest.mock import patch

rg_params = {
    "name_prefix": "clitest-baseline-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-baseline-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}

# Run this test in single test live mode only
# 'azdev test test_load_test_mark_compare_baseline --live'
class LoadTestScenarioBaselineTrends(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioBaselineTrends, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    # Live only because the test runs are created with no wait
    @live_only()
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_mark_compare_baseline(self, rg, load):
        # Create a test and test run
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_BASELINE_TRENDS_ID,
                "test_run_id": LoadTestRunConstants.BASELINE_TRENDS_TEST_RUN_ID_1,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        create_test(self)
        create_test_run(self, no_wait=True)
        time.sleep(10) # sleep to ensure test run is created and progressed
        # Stop the test run before completing
        self.cmd(
            "az load test-run stop "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes",
        )
        time.sleep(10) # sleep to ensure test run is stopped
        
        # Invalid: Test run statistics are not processed yet
        msg = "Sampler statistics are not yet available"
        _configure_command_assert_exception(self, message=msg)

        time.sleep(60) # sleep to ensure test run statistics are processed
        # Valid: Set the baseline test run
        checks = [
            JMESPathCheck("baselineTestRunId", LoadTestRunConstants.BASELINE_TRENDS_TEST_RUN_ID_1),
        ]
        self.cmd(
            "az load test set-baseline "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--test-run-id {test_run_id} ",
            checks=checks,
        )
        
        # Create another test run
        self.kwargs.update(
            {
                "test_run_id": LoadTestRunConstants.BASELINE_TRENDS_TEST_RUN_ID_2,
            }
        )
        create_test_run(self, no_wait=True)
        
        # Invalid: Test run is not in a valid status to be set as baseline
        msg = "Test run with ID: " + self.kwargs["test_run_id"] + " does not have " \
            "a valid test run status"
        _configure_command_assert_exception(self, message=msg)
        time.sleep(20) # sleep to ensure test run is created and progressed
        # Stop the test run before completing to give CANCELLED status
        self.cmd(
            "az load test-run stop "
            "--test-run-id {test_run_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes",
        )

        time.sleep(60) # sleep to ensure test run statistics are processed
        self.cmd(
            "az load test-run list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        )
        
        # Create a different test and test run
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "test_run_id": LoadTestRunConstants.CREATE_TEST_RUN_ID,
            }
        )
        create_test(self)
        create_test_run(self)
        
        # Invalid: Try viewing trends for a test without a baseline test run
        msg = "Test with ID: " + self.kwargs["test_id"] + " does not have a baseline test run associated with it."
        _configure_command_assert_exception(self, message=msg, is_show_trends=True)
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_BASELINE_TRENDS_ID,
                "response_time_aggregate": "P99",
            }
        )
        
        # Invalid: Try setting a test run as baseline that is not associated with the test
        msg = "Test run with ID: " + self.kwargs["test_run_id"] + " is not " \
            "associated with test ID: " + LoadTestConstants.LOAD_TEST_BASELINE_TRENDS_ID
        _configure_command_assert_exception(self, message=msg)
        
        # Valid: Show trends for a test with a baseline test run
        response = self.cmd(
            "az load test compare-to-baseline "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()
        assert len(response) >= 1
        assert response[0]["Name"] == LoadTestRunConstants.BASELINE_TRENDS_TEST_RUN_ID_1
        assert "Response time" in response[0]
        
        # Valid: Show trends for a test with a baseline test run with aggregation param
        response = self.cmd(
            "az load test compare-to-baseline "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--aggregation {response_time_aggregate} ",
        ).get_output_in_json()
        assert "Response time" in response[0]


def _configure_command_assert_exception(self, message, is_show_trends=False):
    command = "az load test "
    if is_show_trends:
        command += "compare-to-baseline "
    else:
        command += "set-baseline --test-run-id {test_run_id} "
    command += "--test-id {test_id} " \
            "--load-test-resource {load_test_resource} " \
            "--resource-group {resource_group} "
    try:
        self.cmd(command)
    except Exception as e:
        assert message in str(e)
