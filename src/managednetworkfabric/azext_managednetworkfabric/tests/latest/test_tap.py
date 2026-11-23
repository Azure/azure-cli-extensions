# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Tap tests scenarios
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
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("networkPacketBrokerId", attr(test, "npbId")),
            test.check("pollingType", attr(test, "pollingType")),
            test.check("destinations", attr(test, "destinations")),
        ],
    )
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("networkPacketBrokerId", attr(test, "npbId")),
            test.check("pollingType", attr(test, "pollingType")),
            test.check("destinations", attr(test, "destinations")),
        ],
    )
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update_scenario1(test, checks=[])
    step_update_admin_state_Enable(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    step_update_admin_state_Disable(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    step_delete(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("networkPacketBrokerId", attr(test, "npbId")),
            test.check("pollingType", attr(test, "pollingType")),
            test.check("destinations", attr(test, "destinations")),
        ],
    )
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """Network Tap create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap create --resource-group {rg} --location {location} --resource-name {name} --npb-id {npbId} --polling-type {pollingType} "
        " --destinations {destinations} --annotation {annotation} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """Network Tap create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap create --resource-group {rg} --location {location} --resource-name {name} --network-packet-broker-id {npbId} "
        " --polling-type {pollingType} --destinations {destinations} --annotation {annotation}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_show(test, checks=None):
    """Network Tap show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap show --resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """Network Tap list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric tap list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """Network Tap list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric tap list")


def step_update_scenario1(test, checks=None):
    """Network Tap Rule update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap update --resource-name {name} --resource-group {rg} --destinations {updatedDestinations} --polling-type {updatedPollingType} --annotation {annotation}"
        " --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """Network Tap Rule update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap update --resource-name {name} --resource-group {rg} --destinations {updatedDestinations} --polling-type {updatedPollingType} --annotation {annotation}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_admin_state_Enable(test, checks=None):
    """Network Tap Update admin state operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap update-admin-state --resource-group {rg} --resource-name {name} --state "
        "{stateEnable} -f {force}",
        checks=checks,
    )


def step_update_admin_state_Disable(test, checks=None):
    """Network Tap Update admin state operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric tap update-admin-state --resource-group {rg} --resource-name {name} --state "
        "{stateDisable} --resource-ids {resourceIds} --force {force}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """Network Tap delete operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric tap delete --resource-name {name} --resource-group {rg}")


class GA_TapScenarioTest1(ScenarioTest):
    """Network Tap Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_TAP", "name"),
                "annotation": CONFIG.get("NETWORK_TAP", "annotation"),
                "rg": CONFIG.get("NETWORK_TAP", "resource_group"),
                "location": CONFIG.get("NETWORK_TAP", "location"),
                "npbId": CONFIG.get("NETWORK_TAP", "network_packet_broker_id"),
                "pollingType": CONFIG.get("NETWORK_TAP", "polling_type"),
                "destinations": CONFIG.get("NETWORK_TAP", "destinations"),
                "stateEnable": CONFIG.get("NETWORK_TAP", "state_enable"),
                "stateDisable": CONFIG.get("NETWORK_TAP", "state_disable"),
                "updatedDestinations": CONFIG.get(
                    "NETWORK_TAP", "updated_destinations"
                ),
                "updatedPollingType": CONFIG.get("NETWORK_TAP", "updated_polling_type"),
                "resourceIds": CONFIG.get("NETWORK_TAP", "resource_ids"),
                "force": CONFIG.get("NETWORK_TAP", "force_flag"),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "NETWORK_TAP", "expected_provisioning_state"
                ),
                "expectedStatus": CONFIG.get("NETWORK_TAP", "expected_status"),
            }
        )

    def test_GA_tap_scenario1(self):
        """test scenario for Network Tap CRUD operations"""
        call_scenario1(self)

    def test_GA_tap_scenario2(self):
        """Test scenario 2 with alternate command parameters."""
        call_scenario2(self)
        self.assertTrue(self.cassette.all_played)
