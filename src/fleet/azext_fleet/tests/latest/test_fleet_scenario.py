# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class FleetScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='fleet-cli-', location='centraluseuap', random_name_length=15)
    def test_fleet(self):

        self.kwargs.update({
            'name': self.create_random_name(prefix='fleet-', length=15),
            'member_name': self.create_random_name(prefix='fleet-mc-', length=15),
            'dns_prefix': 'dns-prefix',
        })

        self.cmd('fleet create -g {rg} -n {name} --dns-name-prefix {dns_prefix}', checks=[
            self.check('name', '{name}')
        ])

        self.cmd('fleet credentials list -g {rg} -n {name} --overwrite-existing')

        mc_id = self.cmd('aks create -g {rg} -n {member_name}', checks=[
            self.check('name', '{member_name}')
        ]).get_output_in_json()['id']

        self.kwargs.update({
            'mc_id': mc_id,
        })

        self.cmd('fleet member join -g {rg} -n {name} --member-cluster-id {mc_id}', checks=[
            self.check('name', '{member_name}'),
            self.check('clusterResourceId', '{mc_id}')
        ])

        fleet_members = self.cmd('fleet member list -g {rg} -n {name}').get_output_in_json()
        self.assertEqual(len(fleet_members), 1)
        
        self.cmd('fleet member remove -g {rg} -n {name} --member-name {member_name}')

        self.cmd('fleet delete -g {rg} -n {name}')
