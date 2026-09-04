# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import argparse
import pytest
import unittest
import time
from types import SimpleNamespace
from unittest.mock import patch

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.core.azclierror import RequiredArgumentMissingError, ResourceNotFoundError, InvalidArgumentValueError, ForbiddenError, ServiceError
from azure.cli.command_modules.role._msgrpah._graph_client import GraphError
from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, get_test_workspace_storage, get_test_workspace_storage_grs, get_test_workspace_random_name, get_test_workspace_random_long_name, get_test_capabilities, get_test_workspace_provider_sku_list, get_test_workspace_v2_provider_sku_list, all_providers_are_in_capabilities, issue_cmd_with_param_missing
from ..._version_check_helper import check_version
from ..._params import QuotaAction
from datetime import datetime
from ...__init__ import CLI_REPORTED_VERSION
from ...operations.workspace import _apply_target_quotas, _require_v2_workspace, _validate_storage_account, _autoadd_providers, list_users, update, QUANTUM_WORKSPACE_DATA_CONTRIBUTOR_ROLE_ID, QUANTUM_WORKSPACE_OWNER_ROLE_ID, SUPPORTED_STORAGE_SKU_TIERS, SUPPORTED_STORAGE_KINDS, DEPLOYMENT_NAME_PREFIX
from ...operations.workspace import _merge_workspace_quotas
from ...commands import transform_workspace_quotas
from ...vendored_sdks.azure_mgmt_quantum.models import Provider, TargetQuotaAllocations
from ...vendored_sdks.azure_quantum_python._client.operations._operations import (
    build_services_quotas_list_quota_usages_request,
)

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
    @live_only()
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
        self.cmd(f'az quantum workspace set -g {test_resource_group} -w {test_workspace} -o json', checks=[
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
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()
        test_storage_account_grs = get_test_workspace_storage_grs()
        test_provider_sku_list = get_test_workspace_provider_sku_list()

        if all_providers_are_in_capabilities(test_provider_sku_list, get_test_capabilities()):
            # create
            self.cmd(f'az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json --skip-role-assignment', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
            ])

            time.sleep(10)  # Wait for the workspace to be provisioned

            # set
            self.cmd(f'az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp)
            ])

            # list quotas
            results = self.cmd('az quantum workspace quotas -o json').get_output_in_json()
            assert len(results) > 0
            assert len(results[0]["dimension"]) > 0
            assert results[0]["holds"] >= 0.0

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create workspace with "--skip-role-assignment" and "--skip-autoadd" parameters
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --skip-autoadd --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json --skip-role-assignment', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Repeat without the "--skip-role-assignment" or "--skip-autoadd" parameters (Uses ARM template and adds basic plans)
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create a workspace specifying "--skip-autoadd"
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --auto-accept --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create a workspace specifying a storage account that is not Standard_LRS
            test_workspace_temp = get_test_workspace_random_name()
            self.cmd(f'az quantum workspace create --auto-accept --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account_grs} -r {test_provider_sku_list} -o json', checks=[
                self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp),
            ])

            # delete
            self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
                self.check("name", test_workspace_temp),
                self.check("properties.provisioningState", "Deleting")
            ])

            # Create a workspace with a maximum length name, but make sure the deployment name was truncated to a valid length
            test_workspace_temp = get_test_workspace_random_long_name()
            self.cmd(f'az quantum workspace create --auto-accept --skip-autoadd -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account_grs} -r {test_provider_sku_list} -o json', checks=[
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
    def test_workspace_v2_create_destroy(self):
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_storage_account = get_test_workspace_storage()
        # V2 workspaces use a different provider model than V1. The e2e pipeline
        # supplies the V2 providers per-location via AZURE_QUANTUM_WORKSPACE_V2_PROVIDERS
        # (each paired with the "default" SKU), not via the V1 provider/capabilities
        # variables. Use those params so this test creates the same kind of V2
        # workspace the pipeline expects.
        test_provider_sku_list = get_test_workspace_v2_provider_sku_list()

        if not test_provider_sku_list:
            self.skipTest(f"Skipping test_workspace_v2_create_destroy: No V2 providers configured for location '{test_location}' in AZURE_QUANTUM_WORKSPACE_V2_PROVIDERS")

        # Create V2 workspace via ARM template path
        test_workspace_temp = get_test_workspace_random_name()
        self.cmd(f'az quantum workspace create --workspace-kind V2 --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r "{test_provider_sku_list}" -o json', checks=[
            self.check("name", DEPLOYMENT_NAME_PREFIX + test_workspace_temp)
        ])
        self.cmd(f'az quantum workspace show -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("properties.workspaceKind", "V2")
        ])
        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("properties.provisioningState", "Deleting")
        ])

        # Create a V2 workspace via --skip-role-assignment path
        test_workspace_temp = get_test_workspace_random_name()
        self.cmd(f'az quantum workspace create --workspace-kind V2 --auto-accept --skip-role-assignment -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r "{test_provider_sku_list}" -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("properties.provisioningState", "Accepted")
        ])
        self.cmd(f'az quantum workspace show -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("properties.workspaceKind", "V2")
        ])
        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("properties.provisioningState", "Deleting")
        ])

    @live_only()
    def test_workspace_keys(self):
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()
        test_provider_sku_list = get_test_workspace_provider_sku_list()

        # create
        self.cmd(f'az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
            self.check("properties.provisioningState", "Succeeded")
        ])

        # set
        self.cmd(f'az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
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

    @live_only()
    def test_workspace_user(self):
        import random
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()
        test_provider_sku_list = get_test_workspace_provider_sku_list()
        test_identity_name = "e2e-test-id" + str(random.randint(1000000, 9999999))

        # create a workspace to manage users on
        self.cmd(f'az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r {test_provider_sku_list} -o json', checks=[
            self.check("properties.provisioningState", "Succeeded")
        ])

        # Create a user-assigned managed identity to use as the assignee. Using its
        # object id (and '--assignee-object-id') keeps the test runnable under both
        # user and service-principal logins, since no Microsoft Graph lookup is needed.
        identity = self.cmd(f'az identity create -g {test_resource_group} -n {test_identity_name} -l {test_location} -o json').get_output_in_json()
        test_object_id = identity["principalId"]

        # grant access using the object id, relying on the default role. Verify the
        # default 'Quantum Workspace Data Contributor' role was assigned.
        self.cmd(f'az quantum workspace user create -g {test_resource_group} --workspace-name {test_workspace_temp} --assignee-object-id {test_object_id} -o json', checks=[
            self.check("principalId", test_object_id),
            self.check("ends_with(roleDefinitionId, 'c1410b24-3e69-4857-8f86-4d0a2e603250')", True)
        ])

        # The managed identity has principalType ServicePrincipal, so the user-only list excludes it.
        self.cmd(f'az quantum workspace user list -g {test_resource_group} --workspace-name {test_workspace_temp} --include-inherited false -o json', checks=[
            self.check(f"length([?principalId=='{test_object_id}'])", 0)
        ])

        # remove access using the object id and an explicit role
        self.cmd(f'az quantum workspace user delete -g {test_resource_group} --workspace-name {test_workspace_temp} --assignee-object-id {test_object_id} --role c1410b24-3e69-4857-8f86-4d0a2e603250 --yes')

        # clean up the managed identity
        self.cmd(f'az identity delete -g {test_resource_group} -n {test_identity_name}')

        # delete the workspace
        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
            self.check("name", test_workspace_temp),
            self.check("properties.provisioningState", "Deleting")
        ])

    # @pytest.fixture(autouse=True)
    # def _pass_fixtures(self, capsys):
    #     self.capsys = capsys
    # # See "TODO" in issue_cmd_with_param_missing in utils.py

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

    def test_quota_validation(self):
        allocation = QuotaAction._validate({
            'providerId': 'provider',
            'targetId': 'provider.target-1',
            'standardMinutesLifetime': '500',
            'highMinutesLifetime': 50
        }, '--quota')
        assert allocation == {
            'providerId': 'provider',
            'targetId': 'provider.target-1',
            'standardMinutesLifetime': 500,
            'highMinutesLifetime': 50
        }

        with self.assertRaises(InvalidArgumentValueError):
            QuotaAction._validate({
                'providerId': 'provider',
                'targetId': 'invalid target',
                'standardMinutesLifetime': 500
            }, '--quota')

        with self.assertRaises(InvalidArgumentValueError):
            QuotaAction._validate({
                'providerId': 'provider',
                'targetId': 'provider.target',
                'standardMinutesLifetime': -1
            }, '--quota')

    def test_quota_action_repeated_allocations(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--quota', action=QuotaAction, nargs='+')

        result = parser.parse_args([
            '--quota',
            'providerId=provider',
            'targetId=provider.target-1',
            'standardMinutesLifetime=500',
            '--quota',
            'providerId=provider',
            'targetId=provider.target-2',
            'standardMinutesLifetime=250'
        ])

        assert len(result.quota) == 2
        assert result.quota[0]['targetId'] == 'provider.target-1'
        assert result.quota[1]['targetId'] == 'provider.target-2'

        with self.assertRaises(InvalidArgumentValueError):
            parser.parse_args([
                '--quota',
                'providerId=provider',
                'targetId=provider.target',
                'standardMinutesLifetime=500',
                '--quota',
                'providerId=PROVIDER',
                'targetId=PROVIDER.TARGET',
                'standardMinutesLifetime=250'
            ])

    def test_quota_key_aliases(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--quota', action=QuotaAction, nargs='+')

        result = parser.parse_args([
            '--quota',
            'provider-id=provider',
            'target-id=provider.target-1',
            'standard-minutes-lifetime=500',
            'high-minutes-lifetime=50',
            '--quota',
            'Provider_Id=provider',
            'Target_Id=provider.target-2',
            'Standard_Minutes_Lifetime=250'
        ])

        assert result.quota[0] == {
            'providerId': 'provider',
            'targetId': 'provider.target-1',
            'standardMinutesLifetime': 500,
            'highMinutesLifetime': 50
        }
        assert result.quota[1] == {
            'providerId': 'provider',
            'targetId': 'provider.target-2',
            'standardMinutesLifetime': 250
        }

    def test_quota_rejects_duplicate_key_in_single_flag(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--quota', action=QuotaAction, nargs='+')

        # Two targets crammed into a single --quota must not be silently merged.
        with self.assertRaises(InvalidArgumentValueError):
            parser.parse_args([
                '--quota',
                'providerId=provider',
                'targetId=provider.target-1',
                'standardMinutesLifetime=500',
                'providerId=provider',
                'targetId=provider.target-2',
                'standardMinutesLifetime=250'
            ])

        # camelCase and kebab-case spellings of the same key also collide.
        with self.assertRaises(InvalidArgumentValueError):
            parser.parse_args([
                '--quota',
                'targetId=provider.target-1',
                'target-id=provider.target-2',
                'providerId=provider',
                'standardMinutesLifetime=500'
            ])

    def test_quota_rejects_float(self):
        with self.assertRaises(InvalidArgumentValueError):
            QuotaAction._validate({
                'providerId': 'provider',
                'targetId': 'provider.target',
                'standardMinutesLifetime': 500.5
            }, '--quota')

        with self.assertRaises(InvalidArgumentValueError):
            QuotaAction._validate({
                'providerId': 'provider',
                'targetId': 'provider.target',
                'standardMinutesLifetime': '500.5'
            }, '--quota')

    def test_apply_target_quotas(self):
        provider = Provider(provider_id='provider', provider_sku='default')

        _apply_target_quotas([provider], [{
            'providerId': 'provider',
            'targetId': 'provider.target',
            'standardMinutesLifetime': 500,
            'highMinutesLifetime': 50
        }])

        assert len(provider.target_quotas) == 1
        assert provider.target_quotas[0].target_id == 'provider.target'
        assert provider.target_quotas[0].standard_minutes_lifetime == 500
        assert provider.target_quotas[0].high_minutes_lifetime == 50

    def test_apply_target_quotas_preserves_omitted_values(self):
        provider = Provider(
            provider_id='provider',
            provider_sku='default',
            target_quotas=[TargetQuotaAllocations(
                target_id='provider.target',
                standard_minutes_lifetime=500,
                high_minutes_lifetime=50
            )]
        )

        _apply_target_quotas([provider], [{
            'providerId': 'provider',
            'targetId': 'provider.target',
            'standardMinutesLifetime': 0
        }], preserve_existing=True)

        assert provider.target_quotas[0].standard_minutes_lifetime == 0
        assert provider.target_quotas[0].high_minutes_lifetime == 50

    def test_target_quota_validation_errors(self):
        with self.assertRaises(InvalidArgumentValueError):
            _require_v2_workspace('V1')

        with self.assertRaises(InvalidArgumentValueError):
            _apply_target_quotas([Provider(provider_id='provider')], [{
                'providerId': 'other-provider',
                'targetId': 'provider.target',
                'standardMinutesLifetime': 500
            }])

        with self.assertRaises(InvalidArgumentValueError):
            _apply_target_quotas([Provider(provider_id='provider')], [{
                'providerId': 'provider',
                'targetId': 'provider.target',
                'highMinutesLifetime': 50
            }])

    @unittest.mock.patch('azext_quantum.operations.workspace.WorkspaceInfo')
    @unittest.mock.patch('azext_quantum.operations.workspace.cf_workspaces')
    def test_update_target_quota_and_api_key(self, mock_cf_workspaces, mock_workspace_info):
        provider = Provider(
            provider_id='provider',
            provider_sku='default',
            target_quotas=[TargetQuotaAllocations(
                target_id='provider.target',
                standard_minutes_lifetime=500,
                high_minutes_lifetime=50
            )]
        )
        workspace = unittest.mock.MagicMock()
        workspace.properties.workspace_kind = 'V2'
        workspace.properties.providers = [provider]
        workspace.properties.api_key_enabled = False
        workspace.properties.endpoint_uri = 'https://workspace.quantum.azure.com'

        client = mock_cf_workspaces.return_value
        client.get.return_value = workspace
        client.begin_create_or_update.return_value.result.return_value = workspace
        info = mock_workspace_info.return_value
        info.resource_group = 'group'
        info.name = 'workspace'

        result = update(
            unittest.mock.MagicMock(),
            resource_group_name='group',
            workspace_name='workspace',
            enable_key='true',
            quota=[{
                'providerId': 'provider',
                'targetId': 'provider.target',
                'standardMinutesLifetime': 0
            }]
        )

        assert result is workspace
        assert workspace.properties.api_key_enabled is True
        assert provider.target_quotas[0].standard_minutes_lifetime == 0
        assert provider.target_quotas[0].high_minutes_lifetime == 50
        client.begin_create_or_update.assert_called_once_with('group', 'workspace', workspace)

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

    def test_get_workspace_resource_id(self):
        print("test_get_workspace_resource_id")
        from ...operations.workspace import _get_workspace_resource_id

        class TestWorkspaceInfo(object):
            subscription = "00000000-0000-0000-0000-000000000000"
            resource_group = "MyResourceGroup"
            name = "MyWorkspace"
            __test__ = False

        resource_id = _get_workspace_resource_id(TestWorkspaceInfo())
        assert resource_id == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyResourceGroup/providers/Microsoft.Quantum/Workspaces/MyWorkspace"


class QuantumWorkspaceQuotasTest(unittest.TestCase):

    def test_build_workspace_quotas_list_quota_usages_request(self):
        request = build_services_quotas_list_quota_usages_request(
            subscription_id='00000000-0000-0000-0000-000000000000',
            resource_group_name='MyResourceGroup',
            workspace_name='MyWorkspace',
            provider_id='ionq',
        )
        self.assertEqual(request.method, 'GET')
        self.assertIn(
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyResourceGroup/providers/Microsoft.Quantum/workspaces/MyWorkspace/quotaUsages',
            request.url,
        )
        self.assertIn('providerId=ionq', request.url)
        self.assertIn('api-version=2026-01-15-preview', request.url)

    def test_merge_workspace_quotas_with_usage(self):
        workspace = SimpleNamespace(location='eastus', properties=SimpleNamespace(providers=[
            SimpleNamespace(provider_id='ionq', target_quotas=[
                SimpleNamespace(target_id='ionq.qpu', standard_minutes_lifetime=30, high_minutes_lifetime=15),
            ]),
        ]))
        legacy_quotas = [{
            'dimension': 'emulator_hours', 'providerId': 'pasqal', 'scope': 'Subscription',
            'limit': 5.0, 'utilization': 1.0, 'holds': 0.0, 'period': 'Monthly'
        }]
        usages = [
            SimpleNamespace(provider_id='ionq', target_id='ionq.qpu',
                            usage=SimpleNamespace(standard_minutes_lifetime=5, high_minutes_lifetime=2)),
        ]

        rows = _merge_workspace_quotas(workspace, usages, legacy_quotas)

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], legacy_quotas[0])
        self.assertEqual(rows[1], {
            'dimension': 'StandardMinutesLifetime',
            'providerId': 'ionq',
            'scope': 'Workspace',
            'limit': 30,
            'utilization': 5,
            'holds': 0.0,
            'period': 'None',
            'targetId': 'ionq.qpu',
        })
        self.assertEqual(rows[2], {
            'dimension': 'HighMinutesLifetime',
            'providerId': 'ionq',
            'scope': 'Workspace',
            'limit': 15,
            'utilization': 2,
            'holds': 0.0,
            'period': 'None',
            'targetId': 'ionq.qpu',
        })

    def test_merge_workspace_quotas_without_usage(self):
        workspace = SimpleNamespace(location='eastus', properties=SimpleNamespace(providers=[
            SimpleNamespace(provider_id='ionq', target_quotas=[
                SimpleNamespace(target_id='ionq.qpu', standard_minutes_lifetime=30, high_minutes_lifetime=None),
            ]),
        ]))

        rows = _merge_workspace_quotas(workspace, [])

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['dimension'], 'StandardMinutesLifetime')
        self.assertEqual(rows[0]['limit'], 30)
        self.assertEqual(rows[0]['utilization'], 0)
        self.assertEqual(rows[1]['dimension'], 'HighMinutesLifetime')
        self.assertEqual(rows[1]['limit'], 0)
        self.assertEqual(rows[1]['utilization'], 0)

    def test_merge_workspace_quotas_matches_on_provider_and_target(self):
        workspace = SimpleNamespace(location='eastus', properties=SimpleNamespace(providers=[
            SimpleNamespace(provider_id='ionq', target_quotas=[
                SimpleNamespace(target_id='shared.target', standard_minutes_lifetime=30, high_minutes_lifetime=15),
            ]),
        ]))
        usages = [
            # Same target id but a different provider -> must not match.
            SimpleNamespace(provider_id='quantinuum', target_id='shared.target',
                            usage=SimpleNamespace(standard_minutes_lifetime=9, high_minutes_lifetime=4)),
        ]

        rows = _merge_workspace_quotas(workspace, usages)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['providerId'], 'ionq')
        self.assertEqual(rows[0]['utilization'], 0)

    def test_merge_workspace_quotas_includes_usage_without_allocation(self):
        workspace = SimpleNamespace(location='eastus', properties=SimpleNamespace(providers=[
            SimpleNamespace(provider_id='ionq', target_quotas=[]),
        ]))
        usages = [
            SimpleNamespace(provider_id='IONQ', target_id='ionq.retired-target',
                            usage=SimpleNamespace(standard_minutes_lifetime=9, high_minutes_lifetime=None)),
        ]

        rows = _merge_workspace_quotas(workspace, usages)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['targetId'], 'ionq.retired-target')
        self.assertEqual(rows[0]['limit'], 0)
        self.assertEqual(rows[0]['utilization'], 9)
        self.assertEqual(rows[1]['limit'], 0)
        self.assertEqual(rows[1]['utilization'], 0)

    def test_merge_workspace_quotas_handles_missing_properties(self):
        workspace = SimpleNamespace(location='eastus', properties=None)
        legacy_quotas = [{'dimension': 'legacy'}]
        self.assertEqual(_merge_workspace_quotas(workspace, [], legacy_quotas), legacy_quotas)

    def test_transform_workspace_quotas_preserves_mixed_dimensions(self):
        quotas = [
            {
                'dimension': 'emulator_hours', 'providerId': 'pasqal', 'scope': 'Subscription',
                'limit': 5.0, 'utilization': 1.0, 'holds': 0.0, 'period': 'Monthly'
            },
            {
                'dimension': 'StandardMinutesLifetime', 'providerId': 'ionq', 'scope': 'Workspace',
                'limit': 1200, 'utilization': 27.000000000000007, 'holds': 0.0, 'period': 'None',
                'targetId': 'ionq.qpu'
            },
        ]

        table = transform_workspace_quotas(quotas)

        self.assertEqual(list(table[0].keys()), [
            'Dimension', 'Provider ID', 'Scope', 'Target', 'Limit', 'Utilization', 'Holds', 'Period'
        ])
        self.assertEqual(table[0]['Target'], '')
        self.assertEqual(table[0]['Limit'], 5.0)
        self.assertEqual(table[0]['Utilization'], 1.0)
        self.assertEqual(table[1]['Target'], 'ionq.qpu')
        self.assertEqual(table[1]['Limit'], 1200)
        self.assertEqual(table[1]['Utilization'], 27.0)

    def test_quotas_handler_queries_each_provider_and_merges(self):
        info = SimpleNamespace(subscription='sub', resource_group='rg', name='ws', endpoint=None)
        workspace = SimpleNamespace(location='eastus', properties=SimpleNamespace(workspace_kind='V2', providers=[
            SimpleNamespace(provider_id='ionq', target_quotas=[
                SimpleNamespace(target_id='ionq.qpu', standard_minutes_lifetime=30, high_minutes_lifetime=15),
            ]),
            SimpleNamespace(provider_id='pasqal', target_quotas=None),
        ]))
        legacy_row = {
            'dimension': 'emulator_hours', 'providerId': 'pasqal', 'scope': 'Subscription',
            'limit': 5.0, 'utilization': 1.0, 'holds': 0.0, 'period': 'Monthly'
        }

        usage_by_provider = {
            'ionq': [SimpleNamespace(provider_id='ionq', target_id='ionq.qpu',
                                     usage=SimpleNamespace(standard_minutes_lifetime=5, high_minutes_lifetime=2))],
            'pasqal': [],
        }
        queried = []

        def fake_list_quota_usages(*args):
            provider_id = args[-1]
            queried.append(provider_id)
            return usage_by_provider[provider_id]

        legacy_client = SimpleNamespace(list=lambda *_: [legacy_row])
        v2_client = SimpleNamespace(list_quota_usages=fake_list_quota_usages)

        def fake_client_factory(*args):
            endpoint = args[-1]
            return legacy_client if endpoint == 'https://eastus.quantum.azure.com/' else v2_client

        from ...operations import workspace as workspace_ops
        with patch.object(workspace_ops, 'WorkspaceInfo', return_value=info), \
                patch.object(workspace_ops, 'cf_workspaces', return_value=SimpleNamespace(get=lambda rg, ws: workspace)), \
                patch.object(workspace_ops, 'base_url', return_value='https://eastus.quantum.azure.com/'), \
                patch.object(workspace_ops, 'base_url_v2', return_value='https://eastus-v2.quantum.azure.com/'), \
                patch.object(workspace_ops, 'cf_quotas', side_effect=fake_client_factory) as client_factory:
            cmd = SimpleNamespace(cli_ctx=object())
            rows = workspace_ops.quotas(cmd, 'rg', 'ws')

        self.assertEqual(set(queried), {'ionq', 'pasqal'})
        self.assertEqual(client_factory.call_count, 2)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], legacy_row)
        self.assertEqual(rows[1]['dimension'], 'StandardMinutesLifetime')
        self.assertEqual(rows[1]['limit'], 30)
        self.assertEqual(rows[1]['utilization'], 5)
        self.assertEqual(rows[2]['dimension'], 'HighMinutesLifetime')
        self.assertEqual(rows[2]['limit'], 15)
        self.assertEqual(rows[2]['utilization'], 2)

    def test_quotas_handler_keeps_v1_behavior_without_v2_usage_calls(self):
        info = SimpleNamespace(subscription='sub', resource_group='rg', name='ws', endpoint=None)
        workspace = SimpleNamespace(location='eastus', properties=SimpleNamespace(
            workspace_kind='V1', providers=[SimpleNamespace(provider_id='pasqal', target_quotas=None)]))
        legacy_row = {
            'dimension': 'emulator_hours', 'providerId': 'pasqal', 'scope': 'Subscription',
            'limit': 5.0, 'utilization': 1.0, 'holds': 0.0, 'period': 'Monthly'
        }
        legacy_client = SimpleNamespace(list=lambda subscription, resource_group, workspace_name: [legacy_row])

        from ...operations import workspace as workspace_ops
        with patch.object(workspace_ops, 'WorkspaceInfo', return_value=info), \
                patch.object(workspace_ops, 'cf_workspaces', return_value=SimpleNamespace(get=lambda rg, ws: workspace)), \
                patch.object(workspace_ops, 'base_url', return_value='https://eastus.quantum.azure.com/'), \
                patch.object(workspace_ops, 'cf_quotas', return_value=legacy_client) as client_factory:
            rows = workspace_ops.quotas(SimpleNamespace(cli_ctx=object()), 'rg', 'ws')

        self.assertEqual(rows, [legacy_row])
        client_factory.assert_called_once()


class QuantumWorkspaceUserListTest(unittest.TestCase):
    def test_list_users_scopes_to_workspace(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "oid", "principalName": "user@contoso.com", "principalType": "User"}]
        stubs = [{"id": "oid", "displayName": "Contoso User", "mail": "user@contoso.com", "userPrincipalName": "user@contoso.com"}]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]) as list_role_assignments, \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", return_value=stubs):
            cmd = SimpleNamespace(cli_ctx=object())
            result = list_users(cmd, "rg", "ws")

        expected_scope = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Quantum/Workspaces/ws"
        queried = {call.kwargs["role"]: (call.kwargs["scope"], call.kwargs["include_inherited"]) for call in list_role_assignments.call_args_list}
        self.assertEqual(queried[QUANTUM_WORKSPACE_DATA_CONTRIBUTOR_ROLE_ID], (expected_scope, True))
        self.assertEqual(queried[QUANTUM_WORKSPACE_OWNER_ROLE_ID], (expected_scope, True))
        self.assertEqual(result[0]["displayName"], "Contoso User")
        self.assertEqual(result[0]["mail"], "user@contoso.com")
        self.assertEqual(result[0]["roleDefinitionName"], "Quantum Workspace Data Contributor")

    def test_list_users_includes_owner_and_contributor_roles(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        owner = [{"principalId": "o", "principalName": "owner@contoso.com", "principalType": "User", "roleDefinitionName": "Quantum Workspace Owner"}]
        contributor = [{"principalId": "c", "principalName": "contrib@contoso.com", "principalType": "User", "roleDefinitionName": "Quantum Workspace Data Contributor"}]
        stubs = [
            {"id": "o", "displayName": "Owner User", "mail": "owner@contoso.com", "userPrincipalName": "owner@contoso.com"},
            {"id": "c", "displayName": "Contrib User", "mail": "contrib@contoso.com", "userPrincipalName": "contrib@contoso.com"},
        ]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[contributor, owner]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", return_value=stubs):
            cmd = SimpleNamespace(cli_ctx=object())
            result = list_users(cmd, "rg", "ws")

        self.assertEqual([user["roleDefinitionName"] for user in result], ["Quantum Workspace Data Contributor", "Quantum Workspace Owner"])

    def test_list_users_can_exclude_inherited(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", return_value=[]) as list_role_assignments:
            cmd = SimpleNamespace(cli_ctx=object())
            list_users(cmd, "rg", "ws", include_inherited=False)

        expected_scope = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Quantum/Workspaces/ws"
        queried = {call.kwargs["role"]: (call.kwargs["scope"], call.kwargs["include_inherited"]) for call in list_role_assignments.call_args_list}
        self.assertEqual(queried[QUANTUM_WORKSPACE_DATA_CONTRIBUTOR_ROLE_ID], (expected_scope, False))
        self.assertEqual(queried[QUANTUM_WORKSPACE_OWNER_ROLE_ID], (expected_scope, False))

    def test_list_users_excludes_groups_and_service_principals(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [
            {"principalId": "u", "principalType": "User"},
            {"principalId": "g", "principalType": "Group"},
            {"principalId": "sp", "principalType": "ServicePrincipal"},
        ]
        stubs = [{"id": "u", "displayName": "User One", "mail": "u@contoso.com", "userPrincipalName": "u@contoso.com"}]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", return_value=stubs):
            cmd = SimpleNamespace(cli_ctx=object())
            result = list_users(cmd, "rg", "ws")

        self.assertEqual([user["principalId"] for user in result], ["u"])
        self.assertEqual(result[0]["displayName"], "User One")

    def test_list_users_falls_back_to_upn_when_display_name_missing(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User", "roleDefinitionName": "Quantum Workspace Data Contributor"}]
        # Graph resolves the principal but returns no displayName/mail (only the UPN).
        stubs = [{"id": "u", "userPrincipalName": "user@contoso.com"}]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", return_value=stubs):
            cmd = SimpleNamespace(cli_ctx=object())
            result = list_users(cmd, "rg", "ws")

        # Name and Email fall back to the UPN from Graph.
        self.assertEqual(result[0]["displayName"], "user@contoso.com")
        self.assertEqual(result[0]["mail"], "user@contoso.com")

    def test_list_users_retries_graph_error(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        stubs = [{"id": "u", "displayName": "User One", "mail": "u@contoso.com"}]
        response = SimpleNamespace(status_code=429, headers={"Retry-After": "3"})
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()) as graph_client_factory, \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=[GraphError("temporary", response), stubs]) as get_object_stubs, \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            cmd = SimpleNamespace(cli_ctx=object())
            result = list_users(cmd, "rg", "ws")

        self.assertEqual(result[0]["displayName"], "User One")
        graph_client_factory.assert_called_once_with(cmd.cli_ctx)
        self.assertEqual(get_object_stubs.call_count, 2)
        sleep.assert_called_once_with(3.0)

    def test_list_users_clamps_retry_after(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        stubs = [{"id": "u", "displayName": "User One"}]
        response = SimpleNamespace(status_code=429, headers={"Retry-After": "3600"})
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=[GraphError("temporary", response), stubs]), \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            list_users(SimpleNamespace(cli_ctx=object()), "rg", "ws")

        sleep.assert_called_once_with(60)

    def test_list_users_uses_exponential_backoff_without_retry_after(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        stubs = [{"id": "u", "displayName": "User One"}]
        response = SimpleNamespace(status_code=503, headers={})
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=[GraphError("temporary", response), stubs]), \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            list_users(SimpleNamespace(cli_ctx=object()), "rg", "ws")

        sleep.assert_called_once_with(1)

    def test_list_users_retries_graph_error_without_status_code(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        stubs = [{"id": "u", "displayName": "User One"}]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=[GraphError("temporary", None), stubs]) as get_object_stubs, \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            result = list_users(SimpleNamespace(cli_ctx=object()), "rg", "ws")

        self.assertEqual(result[0]["displayName"], "User One")
        self.assertEqual(get_object_stubs.call_count, 2)
        sleep.assert_called_once_with(1)

    def test_list_users_does_not_retry_permanent_graph_error(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        response = SimpleNamespace(status_code=403, headers={})
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=GraphError("forbidden", response)) as get_object_stubs, \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            with self.assertRaises(ForbiddenError):
                list_users(SimpleNamespace(cli_ctx=object()), "rg", "ws")

        get_object_stubs.assert_called_once()
        sleep.assert_not_called()

    def test_list_users_does_not_retry_unexpected_error(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=ValueError("unexpected")) as get_object_stubs, \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            with self.assertRaises(ValueError):
                list_users(SimpleNamespace(cli_ctx=object()), "rg", "ws")

        get_object_stubs.assert_called_once()
        sleep.assert_not_called()

    def test_list_users_falls_back_when_principal_not_in_directory(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "missing", "principalName": "ghost@contoso.com", "principalType": "User"}]
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", return_value=[]) as get_object_stubs, \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            cmd = SimpleNamespace(cli_ctx=object())
            result = list_users(cmd, "rg", "ws")

        # A principal Graph cannot resolve falls back to the principal name; the command still succeeds.
        self.assertEqual(result[0]["displayName"], "ghost@contoso.com")
        self.assertEqual(result[0]["mail"], "ghost@contoso.com")
        get_object_stubs.assert_called_once()
        sleep.assert_not_called()

    def test_list_users_raises_after_persistent_transient_error(self):
        info = SimpleNamespace(subscription="sub", resource_group="rg", name="ws", endpoint=None)
        assignments = [{"principalId": "u", "principalType": "User"}]
        response = SimpleNamespace(status_code=429, headers={})
        with patch("azext_quantum.operations.workspace.WorkspaceInfo", return_value=info), \
                patch("azure.cli.command_modules.role.custom.list_role_assignments", side_effect=[assignments, []]), \
                patch("azure.cli.command_modules.role.graph_client_factory", return_value=object()), \
                patch("azure.cli.command_modules.role.custom._get_object_stubs", side_effect=GraphError("throttled", response)) as get_object_stubs, \
                patch("azext_quantum.operations.workspace.time.sleep") as sleep:
            cmd = SimpleNamespace(cli_ctx=object())
            with self.assertRaisesRegex(ServiceError, "Please try again later"):
                list_users(cmd, "rg", "ws")

        self.assertEqual(get_object_stubs.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_transform_users(self):
        from ...commands import transform_users
        rows = transform_users([{
            "principalId": "oid",
            "principalName": "user@contoso.com",
            "displayName": "Contoso User",
            "mail": "user@contoso.com",
            "createdOn": "2026-06-24T16:53:26.107178+00:00",
            "principalType": "User",
            "roleDefinitionName": "Quantum Workspace Data Contributor",
            "scope": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Quantum/Workspaces/ws"
        }])
        self.assertEqual(rows[0]["Name"], "Contoso User")
        self.assertEqual(rows[0]["Email"], "user@contoso.com")
        self.assertEqual(rows[0]["Role"], "Quantum Workspace Data Contributor")
        self.assertEqual(rows[0]["Time Added"], "2026-06-24T16:53:26.107178+00:00")

        # Email falls back to the principal name when Graph did not return a mail address.
        fallback = transform_users([{"principalName": "fallback@contoso.com"}])
        self.assertEqual(fallback[0]["Email"], "fallback@contoso.com")
        self.assertIsNone(fallback[0]["Name"])
