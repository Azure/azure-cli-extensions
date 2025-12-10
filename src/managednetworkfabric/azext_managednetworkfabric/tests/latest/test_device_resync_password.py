# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

from azure.cli.testsdk.scenario_tests import AllowLargeResponse

"""
Device tests scenarios
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
<<<<<<<< HEAD:src/managednetworkfabric/azext_managednetworkfabric/tests/latest/test_nf_discard_commit_batch.py
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
========
    setup_scenario1(test)
    step_resync_password(test, checks=[])
    cleanup_scenario1(test)


def step_resync_password(test, checks=None):
    """Device resync-password operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device resync-password --resource-group {rg} --resource-name {name}",
        checks=checks,
>>>>>>>> upstream/main:src/managednetworkfabric/azext_managednetworkfabric/tests/latest/test_device_resync_password.py
    )


class GA_DeviceResyncPasswordScenarioTest1(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
<<<<<<<< HEAD:src/managednetworkfabric/azext_managednetworkfabric/tests/latest/test_nf_discard_commit_batch.py
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "commitBatchId": CONFIG.get("NETWORK_FABRIC", "commit_nf_batch_id"),
========
                "rg": CONFIG.get("NETWORK_DEVICE", "resource_group"),
                "name": CONFIG.get("NETWORK_DEVICE", "name"),
>>>>>>>> upstream/main:src/managednetworkfabric/azext_managednetworkfabric/tests/latest/test_device_resync_password.py
            }
        )

    @AllowLargeResponse()
    def test_GA_device_resync_password_scenario1(self):
        """test scenario for Device resync-password operation"""
        call_scenario1(self)
