# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Internal Network tests scenarios
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
    step_update_scenario1(test, checks=[])
    step_show_scenario1(test, checks=[])
    step_list_resource_group_scenario1(test, checks=[])
    step_delete_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_create_scenario2(test, checks=[])
    step_update_scenario2(test, checks=[])
    step_show_scenario2(test, checks=[])
    step_list_resource_group_scenario2(test, checks=[])
    step_delete_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """internalnetwork create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork create --resource-group {rg} --l3-isolation-domain-name {l3Domain} --resource-name {name} --vlan-id {vlanId} "
        " --nat-ipv4-prefix-limit {nativeIpv4PrefixLimit} --nat-ipv6-prefix-limit {nativeIpv6PrefixLimit} --mtu {mtu} --connected-ipv4-subnets {connectedIpv4Subnets} "
        " --annotation {annotation} --is-monitoring-enabled {isMonitoringEnabled} --static-route-config {staticRouteConf} --bgp-configuration {bgpConf}"
        " --ingress-acl-id {ingressAclId} --egress-acl-id {egressAclId} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}"
        " --connected-ipv6-subnets {connectedIpv6Subnets} --extension {extension}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """internalnetwork create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork create --resource-group {rg} --l3domain {l3Domain} --resource-name {name} --vlan-id {vlanId} "
        " --native-ipv4-prefix-limit {nativeIpv4PrefixLimit} --native-ipv6-prefix-limit {nativeIpv6PrefixLimit} --mtu {mtu} --connected-ipv4-subnets {connectedIpv4Subnets} "
        " --annotation {annotation} --is-monitoring-enabled {isMonitoringEnabled} --static-route-configuration {staticRouteConf} --bgp-configuration {bgpConf}"
        " --ingress-acl-id {ingressAclId} --egress-acl-id {egressAclId} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}"
        " --connected-ipv6-subnets {connectedIpv6Subnets} --extension {extension}",
        checks=checks,
    )


def step_update_scenario1(test, checks=None):
    """internalnetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork update --resource-group {rg} --resource-name {name} --l3domain {l3Domain} "
        " --connected-ipv4-subnets {updatedConnectedIpv4Subnets} --static-route-config {updatedStaticRouteConf} --connected-ipv6-subnets {connectedIpv6Subnets}"
        " --bgp-configuration {updatedBgpConf} --nat-ipv4-prefix-limit {updatedNativeIpv4PrefixLimit} --annotation {annotation}"
        " --nat-ipv6-prefix-limit {updatedNativeIpv6PrefixLimit} --is-monitoring-enabled {isMonitoringEnabled} --mtu {mtu}"
        " --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """internalnetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork update --resource-group {rg} --resource-name {name} --l3-isolation-domain-name {l3Domain} "
        " --connected-ipv4-subnets {updatedConnectedIpv4Subnets} --static-route-configuration {updatedStaticRouteConf} --connected-ipv6-subnets {connectedIpv6Subnets}"
        " --bgp-configuration {updatedBgpConf} --native-ipv4-prefix-limit {updatedNativeIpv4PrefixLimit} --annotation {annotation}"
        " --native-ipv6-prefix-limit {updatedNativeIpv6PrefixLimit} --is-monitoring-enabled {isMonitoringEnabled} --mtu {mtu}"
        " --ingress-acl-id {ingressAclId} --egress-acl-id {egressAclId} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}",
        checks=checks,
    )


def step_show_scenario1(test, checks=None):
    """internalnetwork show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork show --resource-name {name} --l3domain {l3Domain} --resource-group {rg}"
    )


def step_show_scenario2(test, checks=None):
    """internalnetwork show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork show --resource-name {name} --l3-isolation-domain-name {l3Domain} --resource-group {rg}"
    )


def step_list_resource_group_scenario1(test, checks=None):
    """internalnetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork list --resource-group {rg} --l3domain {l3Domain}"
    )


def step_list_resource_group_scenario2(test, checks=None):
    """internalnetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork list --resource-group {rg} --l3-isolation-domain-name {l3Domain}"
    )


def step_delete_scenario1(test, checks=None):
    """internalnetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork delete --resource-name {name} --l3domain {l3Domain} --resource-group {rg}"
    )


def step_delete_scenario2(test, checks=None):
    """internalnetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internalnetwork delete --resource-name {name} --l3-isolation-domain-name {l3Domain} --resource-group {rg}"
    )


class GA_InternalNetworkScenarioTest1(ScenarioTest):
    """Internal Network Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("INTERNAL_NETWORK", "name"),
                "annotation": CONFIG.get("INTERNAL_NETWORK", "annotation"),
                "rg": CONFIG.get("INTERNAL_NETWORK", "resource_group"),
                "l3Domain": CONFIG.get("INTERNAL_NETWORK", "l3_domain"),
                "vlanId": CONFIG.get("INTERNAL_NETWORK", "vlan_id"),
                "mtu": CONFIG.get("INTERNAL_NETWORK", "mtu"),
                "extension": CONFIG.get("INTERNAL_NETWORK", "extension"),
                "isMonitoringEnabled": CONFIG.get(
                    "INTERNAL_NETWORK", "is_monitoring_enabled"
                ),
                "connectedIpv4Subnets": CONFIG.get(
                    "INTERNAL_NETWORK", "connected_Ipv4_subnets"
                ),
                "connectedIpv6Subnets": CONFIG.get(
                    "INTERNAL_NETWORK", "connected_Ipv6_subnets"
                ),
                "updatedConnectedIpv4Subnets": CONFIG.get(
                    "INTERNAL_NETWORK", "updated_connected_Ipv4_subnets"
                ),
                "staticRouteConf": CONFIG.get("INTERNAL_NETWORK", "static_route_conf"),
                "updatedStaticRouteConf": CONFIG.get(
                    "INTERNAL_NETWORK", "updated_static_route_conf"
                ),
                "bgpConf": CONFIG.get("INTERNAL_NETWORK", "bgp_conf"),
                "updatedBgpConf": CONFIG.get("INTERNAL_NETWORK", "updated_bgp_conf"),
                "importRoutePolicy": CONFIG.get(
                    "INTERNAL_NETWORK", "import_route_policy"
                ),
                "exportRoutePolicy": CONFIG.get(
                    "INTERNAL_NETWORK", "export_route_policy"
                ),
                "nativeIpv4PrefixLimit": CONFIG.get(
                    "INTERNAL_NETWORK", "native_ipv4_prefix_limit"
                ),
                "updatedNativeIpv4PrefixLimit": CONFIG.get(
                    "INTERNAL_NETWORK", "updated_native_ipv4_prefix_limit"
                ),
                "nativeIpv6PrefixLimit": CONFIG.get(
                    "INTERNAL_NETWORK", "native_ipv6_prefix_limit"
                ),
                "updatedNativeIpv6PrefixLimit": CONFIG.get(
                    "INTERNAL_NETWORK", "updated_native_ipv6_prefix_limit"
                ),
                "ingressAclId": CONFIG.get("INTERNAL_NETWORK", "ingress_acl_id"),
                "egressAclId": CONFIG.get("INTERNAL_NETWORK", "egress_acl_id"),
            }
        )

    def test_GA_internalnetwork_scenario1(self):
        """test scenario for internalnetwork CRUD operations"""
        call_scenario1(self)
