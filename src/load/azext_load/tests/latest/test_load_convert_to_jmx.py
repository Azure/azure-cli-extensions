# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
)

rg_params = {
    "name_prefix": "clitest-converttojmx-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-converttojmx-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}

class LoadTestScenarioConvertToJmx(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioConvertToJmx, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_convert_to_jmx(self, rg, load):
        # Create a URL test and convert it to JMX
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_CONVERT_TO_JMX_ID,
                "load_test_config_file": LoadTestConstants.ADVANCED_URL_LOAD_TEST_CONFIG_FILE,
                "autostop_error_rate": LoadTestConstants.AUTOSTOP_ERROR_RATE,
                "autostop_error_rate_time_window": LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW,
            }
        )
        checks = [
            JMESPathCheck("testId", LoadTestConstants.LOAD_TEST_CONVERT_TO_JMX_ID),
            JMESPathCheck("kind", LoadTestConstants.ADVANCED_URL_TEST_TYPE),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" '
            "--autostop-error-rate {autostop_error_rate} "
            "--autostop-time-window {autostop_error_rate_time_window} ",
            checks=checks,
        )
        checks = [
            JMESPathCheck("testId", LoadTestConstants.LOAD_TEST_CONVERT_TO_JMX_ID),
            JMESPathCheck("kind", "JMX"),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test convert-to-jmx "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--yes",
            checks=checks,
        )
        
        # Invalid: Convert a non-URL test to JMX
        _configure_command_assert_exception(
            self,
            f"Test with test ID: {LoadTestConstants.LOAD_TEST_CONVERT_TO_JMX_ID} is not of type URL"
        )
        
        # Invalid: Convert a non-existent test to JMX
        self.kwargs.update({"test_id": LoadTestConstants.INVALID_UPDATE_TEST_ID})
        _configure_command_assert_exception(
            self,
            f"Test couldn't find with given identifier {LoadTestConstants.INVALID_UPDATE_TEST_ID}"
        )


def _configure_command_assert_exception(self, message):
    command = "az load test convert-to-jmx " \
              "--test-id {test_id} " \
              "--load-test-resource {load_test_resource} " \
              "--resource-group {resource_group} " \
              "--yes" 
    try:
        self.cmd(command)
    except Exception as e:
        assert message in str(e)
