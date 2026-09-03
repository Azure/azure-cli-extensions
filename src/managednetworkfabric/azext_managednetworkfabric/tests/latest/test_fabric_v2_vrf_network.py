# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 VRF Network test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the VRF Network CRUD lifecycle."""
    step_create_scenario1(
        test,
        [
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("description", test.kwargs["description"].strip('"')),
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
    """Test VRF Network create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
    )
    step_show_scenario2(test)
    step_list_scenario2(test)
    step_delete_scenario2(test)


def step_create_scenario1(test, checks=None):
    """Create a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--location {location} --description {description} "
        "--vlan-resource-id {vlanResourceId} --connected-subnets {connectedSubnets} "
        "--management-policy {managementPolicy} --mtu {mtu} "
        "--arista-cv-config {aristaCvConfig} --cisco-aci-config {ciscoAciConfig} "
        "--platform-managed-config {platformManagedConfig} "
        "--user-managed-config {userManagedConfig} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} --desc {description} "
        "--vlan-id {vlanResourceId} --conn-subnets {connectedSubnets} "
        "--mgt-policy {managementPolicy} --mtu {mtu} --acvc {aristaCvConfig} "
        "--cisco-aci-config {ciscoAciConfig} --pmc {platformManagedConfig} "
        "--pm-config {platformManagedConfig} --um-config {userManagedConfig} "
        "--tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network show --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_show_scenario2(test, checks=None):
    """Show a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network show --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--description {updatedDescription} --vlan-resource-id {vlanResourceId} "
        "--connected-subnets {connectedSubnets} "
        "--management-policy {updatedManagementPolicy} --mtu {updatedMtu} "
        "--arista-cv-config {aristaCvConfig} --cisco-aci-config {ciscoAciConfig} "
        "--platform-managed-config {platformManagedConfig} "
        "--user-managed-config {userManagedConfig} --tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --desc {updatedDescription} "
        "--vlan-id {vlanResourceId} --conn-subnets {connectedSubnets} "
        "--mgt-policy {updatedManagementPolicy} --mtu {updatedMtu} "
        "--acvc {aristaCvConfig} --cisco-aci-config {ciscoAciConfig} "
        "--pmc {platformManagedConfig} --pm-config {platformManagedConfig} "
        "--um-config {userManagedConfig} --tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List VRF Networks by VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network list --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName}",
        checks=checks or [],
    )


def step_list_scenario2(test, checks=None):
    """List VRF Networks by VRF using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network list --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a VRF Network."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_delete_scenario2(test, checks=None):
    """Delete a VRF Network using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf network delete --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2VrfNetworkScenarioTest(ScenarioTest):
    """Fabric v2 VRF Network scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_VRF_NETWORK", "name"),
                "rg": CONFIG.get("FABRIC_V2_VRF_NETWORK", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_VRF_NETWORK", "fabric_name"),
                "vrfName": CONFIG.get("FABRIC_V2_VRF_NETWORK", "vrf_name"),
                "location": CONFIG.get("FABRIC_V2_VRF_NETWORK", "location"),
                "description": CONFIG.get("FABRIC_V2_VRF_NETWORK", "description"),
                "updatedDescription": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "updated_description"
                ),
                "vlanResourceId": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "vlan_resource_id"
                ),
                "connectedSubnets": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "connected_subnets"
                ),
                "managementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "management_policy"
                ),
                "updatedManagementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "updated_management_policy"
                ),
                "mtu": CONFIG.get("FABRIC_V2_VRF_NETWORK", "mtu"),
                "updatedMtu": CONFIG.get("FABRIC_V2_VRF_NETWORK", "updated_mtu"),
                "aristaCvConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "arista_cv_config"
                ),
                "ciscoAciConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "cisco_aci_config"
                ),
                "platformManagedConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "platform_managed_config"
                ),
                "userManagedConfig": CONFIG.get(
                    "FABRIC_V2_VRF_NETWORK", "user_managed_config"
                ),
                "tags": CONFIG.get("FABRIC_V2_VRF_NETWORK", "tags"),
                "updatedTags": CONFIG.get("FABRIC_V2_VRF_NETWORK", "updated_tags"),
            }
        )

    def test_fabric_v2_vrf_network_scenario1(self):
        """Test Fabric v2 VRF Network CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_vrf_network_scenario2(self):
        """Test Fabric v2 VRF Network CRUD operations with parameter aliases."""
        call_scenario2(self)
