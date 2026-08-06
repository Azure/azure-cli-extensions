# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Neighbor Group tests scenarios
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
    """Testcase: scenario"""
    setup_scenario(test)
    step_create_scenario1(test, checks=[])
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update_scenario1(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario"""
    setup_scenario(test)
    step_create_scenario2(test, checks=[])
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """Neighbor Group create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric neighborgroup create --resource-group {rg} --location {location} --resource-name {name} --destination {destination} --annotation {annotation}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """Neighbor Group create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric neighborgroup create --resource-group {rg} --location {location} --resource-name {name} --destination {destination} --annotation {annotation}"
        " --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_show(test, checks=None):
    """Neighbor Group show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric neighborgroup show --resource-name {name} --resource-group {rg}"
    )


def step_list_resource_group(test, checks=None):
    """Neighbor Group list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric neighborgroup list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """Neighbor Group list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric neighborgroup list")


def step_update_scenario1(test, checks=None):
    """Neighbor Group update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric neighborgroup update --resource-group {rg} --resource-name {name} --destination {destinationUpdate} --annotation {annotation}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """Neighbor Group update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric neighborgroup update --resource-group {rg} --resource-name {name} --destination {destinationUpdate} --annotation {annotation}"
        " --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """Neighbor Group delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric neighborgroup delete --resource-name {name} --resource-group {rg}"
    )


class GA_NeighborGroupScenarioTest1(ScenarioTest):
    """Neighbor Group Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NEIGHBOR_GROUP", "name"),
                "rg": CONFIG.get("NEIGHBOR_GROUP", "resource_group"),
                "location": CONFIG.get("NEIGHBOR_GROUP", "location"),
                "destination": CONFIG.get("NEIGHBOR_GROUP", "destination"),
                "destinationUpdate": CONFIG.get("NEIGHBOR_GROUP", "destination_update"),
                "annotation": CONFIG.get("NETWORK_TAP_RULE", "annotation"),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_neighborgroup_scenario1(self):
        """test scenario for Neighbor Group CRUD operations"""
        call_scenario1(self)
