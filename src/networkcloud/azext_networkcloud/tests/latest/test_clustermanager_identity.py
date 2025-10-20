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


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1 manipulate clustermanager identities"""
    setup_scenario(test)
    step_assign_system_assigned_identity_scenario1(test)
    step_remove_system_assigned_identity_scenario1(test)
    step_assign_user_assigned_identity_scenario1(test)
    step_remove_user_assigned_identity_scenario1(test)
    step_show_scenario1(test)
    cleanup_scenario(test)


def call_scenario2(test):
    """# Testcase: scenario2 manipulate clustermanager identities"""
    setup_scenario(test)
    step_assign_system_assigned_identity_scenario2(test)
    step_assign_user_assigned_identity_scenario2(test)
    step_remove_system_assigned_identity_scenario2(test)
    step_remove_user_assigned_identity_scenario2(test)
    step_show_scenario2(test)
    cleanup_scenario(test)


def step_assign_system_assigned_identity_scenario1(test):
    """clustermanager identity assign system-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --mi-system-assigned",
        checks=[],
    )


def step_assign_system_assigned_identity_scenario2(test):
    """clustermanager identity assign system-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --system-assigned",
        checks=[],
    )


def step_assign_user_assigned_identity_scenario1(test):
    """clustermanager identity assign user-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity assign --cluster-manager-name {name} --resource-group {rg} --mi-user-assigned {miUserAssigned}",
        checks=[],
    )


def step_assign_user_assigned_identity_scenario2(test):
    """clustermanager identity assign user-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --user-assigned {miUserAssigned}",
        checks=[],
    )


def step_remove_system_assigned_identity_scenario1(test):
    """clustermanager identity remove system-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity remove --name {name} --resource-group {rg} --mi-system-assigned",
        checks=[],
    )


def step_remove_system_assigned_identity_scenario2(test):
    """clustermanager identity remove system-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity remove --name {name} --resource-group {rg} --system-assigned",
        checks=[],
    )


def step_remove_user_assigned_identity_scenario1(test):
    """clustermanager identity remove user-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity remove --cluster-manager-name {name} --resource-group {rg} --mi-user-assigned {miUserAssigned}",
        checks=[],
    )


def step_remove_user_assigned_identity_scenario2(test):
    """clustermanager identity remove user-assigned operation"""
    test.cmd(
        "az networkcloud clustermanager identity remove --cluster-manager-name {name} --resource-group {rg} --user-assigned {miUserAssigned}",
        checks=[],
    )


def step_show_scenario1(test):
    """clustermanager identity show operation"""
    test.cmd(
        "az networkcloud clustermanager identity show --name {name} --resource-group {rg}",
        checks=[],
    )


def step_show_scenario2(test):
    """clustermanager identity show operation"""
    test.cmd(
        "az networkcloud clustermanager identity show --cluster-manager-name {name} --resource-group {rg}",
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
