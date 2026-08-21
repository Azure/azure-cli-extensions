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


def call_scenario1(test):
    """Test the Fabric v2 CRUD lifecycle."""
    name = test.kwargs["name"].strip('"')
    step_create_scenario1(
        test,
        [test.check("name", name), test.check("kind", test.kwargs["kind"].strip('"'))],
    )
    step_show(test, [test.check("name", name)])
    step_update_scenario1(
        test,
        [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
    )
    step_list_resource_group(test, checks=[test.check("[0].name", name)])
    step_list_subscription(test, checks=[test.check("[0].name", name)])
    step_delete(test)


def call_scenario2(test):
    """Test Fabric v2 create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        [test.check("description", test.kwargs["updatedDescription"].strip('"'))],
    )


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
            }
        )

    def test_fabric_v2_scenario1(self):
        """Test Fabric v2 CRUD operations."""
        call_scenario1(self)

    def test_fabric_v2_scenario2(self):
        """Test Fabric v2 CRUD operations with parameter aliases."""
        call_scenario2(self)
