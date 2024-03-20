# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import pytest
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.core.azclierror import RequiredArgumentMissingError, ResourceNotFoundError, InvalidArgumentValueError
from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, get_test_workspace_storage, get_test_workspace_storage_grs, get_test_workspace_random_name, get_test_workspace_random_long_name, get_test_capabilities, get_test_workspace_provider_sku_list, all_providers_are_in_capabilities, issue_cmd_with_param_missing
from ..._version_check_helper import check_version
from datetime import datetime
from ...__init__ import CLI_REPORTED_VERSION
from ...operations.workspace import _validate_storage_account, _autoadd_providers, SUPPORTED_STORAGE_SKU_TIERS, SUPPORTED_STORAGE_KINDS, DEPLOYMENT_NAME_PREFIX

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# Classes patterned after classes in azext_quantum.vendored_sdks.azure_mgmt_quantum.models._models_py3.py
# Used in test_autoadd_providers()
class TestSkuDescription(object):
    def __init__(self, id, auto_add):
        self.id = id
        self.auto_add = auto_add

    __test__ = False


class TestManagedApplicationDescription(object):
    def __init__(self, offer_id, publisher_id):
        self.offer_id = offer_id
        self.publisher_id = publisher_id

    __test__ = False


class TestPropertyDescription(object):
    def __init__(self, managed_application, skus):
        self.managed_application = TestManagedApplicationDescription(None, None)
        self.skus = [TestSkuDescription(None, False)]

    __test__ = False


class TestProviderDescription:
    def __init__(self, id, properties):
        return

    __test__ = False
    id = None
    properties = TestPropertyDescription(TestManagedApplicationDescription(None, None), [TestSkuDescription(None, None)])
# End of test_autoadd_providers() class definitions


class QuantumWorkspacesScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_workspace(self):
        print("test_workspace")
        # clear
        self.cmd('az quantum workspace clear')

        # initialize values
        test_location = get_test_workspace_location()
        test_workspace = get_test_workspace()
        test_resource_group = get_test_resource_group()

        # list
        workspaces = self.cmd(f'az quantum workspace list -l {test_location} -o json').get_output_in_json()
        assert len(workspaces) > 0
        self.cmd('az quantum workspace list -o json', checks=[
            self.check(f"[?name=='{test_workspace}'].resourceGroup | [0]", test_resource_group)
        ])

        # set
        self.cmd(f'az quantum workspace set -g {test_resource_group} -w {test_workspace} -l {test_location} -o json', checks=[
            self.check("name", test_workspace)
        ])

        # show
        self.cmd('az quantum workspace show -o json', checks=[
            self.check("name", test_workspace)
        ])

        # clear
        self.cmd('az quantum workspace clear')

    @live_only()
    def test_workspace_create_destroy(self):
        print("test_workspace_create_destroy")
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()
        test_storage_account_grs = get_test_workspace_storage_grs()
        test_provider_sku_list = get_test_workspace_provider_sku_list()

        if all_providers_are_in_capabilities(test_provider_sku_list, get_test_capabilities()):
            # create
            self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json --skip-role-assignment', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create workspace with "--skip-role-assignment" and "--skip-autoadd" parameters
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json --skip-role-assignment', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Repeat without the "--skip-role-assignment" or "--skip-autoadd" parameters (Uses ARM template and adds C4A plans)
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create a workspace specifying "--skip-autoadd"
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create a workspace specifying a storage account that is not Standard_LRS
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account_grs} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create a workspace with a maximum length name, but make sure the deployment name was truncated to a valid length
            test_workspace_temp = get_test_workspace_random_long_name()
            self.cmd(f'az quantum workspace create --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account_grs} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", (DEPLOYMENT_NAME_PREFIX + test_workspace_temp)[:64]),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])
        else:
            self.skipTest(f"Skipping test_workspace_create_destroy: One or more providers in '{test_provider_sku_list}' not found in AZURE_QUANTUM_CAPABILITIES")

    @live_only()
    def test_workspace_keys(self):
        print("test_workspace_keys")
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()
        test_provider_sku_list = get_test_workspace_provider_sku_list()

        # create
        self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
            self.check("properties.provisioningState", "Succeeded")
        ])

        # set
        self.cmd(f'az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -o json', checks=[
            self.check("name", test_workspace_temp)
        ])

        # enable api keys
        self.cmd('az quantum workspace update --enable-api-key True -o json', checks=[
            self.check("properties.apiKeyEnabled", True)
        ])

        # list keys
        self.cmd('az quantum workspace keys list -o json', checks=[
            self.check("apiKeyEnabled", True)
        ])

        # regenerate primary keys
        self.cmd('az quantum workspace keys regenerate --key-type Primary -o json', expect_failure=False)

        # regenerate secondary keys
        self.cmd('az quantum workspace keys regenerate --key-type Secondary -o json', expect_failure=False)

        # regenerate primary and secondary keys
        self.cmd('az quantum workspace keys regenerate --key-type Primary,Secondary -o json', expect_failure=False)

        # disable api keys
        self.cmd('az quantum workspace update --enable-api-key False -o json')

        self.cmd('az quantum workspace keys list -o json', checks=[
            self.check("apiKeyEnabled", False)
        ])

        # delete
        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("properties.provisioningState", "Deleting")
        ])

    # @pytest.fixture(autouse=True)
    # def _pass_fixtures(self, capsys):
    #     self.capsys = capsys
    # # See "TODO" in issue_cmd_with_param_missing in utils.py

    @live_only()
    def test_workspace_errors(self):
        print("test_workspace_errors")
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()

        # Attempt to create workspace, but omit the storage account parameter
        issue_cmd_with_param_missing(self, f'az quantum workspace create -w {test_workspace_temp} -l {test_location} -g {test_resource_group} -r "microsoft-qc/learn-and-develop"', 'az quantum workspace create -g MyResourceGroup -w MyWorkspace -l MyLocation -r "MyProvider1 / MySKU1, MyProvider2 / MySKU2" -a MyStorageAccountName To display a list of available providers and their SKUs, use the following command: az quantum offerings list -l MyLocation -o table\nCreate a new Azure Quantum workspace with a specific list of providers.')

    @live_only()
    def test_version_check(self):
        print("test_version_check")
        # initialize values
        test_old_date = "2021-04-01"
        test_today = str(datetime.today()).split(' ')[0]
        test_old_reported_version = "0.1.0"
        test_current_reported_version = CLI_REPORTED_VERSION
        test_none_version = None
        test_config = None

        message = check_version(test_config, test_current_reported_version, test_old_date)
        assert message is None

        message = check_version(test_config, test_old_reported_version, test_old_date)
        assert message is None
        # NOTE: The behavior of this test case changed during April 2022, cause unknown.
        # Temporary fix was:
        # assert message == f"\nVersion {test_old_reported_version} of the quantum extension is installed locally, but version {test_current_reported_version} is now available.\nYou can use 'az extension update -n quantum' to upgrade.\n"

        # No message is generated if either version number is unavailable.
        message = check_version(test_config, test_none_version, test_today)
        assert message is None

    def test_validate_storage_account(self):
        print("test_validate_storage_account")
        # Calls with valid parameters should not raise errors
        _validate_storage_account('tier', 'Standard', SUPPORTED_STORAGE_SKU_TIERS)
        _validate_storage_account('kind', 'Storage', SUPPORTED_STORAGE_KINDS)
        _validate_storage_account('kind', 'StorageV2', SUPPORTED_STORAGE_KINDS)

        # Invalid parameters should raise errors
        try:
            _validate_storage_account('tier', 'Premium', SUPPORTED_STORAGE_SKU_TIERS)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "Storage account tier 'Premium' is not supported.\nStorage account tier currently supported: Standard"

        try:
            _validate_storage_account('kind', 'BlobStorage', SUPPORTED_STORAGE_KINDS)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "Storage account kind 'BlobStorage' is not supported.\nStorage account kinds currently supported: Storage, StorageV2"

    def test_autoadd_providers(self):
        print("test_autoadd_providers")
        test_managed_application = TestManagedApplicationDescription(None, None)
        test_skus = [TestSkuDescription(None, False)]
        test_provider_properties = TestPropertyDescription(test_managed_application, test_skus)
        test_provider = TestProviderDescription("", test_provider_properties)

        # Populate providers_in_region with an auto_add provider:
        test_provider.id = "foo"
        test_provider.properties.managed_application.offer_id = "foo_offer"
        test_provider.properties.managed_application.publisher_id = "foo0123456789"
        test_provider.properties.skus[0].id = "foo_credits_for_all_plan"
        test_provider.properties.skus[0].auto_add = True
        providers_in_region = []
        providers_in_region.append(test_provider)
        providers_selected = []
        cmd = None
        workspace_location = None
        _autoadd_providers(cmd, providers_in_region, providers_selected, workspace_location, True)
        assert providers_selected[0] == {"provider_id": "foo", "sku": "foo_credits_for_all_plan", "offer_id": "foo_offer", "publisher_id": "foo0123456789"}
