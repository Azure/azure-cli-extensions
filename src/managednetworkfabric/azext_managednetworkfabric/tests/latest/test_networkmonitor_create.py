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


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_create(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """Network Monitor create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor create --resource-group {rg} --location {location} --network-monitor-name {name}"
        " --bmp-configuration {bmpConfiguration}",
        checks=checks,
    )


class GA_NetworkMonitorCreateScenarioTest1(ScenarioTest):
    """NetworkMonitor Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_MONITOR", "name"),
                "rg": CONFIG.get("NETWORK_MONITOR", "resource_group"),
                "location": CONFIG.get("NETWORK_MONITOR", "location"),
                "bmpConfiguration": CONFIG.get("NETWORK_MONITOR", "bmp_configuration"),
            }
        )

    def test_GA_networkmonitor_create_scenario1(self):
        """test scenario for NetworkMonitor create operations"""
        call_scenario1(self)
