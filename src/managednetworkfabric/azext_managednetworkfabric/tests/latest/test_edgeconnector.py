# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""Edge Connector test scenarios."""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG


def call_scenario1(test):
    """Test the Edge Connector CRUD lifecycle."""
    step_create_scenario1(
        test,
        checks=[
            test.check("name", test.kwargs["name"].strip('"')),
            test.check("description", test.kwargs["description"].strip('"')),
        ],
    )
    step_show(test, checks=[test.check("name", test.kwargs["name"].strip('"'))])
    step_update_scenario1(
        test,
        checks=[
            test.check("description", test.kwargs["updatedDescription"].strip('"'))
        ],
    )
    name_check = test.check("[0].name", test.kwargs["name"].strip('"'))
    step_list_resource_group(test, checks=[name_check])
    step_list_subscription(test, checks=[name_check])
    step_delete(test)


def call_scenario2(test):
    """Test Edge Connector create and update parameter aliases."""
    step_create_scenario2(test)
    step_update_scenario2(
        test,
        checks=[
            test.check("description", test.kwargs["updatedDescription"].strip('"'))
        ],
    )


def step_create_scenario1(test, checks=None):
    """Create an Edge Connector."""
    test.cmd(
        "az networkfabric edgeconnector create --resource-group {rg} "
        "--resource-name {name} --location {location} "
        "--description {description} "
        "--connectivity tunnel-type={tunnelType} "
        "custom-location-id={customLocationId} --tags {tags}",
        checks=checks or [],
    )


def step_create_scenario2(test, checks=None):
    """Create an Edge Connector using parameter aliases."""
    test.cmd(
        "az networkfabric edgeconnector create --resource-group {rg} "
        "--resource-name {name} --location {location} --desc {description} "
        "--connectivity tunnel-type={tunnelType} "
        "custom-location-id={customLocationId} --tags {tags}",
        checks=checks or [],
    )


def step_show(test, checks=None):
    """Show an Edge Connector."""
    test.cmd(
        "az networkfabric edgeconnector show --resource-group {rg} "
        "--resource-name {name}",
        checks=checks or [],
    )


def step_update_scenario1(test, checks=None):
    """Update an Edge Connector."""
    test.cmd(
        "az networkfabric edgeconnector update --resource-group {rg} "
        "--resource-name {name} --description {updatedDescription} "
        "--connectivity tunnel-type={tunnelType} "
        "custom-location-id={customLocationId} --tags {updatedTags}",
        checks=checks or [],
    )


def step_update_scenario2(test, checks=None):
    """Update an Edge Connector using parameter aliases."""
    test.cmd(
        "az networkfabric edgeconnector update --resource-group {rg} "
        "--resource-name {name} --desc {updatedDescription} "
        "--connectivity tunnel-type={tunnelType} "
        "custom-location-id={customLocationId} --tags {updatedTags}",
        checks=checks or [],
    )


@AllowLargeResponse()
def step_list_resource_group(test, checks=None):
    """List Edge Connectors by resource group."""
    test.cmd(
        "az networkfabric edgeconnector list --resource-group {rg}",
        checks=checks or [],
    )


@AllowLargeResponse()
def step_list_subscription(test, checks=None):
    """List Edge Connectors by subscription."""
    test.cmd("az networkfabric edgeconnector list", checks=checks or [])


def step_delete(test, checks=None):
    """Delete an Edge Connector."""
    test.cmd(
        "az networkfabric edgeconnector delete --resource-group {rg} "
        "--resource-name {name}",
        checks=checks or [],
    )


class EdgeConnectorScenarioTest(ScenarioTest):
    """Edge Connector scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("EDGE_CONNECTOR", "name"),
                "rg": CONFIG.get("EDGE_CONNECTOR", "resource_group"),
                "location": CONFIG.get("EDGE_CONNECTOR", "location"),
                "description": CONFIG.get("EDGE_CONNECTOR", "description"),
                "updatedDescription": CONFIG.get(
                    "EDGE_CONNECTOR", "updated_description"
                ),
                "customLocationId": CONFIG.get("EDGE_CONNECTOR", "custom_location_id"),
                "tunnelType": CONFIG.get("EDGE_CONNECTOR", "tunnel_type"),
                "tags": CONFIG.get("EDGE_CONNECTOR", "tags"),
                "updatedTags": CONFIG.get("EDGE_CONNECTOR", "updated_tags"),
            }
        )

    def test_edgeconnector_scenario1(self):
        """Test Edge Connector CRUD operations."""
        call_scenario1(self)

    def test_edgeconnector_scenario2(self):
        """Test Edge Connector CRUD operations with parameter aliases."""
        call_scenario2(self)
