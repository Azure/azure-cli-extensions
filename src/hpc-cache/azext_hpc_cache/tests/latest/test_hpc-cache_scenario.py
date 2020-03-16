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
        self.cmd('az storage account create -n {} -g {} -l eastus --sku Standard_LRS'.format(storage_name, resource_group))
        self.cmd('az network vnet create -g {} -n {}'.format(resource_group, vnet_name))
        subscription_id = self.current_subscription()
        self.cmd('az hpc-cache create '
                 '--resource-group {} '
                 '--name {} '
                 '--location "eastus" '
                 '--cache-size-gb "3072" '
                 '--subnet "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/default" '
                 '--sku-name "Standard_2G"'.format(resource_group, cache_name, subscription_id, resource_group, vnet_name),
                 checks=[])
        container_name = self.create_random_name(length=10)
        self.cmd('az storage container create -n {container_name} -g {rg} --account-name {storage_name}')
        self.cmd('az hpc-cache blob-storage-target create '
                 '--resource-group {} '
                 '--cache-name {} '
                 '--name "st1" '
                 '--storage-account "/subscriptions/{}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{}" '
                 '--container-name {} --virtual-namespace-path "/test"'.format(resource_group, cache_name,
                                                                               subscription_id, resource_group,
                                                                               storage_name, container_name),
                 checks=[])

        self.cmd('az hpc-cache storage-target show '
                 '--resource-group {rg} '
                 '--cache-name {cache_name} '
                 '--name "st1"',
                 checks=[])

        self.cmd('az hpc-cache show '
                 '--resource-group {rg} '
                 '--name "sc1"',
                 checks=[])

        self.cmd('az hpc-cache list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az hpc-cache usage-model list',
                 checks=[])

        self.cmd('az hpc-cache list',
                 checks=[])

        self.cmd('az hpc-cache skus list',
                 checks=[])

        self.cmd('az hpc-cache upgrade-firmware '
                 '--resource-group {rg} '
                 '--name "sc1"',
                 checks=[])

        self.cmd('az hpc-cache flush '
                 '--resource-group {rg} '
                 '--name {cache_name}',
                 checks=[])

        self.cmd('az hpc-cache start '
                 '--resource-group {rg} '
                 '--name {cache_name}',
                 checks=[])

        self.cmd('az hpc-cache stop '
                 '--resource-group {rg} '
                 '--name {cache_name}',
                 checks=[])

        self.cmd('az hpc-cache storage-target remove '
                 '--resource-group {rg} '
                 '--cache-name {cache_name} '
                 '--name "st1"',
                 checks=[])

        self.cmd('az hpc-cache delete '
                 '--resource-group {rg} '
                 '--name {cache_name}',
                 checks=[])
