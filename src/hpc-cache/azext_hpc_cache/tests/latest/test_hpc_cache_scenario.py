# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import mock

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageCacheScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_test_hpc_cache')
    def test_hpc_cache(self, resource_group):

        self.kwargs.update({
            'loc': 'eastus',
            'vnet_name': self.create_random_name(prefix='vnetname', length=24),
            'cache_name': self.create_random_name(prefix='cachename', length=24),
            'storage_name': self.create_random_name(prefix='storagename', length=24),
            'container_name': self.create_random_name(prefix='containername', length=24)
        })

        storage_id = self.cmd('az storage account create -n {storage_name} -g {rg} -l {loc} '
                              '--sku Standard_LRS --https-only').get_output_in_json()['id']
        self.kwargs.update({'storage_id': storage_id})

        self.cmd('az storage container create -n {container_name} --account-name {storage_name}')

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('az role assignment create --assignee  677a61e9-086e-4f13-986a-11aaedc31416 '
                     '--role "Storage Account Contributor" --scope {}'.format(storage_id))

        vnet_id = self.cmd('az network vnet create -g {rg} -n {vnet_name} -l {loc} --address-prefix 10.7.0.0/16 '
                           '--subnet-name default --subnet-prefix 10.7.0.0/24').get_output_in_json()['newVNet']['id']
        self.kwargs.update({'vnet_id': vnet_id})

        self.cmd('az hpc-cache create '
                 '--resource-group {rg} '
                 '--name {cache_name} '
                 '--location {loc} '
                 '--cache-size-gb "3072" '
                 '--subnet "{vnet_id}/subnets/default" '
                 '--sku-name "Standard_2G"',
                 checks=[
                     self.check('name', '{cache_name}')
                 ])

        self.cmd('az hpc-cache wait --resource-group {rg} --name {cache_name} --created', checks=[])

        self.cmd('az hpc-cache upgrade-firmware --resource-group {rg} --name {cache_name}', checks=[])

        from msrestazure.azure_exceptions import CloudError
        with self.assertRaisesRegexp(CloudError, 'ResourceNotFound'):
            self.cmd('az hpc-cache update '
                     '--resource-group {rg} '
                     '--name "{cache_name}123" '
                     '--tags key=val key2=val2',
                     checks=[
                         self.check('name', '{cache_name}'),
                         self.check('tags', {'key': 'val', 'key2': 'val2'})
                     ])

        self.cmd('az hpc-cache update '
                 '--resource-group {rg} '
                 '--name {cache_name} '
                 '--tags key=val key2=val2',
                 checks=[
                     self.check('name', '{cache_name}'),
                     self.check('tags', {'key': 'val', 'key2': 'val2'})
                 ])

        self.cmd('az hpc-cache show --resource-group {rg} --name {cache_name}',
                 checks=[self.check('name', '{cache_name}')])

        self.cmd('az hpc-cache usage-model list --query "[?modelName==\'WRITE_AROUND\']" ',
                 checks=[self.check('length(@)', 1)])

        self.cmd('az hpc-cache list --query "[?name==\'{cache_name}\']" ',
                 checks=[self.check('length(@)', 1)])

        self.cmd('az hpc-cache skus list --query "[?name==Standard_8G]" ',
                 checks=[self.check("length(@) != '0'", True)])

        self.cmd('az hpc-cache flush --resource-group {rg} --name {cache_name}',
                 checks=[self.check('status', 'Succeeded')])

        self.cmd('az hpc-cache stop --resource-group {rg} --name {cache_name}',
                 checks=[self.check('status', 'Succeeded')])

        self.cmd('az hpc-cache start --resource-group {rg} --name {cache_name}',
                 checks=[self.check('status', 'Succeeded')])

        self.cmd('az hpc-cache delete --resource-group {rg} --name {cache_name}',
                 checks=[self.check('status', 'Succeeded')])

        self.cmd('az hpc-cache list --query "[?name==\'{cache_name}\']" ',
                 checks=[self.check('length(@)', 0)])

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_hpc_storage_target')
    def test_hpc_storage_target(self, resource_group):

        self.kwargs.update({
            'loc': 'eastus',
            'vnet_name': self.create_random_name(prefix='vnetname', length=24),
            'cache_name': self.create_random_name(prefix='cachename', length=24),
            'storage_name': self.create_random_name(prefix='storagename', length=24),
            'container_name': self.create_random_name(prefix='containername', length=24),
            'blob_target_name': self.create_random_name(prefix='blobtarget', length=24)
        })

        storage_id = self.cmd('az storage account create -n {storage_name} -g {rg} -l {loc} '
                              '--sku Standard_LRS --https-only').get_output_in_json()['id']
        self.kwargs.update({'storage_id': storage_id})

        self.cmd('az storage container create -n {container_name} --account-name {storage_name}')

        with mock.patch('azure.cli.command_modules.role.custom._gen_guid', side_effect=self.create_guid):
            self.cmd('az role assignment create --assignee  677a61e9-086e-4f13-986a-11aaedc31416 '
                     '--role "Storage Account Contributor" --scope {}'.format(storage_id))

        vnet_id = self.cmd('az network vnet create -g {rg} -n {vnet_name} -l {loc} --address-prefix 10.7.0.0/16 '
                           '--subnet-name default --subnet-prefix 10.7.0.0/24').get_output_in_json()['newVNet']['id']
        self.kwargs.update({'vnet_id': vnet_id})

        self.cmd('az hpc-cache create '
                 '--resource-group {rg} '
                 '--name {cache_name} '
                 '--location {loc} '
                 '--cache-size-gb "3072" '
                 '--subnet "{vnet_id}/subnets/default" '
                 '--sku-name "Standard_2G"',
                 checks=[
                     self.check('name', '{cache_name}')
                 ])

        self.cmd('az hpc-cache blob-storage-target add '
                 '--resource-group {rg} '
                 '--cache-name {cache_name} '
                 '--name {blob_target_name} '
                 '--storage-account "{storage_id}" '
                 '--container-name {container_name} --virtual-namespace-path "/test"',
                 checks=[
                     self.check('name', '{blob_target_name}')
                 ])

        self.cmd('az hpc-cache storage-target show '
                 '--resource-group {rg} '
                 '--cache-name {cache_name} '
                 '--name {blob_target_name}',
                 checks=[
                     self.check('name', '{blob_target_name}')
                 ])

        self.cmd('az hpc-cache storage-target list --resource-group {rg} --cache-name {cache_name} ',
                 checks=[self.check('length(@)', 1)])

        self.cmd('az hpc-cache storage-target remove '
                 '--resource-group {rg} '
                 '--cache-name {cache_name} '
                 '--name {blob_target_name}',
                 checks=[self.check('status', 'Succeeded')])

        self.cmd('az hpc-cache delete --resource-group {rg} --name {cache_name}',
                 checks=[self.check('status', 'Succeeded')])
