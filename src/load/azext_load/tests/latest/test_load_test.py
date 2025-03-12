# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import tempfile

from azext_load.tests.latest.constants import LoadTestConstants
from azext_load.tests.latest.helper import create_test, delete_test
from azext_load.tests.latest.preparers import LoadTestResourcePreparer
from azure.cli.testsdk import (
    JMESPathCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    VirtualNetworkPreparer,
    StorageAccountPreparer,
    create_random_name,
    live_only,
)
from knack.log import get_logger

logger = get_logger(__name__)

rg_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "resource_group",
    "parameter_name": "rg",
    "random_name_length": 30,
}
load_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "load_test_resource",
    "parameter_name": "load",
    "resource_group_key": "resource_group",
    "random_name_length": 30,
}
vnet_params = {
    "name_prefix": "clitest-load-",
    "location": "eastus",
    "key": "virtual_network",
    "parameter_name": "vnet",
    "resource_group_key": "resource_group",
    "resource_group_parameter_name": "rg",
    "random_name_length": 30,
}
sa_params = {
    "name_prefix": "clitestload",
    "location": "eastus",
    "key": "storage_account",
    "parameter_name": "storage_account",
    "resource_group_parameter_name": "rg",
    "length": 20,
    "allow_shared_key_access": False,
}


class LoadTestScenario(ScenarioTest):
    def __init__(self, *args, **kwargs):
        super(LoadTestScenario, self).__init__(*args, **kwargs)
        self.kwargs.update({"subscription_id": self.get_subscription_id()})

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @VirtualNetworkPreparer(**vnet_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_create(self, rg, load, vnet):
        # GET SUBNET ID
        result = self.cmd(
            "az network vnet subnet list --resource-group {resource_group} --vnet-name {virtual_network}"
        ).get_output_in_json()
        subnet_id = result[0]["id"]

        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "certificate": LoadTestConstants.CERTIFICATE,
                "secret": LoadTestConstants.SECRETS,
                "description": LoadTestConstants.DESCRIPTION,
                "display_name": LoadTestConstants.DISPLAY_NAME,
                "engine_instance": LoadTestConstants.ENGINE_INSTANCE,
                "keyvault_reference_id": LoadTestConstants.KEYVAULT_REFERENCE_ID,
                "env": LoadTestConstants.VALID_ENV_RPS,
                "split_csv": LoadTestConstants.SPLIT_CSV_TRUE,
                "subnet_id": subnet_id,
                "disable_public_ip": LoadTestConstants.DISABLE_PUBLIC_IP_TRUE,
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("description", self.kwargs["description"]),
            JMESPathCheck("displayName", self.kwargs["display_name"]),
            JMESPathCheck(
                "keyvaultReferenceIdentityId", self.kwargs["keyvault_reference_id"]
            ),
            JMESPathCheck("subnetId", self.kwargs["subnet_id"]),
            JMESPathCheck("publicIPDisabled", True),
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", True),
            JMESPathCheck("environmentVariables.rps", "10"),
            JMESPathCheck("autoStopCriteria.autoStopDisabled", True),
        ]
        # Create load test with all parameters
        response = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" '
            "--env {env} "
            "--description {description} "
            "--display-name {display_name} "
            "--engine-instance {engine_instance} "
            "--certificate {certificate} "
            "--secret {secret} "
            "--keyvault-reference-id {keyvault_reference_id} "
            "--subnet-id {subnet_id} "
            "--split-csv {split_csv} "
            "--disable-public-ip {disable_public_ip} ",
            checks=checks,
        ).get_output_in_json()

        assert self.kwargs["certificate"] == response.get("certificate").get(
            "name"
        ) + "=" + response.get("certificate").get("value")
        assert self.kwargs[
            "secret"
        ] == LoadTestConstants.SECRET_NAME1 + "=" + response.get("secrets").get(
            LoadTestConstants.SECRET_NAME1
        ).get(
            "value"
        ) + " " + LoadTestConstants.SECRET_NAME2 + "=" + response.get(
            "secrets"
        ).get(
            LoadTestConstants.SECRET_NAME2
        ).get(
            "value"
        )

        # verify failureCriteria
        pass_fail_metric = response.get("passFailCriteria", {}).get(
            "passFailMetrics", {}
        )
        # Do not perform equality checks with floating point values.
        # Use a tolerance value to check if the values are close enough.
        for item in pass_fail_metric.values():
            if item.get("clientMetric") == "requests_per_sec":
                assert abs(item.get("value") - 78.0) < LoadTestConstants.FLOAT_TOLERANCE
                assert item.get("condition") == ">"
                assert item.get("aggregate") == "avg"
            elif item.get("clientMetric") == "error":
                assert abs(item.get("value") - 50.0) < LoadTestConstants.FLOAT_TOLERANCE
                assert item.get("condition") == ">"
                assert item.get("aggregate") == "percentage"
            elif item.get("clientMetric") == "response_time_ms":
                if item.get("aggregate") == "p75":
                    assert item.get("condition") == ">"
                    assert abs(item.get("value") - 380.0) < LoadTestConstants.FLOAT_TOLERANCE
                if item.get("aggregate") == "p99":
                    assert item.get("condition") == ">"
                    assert abs(item.get("value") - 520.0) < LoadTestConstants.FLOAT_TOLERANCE
                if item.get("aggregate") == "p99.9":
                    assert item.get("condition") == ">"
                    assert abs(item.get("value") - 540.0) < LoadTestConstants.FLOAT_TOLERANCE
            else:
                assert abs(item.get("value") - 200.0) < LoadTestConstants.FLOAT_TOLERANCE
                assert item.get("condition") == ">"
                assert item.get("aggregate") == "avg"
                assert item.get("requestName") == "GetCustomerDetails"

        # Invalid create test cases
        # 1. Creating test with existing test id
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
            )
        except Exception as e:
            assert "Test with given test ID " in str(e)

        # 2. Provide invalid path for load test config file
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--load-test-config-file "invalid_path.yaml" '
            )
        except Exception as e:
            assert "Provided path" in str(e)

        self.kwargs.update(
            {
                "certificate": LoadTestConstants.INVALID_CERTIFICATE,
                "secret": LoadTestConstants.INVALID_SECRET,
                "env": LoadTestConstants.INVALID_ENV,
            }
        )
        # 3 Invalid certificate check
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--certificate "{certificate}" '
            )
        except Exception as e:
            assert "Invalid Azure Key Vault Certificate URL:" in str(e)

        # 4 Invalid secret check
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--secret "{secret}" '
            )
        except Exception as e:
            assert "Invalid Azure Key Vault Secret URL:" in str(e)

        # 5 Invalid env check
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--env "{env}" '
            )
        except Exception as e:
            assert "Invalid env argument" in str(e)

        # 6 Invalid subnet id check
        self.kwargs.update(
            {
                "subnet_id": LoadTestConstants.INVALID_SUBNET_ID,
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--subnet-id "{subnet_id}" '
            )
        except Exception as e:
            assert "not a valid Azure subnet resource ID" in str(e)

        # 7 Invalid test plan file
        self.kwargs.update({"test_plan": LoadTestConstants.ADDITIONAL_FILE})
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--test-plan "{test_plan}" '
            )
        except Exception as e:
            assert "Invalid test plan file extension:" in str(e)

        # 8 Invalid split csv
        self.kwargs.update({"split_csv": "Random Text"})
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--split-csv "{split_csv}" '
            )
        except Exception as e:
            assert "Invalid split-csv value:" in str(e)

        # 9 Invalid PF criteria in config file
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.INVALID_PF_TEST_ID,
                "load_test_config_file": LoadTestConstants.INVALID_LOAD_TEST_CONFIG_FILE,
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--load-test-config-file "{load_test_config_file}" '
            )
        except Exception as e:
            assert "Invalid failure criteria:" in str(e)

        # 10 Invalid - ZIP artifacts count exceeding limit 5 in config file
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.INVALID_ZIP_COUNT_TEST_ID,
                "load_test_config_file": LoadTestConstants.INVALID_ZIP_ARTIFACT_LOAD_TEST_CONFIG_FILE,
            }
        )
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--load-test-config-file "{load_test_config_file}" '
            )
        except Exception as e:
            assert "QuotaExceeded" in str(e)

        # 11 Invalid public IP disabled
        self.kwargs.update({"public_ip_disabled": "Random"})
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--disable-public-ip "{public_ip_disabled}" ',
            )
        except Exception as e:
            assert "Invalid disable-public-ip value:" in str(e)
        
        # 12 Invalid public IP disabled true in case of public test
        self.kwargs.update(
            {
                "public_ip_disabled": "true",
                "test_id": LoadTestConstants.INVALID_DISABLED_PUBLIC_IP_TEST_ID
            })
        try:
            self.cmd(
                "az load test create "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--disable-public-ip "{public_ip_disabled}" ',
            )
        except Exception as e:
            assert "InvalidNetworkConfigurationException" in str(e)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_list(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LIST_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        create_test(self)

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert len(tests) > 0
        assert "fake_test_id" not in [test["testId"] for test in tests]
        assert self.kwargs["test_id"] in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_show(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.SHOW_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        create_test(self)

        test = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert self.kwargs["test_id"] == test.get("testId")

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_delete(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.DELETE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )

        create_test(self)

        delete_test(
            self,
            load_test_resource=self.kwargs["load_test_resource"],
            resource_group=self.kwargs["resource_group"],
            test_id=self.kwargs["test_id"],
        )

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] not in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_download_files(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.DOWNLOAD_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"path": temp_dir})

            create_test(self)

            self.cmd(
                "az load test download-files "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{path}" '
                "--force "
            )

            files = self.cmd(
                "az load test file list "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} ",
            ).get_output_in_json()

            files_in_dir = [
                f
                for f in os.listdir(temp_dir)
                if os.path.isfile(os.path.join(temp_dir, f))
            ]
            for file in files:
                assert file["fileName"] in files_in_dir

        # Invalid download-files test case
        # 1. INVALID PATH IN DOWNLOAD TEST CASE
        self.kwargs.update(
            {
                "path": r"\INVALID_PATH",
            }
        )
        try:
            self.cmd(
                "az load test download-files "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                '--path "{path}"'
            )
        except Exception as e:
            assert "Provided path" in str(e)

        time.sleep(10)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_create_with_args(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_WITH_ARGS_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "display_name": "Create_with_args_test",
                "test_description": "This is a load test created with arguments",
                "test_plan": LoadTestConstants.TEST_PLAN,
                "engine_instances": "1",
                "env": "a=2 b=3",
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.engineInstances", 1),
            JMESPathCheck("environmentVariables.a", 2),
            JMESPathCheck("environmentVariables.b", 3),
        ]

        test = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--display-name '{display_name}' "
            "--description '{test_description}' "
            '--test-plan "{test_plan}" '
            "--engine-instances {engine_instances} "
            "--env {env} ",
            checks=checks,
        ).get_output_in_json()

        assert self.kwargs["test_id"] == test.get("testId")

        tests = self.cmd(
            "az load test list "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group}"
        ).get_output_in_json()

        assert self.kwargs["test_id"] in [test.get("testId") for test in tests]

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_update_with_config(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.UPDATE_WITH_CONFIG_TEST_ID,
                "display_name": "Create_with_args_test",
                "test_description": "This is a load test created with arguments",
                "test_plan": LoadTestConstants.TEST_PLAN,
                "engine_instances": "5",
                "env": "a=2 b=3",
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.engineInstances", 5),
            JMESPathCheck("environmentVariables.a", 2),
            JMESPathCheck("environmentVariables.b", 3),
        ]

        test = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--display-name '{display_name}' "
            "--description '{test_description}' "
            '--test-plan "{test_plan}" '
            "--engine-instances {engine_instances} "
            "--env {env} ",
            checks=checks,
        ).get_output_in_json()

        assert self.kwargs["test_id"] == test.get("testId")

        self.kwargs.pop("test_description")
        self.kwargs.pop("test_plan")
        self.kwargs.pop("engine_instances")
        self.kwargs.pop("env")
        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "env": "c=5",
            }
        )
        checks = [
            JMESPathCheck("loadTestConfiguration.engineInstances", 1),
            JMESPathCheck("keyvaultReferenceIdentityType", "SystemAssigned"),
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", True),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} "
            "--env {env} ",
            checks=checks,
        )

        response = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert self.kwargs["test_id"] == response.get("testId")
        assert response.get("loadTestConfiguration").get("splitAllCSVs")
        assert response.get("environmentVariables").get("c") == "5"
        assert response.get("environmentVariables").get("rps") == "1"
        assert not response.get("environmentVariables").get("a")

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @VirtualNetworkPreparer(**vnet_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_create_and_update_vnet(self, rg, load):
        # GET SUBNET ID
        result = self.cmd(
            "az network vnet subnet list --resource-group {resource_group} --vnet-name {virtual_network}"
        ).get_output_in_json()
        subnet_id = result[0]["id"]
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.CREATE_AND_UPDATE_VNET_TEST_ID,
                "display_name": "Create_and_update_vnet_with_config_test",
                "test_description": "This is a load test created with config specific to vnet",
                "test_plan": LoadTestConstants.TEST_PLAN,
                "engine_instances": "5",
                "subnet_id": subnet_id,
                "disable_public_ip": LoadTestConstants.DISABLE_PUBLIC_IP_TRUE,
            }
        )

        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.engineInstances", 5),
            JMESPathCheck("subnetId", subnet_id),
            JMESPathCheck("publicIPDisabled", True),
        ]

        # Create load test with disable public ip provided as parameters
        test = self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--display-name '{display_name}' "
            "--description '{test_description}' "
            '--test-plan "{test_plan}" '
            "--engine-instances {engine_instances} "
            "--subnet-id {subnet_id} "
            "--disable-public-ip {disable_public_ip} ",
            checks=checks,
        ).get_output_in_json()

        assert self.kwargs["test_id"] == test.get("testId")

        checks = [
            JMESPathCheck("publicIPDisabled", False),
        ]

        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PUBLIC_IP_DISABLED_FALSE,
            }
        )
        
        # Update test with config having public IP disabled as false
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} ",
            checks=checks,
        )

        response = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert self.kwargs["test_id"] == response.get("testId")
        assert not response.get("publicIPDisabled")

        # Update test with config having public IP disabled as true
        checks = [
            JMESPathCheck("publicIPDisabled", True),
        ]

        self.kwargs.update(
            {
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_PUBLIC_IP_DISABLED_TRUE,
            }
        )
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} "
            "--subnet-id {subnet_id}",
            checks=checks,
        )

        response = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert response.get("publicIPDisabled")

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_update(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.UPDATE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )

        create_test(self)
        self.kwargs.update(
            {
                "engine_instance": 11,
                "keyvault_reference_id": "null",
                "split_csv": LoadTestConstants.SPLIT_CSV_FALSE,
            }
        )
        checks = [
            JMESPathCheck(
                "loadTestConfiguration.engineInstances", self.kwargs["engine_instance"]
            ),
            JMESPathCheck("keyvaultReferenceIdentityType", "SystemAssigned"),
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", False),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--engine-instance {engine_instance} "
            "--keyvault-reference-id {keyvault_reference_id} "
            "--split-csv {split_csv} ",
            checks=checks,
        )

        response = self.cmd(
            "az load test show "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} ",
        ).get_output_in_json()

        assert self.kwargs["test_id"] == response.get("testId")
        assert not response.get("loadTestConfiguration").get("splitAllCSVs")
        assert "SystemAssigned" == response.get("keyvaultReferenceIdentityType")

        # Invalid test cases for update command
        # Update a test which doesnt exist
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.INVALID_UPDATE_TEST_ID,
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--engine-instances 11 ",
            )
        except Exception as e:
            assert "Test with given test ID " in str(e)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_app_component(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.APP_COMPONENT_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )
        # GET STORAGE ACCOUNT ID
        result = self.cmd(
            "az storage account show --name {storage_account} --resource-group {resource_group}"
        ).get_output_in_json()
        storage_account_id = result["id"]
        storage_account_name = result["name"]
        storage_account_type = result["type"]
        storage_account_kind = result["kind"]
        create_test(self)
        self.kwargs.update(
            {
                "app_component_id": storage_account_id,
                "app_component_name": storage_account_name,
                "app_component_type": storage_account_type,
                "app_component_kind": storage_account_kind,
            }
        )

        # TODO: Create an Azure resource for app component
        self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" '
            '--app-component-kind "{app_component_kind}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        self.cmd(
            "az load test app-component remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-id "{app_component_id}" '
            "--yes"
        )

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_server_metric(self, rg, load):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.SERVER_METRIC_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
            }
        )
        # GET STORAGE ACCOUNT ID
        result = self.cmd(
            "az storage account show --name {storage_account} --resource-group {resource_group}"
        ).get_output_in_json()
        storage_account_id = result["id"]
        storage_account_name = result["name"]
        storage_account_type = result["type"]
        storage_account_kind = result["kind"]
        create_test(self)
        self.kwargs.update(
            {
                "app_component_id": storage_account_id,
                "app_component_name": storage_account_name,
                "app_component_type": storage_account_type,
                "app_component_kind": storage_account_kind,
            }
        )

        self.cmd(
            "az load test app-component add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--app-component-name "{app_component_name}" '
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" '
            '--app-component-kind "{app_component_kind}" ',
        ).get_output_in_json()

        app_components = self.cmd(
            "az load test app-component list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        app_component = app_components.get("components", {}).get(
            self.kwargs["app_component_id"]
        )
        assert app_component is not None and self.kwargs[
            "app_component_id"
        ] == app_component.get("resourceId")

        # SERVER METRIC ADD AND LIST IT TO CHECK
        self.kwargs.update(
            {
                "server_metric_id": LoadTestConstants.SERVER_METRIC_ID.format(
                    storage_account_id
                ),
                "server_metric_name": LoadTestConstants.SERVER_METRIC_NAME,
                "server_metric_namespace": LoadTestConstants.SERVER_METRIC_NAMESPACE,
                "aggregation": LoadTestConstants.AGGREGATION,
            }
        )
        self.cmd(
            "az load test server-metric add "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            '--metric-name " {server_metric_name}" '
            '--metric-namespace "{server_metric_namespace}" '
            "--aggregation {aggregation} "
            '--app-component-type "{app_component_type}" '
            '--app-component-id "{app_component_id}" ',
        ).get_output_in_json()

        server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        server_metric = server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

        # REMOVE SERVER METRIC AND LIST IT TO CHECK
        assert server_metric is not None
        # assert self.kwargs[
        #    "server_metric_id"
        # ] == server_metric.get("id")

        self.cmd(
            "az load test server-metric remove "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--metric-id "{server_metric_id}" '
            "--yes"
        )

        server_metrics = self.cmd(
            "az load test server-metric list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert not server_metrics.get("metrics", {}).get(
            self.kwargs["server_metric_id"]
        )

    @live_only()
    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    def test_load_test_file(self):
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.FILE_TEST_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
                "test_plan": LoadTestConstants.TEST_PLAN,
                "file_name": LoadTestConstants.FILE_NAME,
                "file_type": LoadTestConstants.FILE_TYPE,
            }
        )

        create_test(self)

        self.cmd(
            "az load test file delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-name {file_name} "
            "--yes"
        )

        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] not in [file["fileName"] for file in files]

        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-type {file_type} "
            '--path "{test_plan}" '
        )

        time.sleep(10)

        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()

        assert self.kwargs["file_name"] in [file["fileName"] for file in files]

        with tempfile.TemporaryDirectory(
            prefix="clitest-load-", suffix=create_random_name(prefix="", length=5)
        ) as temp_dir:
            self.kwargs.update({"download_path": temp_dir})

            self.cmd(
                "az load test file download "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--file-name {file_name} "
                '--path "{download_path}" '
                "--force "
            )

            assert os.path.exists(os.path.join(temp_dir, self.kwargs["file_name"]))
            
        # SUCCESS case of ZIP artifact load
        self.kwargs.update({
            "file_name": LoadTestConstants.ZIP_ARTIFACT_NAME,
            "file_type": LoadTestConstants.ZIP_ARTIFACT_TYPE,
            "file_path": LoadTestConstants.ZIP_ARTIFACT_FILE
        })
        response = self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-type {file_type} "
            '--path "{file_path}" '
        ).get_output_in_json()
        assert self.kwargs["file_name"] == response["fileName"]
        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert self.kwargs["file_name"] in [file["fileName"] for file in files]
        self.cmd(
            "az load test file delete "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--file-name {file_name} "
            "--yes"
        )
        files = self.cmd(
            "az load test file list "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
        ).get_output_in_json()
        assert self.kwargs["file_name"] not in [file["fileName"] for file in files]
        
        # INVALID case of ZIP artifact containing sub-directories
        self.kwargs.update({
            "file_name": LoadTestConstants.INVALID_ZIP_ARTIFACT_WITH_SUBDIR_NAME,
            "file_type": LoadTestConstants.ZIP_ARTIFACT_TYPE,
            "file_path": LoadTestConstants.INVALID_ZIP_ARTIFACT_WITH_SUBDIR_FILE
        })
        try:
            self.cmd(
                "az load test file upload "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--file-type {file_type} "
                '--path "{file_path}" '
            )
        except Exception as e:
            assert "Zip file containing sub-directories in the zip entry are not supported" in str(e)
        
        # INVALID case of file with same name and different types should throw error
        
        # Uploading json file without file type. Default type would be ADDITIONAL_ARTIFACTS
        self.kwargs.update(
            {
                "file_path": LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_PATH,
            }
        )
        checks = [
            JMESPathCheck("fileType", "ADDITIONAL_ARTIFACTS"),
            JMESPathCheck("fileName", LoadTestConstants.ADVANCED_TEST_URL_CONFIG_FILE_NAME),
        ]
        self.cmd(
            "az load test file upload "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--path "{file_path}" ',
            checks=checks,
        )
        # Trying to upload same file with different file type
        # Expected to throw INVALIDFILENAMEEXCEPTION
        self.kwargs.update(
            {
                "file_type": LoadTestConstants.ADVANCED_URL_FILE_TYPE,
            }
        )

        try:
            self.cmd(
                "az load test file upload "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--file-type {file_type} "
                '--path "{file_path}" '
            )
        except Exception as e:
            assert "InvalidFileName" in str(e)
        
        # INVALID case of ZIP artifact size > 50MB
        # This is commented because it requires a resource of size > 50 MB
        # storing which in GitHub is not recommended
        # ----------
        # self.kwargs.update({
        #     "file_name": LoadTestConstants.INVALID_ZIP_ARTIFACT_NAME,
        #     "file_type": LoadTestConstants.ZIP_ARTIFACT_TYPE,
        #     "file_path": LoadTestConstants.INVALID_ZIP_ARTIFACT_FILE
        # })
        # try:
        #     self.cmd(
        #         "az load test file upload "
        #         "--test-id {test_id} "
        #         "--load-test-resource {load_test_resource} "
        #         "--resource-group {resource_group} "
        #         "--file-type {file_type} "
        #         '--path "{file_path}" '
        #     )
        # except Exception as e:
        #     assert "exceeds size limit of 50 MB" in str(e)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_kvrefid(self, rg, load):
        # Create load test from config file with keyvault reference id
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_KVREFID,
            }
        )
        checks = [
            JMESPathCheck("testId", LoadTestConstants.LOAD_TEST_KVREF_ID),
            JMESPathCheck(
                "keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID
            ),
        ]
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" ',
            checks=checks,
        )
        # Update test with keyvault reference id null using parameters
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "keyvault_reference_id": "null",
            }
        )
        checks = [
            JMESPathCheck("keyvaultReferenceIdentityType", "SystemAssigned"),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--keyvault-reference-id {keyvault_reference_id} ",
            checks=checks,
        )
        # Update test with keyvault reference id using parameters
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "keyvault_reference_id": LoadTestConstants.KEYVAULT_REFERENCE_ID,
            }
        )
        checks = [
            JMESPathCheck("keyvaultReferenceIdentityType", "UserAssigned"),
            JMESPathCheck(
                "keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID
            ),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--keyvault-reference-id {keyvault_reference_id} ",
            checks=checks,
        )
        # Update test with keyvault reference id not provided in config file
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        checks = [
            JMESPathCheck("keyvaultReferenceIdentityType", "SystemAssigned"),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} ",
            checks=checks,
        )
        # Update test with keyvault reference id using CLI arguments when
        # both parameters and config file are provided
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "keyvault_reference_id": LoadTestConstants.KEYVAULT_REFERENCE_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_KVREFID,
            }
        )
        checks = [
            JMESPathCheck("keyvaultReferenceIdentityType", "UserAssigned"),
            JMESPathCheck(
                "keyvaultReferenceIdentityId", LoadTestConstants.KEYVAULT_REFERENCE_ID
            ),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} "
            "--keyvault-reference-id {keyvault_reference_id} ",
            checks=checks,
        )
        # Invalid test case for keyvault reference id
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "keyvault_reference_id": "Random",
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--keyvault-reference-id {keyvault_reference_id} ",
            )
        except Exception as e:
            assert "Invalid keyvault-ref-id value" in str(e)
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_KVREF_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_INVALID_KVREFID,
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--load-test-config-file "{load_test_config_file}" '
                "--resource-group {resource_group} ",
            )
        except Exception as e:
            assert "Key vault reference identity should be a valid resource id" in str(e)

    @ResourceGroupPreparer(**rg_params)
    @LoadTestResourcePreparer(**load_params)
    @StorageAccountPreparer(**sa_params)
    def test_load_test_splitcsv(self, rg, load):
        # Create load test from config file with split csv true
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE,
            }
        )
        checks = [
            JMESPathCheck("testId", self.kwargs["test_id"]),
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", True),
        ]
        self.cmd(
            "az load test create "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" ',
            checks=checks,
        )
        # Update test with split csv false from CLI arguments
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "split_csv": LoadTestConstants.SPLIT_CSV_FALSE,
            }
        )
        checks = [
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", False),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--split-csv {split_csv} ",
            checks=checks,
        )
        # Update test with split csv true from CLI arguments
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "split_csv": LoadTestConstants.SPLIT_CSV_TRUE,
            }
        )
        checks = [
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", True),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            "--split-csv {split_csv} ",
            checks=checks,
        )
        # Update test with split csv false using config file
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_SPLITCSV_FALSE,
            }
        )
        checks = [
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", False),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            "--resource-group {resource_group} "
            '--load-test-config-file "{load_test_config_file}" ',
            checks=checks,
        )
        # Update test with split csv CLI parameter when
        # both config file and CLI parameter are provided
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "split_csv": LoadTestConstants.SPLIT_CSV_TRUE,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_SPLITCSV_FALSE,
            }
        )
        checks = [
            JMESPathCheck("loadTestConfiguration.splitAllCSVs", True),
        ]
        self.cmd(
            "az load test update "
            "--test-id {test_id} "
            "--load-test-resource {load_test_resource} "
            '--load-test-config-file "{load_test_config_file}" '
            "--resource-group {resource_group} "
            "--split-csv {split_csv} ",
            checks=checks,
        )
        # Invalid test case for split csv
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "split_csv": "Random",
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                "--resource-group {resource_group} "
                "--split-csv {split_csv} ",
            )
        except Exception as e:
            assert "Invalid split-csv value: Random. Allowed values: true, false, yes, no, y, n" in str(e)
        self.kwargs.update(
            {
                "test_id": LoadTestConstants.LOAD_TEST_SPLITCSV_ID,
                "load_test_config_file": LoadTestConstants.LOAD_TEST_CONFIG_FILE_INVALID_SPLITCSV,
            }
        )
        try:
            self.cmd(
                "az load test update "
                "--test-id {test_id} "
                "--load-test-resource {load_test_resource} "
                '--load-test-config-file "{load_test_config_file}" '
                "--resource-group {resource_group} ",
            )
        except Exception as e:
            assert "Invalid value for splitAllCSVs. Allowed values are boolean true or false" in str(e)
