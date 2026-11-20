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


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_commit_batch_status_scenario1(
        test,
        checks=[
            test.check("status", attr(test, "expectedStatus")),
        ],
    )
    cleanup_scenario(test)


def step_commit_batch_status_scenario1(test, checks=None):
    """nf commit batch status operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric commit-batch-status --resource-name {name} --resource-group {resourceGroup} "
        "--commit-batch-id {commitBatchId}",
        checks=checks,
    )


class GA_NFCommitBatchStatusScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "commitBatchId": CONFIG.get("NETWORK_FABRIC", "commit_nf_batch_id"),
                "expectedStatus": CONFIG.get("NETWORK_FABRIC", "expected_status"),
            }
        )

    def test_GA_nf_commit_batch_status_scenario1(self):
        """test scenario for NF commit batch status operations"""
        call_scenario1(self)
