# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Cluster manager identity tests scenarios
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
    """# Testcase: scenario1 manipulate clustermanager identities"""
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
    """clustermanager identity assign system-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --mi-system-assigned",
        checks=[test.check("type", "SystemAssigned")],
    )


def step_assign_user_assigned_identity(test):
    """clustermanager identity assign user-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --mi-user-assigned {miUserAssigned}",
        checks=[test.check("type", "UserAssigned")],
    )


def step_remove_system_assigned_identity(test):
    """clustermanager identity remove system-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity remove --name {name} --resource-group {rg} --mi-system-assigned",
        checks=[],
    )


def step_remove_user_assigned_identity(test):
    """clustermanager identity remove user-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity remove --name {name} --resource-group {rg} --mi-user-assigned {miUserAssigned}",
        checks=[],
    )


def step_show(test):
    """clustermanager identity show operation"""
    test.cmd(
        "az networkcloud clustermanager identity show --name {name} --resource-group {rg}",
        checks=[],
    )


class ClusterManagerIdentityScenarioTest(ScenarioTest):
    """clustermanager identity scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("CLUSTER_MANAGER_IDENTITY", "cm_name"),
                "rg": CONFIG.get("CLUSTER_MANAGER_IDENTITY", "resource_group_name"),
                "miUserAssigned": CONFIG.get(
                    "CLUSTER_MANAGER_IDENTITY", "mi_user_assigned"
                ),
            }
        )

    def test_clustermanager_identity_scenario1(self):
        """test scenario for clustermanager identity operations"""
        call_scenario1(self)
