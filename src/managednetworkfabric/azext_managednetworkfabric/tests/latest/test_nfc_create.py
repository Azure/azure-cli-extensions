# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NFC tests scenarios
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
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_create_scenario2(test, checks=[])
    cleanup_scenario(test)


def call_scenario3(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_create_scenario3(test, checks=[])
    cleanup_scenario(test)


def step_create_scenario1(test, checks=None):
    """nfc create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller create --resource-group {rg} --location {location} --resource-name {name} --annotation {annotation}"
        " --ipv4-address-space {ipv4AddressSpace} --ipv6-address-space {ipv6AddressSpace} --is-workload-management-network-enabled {isWorkloadManagementNetworkEnabled} --nfc-sku {nfcSku}"
        " --infra-er-connections {infraERConnections} --workload-express-route-connections {workloadERConnections} --mrg name={managedResourceGroupName} --mrg location={managedResourceGroupLocation}"
        " --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """nfc create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller create --resource-group {rg} --location {location} --resource-name {name} --annotation {annotation}"
        " --ipv4-address-space {ipv4AddressSpace} --ipv6-address-space {ipv6AddressSpace} --is-workload-management-network-enabled {isWorkloadManagementNetworkEnabled} --nfc-sku {nfcSku}"
        " --infrastructure-express-route-connections {infraERConnections} --workload-er-connections {workloadERConnections} --mrg name={managedResourceGroupName} --mrg location={managedResourceGroupLocation}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_create_scenario3(test, checks=None):
    """nfc create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller create --resource-group {rg} --location {location} --resource-name {name} --annotation {annotation}"
        " --ipv4-address-space {ipv4AddressSpace} --ipv6-address-space {ipv6AddressSpace} --wl-mgt-net-enabled {isWorkloadManagementNetworkEnabled} --nfc-sku {nfcSku}"
        " --infra-er-connections {infraERConnections} --wl-er-connections {workloadERConnections} --managed-resource-group-configuration {managementResourceGroupConfig}"
        " --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


class GA_NFCCreateScenarioTest1(ScenarioTest):
    """NFCScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "name"),
                "annotation": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "annotation"),
                "rg": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "resource_group"),
                "location": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "location"),
                "infraERConnections": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "infra_ER_Connections"
                ),
                "workloadERConnections": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "workload_ER_Connections"
                ),
                "ipv4AddressSpace": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "ipv4_address_space"
                ),
                "ipv6AddressSpace": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "ipv6_address_space"
                ),
                "isWorkloadManagementNetworkEnabled": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER",
                    "is_workload_management_network_enabled",
                ),
                "deleteNFCName": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "delete_nfc_name"
                ),
                "nfcSku": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "nfc_sku"),
                "managedResourceGroupName": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "mrg_name"
                ),
                "managedResourceGroupLocation": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "mrg_location"
                ),
                "managementResourceGroupConfig": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "management_resource_group_config"
                ),
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_nfc_create_scenario1(self):
        """test scenario for NFC CRUD operations"""
        call_scenario1(self)
