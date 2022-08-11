# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class FleetScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='fleet-cli-', location='centraluseuap', random_name_length=15)
    def test_fleet(self):

        self.kwargs.update({
            'name': self.create_random_name(prefix='fleet-', length=15),
            'member_name': self.create_random_name(prefix='fleet-mc-', length=15),
            'dns_prefix': 'dns-prefix',
        })

        fleet_create = self.cmd('fleet create -g {rg} -n {name} --dns-name-prefix {dns_prefix}', checks=[
            self.check('name', '{name}')
        ])
        print(fleet_create)

        mc = self.cmd('aks create -g {rg} -n {member_name}', checks=[
            self.check('name', '{member_name}')
        ]).get_output_in_json()
        print(mc)
        mc_id = mc['id']

        self.kwargs.update({
            'mc_id': mc_id,
        })

        fleet_member_join = self.cmd('fleet member join -g {rg} -n {name} --member-cluster-id {mc_id}', checks=[
            self.check('name', '{member_name}'),
            self.check('clusterResourceId', '{mc_id}')
        ])
        print(fleet_member_join)

        fleet_list1 = self.cmd('fleet member list -g {rg} -n {name}').get_output_in_json()
        print(fleet_list1)
        
        fleet_member_remove = self.cmd('fleet member remove -g {rg} -n {name} --member-name {member_name}', checks=[
            self.check('name', '{name}'),
            self.check('clusterResourceId', '{mc_id}')
        ])
        print(fleet_member_remove)
        
        fleet_list2 = self.cmd('fleet member list -g {rg} -n {name}').get_output_in_json()
        print(fleet_list2)
        self.assertTrue(len(fleet_list2), len(fleet_list1) - 1)

        fleet_delete = self.cmd('fleet delete -g {rg} -n {name}')
        print(fleet_delete)