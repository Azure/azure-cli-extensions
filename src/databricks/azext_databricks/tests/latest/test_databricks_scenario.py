# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, KeyVaultPreparer)
from msrestazure.tools import resource_id

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DatabricksClientScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks')
    @KeyVaultPreparer(location='eastus')
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
                 '--location "eastus" '
                 '--sku premium '
                 '--enable-no-public-ip',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium'),
                         self.check('parameters.enableNoPublicIp.value', True)])

        managed_resource_group_id = '/subscriptions/{}/resourceGroups/{}'.format(subscription_id, self.kwargs.get('managed_resource_group', ''))
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {custom_workspace_name} '
                 '--location "westus" '
                 '--sku standard '
                 '--managed-resource-group {managed_resource_group} '
                 '--tags env=dev',
                 checks=[self.check('name', '{custom_workspace_name}'),
                         self.check('managedResourceGroupId', managed_resource_group_id),
                         self.check('tags.env', 'dev')])

        workspace = self.cmd('az databricks workspace update '
                             '--resource-group {rg} '
                             '--name {workspace_name} '
                             '--tags type=test env=dev '
                             '--prepare-encryption',
                             checks=[self.check('tags.type', 'test'),
                                     self.check('tags.env', 'dev'),
                                     self.check('parameters.prepareEncryption.value', True),
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
                         self.check('parameters.encryption.value.KeyName', '{key_name}'),
                         self.check('parameters.encryption.value.keyversion', '{key_version}'),
                         self.check('parameters.encryption.value.keyvaulturi', '{key_vault}')])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--key-source Default',
                 checks=[self.check('parameters.encryption.value.keySource', 'Default'),
                         self.not_exists('parameters.encryption.value.KeyName')])

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

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_v1', location="westus")
    def test_databricks_v1(self, resource_group):
        self.kwargs.update({
            'workspace_name': 'my-test-workspace'
        })

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location westus '
                 '--sku premium '
                 '--public-network-access Enabled '
                 '--required-nsg-rules AllRules',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium'),
                         self.check('publicNetworkAccess', 'Enabled'),
                         self.check('requiredNsgRules', 'AllRules')])

        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--sku standard ',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'standard')])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

    @ResourceGroupPreparer(name_prefix='cli_test_access_connector', location="westus")
    def test_access_connector(self, resource_group):
        self.kwargs.update({
            'access_connector_name': 'my-test-access-connector',
            'type': 'SystemAssigned',
        })

        self.cmd('az databricks access-connector create '
                 '--resource-group {rg} '
                 '--name {access_connector_name} '
                 '--location westus '
                 '--identity-type {type} ',
                 checks=[self.check('name', '{access_connector_name}'),
                         self.check('properties.provisioningState', 'Succeeded'),
                         self.check('identity.type', 'SystemAssigned')])

        self.cmd('az databricks access-connector update '
                 '--resource-group {rg} '
                 '--name {access_connector_name} '
                 '--identity-type None '
                 '--tags key=value ',
                 checks=[self.check('name', '{access_connector_name}'),
                         self.check('properties.provisioningState', 'Succeeded'),
                         self.check('identity.type', 'None')])

        self.cmd('az databricks access-connector list '
                 '--resource-group {rg} ',
                 checks=[self.check('length(@)', 1)])

        self.cmd('az databricks access-connector show '
                 '--resource-group {rg} '
                 '--name {access_connector_name} ',
                 checks=[self.check('name', '{access_connector_name}'),
                         self.check('properties.provisioningState', 'Succeeded')])

        self.cmd('az databricks access-connector delete '
                 '--resource-group {rg} '
                 '--name {access_connector_name} ',
                 checks=[])

    @ResourceGroupPreparer(name_prefix='cli_test_access_connector', location="westus")
    def test_access_connector_v2(self, resource_group):
        self.kwargs.update({
            'identity_name': 'my-test-identity',
            'access_connector_name': 'my-test-access-connector',
            'type': 'UserAssigned',
        })

        self.kwargs['identity_id'] = self.cmd('az identity create -n {identity_name} -g {rg}').get_output_in_json()['id']
        self.cmd('az databricks access-connector create '
                 '--resource-group {rg} '
                 '--name {access_connector_name} '
                 '--location westus '
                 '--identity-type {type} '
                 '--user-assigned-identities {{{identity_id}:{{}}}}',
                 checks=[self.check('name', '{access_connector_name}'),
                         self.check('properties.provisioningState', 'Succeeded'),
                         self.check('identity.type', 'UserAssigned'),
                         self.check('type(identity.userAssignedIdentities)', 'object')])

        self.cmd('az databricks access-connector delete '
                 '--resource-group {rg} '
                 '--name {access_connector_name} ',
                 checks=[])

        self.cmd('az databricks access-connector create '
                 '--resource-group {rg} '
                 '--name {access_connector_name} '
                 '--location westus '
                 '--identity-type None ',
                 checks=[self.check('name', '{access_connector_name}'),
                         self.check('properties.provisioningState', 'Succeeded'),
                         self.check('identity.type', 'None')])

        self.cmd('az databricks access-connector update '
                 '--resource-group {rg} '
                 '--name {access_connector_name} '
                 '--identity-type {type} '
                 '--user-assigned-identities {{{identity_id}:{{}}}}',
                 checks=[self.check('name', '{access_connector_name}'),
                         self.check('properties.provisioningState', 'Succeeded'),
                         self.check('identity.type', 'UserAssigned'),
                         self.check('type(identity.userAssignedIdentities)', 'object')])

        self.cmd('az databricks access-connector delete '
                 '--resource-group {rg} '
                 '--name {access_connector_name} ',
                 checks=[])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_v2', location="eastus2euap")
    def test_databricks_v2(self, resource_group):
        self.kwargs.update({
            'workspace_name': self.create_random_name(prefix='wn', length=12),
            'status': 'Rejected',
            'description': 'Rejected by databricksadmin@contoso.com',
            'loc': 'eastus2euap',
            'vnet_name': self.create_random_name(prefix='vnet', length=12),
            'peering_name': self.create_random_name(prefix='peering', length=12),
            'subnet_name': self.create_random_name(prefix='subnet', length=12),
            'npe_name': self.create_random_name(prefix='npe', length=12),
            'nsg_name': self.create_random_name(prefix='nsg', length=12),
        })
        self.cmd('az network nsg create -g {rg} -n {nsg_name}')

        vnet = self.cmd('az network vnet create -g {rg} -n {vnet_name} -l {loc} --nsg {nsg_name}', checks=[
            self.check('newVNet.location', '{loc}'),
            self.check('newVNet.name', '{vnet_name}'),
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()
        self.kwargs['vnet_id'] = vnet['newVNet']['id']

        self.cmd('az network vnet subnet create -g {rg} '
                 '--vnet-name {vnet_name} '
                 '-n private-subnet '
                 '--address-prefixes 10.0.1.0/24 '
                 '--disable-private-endpoint-network-policies false '
                 '--nsg {nsg_name} '
                 '--delegations "Microsoft.Databricks/workspaces"')

        self.cmd('az network vnet subnet create -g {rg} '
                 '--vnet-name {vnet_name} -n public-subnet '
                 '--address-prefixes 10.0.64.0/24 '
                 '--disable-private-endpoint-network-policies false '
                 '--nsg {nsg_name} '
                 '--delegations "Microsoft.Databricks/workspaces"')

        self.cmd('az network vnet subnet create -g {rg} '
                 '-n {subnet_name} '
                 '--vnet-name {vnet_name} '
                 '--disable-private-endpoint-network-policies true '
                 '--address-prefixes 10.0.32.0/24 '
                 '--nsg {nsg_name}')

        databricks_workspace = self.cmd('az databricks workspace create -g {rg} '
                                        '-l {loc} '
                                        '-n {workspace_name} '
                                        '--private-subnet private-subnet '
                                        '--public-subnet public-subnet '
                                        '--vnet {vnet_id} --sku premium',
                                        checks=[self.check('location', '{loc}'),
                                                self.check('name', '{workspace_name}'),
                                                self.check('provisioningState', 'Succeeded')]).get_output_in_json()

        plr = self.cmd('az databricks workspace private-link-resource list -g {rg} --workspace-name {workspace_name}',
                       checks=self.check('length(@)', 2)).get_output_in_json()

        self.kwargs['group_id'] = plr[0]['properties']['groupId']
        self.kwargs['dw_id'] = databricks_workspace['id']

        self.cmd('az databricks workspace private-link-resource show -g {rg} '
                 '--workspace-name {workspace_name} '
                 '-n {group_id}',
                 checks=self.check('name', '{group_id}'))

        self.cmd('az network private-endpoint create -g {rg} '
                 '-n {npe_name} '
                 '--vnet-name {vnet_name} '
                 '--subnet {subnet_name} '
                 '--private-connection-resource-id "{dw_id}" '
                 '--connection-name {npe_name} '
                 '--group-id databricks_ui_api '
                 '-l {loc}',
                 checks=self.check('name', '{npe_name}'))

        self.cmd('az databricks workspace private-endpoint-connection create -g {rg} '
                 '--workspace-name {workspace_name} '
                 '-n {npe_name} '
                 '--status {status} '
                 '--description "{description}"',
                 checks=[self.check('name', '{npe_name}'),
                         self.check('properties.privateLinkServiceConnectionState.status', '{status}'),
                         self.check('properties.privateLinkServiceConnectionState.description', '{description}'),
                         self.check('properties.provisioningState', "Succeeded"),
                         self.check('type', "Microsoft.Databricks/workspaces/privateEndpointConnections")])

        self.cmd('az databricks workspace private-endpoint-connection list -g {rg} '
                 '--workspace-name {workspace_name} ',
                 checks=[self.check('length(@)', 1)])

        self.cmd('az databricks workspace private-endpoint-connection show -g {rg} '
                 '--workspace-name {workspace_name} '
                 '-n {npe_name}',
                 checks=[self.check('name', '{npe_name}')])

        self.cmd('az databricks workspace private-endpoint-connection delete -g {rg} '
                 '--workspace-name {workspace_name} '
                 '-n {npe_name}',
                 checks=[])

        self.cmd('az databricks workspace outbound-endpoint list -g {rg} --workspace-name {workspace_name}',
                 checks=self.check('type(@)', 'array'))

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_v3', location="eastus2euap")
    def test_databricks_v3(self, resource_group):
        self.kwargs.update({
            'workspace_name': self.create_random_name(prefix='wn', length=12),
            'loc': 'eastus2euap',
            'vnet_name': self.create_random_name(prefix='vnet', length=12),
            'subnet_name': self.create_random_name(prefix='subnet', length=12),
            'nsg_name': self.create_random_name(prefix='nsg', length=12),
        })
        self.cmd('az network nsg create -g {rg} -n {nsg_name}')

        vnet = self.cmd('az network vnet create -g {rg} -n {vnet_name} -l {loc} --nsg {nsg_name}', checks=[
            self.check('newVNet.location', '{loc}'),
            self.check('newVNet.name', '{vnet_name}'),
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()
        self.kwargs['vnet_id'] = vnet['newVNet']['id']

        self.cmd('az network vnet subnet create -g {rg} '
                 '--vnet-name {vnet_name} '
                 '-n private-subnet '
                 '--address-prefixes 10.0.1.0/24 '
                 '--disable-private-endpoint-network-policies false '
                 '--nsg {nsg_name} '
                 '--delegations "Microsoft.Databricks/workspaces"')

        self.cmd('az network vnet subnet create -g {rg} '
                 '--vnet-name {vnet_name} -n public-subnet '
                 '--address-prefixes 10.0.64.0/24 '
                 '--disable-private-endpoint-network-policies false '
                 '--nsg {nsg_name} '
                 '--delegations "Microsoft.Databricks/workspaces"')

        self.cmd('az network vnet subnet create -g {rg} '
                 '-n {subnet_name} '
                 '--vnet-name {vnet_name} '
                 '--disable-private-endpoint-network-policies true '
                 '--address-prefixes 10.0.32.0/24 '
                 '--nsg {nsg_name}')

        self.cmd('az databricks workspace create -g {rg} '
                 '-l {loc} '
                 '-n {workspace_name} '
                 '--private-subnet private-subnet '
                 '--public-subnet public-subnet '
                 '--vnet {vnet_id} --sku premium',
                 checks=[self.check('location', '{loc}'),
                         self.check('name', '{workspace_name}'),
                         self.check('provisioningState', 'Succeeded')])

        self.cmd('az databricks workspace update -g {rg} '
                 '-n {workspace_name} '
                 '--public-network-access Disabled '
                 '--required-nsg-rules "NoAzureDatabricksRules" '
                 '--enable-no-public-ip true '
                 '--storage-account-sku-name Standard_GRS',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('publicNetworkAccess', 'Disabled'),
                         self.check('parameters.enableNoPublicIp.value', True),
                         self.check('requiredNsgRules', 'NoAzureDatabricksRules'),
                         self.check('parameters.storageAccountSkuName.value', 'Standard_GRS')])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_create_v1')
    def test_databricks_create_v1(self):
        self.kwargs.update({
            'workspace_name': self.create_random_name(prefix='workspace', length=16),
            'key_vault': "https://test-vault-name.vault.azure.net/",
            'key_name': "test-cmk-key",
            'key_version': "00000000000000000000000000000000"
        })

        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location "eastus" '
                 '--sku premium '
                 '--enable-no-public-ip '
                 '--disk-key-auto-rotation True '
                 '--disk-key-vault {key_vault} '
                 '--disk-key-name {key_name} '
                 '--disk-key-version {key_version} ',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium'),
                         self.check('parameters.enableNoPublicIp.value', True),
                         self.check('encryption.entities.managedDisk.keyVaultProperties.keyVaultUri', '{key_vault}'),
                         self.check('encryption.entities.managedDisk.keyVaultProperties.keyName', '{key_name}'),
                         self.check('encryption.entities.managedDisk.keyVaultProperties.keyVersion', '{key_version}'),
                         self.check('encryption.entities.managedDisk.rotationToLatestKeyVersionEnabled', True)])
        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_create_v2')
    @KeyVaultPreparer(location='eastus')
    def test_databricks_create_v2(self, resource_group, key_vault):
        self.kwargs.update({
            'kv': key_vault,
            'workspace_name': self.create_random_name(prefix='workspace', length=16),
            'oid': "09e25313-21e0-4033-bd7c-179e9e990c73",
            'key_name': 'testkey'
        })
        keyvault = self.cmd('az keyvault show -n {kv} -g {rg}').get_output_in_json()
        self.cmd('az keyvault set-policy -n {kv} --object-id {oid} -g {rg} '
                 '--key-permissions get wrapKey unwrapKey ')

        key = self.cmd('az keyvault key create -n {key_name} --vault-name {kv}').get_output_in_json()
        key_version = key['key']['kid'].rsplit('/', 1)[1]

        self.kwargs.update({'key_version': key_version,
                            'key_vault': keyvault['properties']['vaultUri']})
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location "eastus" '
                 '--sku premium '
                 '--enable-no-public-ip '
                 '--managed-services-key-vault {key_vault} '
                 '--managed-services-key-name {key_name} '
                 '--managed-services-key-version {key_version}',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium'),
                         self.check('encryption.entities.managedServices.keyVaultProperties.keyName', '{key_name}'),
                         self.check('encryption.entities.managedServices.keyVaultProperties.keyVaultUri', '{key_vault}'),
                         self.check('encryption.entities.managedServices.keyVaultProperties.keyVersion', '{key_version}')])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_update_v1')
    def test_databricks_update_v1(self):
        self.kwargs.update({
            'workspace_name': self.create_random_name(prefix='workspace', length=16),
            'key_vault': "https://test-vault-name.vault.azure.net/",
            'key_name': "test-cmk-key",
            'key_version': "00000000000000000000000000000000",
        })
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location "eastus" '
                 '--sku premium '
                 '--enable-no-public-ip '
                 '--prepare-encryption',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium'),
                         self.check('parameters.enableNoPublicIp.value', True)])
        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--disk-key-auto-rotation True '
                 '--disk-key-vault {key_vault} '
                 '--disk-key-name {key_name} '
                 '--disk-key-version {key_version}',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('encryption.entities.managedDisk.keyVaultProperties.keyVaultUri', '{key_vault}'),
                         self.check('encryption.entities.managedDisk.keyVaultProperties.keyName', '{key_name}'),
                         self.check('encryption.entities.managedDisk.keyVaultProperties.keyVersion', '{key_version}'),
                         self.check('encryption.entities.managedDisk.rotationToLatestKeyVersionEnabled', True)])
        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_update_v2')
    @KeyVaultPreparer(location='eastus')
    def test_databricks_update_v2(self, resource_group, key_vault):
        self.kwargs.update({
            'kv': key_vault,
            'workspace_name': self.create_random_name(prefix='workspace', length=16),
            'oid': "09e25313-21e0-4033-bd7c-179e9e990c73",
            'key_name': 'testkey'
        })
        self.cmd('az databricks workspace create '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--location eastus '
                 '--prepare-encryption '
                 '--sku premium '
                 '--enable-no-public-ip')
        keyvault = self.cmd('az keyvault show -n {kv} -g {rg}').get_output_in_json()
        self.cmd('az keyvault set-policy -n {kv} --object-id {oid} -g {rg} '
                 '--key-permissions get wrapKey unwrapKey ')

        key = self.cmd('az keyvault key create -n {key_name} --vault-name {kv}').get_output_in_json()
        key_version = key['key']['kid'].rsplit('/', 1)[1]

        self.kwargs.update({'key_version': key_version,
                            'key_vault': keyvault['properties']['vaultUri']})
        self.cmd('az databricks workspace update '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '--managed-services-key-vault {key_vault} '
                 '--managed-services-key-name {key_name} '
                 '--managed-services-key-version {key_version}',
                 checks=[self.check('name', '{workspace_name}'),
                         self.check('sku.name', 'premium'),
                         self.check('encryption.entities.managedServices.keyVaultProperties.keyName', '{key_name}'),
                         self.check('encryption.entities.managedServices.keyVaultProperties.keyVaultUri', '{key_vault}'),
                         self.check('encryption.entities.managedServices.keyVaultProperties.keyVersion', '{key_version}')])

        self.cmd('az databricks workspace delete '
                 '--resource-group {rg} '
                 '--name {workspace_name} '
                 '-y',
                 checks=[])


class DatabricksVNetPeeringScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=10240)
    @ResourceGroupPreparer(name_prefix='cli_test_databricks_vnet')
    def test_databricks_vnet_peering(self, resource_group):
        self.kwargs.update({
            'workspace_name': self.create_random_name(prefix='databricks', length=24),
            'peering_name': self.create_random_name(prefix='peering', length=24),
            'peering_name_network': self.create_random_name(prefix='peering_n', length=24),
            'vnet_name': self.create_random_name(prefix='vnet', length=24),
            'loc': 'westus'
        })

        vnet = self.cmd('az network vnet create -g {rg} -n {vnet_name} -l {loc}', checks=[
            self.check('newVNet.location', '{loc}'),
            self.check('newVNet.name', '{vnet_name}'),
            self.check('newVNet.provisioningState', 'Succeeded')
        ]).get_output_in_json()
        self.kwargs['vnet_id'] = vnet['newVNet']['id']

        self.cmd('az databricks workspace create -l {loc} -n {workspace_name} -g {rg} --sku standard', checks=[
            self.check('location', '{loc}'),
            self.check('name', '{workspace_name}'),
            self.check('provisioningState', 'Succeeded')
        ])

        # use vnet name to create
        self.cmd('az databricks workspace vnet-peering create -n {peering_name} --workspace-name {workspace_name} -g {rg} --remote-vnet {vnet_name}', checks=[
            self.check('allowForwardedTraffic', False),
            self.check('allowGatewayTransit', False),
            self.check('useRemoteGateways', False),
            self.check('allowVirtualNetworkAccess', True),
            self.check('name', '{peering_name}'),
            self.check('remoteVirtualNetwork.id', '{vnet_id}'),
            self.check('peeringState', 'Initiated')
        ])
        self.cmd('az databricks workspace vnet-peering delete -n {peering_name} --workspace-name {workspace_name} -g {rg}')

        # user vnet id to create
        peering = self.cmd('az databricks workspace vnet-peering create -n {peering_name} --workspace-name {workspace_name} -g {rg} --remote-vnet {vnet_id}', checks=[
            self.check('allowForwardedTraffic', False),
            self.check('allowGatewayTransit', False),
            self.check('useRemoteGateways', False),
            self.check('allowVirtualNetworkAccess', True),
            self.check('name', '{peering_name}'),
            self.check('remoteVirtualNetwork.id', '{vnet_id}'),
            self.check('peeringState', 'Initiated')
        ]).get_output_in_json()

        self.kwargs['peering_id'] = peering['id']
        self.kwargs['databricks_vnet_id'] = peering['databricksVirtualNetwork']['id']

        self.cmd('az databricks workspace vnet-peering list --workspace-name {workspace_name} -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{peering_name}')
        ])
        self.cmd('az databricks workspace vnet-peering show -n {peering_name} --workspace-name {workspace_name} -g {rg}', checks=[
            self.check('allowForwardedTraffic', False),
            self.check('allowGatewayTransit', False),
            self.check('useRemoteGateways', False),
            self.check('allowVirtualNetworkAccess', True),
            self.check('name', '{peering_name}'),
            self.check('remoteVirtualNetwork.id', '{vnet_id}')
        ])

        self.cmd('az databricks workspace vnet-peering update -n {peering_name} --workspace-name {workspace_name} -g {rg} --allow-gateway-transit --allow-virtual-network-access false', checks=[
            self.check('allowForwardedTraffic', False),
            self.check('allowGatewayTransit', True),
            self.check('useRemoteGateways', False),
            self.check('allowVirtualNetworkAccess', False),
            self.check('name', '{peering_name}')
        ])

        self.cmd('az databricks workspace vnet-peering update -n {peering_name} --workspace-name {workspace_name} -g {rg} --allow-gateway-transit false', checks=[
            self.check('allowForwardedTraffic', False),
            self.check('allowGatewayTransit', False),
            self.check('useRemoteGateways', False),
            self.check('allowVirtualNetworkAccess', False),
            self.check('name', '{peering_name}')
        ])

        # network side init
        self.cmd('az network vnet peering create -g {rg} -n {peering_name_network} --vnet-name {vnet_name} --remote-vnet {databricks_vnet_id}', checks=[
            self.check('name', '{peering_name_network}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('peeringState', 'Connected')
        ])

        self.cmd('az databricks workspace vnet-peering show -n {peering_name} --workspace-name {workspace_name} -g {rg}', checks=[
            self.check('peeringState', 'Connected')  # peering established
        ])

        self.cmd('az network vnet peering delete -g {rg} -n {peering_name_network} --vnet-name {vnet_name}')
        self.cmd('az databricks workspace vnet-peering show -n {peering_name} --workspace-name {workspace_name} -g {rg}', checks=[
            self.check('peeringState', 'Disconnected')  # peering disconnected
        ])

        # delete the peering
        self.cmd('az databricks workspace vnet-peering delete -n {peering_name} --workspace-name {workspace_name} -g {rg}')
        self.cmd('az databricks workspace vnet-peering list --workspace-name {workspace_name} -g {rg}', checks=[
            self.check('length(@)', 0)
        ])
