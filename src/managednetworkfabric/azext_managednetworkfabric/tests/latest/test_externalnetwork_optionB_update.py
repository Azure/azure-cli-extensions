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
    step_update_s1(test, checks=[])
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """externalnetwork show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork show --resource-name {name} --l3domain {l3Domain} --resource-group {rg}"
    )


def step_update_s1(test, checks=None):
    """externalnetwork update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork update --resource-group {rg} --l3domain {l3Domain} --resource-name {name} --peering-option {s1PeeringOption} --option-b-properties {updatedOptionBProperties}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """externalnetwork list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork list --resource-group {rg} --l3domain {l3Domain}"
    )


class GA_ExternalNetworkOptionBUpdateScenarioTest1(ScenarioTest):
    """External Network Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("EXTERNAL_NETWORK", "optionb_name"),
                "rg": CONFIG.get("EXTERNAL_NETWORK", "optionb_resource_group"),
                "l3Domain": CONFIG.get("EXTERNAL_NETWORK", "optionb_l3_domain"),
                "s1PeeringOption": CONFIG.get("EXTERNAL_NETWORK", "s1_peering_option"),
                "optionBProperties": CONFIG.get(
                    "EXTERNAL_NETWORK", "option_b_properties"
                ),
                "updatedOptionBProperties": CONFIG.get(
                    "EXTERNAL_NETWORK", "updated_option_b_properties"
                ),
            }
        )

    def test_GA_externalnetwork_optionB_update_scenario1(self):
        """test scenario for externalnetwork CRUD operations"""
        call_scenario1(self)
