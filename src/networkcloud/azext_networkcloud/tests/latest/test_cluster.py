# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Cluster tests scenarios
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
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    # skip testing delete until the cluster can be deleted without being deployed
    # bug reference: https://dev.azure.com/msazuredev/AzureForOperatorsIndustry/_workitems/edit/710955/?triage=true
    # step_delete(test, checks=[])
    # instead the delete is tested in scenario2
    cleanup_scenario1(test)


def setup_scenario2(test):
    """Env setup_scenario2"""
    pass


def cleanup_scenario2(test):
    """Env cleanup_scenario2"""
    pass


def call_scenario2(test):
    """# Testcase: scenario2 temporary split of cluster delete operation to work with the already created and deployed simulator"""
    setup_scenario2(test)
    step_delete_sim(test, checks=[])
    cleanup_scenario2(test)


def setup_scenario3(test):
    """Env setup_scenario3"""
    pass


def cleanup_scenario3(test):
    """Env cleanup_scenario3"""
    pass


def call_scenario3(test):
    """# Testcase: scenario3 temporary split of cluster deploy operation to work with the already created and deployed simulator"""
    setup_scenario3(test)
    step_deploy_sim(test, checks=[])
    cleanup_scenario3(test)


def setup_scenario4(test):
    """Env setup_scenario4"""
    pass


def cleanup_scenario4(test):
    """Env cleanup_scenario4"""
    pass


def call_scenario4(test):
    """# Testcase: scenario4 temporary split of cluster update version operation to work with the already created and deployed simulator"""
    setup_scenario4(test)
    step_update_version_sim(test, checks=[])
    cleanup_scenario4(test)


def setup_scenario5(test):
    """Env setup_scenario5"""
    pass


def cleanup_scenario5(test):
    """Env cleanup_scenario5"""
    pass


def call_scenario5(test):
    """# Testcase: scenario5 temporary split of cluster scan runtime operation to work with the already created and deployed simulator"""
    setup_scenario5(test)
    step_scan_runtime(test, checks=[])
    cleanup_scenario5(test)


def setup_scenario6(test):
    """Env setup_scenario6"""
    pass


def cleanup_scenario6(test):
    """Env cleanup_scenario6"""
    pass


def call_scenario6(test):
    """# Testcase: scenario6 temporary split of cluster update operation for runtime protection configuration, secret-archive, strategy to work with the already created and deployed simulator"""
    setup_scenario6(test)
    step_update_runtime_protection(test, checks=[])
    step_update_secret_archive(test, checks=[])
    step_update_strategy(test, checks=[])
    cleanup_scenario6(test)


def step_create(test, checks=None):
    """cluster create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster create --name {name} --resource-group {rg} --extended-location "
        "name={extendedLocation} type={extendedLocationType} --location {location} "
        "--analytics-workspace-id {analyticsWorkspaceId} --cluster-location {clusterLocation} "
        "--cluster-service-principal application-id={applicationId} password={password} principal-id={principalId} "
        "tenant-id={tenantId} --cluster-type {clusterType} --cluster-version {clusterVersion} "
        "--compute-deployment-threshold type={thresholdType} grouping={thresholdGrouping} value={thresholdValue} "
        "--network-fabric-id {networkFabricId} "
        "--aggregator-or-single-rack-definition network-rack-id={networkRackId}"
        " rack-sku-id={rackSkuId}"
        " rack-serial-number={rackSerialNumber}"
        " rack-location={rackLocation}"
        " availability-zone={availabilityZone}"
        " storage-appliance-configuration-data={storageApplianceConfigurationData}"
        " bare-metal-machine-configuration-data={bareMetalMachineConfigurationData} "
        "--tags {tags}",
        checks=checks,
    )


def step_json_create(test, checks=None):
    """cluster create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster create --name {name} --resource-group {rg} --extended-location "
        "name={extendedLocation} type={extendedLocationType} --location {location} "
        "--analytics-workspace-id {analyticsWorkspaceId} --cluster-location {clusterLocation} "
        "--cluster-service-principal application-id={applicationId} password={password} principal-id={principalId} "
        "tenant-id={tenantId} --cluster-type {clusterType} --cluster-version {clusterVersion} "
        "--compute-deployment-threshold type={thresholdType} grouping={thresholdGrouping} value={thresholdValue} "
        "--network-fabric-id {networkFabricId} --aggregator-or-single-rack-definition {aggregatorOrSingleRackDefinitionDirectory} "
        "--tags {tags}",
        checks=checks,
    )


# Cluster deploy action takes hours and requires at the moment a real lab or updates to the simulator to support it.
# The current test will execute the deploy command in async mode.
def step_deploy_sim(test, checks=None):
    """cluster deploy operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster deploy --no-wait --name {nameDeploy} --resource-group {rgDeploy} --skip-validations-for-machines {skipValidationForMachines}",
        checks=checks,
    )


def step_show(test, checks=None):
    """cluster show operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cluster show --name {name} --resource-group {rg}")


def step_delete(test, checks=None):
    """cluster delete operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cluster delete --name {name} --resource-group {rg} -y")


def step_delete_sim(test, checks=None):
    """cluster delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster delete --name {nameDelete} --resource-group {rgDelete} -y"
    )


def step_list_resource_group(test, checks=None):
    """cluster list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cluster list --resource-group {rg}")


def step_list_subscription(test, checks=None):
    """cluster list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud cluster list")


def step_update(test, checks=None):
    """cluster update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster update --name {name} --cluster-location {clusterLocationUpdate}"
        " --tags {tagsUpdate} --resource-group {rg}"
    )


# Cluster update-version action will take hours to complete.
# The current test will execute the cluster update-version command in async mode.
def step_update_version_sim(test, checks=None):
    """cluster update-version operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster update-version --cluster-name {nameUpdateVersion} --target-cluster-version {versionUpdateVersion} --resource-group {rgUpdateVersion} --no-wait"
    )


def step_update_runtime_protection(test, checks=None):
    """cluster update for runtime-protection-configuration operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster update --name {nameClusterUpdate} --resource-group {rgClusterUpdate} --runtime-protection enforcement-level={enforcementLevel} "
    )


def step_update_secret_archive(test, checks=None):
    """cluster update secret-archive operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster update --name {nameClusterUpdate} --resource-group {rgClusterUpdate} --secret-archive use-key-vault={enabled} key-vault-id={keyVaultId} "
    )


def step_update_strategy(test, checks=None):
    """cluster update strategy operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster update --name {nameClusterUpdate} --resource-group {rgClusterUpdate} --update-strategy strategy-type={strategyType} threshold-type={strategyThresholdType} threshold-value={strategyThresholdValue} max-unavailable={maxUnavailable} wait-time-minutes={waitTimeMinutes}"
    )


def step_scan_runtime(test, checks=None):
    """cluster scan-runtime operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud cluster scan-runtime --name {nameScanActivity} --resource-group {rgScanActivity} --scan-activity {scanActivity}"
    )


class ClusterScenarioTest(ScenarioTest):
    """Cluster scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-cluster-", length=24),
                "extendedLocation": CONFIG.get("CLUSTER", "extended_location"),
                "extendedLocationType": CONFIG.get("CLUSTER", "extended_location_type"),
                "location": CONFIG.get("CLUSTER", "location"),
                "analyticsWorkspaceId": CONFIG.get("CLUSTER", "analytics_workspace_id"),
                "clusterLocation": CONFIG.get("CLUSTER", "cluster_location"),
                "clusterLocationUpdate": CONFIG.get(
                    "CLUSTER", "cluster_location_update"
                ),
                "applicationId": CONFIG.get("CLUSTER", "application_id"),
                "password": CONFIG.get("CLUSTER", "password"),
                "principalId": CONFIG.get("CLUSTER", "principal_id"),
                "tenantId": CONFIG.get("CLUSTER", "tenant_id"),
                "clusterType": CONFIG.get("CLUSTER", "cluster_type"),
                "clusterVersion": CONFIG.get("CLUSTER", "cluster_version"),
                "thresholdType": CONFIG.get("CLUSTER", "threshold_type"),
                "thresholdGrouping": CONFIG.get("CLUSTER", "threshold_grouping"),
                "thresholdValue": CONFIG.get("CLUSTER", "threshold_value"),
                "networkFabricId": CONFIG.get("CLUSTER", "network_fabric_id"),
                "networkRackId": CONFIG.get("CLUSTER", "network_rack_id"),
                "rackSkuId": CONFIG.get("CLUSTER", "rack_sku_id"),
                "rackSerialNumber": CONFIG.get("CLUSTER", "rack_serial_number"),
                "rackLocation": CONFIG.get("CLUSTER", "rack_location"),
                "availabilityZone": CONFIG.get("CLUSTER", "availability_zone"),
                "storageApplianceConfigurationData": CONFIG.get(
                    "CLUSTER", "storage_appliance_configuration_data"
                ),
                "bareMetalMachineConfigurationData": CONFIG.get(
                    "CLUSTER", "bare_metal_machine_configuration_data"
                ),
                "aggregatorOrSingleRackDefinitionDirectory": CONFIG.get(
                    "CLUSTER", "aggregator_or_single_rack_definition_directory"
                ),
                "tags": CONFIG.get("CLUSTER", "tags"),
                "tagsUpdate": CONFIG.get("CLUSTER", "tags_update"),
                "nameUpdateVersion": CONFIG.get("CLUSTER", "name_update_version"),
                "rgUpdateVersion": CONFIG.get("CLUSTER", "rg_update_version"),
                "versionUpdateVersion": CONFIG.get("CLUSTER", "version_update_version"),
                "nameDelete": CONFIG.get("CLUSTER", "name_delete"),
                "rgDelete": CONFIG.get("CLUSTER", "rg_delete"),
                "nameDeploy": CONFIG.get("CLUSTER", "name_deploy"),
                "rgDeploy": CONFIG.get("CLUSTER", "rg_deploy"),
                "skipValidationForMachines": CONFIG.get(
                    "CLUSTER", "skip_validations_for_machines"
                ),
                "nameClusterUpdate": CONFIG.get("CLUSTER", "name_cluster_update"),
                "rgClusterUpdate": CONFIG.get("CLUSTER", "rg_cluster_update"),
                "enforcementLevel": CONFIG.get("CLUSTER", "enforcement_level_update"),
                "keyVaultId": CONFIG.get("CLUSTER", "key_vault_id_update"),
                "enabled": CONFIG.get("CLUSTER", "enabled_update"),
                "strategyType": CONFIG.get("CLUSTER", "strategy_type_update"),
                "strategyThresholdType": CONFIG.get(
                    "CLUSTER", "strategy_threshold_type_update"
                ),
                "strategyThresholdValue": CONFIG.get(
                    "CLUSTER", "strategy_threshold_value_update"
                ),
                "maxUnavailable": CONFIG.get(
                    "CLUSTER", "strategy_max_unavailable_update"
                ),
                "waitTimeMinutes": CONFIG.get("CLUSTER", "wait_time_minutes_update"),
                "nameScanActivity": CONFIG.get("CLUSTER", "name_scan"),
                "scanActivity": CONFIG.get("CLUSTER", "scan_activity"),
                "rgScanActivity": CONFIG.get("CLUSTER", "rg_scan_activity"),
            }
        )

    @AllowLargeResponse()
    @ResourceGroupPreparer(
        name_prefix="clitest_rg"[:7],
        key="rg",
        parameter_name="rg",
        random_name_length=24,
    )
    def test_cluster_scenario1(self):
        """test scenario for Cluster CRU operations (delete is tested separately for now)"""
        call_scenario1(self)

    # scenario2 will use the existing cluster resources created outside of the testing framework because of the API limitations
    def test_cluster_scenario2(self):
        """test scenario for Cluster delete operation"""
        call_scenario2(self)

    # scenario3 will use the existing cluster resources created outside of the testing framework because of the API limitations
    def test_cluster_scenario3(self):
        """test scenario for Cluster deploy operation"""
        call_scenario3(self)

    # scenario4 will use the existing cluster resources created outside of the testing framework because of the API limitations
    def test_cluster_scenario4(self):
        """test scenario for Cluster version update operation"""
        call_scenario4(self)

    def test_cluster_scenario5(self):
        """test scenario for Cluster Scan Runtime operation"""
        call_scenario5(self)

    def test_cluster_scenario6(self):
        """test scenario for Cluster update for runtime protection configuration, secret-archive, strategy operation"""
        call_scenario6(self)
