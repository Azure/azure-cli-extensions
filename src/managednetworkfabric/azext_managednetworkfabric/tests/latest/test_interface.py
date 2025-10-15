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


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_show_scenario1(test, checks=[])
    step_list_resource_group_scenario1(test, checks=[])
    step_update_admin_state_Disable(test, checks=[])
    step_update_admin_state_Enable(test, checks=[])
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_show_scenario2(test, checks=[])
    step_list_resource_group_scenario2(test, checks=[])
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_show_scenario1(test, checks=None):
    """Interface show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface show --resource-name {name} --resource-group {rg} --device {deviceName}"
    )


def step_show_scenario2(test, checks=None):
    """Interface show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface show --resource-name {name} --resource-group {rg} --network-device-name {deviceName}"
    )


def step_list_resource_group_scenario1(test, checks=None):
    """Interface list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface list --resource-group {rg} --device {deviceName}"
    )


def step_list_resource_group_scenario2(test, checks=None):
    """Interface list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface list --resource-group {rg} --network-device-name {deviceName}"
    )


def step_update_scenario1(test, checks=None):
    """Interface Update admin state Enable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update --resource-group {rg} --device {deviceName} --resource-name {name} "
        " --additional-description {additionalDescription} --annotation {annotation}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """Interface Update admin state Enable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update --resource-group {rg} --network-device-name {deviceName} --resource-name {name} "
        " --additional-description {additionalDescription} --annotation {annotation}"
        " --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_admin_state_Enable(test, checks=None):
    """Interface Update admin state Enable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --device {deviceName} --resource-name {name} --state {stateEnable} --resource-ids {resourceIds}"
    )


def step_update_admin_state_Disable(test, checks=None):
    """Interface Update admin state Disable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --network-device-name {deviceName} --resource-name {name} --state {stateDisable} --resource-ids {resourceIds}"
    )


class GA_InterfaceScenarioTest1(ScenarioTest):
    """InterfaceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_INTERFACE", "name"),
                "annotation": CONFIG.get("NETWORK_INTERFACE", "annotation"),
                "rg": CONFIG.get("NETWORK_INTERFACE", "resource_group"),
                "deviceName": CONFIG.get("NETWORK_INTERFACE", "device_name"),
                "stateEnable": CONFIG.get("NETWORK_INTERFACE", "state_enable"),
                "stateDisable": CONFIG.get("NETWORK_INTERFACE", "state_disable"),
                "resourceIds": CONFIG.get("NETWORK_INTERFACE", "resource_ids"),
                "additionalDescription": CONFIG.get(
                    "NETWORK_INTERFACE", "additional_description"
                ),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_Interface_scenario1(self):
        """test scenario for interface CRUD operations"""
        call_scenario1(self)
