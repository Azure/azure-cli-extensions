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
from knack.log import get_logger

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-autostopload-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-autostopload-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}

class LoadTestScenarioAutostop(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioAutostop, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})
    
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_autostop(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "description": LoadTestConstants.DESCRIPTION,
                "display_name": LoadTestConstants.DISPLAY_NAME,
                "engine_instance": LoadTestConstants.ENGINE_INSTANCE,
            }
        )
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
            JMESPathCheck("autoStopCriteria.errorRate", 90.0),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 60),
        ]
        # Create load test with autostop disabled through config file
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" '
            "--description {description} "
            "--display-name {display_name} "
            "--engine-instance {engine_instance} ",
            checks=checks,
        )
        # Update load test with autostop criteria through command line arguments
        self.kwargs.update(
            {
                "autostop_error_rate": LoadTestConstants.AUTOSTOP_ERROR_RATE,
                "autostop_error_rate_time_window": LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--autostop-error-rate {autostop_error_rate} '
            '--autostop-time-window {autostop_error_rate_time_window} '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with autostop criteria when error rate is integer
        # Order of this test case is important as response payload is checked in next test case
        self.kwargs.update(
            {
                "autostop_error_rate": LoadTestConstants.AUTOSTOP_ERROR_RATE_INTEGER,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", float(LoadTestConstants.AUTOSTOP_ERROR_RATE_INTEGER)),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--autostop-error-rate {autostop_error_rate} '
            '--autostop-time-window {autostop_error_rate_time_window} '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with autostop disabled through command line arguments
        # Order of this test case is important as response payload is checked from previous test case
        self.kwargs.update(
            {
                "autostop": LoadTestConstants.AUTOSTOP_DISABLED,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
            JMESPathCheck("autoStopCriteria.errorRate", float(LoadTestConstants.AUTOSTOP_ERROR_RATE_INTEGER)),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--autostop {autostop} '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with autostop criteria through config file
        # Order of this test case is important as response payload for time-window is checked in next test case
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 85.0),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 120),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with autostop criteria through config file: only error rate
        # Order of this test case is important as response payload for time-window is checked from previous test case
        # Order of this test case is important as response payload for error-rate is checked in next test case
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_ERROR_RATE,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 98.5),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 120),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with autostop criteria through config file: only time window
        # Order of this test case is important as response payload for error-rate is checked from previous test case
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_TIME_WINDOW,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 98.5),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 250),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with CLI autostop criteria when both config file and CLI arguments are provided
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP,
                "autostop_error_rate": LoadTestConstants.AUTOSTOP_ERROR_RATE,
                "autostop_error_rate_time_window": LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            '--autostop-error-rate {autostop_error_rate} '
            '--autostop-time-window {autostop_error_rate_time_window} '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update load test with CLI autostop criteria disabled true when
        # config file has autostop criteria and CLI argument is --autostop disable
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP,
                "autostop": LoadTestConstants.AUTOSTOP_DISABLED,
            }
        )
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            '--autostop {autostop} '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Invalid autostop test case: autostop not of string type
        self.kwargs.update({
                "autostop": 1,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--autostop {autostop} '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid autostop type" in str(e)
        # Invalid autostop test case: autostop not in allowed values
        self.kwargs.update({
                "autostop": "random",
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--autostop {autostop} '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Allowed values: enable, disable" in str(e)
        # Invalid autostop test case: autostop error rate > 100.0
        self.kwargs.update({
                "autostop_error_rate": 110.5,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--autostop-error-rate {autostop_error_rate} '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Autostop error rate should be in range of [0.0,100.0]" in str(e)
        # Invalid autostop test case: autostop error rate < 0.0
        self.kwargs.update({
                "autostop_error_rate": -2.5,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--autostop-error-rate {autostop_error_rate} '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Autostop error rate should be in range of [0.0,100.0]" in str(e)
        # Invalid autostop test case: autostop error rate not of float type
        # This is not needed as the argument is type checked
        # argument --autostop-error-rate: invalid float value: 'rate'
        
        # Invalid autostop test case: autostop error rate time window < 0
        self.kwargs.update({
                "autostop_error_rate_time_window": -1,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--autostop-time-window {autostop_error_rate_time_window} '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Autostop error rate time window should be greater than or equal to 0" in str(e)
        # Invalid autostop test case: autostop error rate time window not of integer type
        # This is not needed as the argument is type checked
        # argument --autostop-time-window: invalid int value: '90.4'
        # argument --autostop-time-window: invalid int value: 'window'
        
        # Invalid autostop from config test case: autostop random string
        self.kwargs.update({
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--load-test-config-file "{load_test_config_file}" '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid value for autoStop. Valid values are 'disable' or an object with errorPercentage and timeWindow" in str(e)
        
        # Invalid autostop from config test case: autostop error rate > 100.0
        self.kwargs.update({
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_ERROR_RATE,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--load-test-config-file "{load_test_config_file}" '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid value for errorPercentage. Value should be a number between 0.0 and 100.0" in str(e)
        # Invalid autostop from config test case: autostop time window < 0
        self.kwargs.update({
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_TIME_WINDOW,
            })
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--load-test-config-file "{load_test_config_file}" '
                "--resource-group {resource_group} ",
                checks=checks,
            )
        except Exception as e:
            assert "Invalid value for timeWindow. Value should be an integer greater than or equal to 0" in str(e)
