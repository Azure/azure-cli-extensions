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
from .utils.output_checks import attr


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1 manipulate clustermanager identities"""
    setup_scenario(test)
    step_assign_system_assigned_identity_scenario1(
        test, checks=[test.check("type", attr(test, "systemAssignedType"))]
    )
    step_remove_system_assigned_identity_scenario1(
        test, checks=[test.check("type", attr(test, "noIdentityType"))]
    )
    step_assign_user_assigned_identity_scenario1(
        test, checks=[test.check("type", attr(test, "userAssignedType"))]
    )
    step_remove_user_assigned_identity_scenario1(
        test, checks=[test.check("type", attr(test, "noIdentityType"))]
    )
    step_show_scenario1(test, checks=[test.check("type", attr(test, "noIdentityType"))])
    cleanup_scenario(test)


def call_scenario2(test):
    """# Testcase: scenario2 manipulate clustermanager identities"""
    setup_scenario(test)
    step_assign_system_assigned_identity_scenario2(
        test, checks=[test.check("type", attr(test, "systemAssignedType"))]
    )
    step_assign_user_assigned_identity_scenario2(
        test, checks=[test.check("type", attr(test, "combinedIdentityType"))]
    )
    step_remove_system_assigned_identity_scenario2(
        test, checks=[test.check("type", attr(test, "userAssignedType"))]
    )
    step_remove_user_assigned_identity_scenario2(
        test, checks=[test.check("type", attr(test, "noIdentityType"))]
    )
    step_show_scenario2(test, checks=[test.check("type", attr(test, "noIdentityType"))])
    cleanup_scenario(test)


def step_assign_system_assigned_identity_scenario1(test, checks=None):
    """clustermanager identity assign system-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --mi-system-assigned",
        checks=checks,
    )


def step_assign_system_assigned_identity_scenario2(test, checks=None):
    """clustermanager identity assign system-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --system-assigned",
        checks=checks,
    )


def step_assign_user_assigned_identity_scenario1(test, checks=None):
    """clustermanager identity assign user-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity assign --cluster-manager-name {name} --resource-group {rg} --mi-user-assigned {miUserAssigned}",
        checks=checks,
    )


def step_assign_user_assigned_identity_scenario2(test, checks=None):
    """clustermanager identity assign user-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity assign --name {name} --resource-group {rg} --user-assigned {miUserAssigned}",
        checks=checks,
    )


def step_remove_system_assigned_identity_scenario1(test, checks=None):
    """clustermanager identity remove system-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity remove --name {name} --resource-group {rg} --mi-system-assigned",
        checks=checks,
    )


def step_remove_system_assigned_identity_scenario2(test, checks=None):
    """clustermanager identity remove system-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity remove --name {name} --resource-group {rg} --system-assigned",
        checks=checks,
    )


def step_remove_user_assigned_identity_scenario1(test, checks=None):
    """clustermanager identity remove user-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity remove --cluster-manager-name {name} --resource-group {rg} --mi-user-assigned {miUserAssigned}",
        checks=checks,
    )


def step_remove_user_assigned_identity_scenario2(test, checks=None):
    """clustermanager identity remove user-assigned operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity remove --cluster-manager-name {name} --resource-group {rg} --user-assigned {miUserAssigned}",
        checks=checks,
    )


def step_show_scenario1(test, checks=None):
    """clustermanager identity show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity show --name {name} --resource-group {rg}",
        checks=checks,
    )


def step_show_scenario2(test, checks=None):
    """clustermanager identity show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager identity show --cluster-manager-name {name} --resource-group {rg}",
        checks=checks,
    )


class ClusterManagerIdentityScenarioTest(ScenarioTest):
    """clustermanager identity scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("CLUSTER_MANAGER_IDENTITY", "cm_name"),
                "systemAssignedType": CONFIG.get(
                    "CLUSTER_MANAGER_IDENTITY", "system_assigned_type"
                ),
                "userAssignedType": CONFIG.get(
                    "CLUSTER_MANAGER_IDENTITY", "user_assigned_type"
                ),
                "combinedIdentityType": CONFIG.get(
                    "CLUSTER_MANAGER_IDENTITY", "combined_identity_type"
                ),
                "noIdentityType": CONFIG.get(
                    "CLUSTER_MANAGER_IDENTITY", "no_identity_type"
                ),
                "rg": CONFIG.get("CLUSTER_MANAGER_IDENTITY", "resource_group_name"),
                "miUserAssigned": CONFIG.get(
                    "CLUSTER_MANAGER_IDENTITY", "mi_user_assigned"
                ),
            }
        )

    def test_clustermanager_identity_scenario1(self):
        """test scenario for clustermanager identity operations"""
        call_scenario1(self)
