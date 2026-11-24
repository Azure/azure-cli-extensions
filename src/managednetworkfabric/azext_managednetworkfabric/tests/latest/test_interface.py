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
from .utils.output_checks import attr


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_show_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("connectedTo", attr(test, "expectedConnectedTo")),
            test.check("interfaceType", attr(test, "expectedInterfaceType")),
            test.check("physicalIdentifier", attr(test, "expectedPhysicalIdentifier")),
            test.check(
                "administrativeState", attr(test, "expectedAdministrativeState")
            ),
        ],
    )
    step_list_resource_group_scenario1(test, checks=[])
    step_update_admin_state_Disable(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    step_update_admin_state_Enable(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_show_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("connectedTo", attr(test, "expectedConnectedTo")),
            test.check("interfaceType", attr(test, "expectedInterfaceType")),
            test.check("physicalIdentifier", attr(test, "expectedPhysicalIdentifier")),
            test.check(
                "administrativeState", attr(test, "expectedAdministrativeState")
            ),
        ],
    )
    step_list_resource_group_scenario2(test, checks=[])
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_show_scenario1(test, checks=None):
    """Interface show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface show --resource-name {name} --resource-group {rg} --device {deviceName}",
        checks=checks,
    )


def step_show_scenario2(test, checks=None):
    """Interface show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface show --resource-name {name} --resource-group {rg} --network-device-name {deviceName}",
        checks=checks,
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
        "az networkfabric interface update-admin-state --resource-group {rg} --device {deviceName} "
        "--resource-name {name} --state {stateEnable} --resource-ids {resourceIds} -f {force}",
        checks=checks,
    )


def step_update_admin_state_Disable(test, checks=None):
    """Interface Update admin state Disable operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric interface update-admin-state --resource-group {rg} --network-device-name {deviceName}"
        " --resource-name {name} --state {stateDisable} --resource-ids {resourceIds} --force {force}",
        checks=checks,
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
                "force": CONFIG.get("NETWORK_INTERFACE", "force_flag"),
                "additionalDescription": CONFIG.get(
                    "NETWORK_INTERFACE", "additional_description"
                ),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
                "expectedAdministrativeState": CONFIG.get(
                    "NETWORK_INTERFACE", "expected_administrative_state"
                ),
                "expectedConnectedTo": CONFIG.get(
                    "NETWORK_INTERFACE", "expected_connected_to"
                ),
                "expectedInterfaceType": CONFIG.get(
                    "NETWORK_INTERFACE", "expected_interface_type"
                ),
                "expectedPhysicalIdentifier": CONFIG.get(
                    "NETWORK_INTERFACE", "expected_physical_identifier"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "NETWORK_INTERFACE", "expected_provisioning_state"
                ),
                "expectedStatus": CONFIG.get("NETWORK_INTERFACE", "expected_status"),
            }
        )

    def test_GA_Interface_scenario1(self):
        """test scenario for interface CRUD operations"""
        call_scenario1(self)

    def test_GA_Interface_scenario2(self):
        """Test scenario 2 with alternate command parameters."""
        call_scenario2(self)
        self.assertTrue(self.cassette.all_played)
