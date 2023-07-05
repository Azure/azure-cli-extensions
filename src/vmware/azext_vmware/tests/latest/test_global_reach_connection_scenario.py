# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareGlobalReachConnectionScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareGlobalReachConnectionScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_hcx')
    def test_vmware_global_reach_connection(self):
        self.kwargs.update({
            'loc': 'westcentralus',
            'privatecloud': 'cloud1',
            'global_reach_connection': 'connection1',
            'peer_express_route_circuit': '/subscriptions/12341234-1234-1234-1234-123412341234/resourceGroups/mygroup/providers/Microsoft.Network/expressRouteCircuits/mypeer',
            'authorization_key': '01010101-0101-0101-0101-010101010101',
            'express_route_id': '/subscriptions/{subscription-id}/resourceGroups/tnt13-41a90db2-9d5e-4bd5-a77a-5ce7b58213d6-eastus2/providers/Microsoft.Network/expressroutecircuits/tnt13-41a90db2-9d5e-4bd5-a77a-5ce7b58213d6-eastus2-xconnect'
        })

        self.cmd('az vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 4 --network-block 192.168.48.0/22 --nsxt-password 5rqdLj4GF3cePUe6 --vcenter-password UpfBXae9ZquZSDXk --accept-eula')

        count = len(self.cmd('az vmware global-reach-connection list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        rsp = self.cmd('az vmware global-reach-connection create -g {rg} -c {privatecloud} -n {global_reach_connection} --peer-express-route-circuit {peer_express_route_circuit} --authorization-key {authorization_key} --express-route-id {express_route_id}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/globalReachConnections')
        self.assertEqual(rsp['name'], self.kwargs.get('global_reach_connection'))

        count = len(self.cmd('az vmware global-reach-connection list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        self.cmd('vmware global-reach-connection show -g {rg} -c {privatecloud} -n {global_reach_connection}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/globalReachConnections')
        self.assertEqual(rsp['name'], self.kwargs.get('global_reach_connection'))

        rsp = self.cmd('vmware global-reach-connection delete -g {rg} -c {privatecloud} -n {global_reach_connection} --yes').output
        self.assertEqual(len(rsp), 0)

        count = len(self.cmd('az vmware global-reach-connection list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')
