# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

# customizations-custom-params={"clustermanager_create": ["--mi-system-assigned", "--mi-user-assigned"], "clustermanager_update": ["--mi-system-assigned", "--mi-user-assigned"]}
# customizations-ignore-removed={"clustermanager_create": ["--identity"], "clustermanager_update": ["--identity"]}

"""
ClusterManager test scenarios
"""

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG
from .utils.output_checks import attr


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1a(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("analyticsWorkspaceId", attr(test, "analyticsWorkspaceId")),
            test.check("fabricControllerId", attr(test, "fabricControllerId")),
            test.check("vmSize", attr(test, "vmSizeDefault")),
            test.check("availabilityZones", attr(test, "availabilityZonesDefault")),
        ],
    )
    step_list_subscription(test)
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def call_scenario1b(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )

    cleanup_scenario1(test)


def call_scenario2(test):
    """# Testcase: scenario2"""
    setup_scenario1(test)
    step_create_vm_size_az(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("analyticsWorkspaceId", attr(test, "analyticsWorkspaceId")),
            test.check("fabricControllerId", attr(test, "fabricControllerId")),
            test.check("vmSize", attr(test, "vmSize")),
            test.check("availabilityZones", attr(test, "availabilityZones")),
        ],
    )
    step_list_subscription(test)
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def call_scenario3(test):
    """# Testcase: scenario3"""
    setup_scenario1(test)
    step_create_systemassigned_managedidentity(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("analyticsWorkspaceId", attr(test, "analyticsWorkspaceId")),
            test.check("fabricControllerId", attr(test, "fabricControllerId")),
            test.check("vmSize", attr(test, "vmSizeDefault")),
            test.check("availabilityZones", attr(test, "availabilityZonesDefault")),
        ],
    )
    step_list_subscription(test)
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def call_scenario4(test):
    """# Testcase: scenario4"""
    setup_scenario1(test)
    step_create_userassigned_managedidentity(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("provisioningState", attr(test, "provisioningState")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("analyticsWorkspaceId", attr(test, "analyticsWorkspaceId")),
            test.check("fabricControllerId", attr(test, "fabricControllerId")),
            test.check("vmSize", attr(test, "vmSizeDefault")),
            test.check("availabilityZones", attr(test, "availabilityZonesDefault")),
        ],
    )
    step_list_subscription(test)
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def call_scenario5(test):
    """# Testcase: scenario5"""
    setup_scenario1(test)
    step_create_UA_SA_managedidentity(test)
    cleanup_scenario1(test)


def call_scenario6(test):
    """# Testcase: scenario5"""
    setup_scenario1(test)
    step_update_relay_scenario1(
        test, checks=[test.check("status", attr(test, "operationStatus"))]
    )
    cleanup_scenario1(test)


def step_create_scenario1(test, checks=None):
    """ClusterManager create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager create --name {name} "
        "--location {location} --resource-group {rg} "
        "--fabric-controller-id {fabricControllerId} "
        "--tags {tags} "
        "--managed-resource-group-configuration name={mrgGroupName} "
        "--analytics-workspace-id {analyticsWorkspaceId} "
        "--rollout-ring {rolloutRing}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """ClusterManager create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager create --cluster-manager-name {name} "
        "--location {location} --resource-group {rg} "
        "--fabric-controller-id {fabricControllerId} "
        "--tags {tags} "
        "--mrg name={mrgGroupName} "
        "--analytics-workspace-id {analyticsWorkspaceId} ",
        checks=checks,
    )


def step_create_vm_size_az(test, checks=None):
    """ClusterManager create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager create --name {name} "
        "--location {location} --resource-group {rg} "
        "--fabric-controller-id {fabricControllerId} "
        "--tags {tags} "
        "--managed-resource-group-configuration name={mrgGroupName} "
        "--analytics-workspace-id {analyticsWorkspaceId} "
        "--vm-size {vmSize} "
        "--availability-zones {availabilityZones}",
        checks=checks,
    )


def step_create_systemassigned_managedidentity(test, checks=None):
    """ClusterManager create operation with system assigned managed identity"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager create --name {name} "
        "--location {location} --resource-group {rg} "
        "--fabric-controller-id {fabricControllerId} "
        "--tags {tags} "
        "--managed-resource-group-configuration name={mrgGroupName} "
        "--mi-system-assigned "
        "--analytics-workspace-id {analyticsWorkspaceId}",
        checks=checks,
    )


def step_create_userassigned_managedidentity(test, checks=None):
    """ClusterManager create operation with user assigned managed identity"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager create --name {name} "
        "--location {location} --resource-group {rg} "
        "--fabric-controller-id {fabricControllerId} "
        "--tags {tags} "
        "--managed-resource-group-configuration name={mrgGroupName} "
        "--mi-user-assigned {uai} "
        "--analytics-workspace-id {analyticsWorkspaceId}",
        checks=checks,
    )


def step_create_UA_SA_managedidentity(test, checks=None):
    """ClusterManager create operation with both system and user assigned managed identity - This test validates that the API properly rejects attempts to use both identity types"""
    if checks is None:
        checks = []
    try:
        test.cmd(
            "az networkcloud clustermanager create --name {name} "
            "--location {location} --resource-group {rg} "
            "--fabric-controller-id {fabricControllerId} "
            "--tags {tags} "
            "--managed-resource-group-configuration name={mrgGroupName} "
            "--mi-system-assigned "
            "--mi-user-assigned {uai} "
            "--analytics-workspace-id {analyticsWorkspaceId}",
            checks=checks,
        )
        assert (
            False
        ), "Command should have failed when both system and user assigned managed identities are specified"
    except Exception as e:
        error_message = str(e)
        expected_message = "Cluster Managers can only have a single Managed Identity. Please choose either a system-assigned or a single user-assigned identity."
        assert (
            expected_message in error_message
        ), f"Expected error message not found. Got: {error_message}"


def step_update_relay_scenario1(test, checks=None):
    """cluster action for update-relay-private-endpoint-connection"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager update-relay-private-endpoint-connection --name {name} --resource-group {rg} "
        "--connection-state {connectionState} --description {description} --private-endpoint-id {endpoint}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """ClusterManager delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager delete --name {name} "
        "--resource-group {rg} --yes",
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
    test.cmd("az networkcloud clustermanager list --resource-group {rg}", checks=checks)


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
        "--tags {tagsUpdate} --resource-group {rg} "
        "--rollout-ring {rolloutRingUpdate}",
        checks=checks,
    )


def step_update_SA_to_UA_managedidentity(test, checks=None):
    """ClusterManager update operation SA to UA"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud clustermanager update --name {name} "
        "--mi-user-assigned {uai}"
        "--tags {tagsUpdate} --resource-group {rg}",
        checks=checks,
    )


class ClusterManagerScenarioTest(ScenarioTest):
    """ClusterManager scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("CLUSTER_MANAGER", "name"),
                "mrgGroupName": CONFIG.get("CLUSTER_MANAGER", "mrg_name"),
                "location": CONFIG.get("CLUSTER_MANAGER", "location"),
                "analyticsWorkspaceId": CONFIG.get(
                    "CLUSTER_MANAGER", "analytics_workspace_id"
                ),
                "fabricControllerId": CONFIG.get(
                    "CLUSTER_MANAGER", "fabric_controller_id"
                ),
                "tags": CONFIG.get("CLUSTER_MANAGER", "tags"),
                "tagsUpdate": CONFIG.get("CLUSTER_MANAGER", "tags_update"),
                "provisioningState": CONFIG.get(
                    "CLUSTER_MANAGER", "provisioning_state"
                ),
                "uai": CONFIG.get("CLUSTER_MANAGER", "uai"),
                "vmSize": CONFIG.get("CLUSTER_MANAGER", "vm_size"),
                "vmSizeDefault": CONFIG.get("CLUSTER_MANAGER", "vm_size_default"),
                "availabilityZones": CONFIG.get(
                    "CLUSTER_MANAGER", "availability_zones"
                ),
                "availabilityZonesDefault": CONFIG.get(
                    "CLUSTER_MANAGER", "availability_zones_default"
                ),
                "rolloutRing": CONFIG.get("CLUSTER_MANAGER", "rollout_ring"),
                "rolloutRingUpdate": CONFIG.get(
                    "CLUSTER_MANAGER", "rollout_ring_update"
                ),
                "connectionState": CONFIG.get(
                    "CLUSTER_MANAGER", "update_relay_connection_state"
                ),
                "description": CONFIG.get(
                    "CLUSTER_MANAGER", "update_relay_description"
                ),
                "endpoint": CONFIG.get(
                    "CLUSTER_MANAGER", "update_relay_private_endpoint"
                ),
                "operationStatus": CONFIG.get("CLUSTER_MANAGER", "operation_status"),
            }
        )

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario1a(self):
        """test scenario for ClusterManager CRUD operations"""
        call_scenario1a(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario1b(self):
        """test scenario for ClusterManager create and update operations"""
        call_scenario1b(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario2(self):
        """test scenario for ClusterManager CRUD operations with custom VM size and availability zones"""
        call_scenario2(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario3(self):
        """test scenario for ClusterManager CRUD operations using system assigned managed identity"""
        call_scenario3(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario4(self):
        """test scenario for ClusterManager CRUD operations using user assigned managed identity"""
        call_scenario4(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario5(self):
        """test scenario for ClusterManager CRUD operations using systemAssigned and user assigned managed identity. Checking for expected 400 bad request"""
        call_scenario5(self)

    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_clustermanager_scenario6(self):
        """test scenario for ClusterManager UpdateRelayPEC"""
        call_scenario6(self)
