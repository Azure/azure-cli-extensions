# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Monitor show/list/delete tests scenarios
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
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """networkmonitor show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor show --network-monitor-name {name} --resource-group {rg}"
    )


def step_list_resource_group(test, checks=None):
    """networkmonitor list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric networkmonitor list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """networkmonitor list by subscription"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric networkmonitor list")


def step_delete(test, checks=None):
    """networkmonitor delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric networkmonitor delete --network-monitor-name {deleteNetworkMonitorName} --resource-group {rg} --yes"
    )


class GA_NetworkMonitorScenarioTest1(ScenarioTest):
    """Network Monitor Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_MONITOR", "name"),
                "rg": CONFIG.get("NETWORK_MONITOR", "resource_group"),
                "location": CONFIG.get("NETWORK_MONITOR", "location"),
                "deleteNetworkMonitorName": CONFIG.get(
                    "NETWORK_MONITOR", "delete_networkmonitor_name"
                ),
            }
        )

    def test_GA_networkmonitor_scenario1(self):
        """test scenario for Network Monitor CRUD operations"""
        call_scenario1(self)
