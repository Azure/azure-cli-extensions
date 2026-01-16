# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import JMESPathCheck, ResourceGroupPreparer, ScenarioTest
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
            JMESPathCheck("loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
            JMESPathCheck("autoStopCriteria.errorRate", 90.0),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 60),
            JMESPathCheck("autoStopCriteria.maximumVirtualUsersPerEngine", 5000),
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
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck(
                "autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW
            ),
            JMESPathCheck(
                "autoStopCriteria.maximumVirtualUsersPerEngine", LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE
            ),
        ]
        _configure_command_jmes_checks(
            self,
            checks,
            autostop_error_rate=LoadTestConstants.AUTOSTOP_ERROR_RATE,
            autostop_error_rate_time_window=LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW,
            autostop_maximum_vu_per_engine=LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE
        )

        # Update load test with autostop criteria when error rate is integer
        # Order of this test case is important as response payload is checked in next test case
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", float(LoadTestConstants.AUTOSTOP_ERROR_RATE_INTEGER)),
            JMESPathCheck(
                "autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW
            ),
            JMESPathCheck(
                "autoStopCriteria.maximumVirtualUsersPerEngine", LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE
            ),
        ]
        _configure_command_jmes_checks(self, checks, autostop_error_rate=LoadTestConstants.AUTOSTOP_ERROR_RATE_INTEGER)

        # Update load test with autostop disabled through command line arguments
        # Order of this test case is important as response payload is checked from previous test case
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
            JMESPathCheck("autoStopCriteria.errorRate", float(LoadTestConstants.AUTOSTOP_ERROR_RATE_INTEGER)),
            JMESPathCheck(
                "autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW
            ),
            JMESPathCheck(
                "autoStopCriteria.maximumVirtualUsersPerEngine", LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE
            ),
        ]
        _configure_command_jmes_checks(self, checks, autostop=LoadTestConstants.AUTOSTOP_DISABLED)

        # Update load test with autostop criteria through config file
        # Order of this test case is important as response payload for time-window is checked in next test case
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 85.0),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 120),
            JMESPathCheck("autoStopCriteria.maximumVirtualUsersPerEngine", 1500),
        ]
        _configure_command_jmes_checks(
            self, checks, load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP
        )

        # Update load test with autostop criteria through config file: only error rate
        # Order of this test case is important as response payload for time-window is checked from previous test case
        # Order of this test case is important as response payload for error-rate is checked in next test case
        # Order of this test case is important as response payload for max-vu-engine is checked in next test case
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 98.5),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 120),
            JMESPathCheck("autoStopCriteria.maximumVirtualUsersPerEngine", 1500),
        ]
        _configure_command_jmes_checks(
            self, checks, load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_ERROR_RATE
        )

        # Update load test with autostop criteria through config file: only time window
        # Order of this test case is important as response payload for error-rate is checked from previous test case
        # Order of this test case is important as response payload for max-vu-engine is checked in next test case
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 98.5),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 250),
            JMESPathCheck("autoStopCriteria.maximumVirtualUsersPerEngine", 1500),
        ]
        _configure_command_jmes_checks(
            self, checks, load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_TIME_WINDOW
        )

        # Update load test with autostop criteria through config file: only time window
        # Order of this test case is important as response payload for max-vu-engine is checked in next test case
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", 98.5),
            JMESPathCheck("autoStopCriteria.errorRateTimeWindowInSeconds", 250),
            JMESPathCheck("autoStopCriteria.maximumVirtualUsersPerEngine", 2500),
        ]
        _configure_command_jmes_checks(
            self, checks, load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP_MAX_VU_ENGINE
        )

        # Update load test with CLI autostop criteria when both config file and CLI arguments are provided
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", False),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck(
                "autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW
            ),
            JMESPathCheck(
                "autoStopCriteria.maximumVirtualUsersPerEngine", LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE
            ),
        ]
        _configure_command_jmes_checks(
            self,
            checks,
            autostop_error_rate=LoadTestConstants.AUTOSTOP_ERROR_RATE,
            autostop_error_rate_time_window=LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW,
            autostop_maximum_vu_per_engine=LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP,
        )

        # Update load test with CLI autostop criteria disabled true when
        # config file has autostop criteria and CLI argument is --autostop disable
        checks = [
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
            JMESPathCheck("autoStopCriteria.errorRate", LoadTestConstants.AUTOSTOP_ERROR_RATE),
            JMESPathCheck(
                "autoStopCriteria.errorRateTimeWindowInSeconds", LoadTestConstants.AUTOSTOP_ERROR_RATE_TIME_WINDOW
            ),
            JMESPathCheck(
                "autoStopCriteria.maximumVirtualUsersPerEngine", LoadTestConstants.AUTOSTOP_MAXIMUM_VIRTUAL_USERS_PER_ENGINE
            ),
        ]
        _configure_command_jmes_checks(
            self,
            checks,
            autostop=LoadTestConstants.AUTOSTOP_DISABLED,
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_AUTOSTOP,
        )

        # Invalid autostop test case: autostop not of string type
        _configure_command_assert_exception(self, "Invalid autostop type", autostop=1)

        # Invalid autostop test case: autostop not in allowed values
        _configure_command_assert_exception(self, "Allowed values: enable, disable", autostop="random")

        # Invalid autostop test case: autostop error rate > 100.0
        _configure_command_assert_exception(
            self, "Autostop error rate should be in range of [0.0,100.0]", autostop_error_rate=110.5
        )

        # Invalid autostop test case: autostop error rate < 0.0
        _configure_command_assert_exception(
            self, "Autostop error rate should be in range of [0.0,100.0]", autostop_error_rate=-2.5
        )

        # Invalid autostop test case: autostop error rate not of float type
        # This is not needed as the argument is type checked
        # argument --autostop-error-rate: invalid float value: 'rate'

        # Invalid autostop test case: autostop error rate time window < 0
        _configure_command_assert_exception(
            self,
            "Autostop error rate time window should be greater than or equal to 0",
            autostop_error_rate_time_window=-1,
        )

        # Invalid autostop test case: autostop maximum VU per engine = 0
        _configure_command_assert_exception(
            self,
            "Autostop maximum users per engine should be greater than 0",
            autostop_maximum_vu_per_engine=0,
        )

        # Invalid autostop test case: autostop maximum VU per engine < 0
        _configure_command_assert_exception(
            self,
            "Autostop maximum users per engine should be greater than 0",
            autostop_maximum_vu_per_engine=0,
        )

        # Invalid autostop test case: autostop error rate time window not of integer type
        # This is not needed as the argument is type checked
        # argument --autostop-time-window: invalid int value: '90.4'
        # argument --autostop-time-window: invalid int value: 'window'

        # Invalid autostop from config test case: autostop random string
        _configure_command_assert_exception(
            self,
            "Invalid value for autoStop. Valid values are 'disable' or an object with errorPercentage, timeWindow and/or maximumVirtualUsersPerEngine",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP,
        )

        # Invalid autostop from config test case: autostop error rate > 100.0
        _configure_command_assert_exception(
            self,
            "Invalid value for errorPercentage. Value should be a number between 0.0 and 100.0",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_ERROR_RATE,
        )

        # Invalid autostop from config test case: autostop time window < 0
        _configure_command_assert_exception(
            self,
            "Invalid value for timeWindow. Value should be an integer greater than or equal to 0",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_TIME_WINDOW,
        )

        # Invalid autostop from config test case: autostop time window < 0
        _configure_command_assert_exception(
            self,
            "Invalid value for maximumVirtualUsersPerEngine. Value should be an integer greater than 0",
            load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE_WITH_INVALID_AUTOSTOP_MAX_VU_PER_ENGINE,
        )


def _configure_command_jmes_checks(
    self,
    checks,
    autostop=None,
    autostop_error_rate=None,
    autostop_error_rate_time_window=None,
    autostop_maximum_vu_per_engine=None,
    load_test_config_file=None,
):
    command = (
        "az load test update "
        "--test-id {test_id} "
        "--load-test-resource {load_test_resource} "
        "--resource-group {resource_group} "
    )
    if autostop is not None:
        self.kwargs.update(
            {
                "autostop": autostop,
            }
        )
        command += "--autostop {autostop} "
    if autostop_error_rate is not None:
        self.kwargs.update(
            {
                "autostop_error_rate": autostop_error_rate,
            }
        )
        command += "--autostop-error-rate {autostop_error_rate} "
    if autostop_error_rate_time_window is not None:
        self.kwargs.update(
            {
                "autostop_error_rate_time_window": autostop_error_rate_time_window,
            }
        )
        command += "--autostop-time-window {autostop_error_rate_time_window} "
    if autostop_maximum_vu_per_engine is not None:
        self.kwargs.update(
            {
                "autostop_maximum_vu_per_engine": autostop_maximum_vu_per_engine,
            }
        )
        command += "--autostop-engine-users {autostop_maximum_vu_per_engine} "
    if load_test_config_file is not None:
        self.kwargs.update(
            {
                "load_test_config_file": load_test_config_file,
            }
        )
        command += '--load-test-config-file "{load_test_config_file}" '
    self.cmd(
        command,
        checks=checks,
    )


def _configure_command_assert_exception(
    self,
    message,
    autostop=None,
    autostop_error_rate=None,
    autostop_error_rate_time_window=None,
    autostop_maximum_vu_per_engine=None,
    load_test_config_file=None,
):
    command = (
        "az load test update "
        "--test-id {test_id} "
        "--load-test-resource {load_test_resource} "
        "--resource-group {resource_group} "
    )
    if autostop is not None:
        self.kwargs.update(
            {
                "autostop": autostop,
            }
        )
        command += "--autostop {autostop} "
    if autostop_error_rate is not None:
        self.kwargs.update(
            {
                "autostop_error_rate": autostop_error_rate,
            }
        )
        command += "--autostop-error-rate {autostop_error_rate} "
    if autostop_error_rate_time_window is not None:
        self.kwargs.update(
            {
                "autostop_error_rate_time_window": autostop_error_rate_time_window,
            }
        )
        command += "--autostop-time-window {autostop_error_rate_time_window} "
    if autostop_maximum_vu_per_engine is not None:
        self.kwargs.update(
            {
                "autostop_maximum_vu_per_engine": autostop_maximum_vu_per_engine,
            }
        )
        command += "--autostop-engine-users {autostop_maximum_vu_per_engine} "
    if load_test_config_file is not None:
        self.kwargs.update(
            {
                "load_test_config_file": load_test_config_file,
            }
        )
        command += '--load-test-config-file "{load_test_config_file}" '
    try:
        self.cmd(
            command,
        )
    except Exception as e:
        assert message in str(e)
