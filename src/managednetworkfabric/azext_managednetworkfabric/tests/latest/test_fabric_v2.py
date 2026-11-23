# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Fabric v2 test scenarios."""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG
from .utils.output_checks import attr


def call_scenario1(test):
    """Test the Fabric v2 CRUD lifecycle."""
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("kind", attr(test, "kind")),
            test.check("description", attr(test, "description")),
            test.check("fabricSku", attr(test, "fabricSku")),
            test.check("customLocationId", attr(test, "customLocationId")),
            test.check(
                "controllerManagedConfig", attr(test, "controllerManagedConfig")
            ),
            test.check("infrastructure", attr(test, "infrastructure")),
            test.check("tenant", attr(test, "tenant")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("kind", attr(test, "kind")),
            test.check("description", attr(test, "description")),
            test.check("fabricSku", attr(test, "fabricSku")),
            test.check("customLocationId", attr(test, "customLocationId")),
            test.check(
                "controllerManagedConfig", attr(test, "controllerManagedConfig")
            ),
            test.check("infrastructure", attr(test, "infrastructure")),
            test.check("tenant", attr(test, "tenant")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_update_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("kind", attr(test, "kind")),
            test.check("description", attr(test, "updatedDescription")),
            test.check("fabricSku", attr(test, "fabricSku")),
            test.check("customLocationId", attr(test, "customLocationId")),
            test.check(
                "controllerManagedConfig", attr(test, "controllerManagedConfig")
            ),
            test.check("infrastructure", attr(test, "infrastructure")),
            test.check("tenant", attr(test, "tenant")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    step_list_resource_group(test, checks=[test.check("[0].name", attr(test, "name"))])
    step_list_subscription(test, checks=[test.check("[0].name", attr(test, "name"))])
    step_delete(test)
    test.assertTrue(test.cassette.all_played)


def call_scenario2(test):
    """Test Fabric v2 create and update parameter aliases."""
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("kind", attr(test, "kind")),
            test.check("description", attr(test, "description")),
            test.check("fabricSku", attr(test, "fabricSku")),
            test.check("customLocationId", attr(test, "customLocationId")),
            test.check(
                "controllerManagedConfig", attr(test, "controllerManagedConfig")
            ),
            test.check("infrastructure", attr(test, "infrastructure")),
            test.check("tenant", attr(test, "tenant")),
            test.check("tags", attr(test, "tags")),
        ],
    )
    step_update_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("kind", attr(test, "kind")),
            test.check("description", attr(test, "updatedDescription")),
            test.check("fabricSku", attr(test, "fabricSku")),
            test.check("customLocationId", attr(test, "customLocationId")),
            test.check(
                "controllerManagedConfig", attr(test, "controllerManagedConfig")
            ),
            test.check("infrastructure", attr(test, "infrastructure")),
            test.check("tenant", attr(test, "tenant")),
            test.check("tags", attr(test, "updatedTags")),
        ],
    )
    test.assertTrue(test.cassette.all_played)


def step_create_scenario1(test, checks=None):
    """Create a Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 create --resource-group {rg} --resource-name {name} "
        "--location {location} --kind {kind} --description {description} "
        "--tags {tags} --system-assigned {systemAssigned} "
        "--user-assigned {userAssigned} --cm-config {controllerManagedConfig} "
        "--custom-location-id {customLocationId} --fabric-sku {fabricSku} "
        "--infrastructure {infrastructure} --tenant {tenant}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create a Fabric using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 create --resource-group {rg} --resource-name {name} "
        "--location {location} --kind {kind} --desc {description} --tags {tags} "
        "--mi-system-assigned {systemAssigned} "
        "--mi-user-assigned {userAssigned} --cmc {controllerManagedConfig} "
        "--cl-id {customLocationId} --fabric-sku {fabricSku} "
        "--infra {infrastructure} --tenant {tenant}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show a Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 show --resource-group {rg} --resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update a Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 update --resource-group {rg} --resource-name {name} "
        "--description {updatedDescription} --tags {updatedTags} "
        "--system-assigned {systemAssigned} --user-assigned {userAssigned} "
        "--cm-config {controllerManagedConfig} --custom-location-id {customLocationId} "
        "--infrastructure {infrastructure} --tenant {tenant}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update a Fabric using parameter aliases."""
    test.cmd(
        "az networkfabric fabric-v2 update --resource-group {rg} --resource-name {name} "
        "--desc {updatedDescription} --tags {updatedTags} "
        "--mi-system-assigned {systemAssigned} "
        "--mi-user-assigned {userAssigned} --cmc {controllerManagedConfig} "
        "--cl-id {customLocationId} --infra {infrastructure} --tenant {tenant}",
        checks=checks or [],
    )


@AllowLargeResponse()
def step_list_resource_group(test, checks=None):
    """List Fabrics by resource group."""
    test.cmd(
        "az networkfabric fabric-v2 list --resource-group {rg}", checks=checks or []
    )


@AllowLargeResponse()
def step_list_subscription(test, checks=None):
    """List Fabrics by subscription."""
    test.cmd("az networkfabric fabric-v2 list", checks=checks or [])


def step_delete(test, checks=None):
    """Delete a Fabric."""
    test.cmd(
        "az networkfabric fabric-v2 delete --resource-group {rg} --resource-name {name}",
        checks=checks or [],
    )


class FabricV2ScenarioTest(ScenarioTest):
    """Fabric v2 scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("FABRIC_V2", "name"),
                "rg": CONFIG.get("FABRIC_V2", "resource_group"),
                "location": CONFIG.get("FABRIC_V2", "location"),
                "kind": CONFIG.get("FABRIC_V2", "kind"),
                "description": CONFIG.get("FABRIC_V2", "description"),
                "updatedDescription": CONFIG.get("FABRIC_V2", "updated_description"),
                "tags": CONFIG.get("FABRIC_V2", "tags"),
                "updatedTags": CONFIG.get("FABRIC_V2", "updated_tags"),
                "systemAssigned": CONFIG.get("FABRIC_V2", "system_assigned"),
                "userAssigned": CONFIG.get("FABRIC_V2", "user_assigned"),
                "controllerManagedConfig": CONFIG.get(
                    "FABRIC_V2", "controller_managed_config"
                ),
                "customLocationId": CONFIG.get("FABRIC_V2", "custom_location_id"),
                "fabricSku": CONFIG.get("FABRIC_V2", "fabric_sku"),
                "infrastructure": CONFIG.get("FABRIC_V2", "infrastructure"),
                "tenant": CONFIG.get("FABRIC_V2", "tenant"),
                "expectedProvisioningState": CONFIG.get(
                    "FABRIC_V2", "expected_provisioning_state"
                ),
            }
        )
        self.vcr.match_on = (*self.vcr.match_on, "body")

    def test_GA_fabric_v2_scenario1(self):
        """Test Fabric v2 CRUD operations."""
        call_scenario1(self)

    def test_GA_fabric_v2_scenario2(self):
        """Test Fabric v2 CRUD operations with parameter aliases."""
        call_scenario2(self)
