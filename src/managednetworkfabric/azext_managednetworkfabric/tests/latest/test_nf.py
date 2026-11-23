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
from .utils.output_checks import attr


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("networkFabricSku", attr(test, "nfSku")),
            test.check("networkFabricControllerId", attr(test, "nfcId")),
            test.check("fabricASN", int(attr(test, "fabricAsn"))),
            test.check("fabricVersion", attr(test, "fabricVersion")),
            test.check("ipv4Prefix", attr(test, "ipv4Prefix")),
            test.check("ipv6Prefix", attr(test, "ipv6Prefix")),
            test.check("rackCount", int(attr(test, "rackCount"))),
            test.check("serverCountPerRack", int(attr(test, "serverCountPerRack"))),
            test.check(
                "terminalServerConfiguration",
                attr(test, "expectedTerminalServerConfiguration"),
            ),
            test.check(
                "managementNetworkConfiguration",
                attr(test, "expectedManagementNetworkConfiguration"),
            ),
            test.check("authorizedTransceiver", attr(test, "authorizedTransceiver")),
        ],
    )
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("networkFabricSku", attr(test, "nfSku")),
            test.check("networkFabricControllerId", attr(test, "nfcId")),
            test.check("fabricASN", int(attr(test, "fabricAsn"))),
            test.check("fabricVersion", attr(test, "fabricVersion")),
            test.check("ipv4Prefix", attr(test, "ipv4Prefix")),
            test.check("ipv6Prefix", attr(test, "ipv6Prefix")),
            test.check("rackCount", int(attr(test, "rackCount"))),
            test.check("serverCountPerRack", int(attr(test, "serverCountPerRack"))),
            test.check(
                "terminalServerConfiguration",
                attr(test, "expectedTerminalServerConfiguration"),
            ),
            test.check(
                "managementNetworkConfiguration",
                attr(test, "expectedManagementNetworkConfiguration"),
            ),
            test.check("authorizedTransceiver", attr(test, "authorizedTransceiver")),
        ],
    )
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("networkFabricSku", attr(test, "nfSku")),
            test.check("networkFabricControllerId", attr(test, "nfcId")),
            test.check("fabricASN", int(attr(test, "fabricAsn"))),
            test.check("fabricVersion", attr(test, "fabricVersion")),
            test.check("ipv4Prefix", attr(test, "ipv4Prefix")),
            test.check("ipv6Prefix", attr(test, "ipv6Prefix")),
            test.check("rackCount", int(attr(test, "rackCount"))),
            test.check("serverCountPerRack", int(attr(test, "serverCountPerRack"))),
            test.check(
                "terminalServerConfiguration",
                attr(test, "expectedTerminalServerConfiguration"),
            ),
            test.check(
                "managementNetworkConfiguration.infrastructureVpnConfiguration.peeringOption",
                attr(test, "managementNetworkConfig")["infrastructureVpnConfiguration"][
                    "peeringOption"
                ],
            ),
            test.check(
                "managementNetworkConfiguration.workloadVpnConfiguration.peeringOption",
                attr(test, "managementNetworkConfig")["workloadVpnConfiguration"][
                    "peeringOption"
                ],
            ),
            test.check("featureFlags", attr(test, "featureFlags")),
            test.check(
                "qosConfiguration.qosConfigurationState",
                attr(test, "qosConfig")["qosConfigurationState"],
            ),
            test.check("authorizedTransceiver", attr(test, "authorizedTransceiver")),
        ],
    )
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """nf create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric create --resource-group {rg} --location {location} --resource-name {name} --nf-sku {nfSku} --nfc-id {nfcId}"
        " --fabric-asn {fabricAsn} --ipv4-prefix {ipv4Prefix} --ipv6-prefix {ipv6Prefix} --rack-count {rackCount} --server-count-per-rack {serverCountPerRack}"
        " --ts-config {terminalServerConf} --managed-network-config {managedNetworkConf}"
        " --control-plane-acls {controlPlaneAcls} --fabric-version {fabricVersion} --annotation {annotation}"
        " --ha-threshold {hardwareAlertThreshold} --storage-account-config {storageAccountConfiguration}"
        " --storage-array-count {storageArrayCount} --trusted-ip-prefixes {trustedIpPrefixes} --unique-rd-config {uniqueRdConfiguration}"
        " --upgrade-profile {upgradeProfile} --secret-archive-settings {secretArchiveSettings} --public-connectivity {publicConnectivity}"
        " --authorized-transceiver {authorizedTransceiver} --tags {tags} --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """nf create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric create --resource-group {rg} --location {location} --resource-name {name} --network-fabric-sku {nfSku} --network-fabric-controller-id {nfcId}"
        " --fabric-asn {fabricAsn} --ipv4-prefix {ipv4Prefix} --ipv6-prefix {ipv6Prefix} --rack-count {rackCount} --server-count-per-rack {serverCountPerRack}"
        " --terminal-server-configuration {terminalServerConf} --control-plane-acls {controlPlaneAcls} --fabric-version {fabricVersion} "
        " --annotation {annotation} --feature-flags {featureFlags} --management-network-configuration {managementNetworkConfig} --qos-configuration {qosConfig}"
        " --hardware-alert-threshold {hardwareAlertThreshold} --storage-account-configuration {storageAccountConfiguration}"
        " --storage-array-count {storageArrayCount} --trusted-ip-prefixes {trustedIpPrefixes} --unique-rd-configuration {uniqueRdConfiguration}"
        " --archive-settings {secretArchiveSettings}"
        " --authorized-transceiver {authorizedTransceiver} --tags {tags} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_show(test, checks=None):
    """nf show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric show --resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """nf list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric fabric list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """nf list by subscription"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric fabric list")


class GA_NFScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "annotation": CONFIG.get("NETWORK_FABRIC", "annotation"),
                "rg": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "location": CONFIG.get("NETWORK_FABRIC", "location"),
                "nfSku": CONFIG.get("NETWORK_FABRIC", "nf_sku"),
                "nfcId": CONFIG.get("NETWORK_FABRIC", "nfc_id"),
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
                "fabricVersion": CONFIG.get("NETWORK_FABRIC", "fabric_version"),
                "hardwareAlertThreshold": CONFIG.get(
                    "NETWORK_FABRIC", "hardware_alert_threshold"
                ),
                "storageAccountConfiguration": CONFIG.get(
                    "NETWORK_FABRIC", "storage_account_configuration"
                ),
                "storageArrayCount": CONFIG.get(
                    "NETWORK_FABRIC", "storage_array_count"
                ),
                "trustedIpPrefixes": CONFIG.get(
                    "NETWORK_FABRIC", "trusted_ip_prefixes"
                ),
                "uniqueRdConfiguration": CONFIG.get(
                    "NETWORK_FABRIC", "unique_rd_configuration"
                ),
                "authorizedTransceiver": CONFIG.get(
                    "NETWORK_FABRIC", "authorized_transceiver"
                ),
                "qosConfig": CONFIG.get("NETWORK_FABRIC", "qos_configuration"),
                "managementNetworkConfig": CONFIG.get(
                    "NETWORK_FABRIC", "management_network_configuration"
                ),
                "featureFlags": CONFIG.get("NETWORK_FABRIC", "feature_flags"),
                "upgradeProfile": CONFIG.get("NETWORK_FABRIC", "upgrade_profile"),
                "secretArchiveSettings": CONFIG.get(
                    "NETWORK_FABRIC", "secret_archive_settings"
                ),
                "publicConnectivity": CONFIG.get(
                    "NETWORK_FABRIC", "public_connectivity"
                ),
                "tags": CONFIG.get("NETWORK_FABRIC", "tags"),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
                "expectedManagementNetworkConfiguration": CONFIG.get(
                    "NETWORK_FABRIC", "expected_management_network_configuration"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "NETWORK_FABRIC", "expected_provisioning_state"
                ),
                "expectedTerminalServerConfiguration": CONFIG.get(
                    "NETWORK_FABRIC", "expected_terminal_server_configuration"
                ),
            }
        )

    def test_GA_nf_scenario1(self):
        """test scenario for NF CRUD operations"""
        call_scenario1(self)

    def test_GA_nf_scenario2(self):
        """Test scenario 2 with alternate command parameters."""
        call_scenario2(self)
        self.assertTrue(self.cassette.all_played)
