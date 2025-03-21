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


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_delete(test, checks=None):
    """nf delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric delete --resource-name {deleteNFName} --resource-group {deleteNFRGName}"
    )


class GA_NFDelteScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "deleteNFRGName": CONFIG.get(
                    "NETWORK_FABRIC", "delete_nf_resource_group"
                ),
                "deleteNFName": CONFIG.get("NETWORK_FABRIC", "delete_nf_name"),
            }
        )

    def test_GA_nf_Delete_scenario1(self):
        """test scenario for NF CRUD operations"""
        call_scenario1(self)
