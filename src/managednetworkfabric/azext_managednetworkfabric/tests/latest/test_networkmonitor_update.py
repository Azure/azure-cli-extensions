# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Monitor update test scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_update_scenario1(test, checks=None):
    """Network Monitor delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor update --network-monitor-name {name} --resource-group {rg} --bmp-configuration {updatedBmpConfiguration}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """Network Monitor delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor update --resource-name {name} --resource-group {rg} --bmp-configuration {updatedBmpConfiguration}",
        checks=checks,
    )


class GA_NetworkMonitorUpdateScenarioTest1(ScenarioTest):
    """NetworkMonitor Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_MONITOR", "name"),
                "rg": CONFIG.get("NETWORK_MONITOR", "resource_group"),
                "location": CONFIG.get("NETWORK_MONITOR", "location"),
                "bmpConfiguration": CONFIG.get("NETWORK_MONITOR", "bmp_configuration"),
                "updatedBmpConfiguration": CONFIG.get(
                    "NETWORK_MONITOR", "updated_bmp_configuration"
                ),
            }
        )

    def test_GA_networkmonitor_update_scenario1(self):
        """test scenario for Network Monitor update/patch operations"""
        call_scenario1(self)
