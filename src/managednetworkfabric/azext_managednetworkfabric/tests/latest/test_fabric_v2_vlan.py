# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 VLAN test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the VLAN CRUD lifecycle."""
    step_create_scenario1(
        test,
        [
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("vlanId", test.kwargs["vlanId"].strip('"')),
        ],
    )
    step_show(test, [test.check("name", test.kwargs["name"].strip('"'))])
    step_update_scenario1(
        test,
        [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
    )
    step_list(test, [test.check("[0].name", test.kwargs["name"].strip('"'))])
    step_delete(test)


def call_scenario2(test):
    """Test VLAN create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
    )


def step_create_scenario1(test, checks=None):
    """Create a VLAN."""
    test.cmd(
        "az networkfabric fabric-v2 vlan create --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name} --location {location} "
        "--vlan-id {vlanId} --description {description} "
        "--management-policy {managementPolicy} --mtu {mtu} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a VLAN using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vlan create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --resource-name {name} "
        "--location {location} --vlan-id {vlanId} --desc {description} "
        "--mgt-policy {managementPolicy} --mtu {mtu} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a VLAN."""
    test.cmd(
        "az networkfabric fabric-v2 vlan show --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a VLAN."""
    test.cmd(
        "az networkfabric fabric-v2 vlan update --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name} "
        "--description {updatedDescription} "
        "--management-policy {updatedManagementPolicy} "
        "--mtu {updatedMtu} --tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a VLAN using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vlan update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --resource-name {name} "
        "--desc {updatedDescription} --mgt-policy {updatedManagementPolicy} "
        "--mtu {updatedMtu} --tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List VLANs by Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 vlan list --resource-group {rg} "
        "--fabric-v2 {fabricName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a VLAN."""
    test.cmd(
        "az networkfabric fabric-v2 vlan delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2VlanScenarioTest(ScenarioTest):
    """Fabric v2 VLAN scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_VLAN", "name"),
                "rg": CONFIG.get("FABRIC_V2_VLAN", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_VLAN", "fabric_name"),
                "location": CONFIG.get("FABRIC_V2_VLAN", "location"),
                "vlanId": CONFIG.get("FABRIC_V2_VLAN", "vlan_id"),
                "description": CONFIG.get("FABRIC_V2_VLAN", "description"),
                "updatedDescription": CONFIG.get(
                    "FABRIC_V2_VLAN", "updated_description"
                ),
                "managementPolicy": CONFIG.get("FABRIC_V2_VLAN", "management_policy"),
                "mtu": CONFIG.get("FABRIC_V2_VLAN", "mtu"),
                "tags": CONFIG.get("FABRIC_V2_VLAN", "tags"),
                "updatedManagementPolicy": CONFIG.get(
                    "FABRIC_V2_VLAN", "updated_management_policy"
                ),
                "updatedMtu": CONFIG.get("FABRIC_V2_VLAN", "updated_mtu"),
                "updatedTags": CONFIG.get("FABRIC_V2_VLAN", "updated_tags"),
            }
        )

    def test_fabric_v2_vlan_scenario1(self):
        """Test Fabric v2 VLAN CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_vlan_scenario2(self):
        """Test Fabric v2 VLAN CRUD operations with parameter aliases."""
        call_scenario2(self)
