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


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def step_show(test, checks=None):
    """Device show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device show --resource-name {name} --resource-group {rg}"
    )


def step_list_resource_group(test, checks=None):
    """Device list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric device list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """Device list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric device list")


def step_update_scenario1(test, checks=None):
    """Device update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device update --resource-group {rg} --resource-name {name} --serial-number {serialNumber} --annotation {annotation} --host-name {hostName}"
        " --identity-selector {identitySelector} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """Device update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device update --resource-group {rg} --resource-name {name} --serial-number {serialNumber} --annotation {annotation} --host-name {hostName}"
        " --identity-selector {identitySelector} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


class GA_DeviceScenarioTest1(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "name"),
                "annotation": CONFIG.get("NETWORK_DEVICE", "annotation"),
                "rg": CONFIG.get("NETWORK_DEVICE", "resource_group"),
                "hostName": CONFIG.get("NETWORK_DEVICE", "host_name"),
                "serialNumber": CONFIG.get("NETWORK_DEVICE", "serial_number"),
                "identitySelector": CONFIG.get("MANAGED_IDENTITY", "identity_selector"),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    @AllowLargeResponse()
    def test_GA_device_scenario1(self):
        """test scenario for Device CRUD operations"""
        call_scenario1(self)
