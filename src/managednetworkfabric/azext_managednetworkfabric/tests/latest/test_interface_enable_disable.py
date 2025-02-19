# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Interface tests scenarios
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
    step_update_admin_state_Enable(test, checks=[])
    step_update_admin_state_Disable(test, checks=[])
    cleanup_scenario1(test)


def step_update_admin_state_Enable(test, checks=None):
    """interface Update admin state operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --resource-name {name} --state {state_Enable} --device {device_name}"
    )


def step_update_admin_state_Disable(test, checks=None):
    """interface Update admin state operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --resource-name {name} --state {state_Disable} --device {device_name}"
    )


class GA_interfaceEnableDisableScenarioTest1(ScenarioTest):
    """Interface Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "rg": CONFIG.get("NETWORK_INTERFACE", "resource_group"),
                "name": CONFIG.get("NETWORK_INTERFACE", "name"),
                "device_name": CONFIG.get("NETWORK_INTERFACE", "device_name"),
                "state_Enable": CONFIG.get("NETWORK_INTERFACE", "state_Enable"),
                "state_Disable": CONFIG.get("NETWORK_INTERFACE", "state_Disable"),
            }
        )

    def test_GA_interface_enable_disable_scenario1(self):
        """test scenario for Interface CRUD operations"""
        call_scenario1(self)
