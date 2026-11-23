# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods

"""AccessBridge test scenarios."""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def call_scenario1(test):
    """Test AccessBridge CRUD operations."""
    step_create(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
            test.check("detailedStatus", attr(test, "detailedStatus")),
            test.check("protocol", attr(test, "protocol")),
            test.check("length(endpoints)", attr(test, "endpointCount")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdateResponse")),
            test.check(
                "securityRules[0].description",
                attr(test, "securityRuleUpdateDescription"),
            ),
            test.check(
                "securityRules[0].direction", attr(test, "securityRuleUpdateDirection")
            ),
        ],
    )
    step_wait(test)
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("networkId", attr(test, "networkId")),
            test.check("ipv4ConnectedPrefix", attr(test, "ipv4ConnectedPrefix")),
            test.check("ipv6ConnectedPrefix", attr(test, "ipv6ConnectedPrefix")),
            test.check(
                "securityRules[0].description",
                attr(test, "securityRuleUpdateDescription"),
            ),
        ],
    )
    step_list_resource_group(
        test,
        checks=[
            test.check("length(@)", attr(test, "resourceGroupCount")),
            test.check("[0].name", attr(test, "name")),
        ],
    )
    step_list_subscription(
        test,
        checks=[
            test.check("length(@)", attr(test, "subscriptionCount")),
            test.check("[0].name", attr(test, "name")),
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
                "provisioningState": CONFIG.get("ACCESS_BRIDGE", "provisioning_state"),
                "detailedStatus": CONFIG.get("ACCESS_BRIDGE", "detailed_status"),
                "tagsUpdateResponse": CONFIG.get(
                    "ACCESS_BRIDGE", "tags_update_response"
                ),
                "securityRuleUpdateDescription": CONFIG.get(
                    "ACCESS_BRIDGE", "security_rule_update_description"
                ),
                "securityRuleUpdateDirection": CONFIG.get(
                    "ACCESS_BRIDGE", "security_rule_update_direction"
                ),
                "protocol": CONFIG.get("ACCESS_BRIDGE", "protocol"),
                "endpointCount": CONFIG.get("ACCESS_BRIDGE", "endpoint_count"),
                "resourceGroupCount": CONFIG.get(
                    "ACCESS_BRIDGE", "resource_group_count"
                ),
                "subscriptionCount": CONFIG.get("ACCESS_BRIDGE", "subscription_count"),
            }
        )

    def test_accessbridge_scenario1(self):
        """Test scenario for AccessBridge CRUD operations."""
        call_scenario1(self)
