# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    VirtualNetworkPreparer,
    ScenarioTest,
)
from knack.log import get_logger

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-regionalload-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-regionalload-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}
vnet_params = {
    "name_prefix": "clitest-regionalload-",
    "location": "eastus",
    "key": "virtual_network",
    "parameter_name": "vnet",
    "resource_group_key": "resource_group",
    "resource_group_parameter_name": "rg",
    "random_name_length": 30,
}

class LoadTestScenarioRegionalLoad(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenarioRegionalLoad, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @VirtualNetworkPreparer(**vnet_params)
    def test_load_test_regional_load_config(self):
        # VALID: Create a load test with regional load configuration from YAML
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.REGIONAL_LOAD_CONFIG_TEST_ID,
                "load_test_config_file": LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE,
            }
        )
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.engineInstances", 4),
        ]
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" ',
            checks=checks,
        ).get_output_in_json()
        regions = [regional_load.get("region") for regional_load in response.get("loadTestConfiguration").get("regionalLoadTestConfig")]
        assert "eastus" in regions
        assert "eastasia" in regions
        
        # INVALID: Update load test with regionewise engines
        # which do not match the total engine instances
        _configure_command_assert_exception(self, "Sum of engine instances in regionwise load test configuration (5) should be equal to total engine instances (4)", regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES)
        
        # VALID: Update load test with regionewise engines
        # and total engine instances from CLI
        self.kwargs.update(
            {
                "engine_instances": LoadTestConstants.ENGINE_INSTANCES,
                "regionwise_engines": LoadTestConstants.REGIONWISE_ENGINES,
            }
        )
        checks = [
            JMESPathCheck("testId", LoadTestConstants.REGIONAL_LOAD_CONFIG_TEST_ID),
            JMESPathCheck("loadTestConfiguration.engineInstances", LoadTestConstants.ENGINE_INSTANCES),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instances {engine_instances} "
            "--regionwise-engines {regionwise_engines} ",
            checks=checks,
        ).get_output_in_json()
        regions = [regional_load.get("region") for regional_load in response.get("loadTestConfiguration").get("regionalLoadTestConfig")]
        assert "eastus" in regions
        assert "germanywestcentral" in regions
        
        # VALID: Update load test with regionwise engines
        # which are re-distributed and argument value has spaces
        self.kwargs.update(
            {
                "regionwise_engines": LoadTestConstants.REGIONWISE_ENGINES_2,
            }
        )
        checks = [
            JMESPathCheck("testId", LoadTestConstants.REGIONAL_LOAD_CONFIG_TEST_ID),
            JMESPathCheck("loadTestConfiguration.engineInstances", LoadTestConstants.ENGINE_INSTANCES),
        ]
        response = self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--regionwise-engines {regionwise_engines} ",
            checks=checks,
        ).get_output_in_json()
        regions = [regional_load.get("region") for regional_load in response.get("loadTestConfiguration").get("regionalLoadTestConfig")]
        assert "eastus" in regions
        assert "southcentralus" in regions
        
        # INVALID: Update load test with regional load configuration from YAML
        # which does not contain the updated total engine instances
        # and the count does not match with existing configuration
        _configure_command_assert_exception(self, "Sum of engine instances in regionwise load test configuration (4) should be equal to total engine instances (5)", load_test_config_file=LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE_NO_TOTAL)
        
        # INVALID: Update load test with regional load configuration from YAML
        # where engine instances do not match count of regional load configuration
        _configure_command_assert_exception(self, "Sum of engine instances in regionwise load test configuration (2) should be equal to total engine instances (3)", load_test_config_file=LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE_COUNT_MISMATCH)
        
        # INVALID: Update load test with regionwise engines from CLI containing invalid region
        _configure_command_assert_exception(self, "Invalid regionwise-engines item key: invalidregion. Expected Azure region", engine_instances=LoadTestConstants.ENGINE_INSTANCES, regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_INVALID_REGION)
        
        # INVALID: Update load test with regionwise engines from CLI containing invalid type for engine count
        _configure_command_assert_exception(self, "Expected integer", engine_instances=LoadTestConstants.ENGINE_INSTANCES, regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_INVALID_TYPE_FLOAT)
        
        # INVALID: Update load test with regionwise engines from CLI containing invalid type for engine count
        _configure_command_assert_exception(self, "Expected integer", engine_instances=LoadTestConstants.ENGINE_INSTANCES, regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_INVALID_TYPE_STRING)
        
        # INVALID: Update load test with regionwise engines from CLI containing no parent region 
        _configure_command_assert_exception(self, "Multi-region load test should contain at-least one engine in the parent region East US from where the test is created", engine_instances=LoadTestConstants.ENGINE_INSTANCES, regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_NO_PARENT_REGION)
        
        # INVALID: Update load test with regionwise engines from CLI where argument value has invalid format
        _configure_command_assert_exception(self, "Expected region=engineCount", regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_INVALID_FORMAT_1)
        
        # INVALID: Update load test with regionwise engines from CLI where argument value has invalid format
        _configure_command_assert_exception(self, "Expected region=engineCount", regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_INVALID_FORMAT_2)
        
        # INVALID: Update load test with regionwise engines from CLI where argument value has invalid format
        _configure_command_assert_exception(self, "Region or engine count cannot be empty", regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_INVALID_FORMAT_3)
        
        # INVALID: Update load test with regional load configuration from YAML
        # which contains invalid region
        _configure_command_assert_exception(self, "Invalid region: randomregion. Expected Azure region", load_test_config_file=LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE_INVALID_REGION)
        
        # INVALID: Update load test with regional load configuration from YAML
        # which contains invalid type for engine count
        _configure_command_assert_exception(self, "Engine instances is required of type integer", load_test_config_file=LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE_INVALID_TYPE_FLOAT)
        
        # INVALID: Update load test with regional load configuration from YAML
        # which contains invalid type for engine count
        _configure_command_assert_exception(self, "Engine instances is required of type integer", load_test_config_file=LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE_INVALID_TYPE_STRING)
        
        # INVALID: Update load test with regional load configuration from YAML
        # where parent region is not present
        _configure_command_assert_exception(self, "Multi-region load test should contain at-least one engine in the parent region East US from where the test is created", load_test_config_file=LoadTestConstants.REGIONAL_LOAD_CONFIG_FILE_NO_PARENT_REGION)
        
        # INVALID: Update load test with regionwise engines containing only 1 region
        _configure_command_assert_exception(self, "Multi-region load tests should contain a minimum of 2 geographic regions in the configuration", regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_1, load_test_config_file=LoadTestConstants.LOAD_TEST_CONFIG_FILE)
        
        # INVALID: Update load test with regionwise engines containing duplicate regions
        _configure_command_assert_exception(self, "Multi-region load test configuration should not contain duplicate region values", engine_instances=LoadTestConstants.ENGINE_INSTANCES, regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES_3)
        
        # INVALID: Multi-region load test does not support private traffic mode
        result = self.cmd(
            "az network vnet subnet list --resource-group {resource_group} --vnet-name {virtual_network}"
        ).get_output_in_json()
        subnet_id = result[0]["id"]
        _configure_command_assert_exception(self, "You can run multi-region load tests only against public endpoints. Select public test traffic mode to proceed", engine_instances=LoadTestConstants.ENGINE_INSTANCES, regionwise_engines=LoadTestConstants.REGIONWISE_ENGINES, subnet_id=subnet_id)
        

def _configure_command_assert_exception(self, message, regionwise_engines=None, engine_instances=None, load_test_config_file=None, subnet_id=None):
    command = "az load test update " \
                "--test-id {test_id} " \
                "--load-test-resource {load_test_resource} " \
                "--resource-group {resource_group} "
    if regionwise_engines:
        self.kwargs.update(
            {
                "regionwise_engines": regionwise_engines,
            }
        )
        command += "--regionwise-engines {regionwise_engines} "
    if engine_instances:
        self.kwargs.update(
            {
                "engine_instances": engine_instances,
            }
        )
        command += "--engine-instances {engine_instances} "
    if load_test_config_file:
        self.kwargs.update(
            {
                "load_test_config_file": load_test_config_file,
            }
        )
        command += '--load-test-config-file "{load_test_config_file}" '
    if subnet_id:
        self.kwargs.update(
            {
                "subnet_id": subnet_id,
            }
        )
        command += "--subnet-id {subnet_id} "
    try:
        self.cmd(command)
    except Exception as e:
        assert message in str(e)
    