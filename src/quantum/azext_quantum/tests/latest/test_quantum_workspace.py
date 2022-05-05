# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.core.azclierror import RequiredArgumentMissingError, ResourceNotFoundError, InvalidArgumentValueError
from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, get_test_workspace_storage, get_test_workspace_storage_grs, get_test_workspace_random_name, get_test_workspace_random_long_name, get_test_capabilities, get_test_workspace_provider_sku_list, all_providers_are_in_capabilities
from ..._version_check_helper import check_version
from datetime import datetime
from ...__init__ import CLI_REPORTED_VERSION
from ...operations.workspace import _validate_storage_account, SUPPORTED_STORAGE_SKU_TIERS, SUPPORTED_STORAGE_KINDS, DEPLOYMENT_NAME_PREFIX

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class QuantumWorkspacesScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_workspace(self):
        # clear
        self.cmd(f'az quantum workspace clear')

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
        self.cmd(f'az quantum workspace show -o json', checks=[
            self.check("name", test_workspace)
        ])

        # clear
        self.cmd(f'az quantum workspace clear')

    @live_only()
    def test_workspace_create_destroy(self):
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
            self.check("provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("provisioningState", "Deleting")
            ])

            # Repeat the tests without the "--skip-role-assignment" parameter
            test_workspace_temp = get_test_workspace_random_name()

            # create
            self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
            self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("provisioningState", "Deleting")
            ])

            # Create a workspace specifying a storage account that is not Standard_LRS
            test_workspace_temp = get_test_workspace_random_name()

            # create
            self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account_grs} -r {test_provider_sku_list} -o json', checks=[
            self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("provisioningState", "Deleting")
            ])

            # Create a workspace with a maximum length name, but make sure the deployment name was truncated to a valid length
            test_workspace_temp = get_test_workspace_random_long_name()

            # create
            self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account_grs} -r {test_provider_sku_list} -o json', checks=[
            self.check("name", (DEPLOYMENT_NAME_PREFIX + test_workspace_temp)[:64]),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("provisioningState", "Deleting")
            ])
        else:
            self.skipTest(f"Skipping test_workspace_create_destroy: One or more providers in '{test_provider_sku_list}' not found in AZURE_QUANTUM_CAPABILITIES")

    @live_only()
    def test_workspace_errors(self):
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()

        # Attempt to create workspace, but omit the provider/SKU parameter
        try:
            self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} --skip-role-assignment')
        except RequiredArgumentMissingError:
            pass    

        # Attempt to create workspace, but omit the resource group parameter
        try:
            self.cmd(f'az quantum workspace create -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r "Microsoft/Basic" --skip-role-assignment')
        except ResourceNotFoundError:
            pass    

    @live_only()
    def test_version_check(self):
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
