# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Packet Broker tests scenarios
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
            test.check("networkDeviceIds", attr(test, "expectedNetworkDeviceIds")),
            test.check("networkFabricId", attr(test, "expectedNetworkFabricId")),
        ],
    )
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """Network Packet Broker show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric npb show --resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """Network Packet Broker list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric npb list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """Network Packet Broker list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric npb list")


class GA_NpbScenarioTest1(ScenarioTest):
    """Network Packet Broker Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "rg": CONFIG.get("NETWORK_PACKET_BROKER", "resource_group"),
                "name": CONFIG.get("NETWORK_PACKET_BROKER", "resource_name"),
                "expectedNetworkDeviceIds": CONFIG.get(
                    "NETWORK_PACKET_BROKER", "expected_network_device_ids"
                ),
                "expectedNetworkFabricId": CONFIG.get(
                    "NETWORK_PACKET_BROKER", "expected_network_fabric_id"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "NETWORK_PACKET_BROKER", "expected_provisioning_state"
                ),
            }
        )

    def test_GA_npb_scenario1(self):
        """test scenario for Network Packet Broker CRUD operations"""
        call_scenario1(self)
