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
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update_admin_state_Disable(test, checks=[])
    step_update_admin_state_Enable(test, checks=[])
    step_update_additional_description(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """Interface show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface show --resource-name {name} --resource-group {rg} --device {deviceName}"
    )


def step_list_resource_group(test, checks=None):
    """Interface list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface list --resource-group {rg} --device {deviceName}"
    )


def step_update_admin_state_Enable(test, checks=None):
    """Interface Update admin state Enable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --device {deviceName} --resource-name {name} --state {stateEnable}"
    )


def step_update_admin_state_Disable(test, checks=None):
    """Interface Update admin state Disable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --device {deviceName} --resource-name {name} --state {stateDisable}"
    )


def step_update_additional_description(test, checks=None):
    """Interface Update admin state Enable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update --resource-group {rg} --device {deviceName} --resource-name {name} --additional-description {additionalDescription}"
    )


class GA_InterfaceScenarioTest1(ScenarioTest):
    """InterfaceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_INTERFACE", "name"),
                "rg": CONFIG.get("NETWORK_INTERFACE", "resource_group"),
                "deviceName": CONFIG.get("NETWORK_INTERFACE", "device_name"),
                "stateEnable": CONFIG.get("NETWORK_INTERFACE", "state_enable"),
                "stateDisable": CONFIG.get("NETWORK_INTERFACE", "state_disable"),
                "additionalDescription": CONFIG.get(
                    "NETWORK_INTERFACE", "additional_description"
                ),
            }
        )

    def test_GA_Interface_scenario1(self):
        """test scenario for interface CRUD operations"""
        call_scenario1(self)
