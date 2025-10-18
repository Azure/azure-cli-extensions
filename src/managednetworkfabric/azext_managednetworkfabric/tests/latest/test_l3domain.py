# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
L3 Domain tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_create_scenario1(test, checks=[])
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_create_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """l3domain create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric l3domain create --resource-group {rg} --resource-name {name} --location {location} --nf-id {nfId}"
        " --redistribute-connected-subnets {redistributeConnectedSubnets} --redistribute-static-routes {redistributeStaticRoutes}"
        " --aggregate-route-configuration {aggregateRouteConf} --connected-subnet-route-policy {connectedSubnetRoutePolicy}"
        " --static-route-route-policy {staticRouteRoutePolicy} --annotation {annotation} --v4route-prefix-limit {ipv4RoutePrefixLimit}"
        " --v6route-prefix-limit {ipv6RoutePrefixLimit} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """l3domain create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric l3domain create --resource-group {rg} --resource-name {name} --location {location} --network-fabric-id {nfId}"
        " --redist-conn-subnets {redistributeConnectedSubnets} --redist-static-routes {redistributeStaticRoutes}"
        " --aggr-route-config {aggregateRouteConf} --cs-route-policy {connectedSubnetRoutePolicy} --export-policy-config {export_policy_config}"
        " --sr-route-policy {staticRouteRoutePolicy} --annotation {annotation} --v4route-prefix-limit {ipv4RoutePrefixLimit}"
        " --v6route-prefix-limit {ipv6RoutePrefixLimit} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_show(test, checks=None):
    """l3domain show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric l3domain show --resource-name {name} --resource-group {rg}"
    )


def step_list_resource_group(test, checks=None):
    """l3domain list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric l3domain list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """l3domain list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric l3domain list")


class GA_L3DomainScenarioTest1(ScenarioTest):
    """L3 Domain Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("L3_ISOLATION_DOMAIN", "name"),
                "annotation": CONFIG.get("L3_ISOLATION_DOMAIN", "annotation"),
                "rg": CONFIG.get("L3_ISOLATION_DOMAIN", "resource_group"),
                "location": CONFIG.get("L3_ISOLATION_DOMAIN", "location"),
                "nfId": CONFIG.get("L3_ISOLATION_DOMAIN", "nf_id"),
                "exportPolicyConfig": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "export_policy_config"
                ),
                "redistributeConnectedSubnets": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "redistribute_connected_subnets"
                ),
                "redistributeStaticRoutes": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "redistribute_static_routes"
                ),
                "connectedSubnetRoutePolicy": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "connected_subnet_route_policy"
                ),
                "aggregateRouteConf": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "aggregate_route_conf"
                ),
                "updatedAggregateRouteConf": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "updated_aggregate_route_conf"
                ),
                "staticRouteRoutePolicy": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "static_route_route_policy"
                ),
                "ipv4RoutePrefixLimit": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "ipv4_route_prefix_limit"
                ),
                "ipv6RoutePrefixLimit": CONFIG.get(
                    "L3_ISOLATION_DOMAIN", "ipv6_route_prefix_limit"
                ),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_l3domain_scenario1(self):
        """test scenario for L3 Domain CRUD operations"""
        call_scenario1(self)
