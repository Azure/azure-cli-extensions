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


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_upgrade(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    cleanup_scenario1(test)


def step_upgrade(test, checks=None):
    """nf upgrade operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric upgrade --resource-name {name} --resource-group {resourceGroup} --action "
        "{upgradeActionStart} --version {upgradeVersion}",
        checks=checks,
    )


class GA_NFUpgradeStartScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "upgradeActionStart": CONFIG.get(
                    "NETWORK_FABRIC", "upgrade_action_start"
                ),
                "upgradeVersion": CONFIG.get("NETWORK_FABRIC", "upgrade_version"),
                "expectedStatus": CONFIG.get("NETWORK_FABRIC", "expected_status"),
            }
        )

    def test_GA_nf_upgrade_start_scenario1(self):
        """test scenario for NF commit operations"""
        call_scenario1(self)
