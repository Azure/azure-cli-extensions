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
    step_validateconfiguration(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
            test.check("properties.url", attr(test, "expectedPropertiesUrl")),
        ],
    )
    cleanup_scenario1(test)


def step_validateconfiguration(test, checks=None):
    """nf validate configuration operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric validate-config --resource-name {name} --resource-group {resourceGroup} "
        "--validate-action {validateAction}",
        checks=checks,
    )


class GA_NFValidateScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "validateAction": CONFIG.get("NETWORK_FABRIC", "validate_action"),
                "expectedPropertiesUrl": CONFIG.get(
                    "NETWORK_FABRIC", "expected_properties_url"
                ),
                "expectedStatus": CONFIG.get("NETWORK_FABRIC", "expected_status"),
            }
        )

    def test_GA_nf_validate_scenario1(self):
        """test scenario for NF validate operations"""
        call_scenario1(self)
