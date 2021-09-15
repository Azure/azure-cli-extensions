# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class VmwareDhcpScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareDhcpScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_dhcp')
    def test_vmware_dhcp(self):
        self.kwargs.update({
            'privatecloud': 'cloud1',
            'dhcp_id': 'dhcp1',
            'display_name': 'dhcpConfigurations1',
            'revision': '1',
            'server_address': '40.1.5.1/24',
            'lease_time': '86400',
            'server_addresses': '40.1.5.1/24'
        })
        
        count = len(self.cmd('az vmware workload-network dhcp list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        dhcpShow = self.cmd('az vmware workload-network dhcp show --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id}').get_output_in_json()
        self.assertEqual(dhcpShow['name'], 'dhcp1')

        dhcpRelayCreate = self.cmd('az vmware workload-network dhcp relay create --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id} --display-name {display_name} --revision {revision} --server-addresses {server_addresses}').get_output_in_json()
        self.assertEqual(dhcpRelayCreate['name'], 'dhcp1')

        dhcpRelayDelete = self.cmd('az vmware workload-network dhcp relay delete --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id}').output
        self.assertEqual(len(dhcpRelayDelete), 0)

        dhcpRelayUpdate = self.cmd('az vmware workload-network dhcp relay update --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id} --display-name {display_name} --revision {revision} --server-addresses {server_addresses}').get_output_in_json()
        self.assertEqual(dhcpRelayUpdate['name'], 'dhcp1')

        dhcpServerCreate = self.cmd('az vmware workload-network dhcp server create --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id} --display-name {display_name} --revision {revision} --server-address {server_address} --lease-time {lease_time}').get_output_in_json()
        self.assertEqual(dhcpServerCreate['name'], 'dhcp1')

        dhcpServerDelete = self.cmd('az vmware workload-network dhcp server delete --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id}').output
        self.assertEqual(len(dhcpServerDelete), 0)

        dhcpServerUpdate = self.cmd('az vmware workload-network dhcp server update --resource-group {rg} --private-cloud {privatecloud} --dhcp-id {dhcp_id} --display-name {display_name} --revision {revision} --server-address {server_address} --lease-time {lease_time}').get_output_in_json()
        self.assertEqual(dhcpServerUpdate['name'], 'dhcp1')
