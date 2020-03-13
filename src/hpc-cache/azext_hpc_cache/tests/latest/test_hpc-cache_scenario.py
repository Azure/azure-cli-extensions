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
    @StorageAccountPreparer(parameter_name='clihpcteststore')
    def test_hpc_cache(self, resource_group):
        vnet_name = self.create_random_name(prefix='cli', length=24)
        self.cmd('az network vnet create -g {rg} -n {vnet_name}')

        self.cmd('az hpc-cache create '
                 '--resource-group {rg} '
                 '--name "sc-cli-test" '
                 '--location "eastus" '
                 '--cache-size-gb "3072" '
                 '--subnet "/subscriptions/{{ subscription_id }}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/default" '
                 '--sku-name "Standard_2G"',
                 checks=[])

        self.cmd('az hpc-cache blob-storage-target create '
                 '--resource-group {rg} '
                 '--cache-name "sc1" '
                 '--name "st1" '
                 '--target-type "nfs3" '
                 '--nfs3-target "10.0.44.44" '
                 '--nfs3-usage-model "READ_HEAVY_INFREQ"',
                 checks=[])

        self.cmd('az hpc-cache storage-target show '
                 '--resource-group {rg} '
                 '--cache-name "sc1" '
                 '--name "st1"',
                 checks=[])

        self.cmd('az hpc-cache operation list',
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

        self.cmd('az hpc-cache operation list',
                 checks=[])

        self.cmd('az hpc-cache upgrade-firmware '
                 '--resource-group {rg} '
                 '--name "sc1"',
                 checks=[])

        self.cmd('az hpc-cache flush '
                 '--resource-group {rg} '
                 '--name "sc"',
                 checks=[])

        self.cmd('az hpc-cache start '
                 '--resource-group {rg} '
                 '--name "sc"',
                 checks=[])

        self.cmd('az hpc-cache stop '
                 '--resource-group {rg} '
                 '--name "sc"',
                 checks=[])

        self.cmd('az hpc-cache update '
                 '--resource-group {rg} '
                 '--name "sc1" '
                 '--location "westus" '
                 '--cache-size-gb "3072" '
                 '--subnet "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.Network/virtualNetworks/{{ virtual_network_name }}/subnets/{{ subnet_name }}" '
                 '--sku-name "Standard_2G"',
                 checks=[])

        self.cmd('az hpc-cache storage-target delete '
                 '--resource-group {rg} '
                 '--cache-name "sc1" '
                 '--name "st1"',
                 checks=[])

        self.cmd('az hpc-cache delete '
                 '--resource-group {rg} '
                 '--name "sc"',
                 checks=[])
