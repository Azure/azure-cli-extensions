# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 VRF Delegation test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the VRF Delegation CRUD lifecycle."""
    step_create_scenario1(
        test,
        [
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("administrativeState", test.kwargs["adminState"].strip('"')),
        ],
    )
    step_show(test, [test.check("name", test.kwargs["name"].strip('"'))])
    step_update_scenario1(
        test,
        [
            test.check(
                "administrativeState",
                test.kwargs["updatedAdminState"].strip('"'),
            )
        ],
    )
    step_list(test, [test.check("[0].name", test.kwargs["name"].strip('"'))])
    step_delete(test)


def call_scenario2(test):
    """Test VRF Delegation create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        [
            test.check(
                "administrativeState",
                test.kwargs["updatedAdminState"].strip('"'),
            )
        ],
    )


def step_create_scenario1(test, checks=None):
    """Create a VRF Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation create --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--location {location} --admin-state {adminState} "
        "--address-prefixes {addressPrefixes} --egress-network {egressNetwork} "
        "--fabric-delegation-id {fabricDelegationId} --limits {limits} "
        "--tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a VRF Delegation using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} --admin-state {adminState} "
        "--address-prefixes {addressPrefixes} --egress-network {egressNetwork} "
        "--fabric-delegation {fabricDelegationId} --limits {limits} "
        "--tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a VRF Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation show --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a VRF Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation update --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--admin-state {updatedAdminState} "
        "--address-prefixes {updatedAddressPrefixes} "
        "--egress-network {updatedEgressNetwork} --tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a VRF Delegation using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --admin-state {updatedAdminState} "
        "--address-prefixes {updatedAddressPrefixes} "
        "--egress-network {updatedEgressNetwork} --tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List VRF Delegations by VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation list --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a VRF Delegation."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delegation delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2VrfDelegationScenarioTest(ScenarioTest):
    """Fabric v2 VRF Delegation scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "name"),
                "rg": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "fabric_name"),
                "vrfName": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "vrf_name"),
                "location": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "location"),
                "adminState": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "admin_state"),
                "updatedAdminState": CONFIG.get(
                    "FABRIC_V2_VRF_DELEGATION", "updated_admin_state"
                ),
                "fabricDelegationId": CONFIG.get(
                    "FABRIC_V2_VRF_DELEGATION", "fabric_delegation_id"
                ),
                "limits": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "limits"),
                "addressPrefixes": CONFIG.get(
                    "FABRIC_V2_VRF_DELEGATION", "address_prefixes"
                ),
                "egressNetwork": CONFIG.get(
                    "FABRIC_V2_VRF_DELEGATION", "egress_network"
                ),
                "tags": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "tags"),
                "updatedAddressPrefixes": CONFIG.get(
                    "FABRIC_V2_VRF_DELEGATION", "updated_address_prefixes"
                ),
                "updatedEgressNetwork": CONFIG.get(
                    "FABRIC_V2_VRF_DELEGATION", "updated_egress_network"
                ),
                "updatedTags": CONFIG.get("FABRIC_V2_VRF_DELEGATION", "updated_tags"),
            }
        )

    def test_fabric_v2_vrf_delegation_scenario1(self):
        """Test Fabric v2 VRF Delegation CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_vrf_delegation_scenario2(self):
        """Test Fabric v2 VRF Delegation CRUD operations with parameter aliases."""
        call_scenario2(self)
