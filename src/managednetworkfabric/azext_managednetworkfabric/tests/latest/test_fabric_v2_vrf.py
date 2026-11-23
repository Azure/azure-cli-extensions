# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 VRF test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def call_scenario1(test):
    """Test the VRF CRUD lifecycle."""
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "description")),
            test.check(
                "aggregateRouteConfiguration",
                attr(test, "updatedAggregateRouteConfiguration"),
            ),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("peeringKind", attr(test, "updatedPeeringKind")),
            test.check("purpose", attr(test, "updatedPurpose")),
            test.check(
                "redistributeConnectedSubnets",
                attr(test, "redistributeConnectedSubnets"),
            ),
            test.check(
                "redistributeStaticRoutes", attr(test, "redistributeStaticRoutes")
            ),
            test.check("segmentationPosture", attr(test, "updatedSegmentationPosture")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "description")),
            test.check(
                "aggregateRouteConfiguration",
                attr(test, "updatedAggregateRouteConfiguration"),
            ),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("peeringKind", attr(test, "updatedPeeringKind")),
            test.check("purpose", attr(test, "updatedPurpose")),
            test.check(
                "redistributeConnectedSubnets",
                attr(test, "redistributeConnectedSubnets"),
            ),
            test.check(
                "redistributeStaticRoutes", attr(test, "redistributeStaticRoutes")
            ),
            test.check("segmentationPosture", attr(test, "updatedSegmentationPosture")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_update_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "updatedDescription")),
            test.check(
                "aggregateRouteConfiguration",
                attr(test, "updatedAggregateRouteConfiguration"),
            ),
            test.check("managementPolicy", attr(test, "updatedManagementPolicy")),
            test.check("peeringKind", attr(test, "updatedPeeringKind")),
            test.check("purpose", attr(test, "updatedPurpose")),
            test.check(
                "redistributeConnectedSubnets",
                attr(test, "updatedRedistributeConnectedSubnets"),
            ),
            test.check(
                "redistributeStaticRoutes",
                attr(test, "updatedRedistributeStaticRoutes"),
            ),
            test.check("segmentationPosture", attr(test, "updatedSegmentationPosture")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    step_list(test, [test.check("[0].name", attr(test, "name"))])
    step_delete(test)
    test.assertTrue(test.cassette.all_played)


def call_scenario2(test):
    """Test VRF create and update parameter aliases."""
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "description")),
            test.check(
                "aggregateRouteConfiguration",
                attr(test, "updatedAggregateRouteConfiguration"),
            ),
            test.check("managementPolicy", attr(test, "managementPolicy")),
            test.check("peeringKind", attr(test, "updatedPeeringKind")),
            test.check("purpose", attr(test, "updatedPurpose")),
            test.check(
                "redistributeConnectedSubnets",
                attr(test, "redistributeConnectedSubnets"),
            ),
            test.check(
                "redistributeStaticRoutes", attr(test, "redistributeStaticRoutes")
            ),
            test.check("segmentationPosture", attr(test, "updatedSegmentationPosture")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_update_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("description", attr(test, "updatedDescription")),
            test.check(
                "aggregateRouteConfiguration",
                attr(test, "updatedAggregateRouteConfiguration"),
            ),
            test.check("managementPolicy", attr(test, "updatedManagementPolicy")),
            test.check("peeringKind", attr(test, "updatedPeeringKind")),
            test.check("purpose", attr(test, "updatedPurpose")),
            test.check(
                "redistributeConnectedSubnets",
                attr(test, "updatedRedistributeConnectedSubnets"),
            ),
            test.check(
                "redistributeStaticRoutes",
                attr(test, "updatedRedistributeStaticRoutes"),
            ),
            test.check("segmentationPosture", attr(test, "updatedSegmentationPosture")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    test.assertTrue(test.cassette.all_played)


def step_create_scenario1(test, checks=None):
    """Create a VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf create --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name} --location {location} "
        "--aggregate-route-configuration {aggregateRouteConfiguration} "
        "--description {description} --management-policy {managementPolicy} "
        "--peering-kind {peeringKind} --purpose {purpose} "
        "--redistribute-connected-subnets {redistributeConnectedSubnets} "
        "--redistribute-static-routes {redistributeStaticRoutes} "
        "--segmentation-posture {segmentationPosture} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a VRF using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf create --resource-group {rg} "
        "--fabric-v2-name {fabricName} --resource-name {name} --location {location} "
        "--aggr-route-config {aggregateRouteConfiguration} "
        "--desc {description} --mgt-policy {managementPolicy} "
        "--peering-kind {peeringKind} --purpose {purpose} "
        "--redist-conn-subnets {redistributeConnectedSubnets} "
        "--redist-static-routes {redistributeStaticRoutes} "
        "--seg-posture {segmentationPosture} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf show --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf update --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name} "
        "--aggregate-route-configuration {updatedAggregateRouteConfiguration} "
        "--description {updatedDescription} "
        "--management-policy {updatedManagementPolicy} "
        "--peering-kind {updatedPeeringKind} --purpose {updatedPurpose} "
        "--redistribute-connected-subnets {updatedRedistributeConnectedSubnets} "
        "--redistribute-static-routes {updatedRedistributeStaticRoutes} "
        "--segmentation-posture {updatedSegmentationPosture} "
        "--tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a VRF using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 vrf update --resource-group {rg} "
        "--fabric-v2-name {fabricName} --resource-name {name} "
        "--aggr-route-config {updatedAggregateRouteConfiguration} "
        "--desc {updatedDescription} --mgt-policy {updatedManagementPolicy} "
        "--peering-kind {updatedPeeringKind} --purpose {updatedPurpose} "
        "--redist-conn-subnets {updatedRedistributeConnectedSubnets} "
        "--redist-static-routes {updatedRedistributeStaticRoutes} "
        "--seg-posture {updatedSegmentationPosture} "
        "--tags {updatedTags}",
        checks=checks or [],
    )


def step_list(test, checks=None):
    """List VRFs by Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 vrf list --resource-group {rg} "
        "--fabric-v2 {fabricName}",
        checks=checks or [],
    )


def step_delete(test, checks=None):
    """Delete a VRF."""
    test.cmd(
        "az networkfabric fabric-v2 vrf delete --resource-group {rg} "
        "--fabric-v2 {fabricName} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2VrfScenarioTest(ScenarioTest):
    """Fabric v2 VRF scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2_VRF", "name"),
                "rg": CONFIG.get("FABRIC_V2_VRF", "resource_group"),
                "fabricName": CONFIG.get("FABRIC_V2_VRF", "fabric_name"),
                "location": CONFIG.get("FABRIC_V2_VRF", "location"),
                "description": CONFIG.get("FABRIC_V2_VRF", "description"),
                "updatedDescription": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_description"
                ),
                "aggregateRouteConfiguration": CONFIG.get(
                    "FABRIC_V2_VRF", "aggregate_route_configuration"
                ),
                "managementPolicy": CONFIG.get("FABRIC_V2_VRF", "management_policy"),
                "peeringKind": CONFIG.get("FABRIC_V2_VRF", "peering_kind"),
                "purpose": CONFIG.get("FABRIC_V2_VRF", "purpose"),
                "redistributeConnectedSubnets": CONFIG.get(
                    "FABRIC_V2_VRF", "redistribute_connected_subnets"
                ),
                "redistributeStaticRoutes": CONFIG.get(
                    "FABRIC_V2_VRF", "redistribute_static_routes"
                ),
                "segmentationPosture": CONFIG.get(
                    "FABRIC_V2_VRF", "segmentation_posture"
                ),
                "tags": CONFIG.get("FABRIC_V2_VRF", "tags"),
                "updatedAggregateRouteConfiguration": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_aggregate_route_configuration"
                ),
                "updatedManagementPolicy": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_management_policy"
                ),
                "updatedPeeringKind": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_peering_kind"
                ),
                "updatedPurpose": CONFIG.get("FABRIC_V2_VRF", "updated_purpose"),
                "updatedRedistributeConnectedSubnets": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_redistribute_connected_subnets"
                ),
                "updatedRedistributeStaticRoutes": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_redistribute_static_routes"
                ),
                "updatedSegmentationPosture": CONFIG.get(
                    "FABRIC_V2_VRF", "updated_segmentation_posture"
                ),
                "updatedTags": CONFIG.get("FABRIC_V2_VRF", "updated_tags"),
                "expectedProvisioningState": CONFIG.get(
                    "FABRIC_V2_VRF", "expected_provisioning_state"
                ),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_fabric_v2_vrf_scenario1(self):
        """Test Fabric v2 VRF CRUD operations."""
        call_scenario1(self)

    def test_GA_fabric_v2_vrf_scenario2(self):
        """Test Fabric v2 VRF CRUD operations with parameter aliases."""
        call_scenario2(self)
