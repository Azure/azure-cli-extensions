# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NF post tests scenarios
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
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_provision(test)
    cleanup_scenario1(test)


def step_provision(test, checks=None):
    """nf provision operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric provision --resource-name {name} --resource-group {resourceGroup}"
    )


class GA_NFProvisionScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
            }
        )

    def test_GA_nf_provision_scenario1(self):
        """test scenario for NF provision operations"""
        call_scenario1(self)
