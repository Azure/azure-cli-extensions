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
    step_lock_fabric_scenario1(test)
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_lock_fabric_scenario2(test)
    cleanup_scenario(test)


def step_lock_fabric_scenario1(test, checks=None):
    """nf lock operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric lock-fabric --resource-name {name} --resource-group {resourceGroup} --lock-type {lockType} --action {action}"
    )


def step_lock_fabric_scenario2(test, checks=None):
    """nf lock operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric fabric lock-fabric --network-fabric-name {name} --resource-group {resourceGroup} --lock-type {lockType} --action {action}"
    )


class GA_NFLockFabricScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "lockType": CONFIG.get("NETWORK_FABRIC", "lock_type"),
                "action": CONFIG.get("NETWORK_FABRIC", "action"),
            }
        )

    def test_GA_nf_lock_fabric_scenario1(self):
        """test scenario for NF lock fabric operations"""
        call_scenario1(self)
