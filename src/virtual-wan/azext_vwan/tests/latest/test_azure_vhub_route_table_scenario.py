# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck, NoneCheck,
                               api_version_constraint)


class AzureVWanRouteTableScenario(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_azure_vwan_route_table')
    def test_azure_vwan_route_table(self, resource_group):
        self.kwargs.update({
            'vwan': 'testvwan',
            'vhub': 'myclitestvhub',
            'routetable': 'testroutetable',
            'rg': 1015
        })
        '''
        # workaround due to service limitation. It should be fixed in the future.
        self.cmd('network vwan create -n {vwan} -g {rg}')
        self.cmd('network vhub create -g {rg} -n {vhub} --vwan {vwan}  --address-prefix 10.0.0.0/24 -l SouthCentralUS')
        '''

        self.cmd('network vhub route-table create -n {routetable} -g {rg} --vhub-name {vhub} --connections All_Vnets --destination-type CIDR --destinations 10.4.0.0/16 10.6.0.0/16 --next-hop-type IPAddress --next-hops 10.0.0.68', checks=[
            self.check('name', self.kwargs['routetable'])
        ])
        self.cmd('network vhub route-table show -n {routetable} -g {rg} --vhub-name {vhub}', checks=[
            self.check('name', self.kwargs['routetable'])
        ])
        self.cmd('network vhub route-table list -g {rg} --vhub-name {vhub}', checks=[
            self.check('@[0].name', self.kwargs['routetable']),
            self.check('length(@)', 1)
        ])

        self.cmd('network vhub route-table update -n {routetable} -g {rg} --vhub-name {vhub} --connections All_Branches', checks=[
            self.check('attachedConnections[0]', 'All_Branches')
        ])

        self.cmd('network vhub route-table route add -n {routetable} -g {rg} --vhub-name {vhub} --destination-type Service --destinations Skype Sharepoint --next-hop-type IPAddress --next-hops "10.0.0.68"', checks=[
            self.check('length(@)', 2)
        ])

        self.cmd('network vhub route-table route remove -n {routetable} -g {rg} --vhub-name {vhub} --index 1', checks=[
            self.check("contains(@[0].destinations, 'Skype')", True),
            self.check("contains(@[0].destinations, 'Sharepoint')", True),
            self.check('length(@)', 1)
        ])

        self.cmd('network vhub route-table delete -n {routetable} -g {rg} --vhub-name {vhub}')
