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


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_update(test, checks=[])
    cleanup_scenario1(test)


def step_update(test, checks=None):
    """nf update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric update --resource-group {rg} --resource-name {name}"
        " --fabric-asn {fabric_asn} --ipv4-prefix {ipv4_prefix} --ipv6-prefix {ipv6_prefix} --rack-count {rack_count} --server-count-per-rack {server_count_per_rack}"
        " --ts-config {terminal_server_conf} --managed-network-config {managed_network_conf} --user-assigned {user_assigned_identity} --control-plane-acls {control_plane_acls}"
        " --hardware-alert-threshold {hardware_alert_threshold} --storage-account-configuration {storage_account_configuration} --trusted-ip-prefixes {trusted_ip_prefixes}"
        " --unique-rd-configuration {unique_rd_configuration} --tags {tags}",
        checks=checks,
    )


class GA_NFUpdateScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "rg": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "fabric_asn": CONFIG.get("NETWORK_FABRIC", "fabric_asn"),
                "ipv4_prefix": CONFIG.get("NETWORK_FABRIC", "ipv4_prefix"),
                "ipv6_prefix": CONFIG.get("NETWORK_FABRIC", "ipv6_prefix"),
                "rack_count": CONFIG.get("NETWORK_FABRIC", "rack_count"),
                "server_count_per_rack": CONFIG.get(
                    "NETWORK_FABRIC", "server_count_per_rack"
                ),
                "terminal_server_conf": CONFIG.get(
                    "NETWORK_FABRIC", "terminal_server_conf"
                ),
                "managed_network_conf": CONFIG.get(
                    "NETWORK_FABRIC", "managed_network_conf"
                ),
                "user_assigned_identity": CONFIG.get(
                    "NETWORK_FABRIC", "user_assigned_identity"
                ),
                "control_plane_acls": CONFIG.get(
                    "NETWORK_FABRIC", "control_plane_acls"
                ),
                "hardware_alert_threshold": CONFIG.get(
                    "NETWORK_FABRIC", "hardware_alert_threshold"
                ),
                "storage_account_configuration": CONFIG.get(
                    "NETWORK_FABRIC", "storage_account_configuration"
                ),
                "trusted_ip_prefixes": CONFIG.get(
                    "NETWORK_FABRIC", "trusted_ip_prefixes"
                ),
                "unique_rd_configuration": CONFIG.get(
                    "NETWORK_FABRIC", "unique_rd_configuration"
                ),
                "tags": CONFIG.get("NETWORK_FABRIC", "tags"),
            }
        )

    def test_GA_nf_update_scenario1(self):
        """test scenario for NF CRUD operations"""
        call_scenario1(self)
