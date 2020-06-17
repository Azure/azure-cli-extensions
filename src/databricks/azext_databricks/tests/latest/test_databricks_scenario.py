# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, KeyVaultPreparer)
from msrestazure.tools import resource_id


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DatabricksClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_databricks')
    @KeyVaultPreparer(location='eastus2euap')
    def test_databricks(self, resource_group, key_vault):
        subscription_id = self.get_subscription_id()
        self.kwargs.update({
            'kv': key_vault,
            'workspace_name': 'my-test-workspace',
            'custom_workspace_name': 'my-custom-workspace',
            'managed_resource_group': 'custom-managed-rg'
        })

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location "eastus2euap" '
                 '--sku premium',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium')])

        managed_resource_group_id = '/subscriptions/{}/resourceGroups/{}'.format(subscription_id, self.kwargs.get('managed_resource_group', ''))
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {custom_workspace_name} '
                 '--location "westus" '
                 '--sku standard '
                 '--managed-resource-group {managed_resource_group}',
                 checks=[self.check('name', '{custom_workspace_name}'),
                         self.check('managedResourceGroupId', managed_resource_group_id)])

        workspace = self.cmd('az databricks workspace update '
                             '--resource-group {rg} '
                             '--name {workspace_name} '
                             '--tags type=test '
                             '--prepare-encryption',
                             checks=[self.check('tags.type', 'test'),
                                     self.exists('storageAccountIdentity.principalId')]).get_output_in_json()
        principalId = workspace['storageAccountIdentity']['principalId']

        self.kwargs.update({'oid': principalId, 'key_name': 'testkey'})

        self.cmd('az keyvault set-policy -n {kv} --object-id {oid} -g {rg} '
                 '--key-permissions get wrapKey unwrapKey recover')

        self.cmd('az keyvault update -n {kv} -g {rg} --set properties.enableSoftDelete=true')

        keyvault = self.cmd('az keyvault update -n {kv} -g {rg} --set properties.enablePurgeProtection=true').get_output_in_json()

        key = self.cmd('az keyvault key create -n {key_name} -p software --vault-name {kv}').get_output_in_json()
        key_version = key['key']['kid'].rsplit('/', 1)[1]

        self.kwargs.update({'key_version': key_version,
                            'key_vault': keyvault['properties']['vaultUri']})

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--key-source Microsoft.KeyVault '
                 '--key-name {key_name} '
                 '--key-version {key_version} '
                 '--key-vault {key_vault}',
                 checks=[self.check('parameters.encryption.value.keySource', 'Microsoft.Keyvault'),
                         self.check('parameters.encryption.value.keyName', '{key_name}'),
                         self.check('parameters.encryption.value.keyVersion', '{key_version}'),
                         self.check('parameters.encryption.value.keyVaultUri', '{key_vault}')])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--key-source Default',
                 checks=[self.check('parameters.encryption.value.keySource', 'Default'),
                         self.not_exists('parameters.encryption.value.keyName')])

        self.cmd('az databricks workspace show '
                 '--resource-group {rg} '
                 '--name {workspace_name}',
                 checks=[self.check('name', '{workspace_name}')])

        workspace_resource_id = resource_id(
            subscription=subscription_id,
            resource_group=resource_group,
            namespace='Microsoft.Databricks',
            type='workspaces',
            name=self.kwargs.get('workspace_name', ''))

        self.cmd('az databricks workspace show '
                 '--ids {}'.format(workspace_resource_id),
                 checks=[self.check('name', '{workspace_name}')])

        self.cmd('az databricks workspace list '
                 '--resource-group {rg} ',
                 checks=[])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {custom_workspace_name} '
                 '-y',
                 checks=[])
