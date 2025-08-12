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
    step_discard_commit_batch(test)
    cleanup_scenario1(test)


def step_discard_commit_batch(test, checks=None):
    """nf discard commit batch operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric discard-commit-batch --resource-name {commitNFName} --resource-group {commitNFRGName}"
    )


class GA_NFDiscardCommitBatchScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "commitNFRGName": CONFIG.get(
                    "NETWORK_FABRIC", "commit_nf_resource_group"
                ),
                "commitNFName": CONFIG.get("NETWORK_FABRIC", "commit_nf_name"),
            }
        )

    def test_GA_nf_discard_commit_batch_scenario1(self):
        """test scenario for NF discard commit batch operations"""
        call_scenario1(self)
