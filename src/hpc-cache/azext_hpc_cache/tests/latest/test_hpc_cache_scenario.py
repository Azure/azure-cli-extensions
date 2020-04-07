# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageCacheScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_hpc_cache')
    def test_hpc_cache(self, resource_group):
        vnet_name = self.create_random_name(prefix='cli', length=24)
        cache_name = self.create_random_name(prefix='cli', length=24)
        storage_name = self.create_random_name(prefix='cli', length=24)
        storage_id = self.cmd('az storage account create -n {} -g {} -l eastus --sku Standard_LRS --https-only'
                              .format(storage_name, resource_group)).get_output_in_json()['id']
        container_name = 'test'
        self.cmd('az storage container create -n {} --account-name {}'.format(container_name, storage_name))
        self.cmd('az role assignment create --assignee  677a61e9-086e-4f13-986a-11aaedc31416 '
                 '--role "Storage Account Contributor" --scope {}'.format(storage_id))
        vnet_id = self.cmd('az network vnet create -g {} -n {} -l eastus --address-prefix 10.7.0.0/16 '
                           '--subnet-name default --subnet-prefix 10.7.0.0/24'
                           .format(resource_group, vnet_name)).get_output_in_json()['newVNet']['id']
        self.cmd('az hpc-cache create '
                 '--resource-group {} '
                 '--name {} '
                 '--location "eastus" '
                 '--cache-size-gb "3072" '
                 '--subnet "{}/subnets/default" '
                 '--sku-name "Standard_2G"'.format(resource_group, cache_name, vnet_id, resource_group, vnet_name),
                 checks=[
                     self.check('name', cache_name)
                 ])

        self.cmd('az hpc-cache blob-storage-target add '
                 '--resource-group {} '
                 '--cache-name {} '
                 '--name "st1" '
                 '--storage-account "{}" '
                 '--container-name {} --virtual-namespace-path "/test"'.format(resource_group, cache_name,
                                                                               storage_id, container_name),
                 checks=[
                     self.check('name', 'st1')
                 ])

        self.cmd('az hpc-cache storage-target show '
                 '--resource-group {} '
                 '--cache-name {} '
                 '--name "st1"'.format(resource_group, cache_name)).get_output_in_json()

        self.cmd('az hpc-cache show '
                 '--resource-group {} '
                 '--name {}'.format(resource_group, cache_name)).get_output_in_json()

        self.cmd('az hpc-cache list '
                 '--resource-group {}'.format(resource_group),
                 checks=[
                     self.check('[0].name', cache_name)
                 ])

        self.cmd('az hpc-cache usage-model list',
                 checks=[])

        self.cmd('az hpc-cache list',
                 checks=[])

        self.cmd('az hpc-cache skus list',
                 checks=[])

        self.cmd('az hpc-cache stop '
                 '--resource-group {} '
                 '--name {}'.format(resource_group, cache_name),
                 checks=[])

        self.cmd('az hpc-cache start '
                 '--resource-group {} '
                 '--name {}'.format(resource_group, cache_name),
                 checks=[])

        self.cmd('az hpc-cache storage-target remove '
                 '--resource-group {} '
                 '--cache-name {} '
                 '--name "st1"'.format(resource_group, cache_name),
                 checks=[])

        self.cmd('az hpc-cache delete '
                 '--resource-group {} '
                 '--name {}'.format(resource_group, cache_name),
                 checks=[])
