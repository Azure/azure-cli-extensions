# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Internet Gateway tests scenarios
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
    step_update_scenario1(test, checks=[])
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("gatewayType", attr(test, "expectedGatewayType")),
            test.check("port", int(attr(test, "expectedPort"))),
            test.check("ipv4Address", attr(test, "expectedIpv4Address")),
            test.check("internetGatewayRuleId", attr(test, "internetGatewayRuleId")),
            test.check(
                "networkFabricControllerId",
                attr(test, "expectedNetworkFabricControllerId"),
            ),
        ],
    )
    step_list_resource_group(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_show(test, checks=None):
    """internetgateway show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internetgateway show --resource-name {name} --resource-group {rg}",
        checks=checks,
    )


def step_update_scenario1(test, checks=None):
    """internetgateway update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internetgateway update --resource-group {rg} --resource-name {name} --gateway-rule-id"
        " {internetGatewayRuleId}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """internetgateway update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric internetgateway update --resource-group {rg} --resource-name {name} "
        "--internet-gateway-rule-id {internetGatewayRuleId}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """internetgateway list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkfabric internetgateway list --resource-group {rg}")


class GA_internetgatewayScenarioTest1(ScenarioTest):
    """Internet Gateway Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("INTERNET_GATEWAY", "name"),
                "rg": CONFIG.get("INTERNET_GATEWAY", "resource_group"),
                "internetGatewayRuleId": CONFIG.get(
                    "INTERNET_GATEWAY", "internet_gateway_rule_id"
                ),
                "expectedGatewayType": CONFIG.get(
                    "INTERNET_GATEWAY", "expected_gateway_type"
                ),
                "expectedIpv4Address": CONFIG.get(
                    "INTERNET_GATEWAY", "expected_ipv4_address"
                ),
                "expectedNetworkFabricControllerId": CONFIG.get(
                    "INTERNET_GATEWAY", "expected_network_fabric_controller_id"
                ),
                "expectedPort": CONFIG.get("INTERNET_GATEWAY", "expected_port"),
                "expectedProvisioningState": CONFIG.get(
                    "INTERNET_GATEWAY", "expected_provisioning_state"
                ),
            }
        )

    def test_GA_internetgateway_scenario1(self):
        """test scenario for internetgateway CRUD operations"""
        call_scenario1(self)

    def test_GA_internetgateway_scenario2(self):
        """Test scenario 2 with alternate command parameters."""
        call_scenario2(self)
        self.assertTrue(self.cassette.all_played)
