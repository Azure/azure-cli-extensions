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
    step_rotate_password_scenario1(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    cleanup_scenario(test)


def step_rotate_password_scenario1(test, checks=None):
    """nf rotate password operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric rotate-password --resource-name {name} --resource-group {resourceGroup}",
        checks=checks,
    )


class GA_NFRotatePasswordScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "expectedStatus": CONFIG.get("NETWORK_FABRIC", "expected_status"),
            }
        )

    def test_GA_nf_rotate_password_scenario1(self):
        """test scenario for NF rotate password operations"""
        call_scenario1(self)
