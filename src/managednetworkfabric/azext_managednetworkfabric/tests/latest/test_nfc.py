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
from .utils.output_checks import attr


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("nfcSku", attr(test, "nfcSku")),
            test.check("ipv4AddressSpace", attr(test, "ipv4AddressSpace")),
            test.check("ipv6AddressSpace", attr(test, "expectedIpv6AddressSpace")),
            test.check(
                "isWorkloadManagementNetworkEnabled",
                attr(test, "isWorkloadManagementNetworkEnabled"),
            ),
            test.check(
                "infrastructureExpressRouteConnections",
                attr(test, "expectedInfrastructureExpressRouteConnections"),
            ),
            test.check(
                "workloadExpressRouteConnections",
                attr(test, "expectedWorkloadExpressRouteConnections"),
            ),
        ],
    )
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """nfc show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller show --resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """nfc list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric controller list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """nfc list by subscription"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric controller list")


def step_delete(test, checks=None):
    """nfc delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller delete --resource-name {deleteNFCName} --resource-group {rg}"
    )


class GA_NFCScenarioTest1(ScenarioTest):
    """NFCScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "name"),
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
                "isWorkloadManagementNetworkEnabled": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER",
                    "is_workload_management_network_enabled",
                ),
                "deleteNFCName": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "delete_nfc_name"
                ),
                "nfcSku": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "nfc_sku"),
                "expectedInfrastructureExpressRouteConnections": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER",
                    "expected_infrastructure_express_route_connections",
                ),
                "expectedIpv6AddressSpace": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "expected_ipv6_address_space"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "expected_provisioning_state"
                ),
                "expectedWorkloadExpressRouteConnections": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER",
                    "expected_workload_express_route_connections",
                ),
            }
        )

    def test_GA_nfc_scenario1(self):
        """test scenario for NFC CRUD operations"""
        call_scenario1(self)
