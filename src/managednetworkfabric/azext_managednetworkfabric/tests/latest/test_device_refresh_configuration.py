# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

from azure.cli.testsdk.scenario_tests import AllowLargeResponse

"""
Device tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_refresh_configuration(test, checks=[])
    cleanup_scenario1(test)


def step_refresh_configuration(test, checks=None):
    """Device refresh-configuration operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device refresh-configuration --resource-group {rg} --resource-name {name}",
        checks=checks,
    )


class GA_DeviceRefreshConfigurationScenarioTest1(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "rg": CONFIG.get("NETWORK_DEVICE", "resource_group"),
                "name": CONFIG.get("NETWORK_DEVICE", "name"),
            }
        )

    @AllowLargeResponse()
    def test_GA_Device_refresh_configuration_scenario1(self):
        """test scenario for Device refresh-configuration operation"""
        call_scenario1(self)
