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


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_discard_commit_batch_scenario1(test)
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_discard_commit_batch_scenario2(test)
    cleanup_scenario(test)


def step_discard_commit_batch_scenario1(test, checks=None):
    """nf discard commit batch operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric discard-commit-batch --resource-name {name} --resource-group {resourceGroup} --commit-batch-id {commitBatchId}"
    )


def step_discard_commit_batch_scenario2(test, checks=None):
    """nf discard commit batch operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric discard-commit-batch --network-fabric-name {name} --resource-group {resourceGroup} --commit-batch-id {commitBatchId}"
    )


class GA_NFDiscardCommitBatchScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "commitBatchId": CONFIG.get("NETWORK_FABRIC", "commit_nf_batch_id"),
            }
        )

    def test_GA_nf_discard_commit_batch_scenario1(self):
        """test scenario for NF discard commit batch operations"""
        call_scenario1(self)
