# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Monitor create test scenarios
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
    step_create_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_create_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """Network Monitor create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor create --resource-group {rg} --location {location} --network-monitor-name {name}"
        " --bmp-configuration {bmpConfiguration} --annotation {annotation}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """Network Monitor create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor create --resource-group {rg} --location {location} --resource-name {name}"
        " --bmp-configuration {bmpConfiguration} --annotation {annotation}",
        checks=checks,
    )


class GA_NetworkMonitorCreateScenarioTest1(ScenarioTest):
    """NetworkMonitor Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_MONITOR", "name"),
                "annotation": CONFIG.get("NETWORK_MONITOR", "annotation"),
                "rg": CONFIG.get("NETWORK_MONITOR", "resource_group"),
                "location": CONFIG.get("NETWORK_MONITOR", "location"),
                "bmpConfiguration": CONFIG.get("NETWORK_MONITOR", "bmp_configuration"),
            }
        )

    def test_GA_networkmonitor_create_scenario1(self):
        """test scenario for NetworkMonitor create operations"""
        call_scenario1(self)
