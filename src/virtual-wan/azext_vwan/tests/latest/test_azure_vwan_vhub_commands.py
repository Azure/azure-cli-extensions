# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck, NoneCheck,
                               api_version_constraint)


class AzureVWanVHubScenario(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_route_table')
    def test_azure_vwan_vhub_basic_scenario(self, resource_group):
        self.kwargs.update({
            'vwan': 'clitestvwan',
            'vhub': 'clitestvhub',
            'rg': resource_group
        })

        self.cmd('network vwan create -n {vwan} -g {rg} --type Standard')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l SouthCentralUS --sku Standard')

        self.cmd('network vhub update -g {rg} -n {vhub} --sku Basic')
        self.cmd('network vwan update -g {rg} -n {vwan} --type Basic')
