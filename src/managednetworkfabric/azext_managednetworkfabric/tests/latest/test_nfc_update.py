# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NNI tests scenarios
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
    step_update(test, checks=[])
    cleanup_scenario1(test)


def step_update(test, checks=None):
    """nni delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller update --resource-name {name} --resource-group {rg} --infra-er-connections {infraERConnections} --workload-er-connections {workloadERConnections}",
        checks=checks,
    )


class GA_NFCUpdateScenarioTest1(ScenarioTest):
    """NFCScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "name"),
                "rg": CONFIG.get("NETWORK_FABRIC_CONTROLLER", "resource_group"),
                "infraERConnections": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "updated_infra_ER_Connections"
                ),
                "workloadERConnections": CONFIG.get(
                    "NETWORK_FABRIC_CONTROLLER", "updated_workload_ER_Connections"
                ),
            }
        )

    def test_GA_nfc_update_scenario1(self):
        """test scenario for NNI CRUD operations"""
        call_scenario1(self)
