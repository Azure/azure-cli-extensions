# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class FleetScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='fleet-cli-', location='centraluseuap', random_name_length=15)
    def test_fleet(self):

        self.kwargs.update({
            'fleet_name': self.create_random_name(prefix='fleet-', length=15),
            'member_name': self.create_random_name(prefix='fleet-mc-', length=15),
        })

        self.cmd('fleet create -g {rg} -n {fleet_name}', checks=[
            self.check('name', '{fleet_name}')
        ])

        self.cmd('fleet patch -g {rg} -n {fleet_name} --tags foo=doo', checks=[
            self.check('name', '{fleet_name}'),
            self.check('tags.foo', 'doo')
        ])

        self.cmd('fleet get -g {rg} -n {fleet_name}', checks=[
            self.check('name', '{fleet_name}')
        ])

        self.cmd('fleet list-by-resource-group -g {rg}', checks=[
            self.check('length([])', 1)
        ])

        self.cmd('fleet list-by-subscription', checks=[
            self.greater_than('length([])', 0)
        ])
        
        self.cmd('fleet get-credentials -g {rg} -n {fleet_name} --overwrite-existing')

        mc_id = self.cmd('aks create -g {rg} -n {member_name}', checks=[
            self.check('name', '{member_name}')
        ]).get_output_in_json()['id']

        self.kwargs.update({
            'mc_id': mc_id,
        })

        self.cmd('fleet member join -g {rg} --fleet-name {fleet_name} -n {member_name} --member-cluster-id {mc_id}', checks=[
            self.check('name', '{member_name}'),
            self.check('clusterResourceId', '{mc_id}')
        ])

        self.cmd('fleet member list -g {rg} --fleet-name {fleet_name}', checks=[
            self.check('length([])', 1)
        ])

        self.cmd('fleet member get -g {rg} --fleet-name {fleet_name} -n {member_name}', checks=[
            self.check('name', '{member_name}')
        ])
        
        self.cmd('fleet member remove -g {rg} --fleet-name {fleet_name} -n {member_name}')

        self.cmd('fleet delete -g {rg} -n {fleet_name}')
