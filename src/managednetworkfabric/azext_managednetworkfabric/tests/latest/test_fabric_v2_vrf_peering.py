# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 VRF Peering test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the VRF Peering CRUD lifecycle."""
    step_create_scenario1(
        test,
        [
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("peerAsn", int(test.kwargs["peerAsn"].strip('"'))),
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
    """Test VRF Peering create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
    )
    step_show_scenario2(test)
    step_list_scenario2(test)
    step_delete_scenario2(test)


def step_create_scenario1(test, checks=None):
    """Create a VRF Peering."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--location {location} --description {description} --peer-asn {peerAsn} "
        "--bfd-enabled {bfdEnabled} --primary-ipv4-prefix {primaryIpv4Prefix} "
        "--primary-ipv6-prefix {primaryIpv6Prefix} "
        "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
        "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
        "--management-policy {managementPolicy} "
        "--arista-cv-config {aristaCvConfig} --cisco-aci-config {ciscoAciConfig} "
        "--platform-mg-config {platformManagedConfig} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a VRF Peering using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} --desc {description} "
        "--peer-asn {peerAsn} --bfd-enabled {bfdEnabled} "
        "--primary-ipv4-prefix {primaryIpv4Prefix} "
        "--primary-ipv6-prefix {primaryIpv6Prefix} "
        "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
        "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
        "--mgt-policy {managementPolicy} --acvc {aristaCvConfig} "
        "--cisco-aci-config {ciscoAciConfig} "
        "--platform-managed-config {platformManagedConfig} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a VRF Peering."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering show --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_show_scenario2(test, checks=None):
    """Show a VRF Peering using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering show --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a VRF Peering."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--description {updatedDescription} --peer-asn {peerAsn} "
        "--bfd-enabled {updatedBfdEnabled} "
        "--primary-ipv4-prefix {primaryIpv4Prefix} "
        "--primary-ipv6-prefix {primaryIpv6Prefix} "
        "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
        "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
        "--management-policy {updatedManagementPolicy} "
        "--arista-cv-config {aristaCvConfig} --cisco-aci-config {ciscoAciConfig} "
        "--platform-mg-config {platformManagedConfig} --tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a VRF Peering using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --desc {updatedDescription} "
        "--peer-asn {peerAsn} --bfd-enabled {updatedBfdEnabled} "
        "--primary-ipv4-prefix {primaryIpv4Prefix} "
        "--primary-ipv6-prefix {primaryIpv6Prefix} "
        "--secondary-ipv4-prefix {secondaryIpv4Prefix} "
        "--secondary-ipv6-prefix {secondaryIpv6Prefix} "
        "--mgt-policy {updatedManagementPolicy} --acvc {aristaCvConfig} "
        "--cisco-aci-config {ciscoAciConfig} "
        "--platform-managed-config {platformManagedConfig} --tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List VRF Peerings by VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering list --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName}",
        checks=checks or [],
    )


def step_list_scenario2(test, checks=None):
    """List VRF Peerings by VRF using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering list --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a VRF Peering."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_delete_scenario2(test, checks=None):
    """Delete a VRF Peering using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf peering delete --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2VrfPeeringScenarioTest(ScenarioTest):
    """Fabric v2 VRF Peering scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_VRF_PEERING", "name"),
                "rg": CONFIG.get("FABRIC_V2_VRF_PEERING", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_VRF_PEERING", "fabric_name"),
                "vrfName": CONFIG.get("FABRIC_V2_VRF_PEERING", "vrf_name"),
                "location": CONFIG.get("FABRIC_V2_VRF_PEERING", "location"),
                "description": CONFIG.get("FABRIC_V2_VRF_PEERING", "description"),
                "updatedDescription": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "updated_description"
                ),
                "bfdEnabled": CONFIG.get("FABRIC_V2_VRF_PEERING", "bfd_enabled"),
                "updatedBfdEnabled": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "updated_bfd_enabled"
                ),
                "peerAsn": CONFIG.get("FABRIC_V2_VRF_PEERING", "peer_asn"),
                "managementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "management_policy"
                ),
                "updatedManagementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "updated_management_policy"
                ),
                "primaryIpv4Prefix": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "primary_ipv4_prefix"
                ),
                "primaryIpv6Prefix": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "primary_ipv6_prefix"
                ),
                "secondaryIpv4Prefix": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "secondary_ipv4_prefix"
                ),
                "secondaryIpv6Prefix": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "secondary_ipv6_prefix"
                ),
                "aristaCvConfig": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "arista_cv_config"
                ),
                "ciscoAciConfig": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "cisco_aci_config"
                ),
                "platformManagedConfig": CONFIG.get(
                    "FABRIC_V2_VRF_PEERING", "platform_managed_config"
                ),
                "tags": CONFIG.get("FABRIC_V2_VRF_PEERING", "tags"),
                "updatedTags": CONFIG.get("FABRIC_V2_VRF_PEERING", "updated_tags"),
            }
        )

    def test_fabric_v2_vrf_peering_scenario1(self):
        """Test Fabric v2 VRF Peering CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_vrf_peering_scenario2(self):
        """Test Fabric v2 VRF Peering CRUD operations with parameter aliases."""
        call_scenario2(self)
