# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 Service Peer test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test the Service Peer CRUD lifecycle."""
    step_create_scenario1(
        test,
        [
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("peerAsn", test.kwargs["peerAsn"].strip('"')),
        ],
    )
    step_show(test, [test.check("name", test.kwargs["name"].strip('"'))])
    step_update_scenario1(
        test,
        [test.check("tags.environment", "updated")],
    )
    step_list(test, [test.check("[0].name", test.kwargs["name"].strip('"'))])
    step_delete(test)


def call_scenario2(test):
    """Test Service Peer create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(test, [test.check("tags.environment", "updated")])


def step_create_scenario1(test, checks=None):
    """Create a Service Peer."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer create --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--location {location} --bfd-enabled {bfdEnabled} --peer-asn {peerAsn} "
        "--tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a Service Peer using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --location {location} "
        "--bfd-enabled {bfdEnabled} --peer-asn {peerAsn} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a Service Peer."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer show --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a Service Peer."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer update --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name} "
        "--tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a Service Peer using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --vrf-name {vrfName} "
        "--resource-name {name} --tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List Service Peers by VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer list --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a Service Peer."""
    test.cmd(
        "az networkfabric fabric-v2 vrf servicepeer delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --vrf {vrfName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2ServicePeerScenarioTest(ScenarioTest):
    """Fabric v2 Service Peer scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_SERVICE_PEER", "name"),
                "rg": CONFIG.get("FABRIC_V2_SERVICE_PEER", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_SERVICE_PEER", "fabric_name"),
                "vrfName": CONFIG.get("FABRIC_V2_SERVICE_PEER", "vrf_name"),
                "location": CONFIG.get("FABRIC_V2_SERVICE_PEER", "location"),
                "bfdEnabled": CONFIG.get("FABRIC_V2_SERVICE_PEER", "bfd_enabled"),
                "peerAsn": CONFIG.get("FABRIC_V2_SERVICE_PEER", "peer_asn"),
                "tags": CONFIG.get("FABRIC_V2_SERVICE_PEER", "tags"),
                "updatedTags": CONFIG.get("FABRIC_V2_SERVICE_PEER", "updated_tags"),
            }
        )

    def test_fabric_v2_servicepeer_scenario1(self):
        """Test Fabric v2 Service Peer CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_servicepeer_scenario2(self):
        """Test Fabric v2 Service Peer CRUD operations with parameter aliases."""
        call_scenario2(self)
