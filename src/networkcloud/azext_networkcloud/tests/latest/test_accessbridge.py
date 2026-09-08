# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""AccessBridge test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def call_scenario1(test):
    """Test AccessBridge CRUD operations."""
    step_create(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("provisioningState", "Succeeded"),
            test.check("detailedStatus", "Running"),
            test.check("protocol", "TCP"),
            test.check("length(endpoints)", 2),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", "{tagsUpdateExpected}"),
            test.check("securityRules[0].description", "Updated management access"),
            test.check("securityRules[0].direction", "Inbound"),
        ],
    )
    step_wait(test)
    step_show(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("networkId", "{networkId}"),
            test.check("ipv4ConnectedPrefix", "{ipv4ConnectedPrefix}"),
            test.check("ipv6ConnectedPrefix", "{ipv6ConnectedPrefix}"),
            test.check("securityRules[0].description", "Updated management access"),
        ],
    )
    step_list_resource_group(
        test,
        checks=[
            test.check("length(@)", 1),
            test.check("[0].name", "{name}"),
        ],
    )
    step_list_subscription(
        test,
        checks=[
            test.check("length(@)", 1),
            test.check("[0].name", "{name}"),
        ],
    )
    step_delete(test)


def step_create(test, checks=None):
    """AccessBridge create operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud accessbridge create --name {name} --resource-group {rg} "
        "--extended-location name={extendedLocation} type={extendedLocationType} "
        "--location {location} --network-id {networkId} "
        "--ipv4-connected-prefix {ipv4ConnectedPrefix} "
        "--ipv6-connected-prefix {ipv6ConnectedPrefix} "
        "--security-rules {securityRules} --tags {tags}",
        checks=checks,
    )


def step_update(test, checks=None):
    """AccessBridge update operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud accessbridge update --name {name} --resource-group {rg} "
        "--security-rules {securityRulesUpdate} --tags {tagsUpdate}",
        checks=checks,
    )


def step_wait(test, checks=None):
    """AccessBridge wait operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud accessbridge wait --name {name} --resource-group {rg} "
        "--created",
        checks=checks,
    )


def step_show(test, checks=None):
    """AccessBridge show operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud accessbridge show --name {name} --resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """AccessBridge list by resource group operation."""
    if checks is None:
        checks = []
    test.cmd("az networkcloud accessbridge list --resource-group {rg}", checks=checks)


def step_list_subscription(test, checks=None):
    """AccessBridge list by subscription operation."""
    if checks is None:
        checks = []
    test.cmd("az networkcloud accessbridge list --top 10", checks=checks)


def step_delete(test, checks=None):
    """AccessBridge delete operation."""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud accessbridge delete --name {name} --resource-group {rg} --yes",
        checks=checks,
    )


class AccessBridgeScenarioTest(ScenarioTest):
    """AccessBridge scenario test."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("ACCESS_BRIDGE", "name"),
                "rg": CONFIG.get("ACCESS_BRIDGE", "resource_group"),
                "location": CONFIG.get("ACCESS_BRIDGE", "location"),
                "extendedLocation": CONFIG.get("ACCESS_BRIDGE", "extended_location"),
                "extendedLocationType": CONFIG.get(
                    "ACCESS_BRIDGE", "extended_location_type"
                ),
                "networkId": CONFIG.get("ACCESS_BRIDGE", "network_id"),
                "ipv4ConnectedPrefix": CONFIG.get(
                    "ACCESS_BRIDGE", "ipv4_connected_prefix"
                ),
                "ipv6ConnectedPrefix": CONFIG.get(
                    "ACCESS_BRIDGE", "ipv6_connected_prefix"
                ),
                "securityRules": CONFIG.get("ACCESS_BRIDGE", "security_rules"),
                "securityRulesUpdate": CONFIG.get(
                    "ACCESS_BRIDGE", "security_rules_update"
                ),
                "tags": CONFIG.get("ACCESS_BRIDGE", "tags"),
                "tagsUpdate": CONFIG.get("ACCESS_BRIDGE", "tags_update"),
                "tagsUpdateExpected": {"environment": "mock", "version": "2"},
            }
        )

    def test_accessbridge_scenario1(self):
        """Test scenario for AccessBridge CRUD operations."""
        call_scenario1(self)
