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


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario"""
    setup_scenario(test)
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario"""
    setup_scenario(test)
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def call_scenario3(test):
    """Testcase: scenario"""
    setup_scenario(test)
    step_update_scenario3(test, checks=[])
    cleanup_scenario(test)


def step_update_scenario1(test, checks=None):
    """nni delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller update --resource-name {name} --resource-group {rg} --infra-er-connections {infraERConnections} --workload-er-connections {workloadERConnections}"
        " --user-assigned {userAssignedIdentity} --system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """nni delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller update --resource-name {name} --resource-group {rg} --infrastructure-express-route-connections {infraERConnections} "
        " --workload-express-route-connections {workloadERConnections} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
        checks=checks,
    )


def step_update_scenario3(test, checks=None):
    """nni delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric controller update --resource-name {name} --resource-group {rg} --infrastructure-express-route-connections {infraERConnections} "
        " --wl-er-connections {workloadERConnections} --mi-user-assigned {userAssignedIdentity} --mi-system-assigned {systemAssignedIdentity}",
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
                "userAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "user_assigned_identity"
                ),
                "systemAssignedIdentity": CONFIG.get(
                    "MANAGED_IDENTITY", "system_assigned_identity"
                ),
            }
        )

    def test_GA_nfc_update_scenario1(self):
        """test scenario for NNI CRUD operations"""
        call_scenario1(self)
