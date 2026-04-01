# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NF tests scenarios
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
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_update_scenario1(test, checks=None):
    """nf update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric update --resource-group {rg} --resource-name {name} --annotation {annotation}"
        " --fabric-asn {fabricAsn} --ipv4-prefix {ipv4Prefix} --ipv6-prefix {ipv6Prefix} --rack-count {rackCount} --server-count-per-rack {serverCountPerRack}"
        " --ts-config {terminalServerConf} --managed-network-config {managedNetworkConf} --user-assigned {userAssignedIdentity} --control-plane-acls {controlPlaneAcls}"
        " --ha-threshold {hardwareAlertThreshold} --storage-account-config {storageAccountConfiguration} --trusted-ip-prefixes {trustedIpPrefixes}"
        " --unique-rd-config {uniqueRdConfiguration} --tags {tags} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """nf update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric update --resource-group {rg} --resource-name {name} --annotation {annotation}"
        " --fabric-asn {fabricAsn} --ipv4-prefix {ipv4Prefix} --ipv6-prefix {ipv6Prefix} --rack-count {rackCount} --server-count-per-rack {serverCountPerRack}"
        " --terminal-server-configuration {terminalServerConf} --user-assigned {userAssignedIdentity} --control-plane-acls {controlPlaneAcls}"
        " --hardware-alert-threshold {hardwareAlertThreshold} --storage-account-configuration {storageAccountConfiguration} --trusted-ip-prefixes {trustedIpPrefixes}"
        " --authorized-transceiver {authorizedTransceiver} --feature-flags {featureFlags} --management-network-configuration {managementNetworkConfig} --qos-configuration {qosConfig}"
        " --unique-rd-configuration {uniqueRdConfiguration} --tags {tags} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


class GA_NFUpdateScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "annotation": CONFIG.get("NETWORK_FABRIC", "annotation"),
                "rg": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "fabricAsn": CONFIG.get("NETWORK_FABRIC", "fabric_asn"),
                "ipv4Prefix": CONFIG.get("NETWORK_FABRIC", "ipv4_prefix"),
                "ipv6Prefix": CONFIG.get("NETWORK_FABRIC", "ipv6_prefix"),
                "rackCount": CONFIG.get("NETWORK_FABRIC", "rack_count"),
                "serverCountPerRack": CONFIG.get(
                    "NETWORK_FABRIC", "server_count_per_rack"
                ),
                "terminalServerConf": CONFIG.get(
                    "NETWORK_FABRIC", "terminal_server_conf"
                ),
                "managedNetworkConf": CONFIG.get(
                    "NETWORK_FABRIC", "managed_network_conf"
                ),
                "controlPlaneAcls": CONFIG.get("NETWORK_FABRIC", "control_plane_acls"),
                "hardwareAlertThreshold": CONFIG.get(
                    "NETWORK_FABRIC", "hardware_alert_threshold"
                ),
                "storageAccountConfiguration": CONFIG.get(
                    "NETWORK_FABRIC", "storage_account_configuration"
                ),
                "trustedIpPrefixes": CONFIG.get(
                    "NETWORK_FABRIC", "trusted_ip_prefixes"
                ),
                "uniqueRdConfiguration": CONFIG.get(
                    "NETWORK_FABRIC", "unique_rd_configuration"
                ),
                "qosConfig": CONFIG.get("NETWORK_FABRIC", "qos_configuration"),
                "managementNetworkConfig": CONFIG.get(
                    "NETWORK_FABRIC", "management_network_configuration"
                ),
                "featureFlags": CONFIG.get("NETWORK_FABRIC", "feature_flags"),
                "authorizedTransceiver": CONFIG.get(
                    "NETWORK_FABRIC", "authorized_transceiver"
                ),
                "tags": CONFIG.get("NETWORK_FABRIC", "tags"),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_nf_update_scenario1(self):
        """test scenario for NF CRUD operations"""
        call_scenario1(self)
