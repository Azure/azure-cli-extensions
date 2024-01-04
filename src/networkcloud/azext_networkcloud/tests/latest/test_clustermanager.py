# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
ClusterManager test scenarios
"""

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

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
    step_create(
        test,
        checks=[
            test.check("name", "{name}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", "{tagsUpdate}"),
            test.check("provisioningState", "Succeeded"),
        ],
    )
    step_show(test, checks=[])
    step_list_subscription(test)
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    """ClusterManager create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager create --name {name} "
        "--location {location} --resource-group {rg} "
        "--fabric-controller-id {fabricControllerId} "
        "--tags {tags} "
        "--managed-resource-group-configuration name={mrg_name} "
        "--analytics-workspace-id {analyticsWorkspaceId}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """ClusterManager delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager delete --name {name} "
        "--resource-group {rg} -y",
        checks=checks,
    )


def step_show(test, checks=None):
    """ClusterManager show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager show --name {name} " "--resource-group {rg}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """ClusterManager list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud clustermanager list --resource-group {rg}")


@AllowLargeResponse
def step_list_subscription(test):
    """ClusterManager list by subscription operation"""
    test.cmd("az networkcloud clustermanager list")


def step_update(test, checks=None):
    """ClusterManager update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager update --name {name} "
        "--tags {tagsUpdate} --resource-group {rg}"
    )


class ClusterManagerScenarioTest(ScenarioTest):
    """ClusterManager scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-cm-", length=24),
                "mrg_name": self.create_random_name(
                    prefix="cli-test-cm-mrg-", length=24
                ),
                "location": CONFIG.get("CLUSTER_MANAGER", "location"),
                "analyticsWorkspaceId": CONFIG.get(
                    "CLUSTER_MANAGER", "analytics_workspace_id"
                ),
                "fabricControllerId": CONFIG.get(
                    "CLUSTER_MANAGER", "fabric_controller_id"
                ),
                "tags": CONFIG.get("CLUSTER_MANAGER", "tags"),
                "tagsUpdate": CONFIG.get("CLUSTER_MANAGER", "tags_update"),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario1(self):
        """test scenario for ClusterManager CRUD operations"""
        call_scenario1(self)
