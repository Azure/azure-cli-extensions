# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NF identity tests scenarios
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
    step_assign_system_assigned_identity(test)
    step_show(test)
    step_remove_system_assigned_identity(test)
    step_assign_user_assigned_identity(test)
    step_show(test)
    step_remove_user_assigned_identity(test)
    step_show(test)
    cleanup_scenario1(test)


def step_assign_system_assigned_identity(test):
    """fabric identity assign system-assigned operation"""
    test.cmd(
        "az networkfabric fabric identity assign --name {name} --resource-group {rg} --system-assigned",
        checks=[test.check("type", "SystemAssigned")],
    )


def step_assign_user_assigned_identity(test):
    """fabric identity assign user-assigned operation"""
    test.cmd(
        "az networkfabric fabric identity assign --name {name} --resource-group {rg} --user-assigned {userAssignedIdentity}",
        checks=[test.check("type", "UserAssigned")],
    )


def step_remove_system_assigned_identity(test):
    """fabric identity remove system-assigned operation"""
    test.cmd(
        "az networkfabric fabric identity remove --name {name} --resource-group {rg} --system-assigned",
        checks=[],
    )


def step_remove_user_assigned_identity(test):
    """fabric identity remove user-assigned operation"""
    test.cmd(
        "az networkfabric fabric identity remove --name {name} --resource-group {rg} --user-assigned {userAssignedIdentity}",
        checks=[],
    )


def step_show(test):
    """fabric identity show operation"""
    test.cmd(
        "az networkfabric fabric identity show --name {name} --resource-group {rg}",
        checks=[],
    )


class GA_NFIdentityScenarioTest1(ScenarioTest):
    """NFIdentityScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "identity_nf_name"),
                "rg": CONFIG.get("NETWORK_FABRIC", "resource_group"),
                "userAssignedIdentity": CONFIG.get(
                    "NETWORK_FABRIC", "user_assigned_identity"
                ),
            }
        )

    def test_GA_nf_identity_scenario1(self):
        """test scenario for NF Identity CRUD operations"""
        call_scenario1(self)
