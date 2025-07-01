# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
External Network tests scenarios
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
    step_create_s1(test, checks=[])
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create_s1(test, checks=None):
    """externalnetwork create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork create --resource-group {rg} --l3domain {l3Domain} --resource-name {name} --peering-option {s1PeeringOption} --option-b-properties {optionBProperties} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}",
        checks=checks,
    )


def step_show(test, checks=None):
    """externalnetwork show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork show --resource-name {name} --l3domain {l3Domain} --resource-group {rg}"
    )


def step_list_resource_group(test, checks=None):
    """externalnetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork list --resource-group {rg} --l3domain {l3Domain}"
    )


def step_delete(test, checks=None):
    """externalnetwork delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork delete --resource-name {name} --l3domain {l3Domain} --resource-group {rg}"
    )


class GA_ExternalNetworkOptionBScenarioTest1(ScenarioTest):
    """External Network Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("EXTERNAL_NETWORK", "optionb_name"),
                "rg": CONFIG.get("EXTERNAL_NETWORK", "optionb_resource_group"),
                "l3Domain": CONFIG.get("EXTERNAL_NETWORK", "optionb_l3_domain"),
                "s1PeeringOption": CONFIG.get("EXTERNAL_NETWORK", "s1_peering_option"),
                "importRoutePolicy": CONFIG.get(
                    "EXTERNAL_NETWORK", "import_route_policy"
                ),
                "exportRoutePolicy": CONFIG.get(
                    "EXTERNAL_NETWORK", "export_route_policy"
                ),
                "optionBProperties": CONFIG.get(
                    "EXTERNAL_NETWORK", "option_b_properties"
                ),
            }
        )

    def test_GA_externalnetwork_optionB_scenario1(self):
        """test scenario for externalnetwork CRUD operations"""
        call_scenario1(self)
