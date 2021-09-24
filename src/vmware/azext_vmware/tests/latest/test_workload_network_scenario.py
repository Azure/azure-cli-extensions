# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

class VmwareWorkloadNetworkScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareWorkloadNetworkScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_workload_network')
    def test_vmware_workload_network(self):
        self.kwargs.update({
            'privatecloud': 'cloud1',
            'dhcp_id': 'dhcp1',
            'display_name': 'testDisplayName',
            'revision': '1',
            'server_address': '40.1.5.1/24',
            'lease_time': '86400',
            'server_addresses': '40.1.5.1/24',
            'dns_service_id': 'dnsService1',
            'dns_service_ip': '5.5.5.5',
            'default_dns_zone': 'defaultDnsZone1',
            'fqdn_zones': 'fqdnZone1',
            'log_level': 'INFO',
            'dns_zone_id': 'dnsZone1',
            'domain': 'domain1',
            'dns_server_ips': '1.1.1.1',
            'source_ip': '8.8.8.8',
            'dns_services': '1',
            'port_mirroring_id': 'portMirroring1',
            'direction': 'BIDIRECTIONAL',
            'source': 'vmGroup1',
            'destination': 'vmGroup2'
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

        dnsServiceList = self.cmd('az vmware workload-network dns-service list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(dnsServiceList), 1, 'count expected to be 1')

        dnsServiceGet = self.cmd('az vmware workload-network dns-service show --resource-group {rg} --private-cloud {privatecloud} --dns-service-id {dns_service_id}').get_output_in_json()
        self.assertEqual(dnsServiceGet['name'], 'portMirroring1')

        dnsServiceCreate = self.cmd('az vmware workload-network dns-service create --resource-group {rg} --private-cloud {privatecloud} --dns-service-id {dns_service_id} --display-name {display_name} --dns-service-ip {dns_service_ip} --default-dns-zone {default_dns_zone} --fqdn-zones {fqdn_zones} --log-level {log_level} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsServiceCreate['name'], 'dnsService1')

        dnsServiceUpdate = self.cmd('az vmware workload-network dns-service update --resource-group {rg} --private-cloud {privatecloud} --dns-service-id {dns_service_id} --display-name {display_name} --dns-service-ip {dns_service_ip} --default-dns-zone {default_dns_zone} --fqdn-zones {fqdn_zones} --log-level {log_level} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsServiceUpdate['name'], 'dnsService1')

        dnsServiceDelete = self.cmd('az vmware workload-network dns-service delete --resource-group {rg} --private-cloud {privatecloud} --dns-service-id {dns_service_id}').output
        self.assertEqual(len(dnsServiceDelete), 0)

        dnsZoneList = self.cmd('az vmware workload-network dns-zone list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(dnsZoneList), 1, 'count expected to be 1')

        dnsZoneGet = self.cmd('az vmware workload-network dns-zone show --resource-group {rg} --private-cloud {privatecloud} --dns-zone-id {dns_zone_id}').get_output_in_json()
        self.assertEqual(dnsZoneGet['name'], 'portMirroring1')

        dnsZoneCreate = self.cmd('az vmware workload-network dns-zone create --resource-group {rg} --private-cloud {privatecloud} --dns-zone-id {dns_zone_id} --display-name {display_name} --domain {domain} --dns-server-ips {dns_server_ips} --source-ip {source_ip} --dns-services {dns_services} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsZoneCreate['name'], 'dnsZone1')

        dnsZoneUpdate = self.cmd('az vmware workload-network dns-zone update --resource-group {rg} --private-cloud {privatecloud} --dns-zone-id {dns_zone_id} --display-name {display_name} --domain {domain} --dns-server-ips {dns_server_ips} --source-ip {source_ip} --dns-services {dns_services} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsZoneUpdate['name'], 'dnsZone1')

        dnsZoneDelete = self.cmd('az vmware workload-network dns-zone delete --resource-group {rg} --private-cloud {privatecloud} --dns-zone-id {dns_zone_id}').output
        self.assertEqual(len(dnsZoneDelete), 0)

        portMirroringList = self.cmd('az vmware workload-network port-mirroring list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(portMirroringList), 1, 'count expected to be 1')

        portMirroringGet = self.cmd('az vmware workload-network port-mirroring show --resource-group {rg} --private-cloud {privatecloud} --port-mirroring-id {port_mirroring_id}').get_output_in_json()
        self.assertEqual(portMirroringGet['name'], 'portMirroring1')

        # Uncomment these unit tests once swagger is fixed

        # portMirroringCreate = self.cmd('az vmware workload-network port-mirroring create --resource-group {rg} --private-cloud {privatecloud} --port-mirroring-id {port_mirroring_id} --display-name {display_name} --direction {direction} --source {source} --destination {destination} --revision {revision}').get_output_in_json()
        # self.assertEqual(portMirroringCreate['name'], 'portMirroring1')

        # portMirroringUpdate = self.cmd('az vmware workload-network port-mirroring update --resource-group {rg} --private-cloud {privatecloud} --port-mirroring-id {port_mirroring_id} --display-name {display_name} --direction {direction} --source {source} --destination {destination} --revision {revision}').get_output_in_json()
        # self.assertEqual(portMirroringUpdate['name'], 'portMirroring1')

        portMirroringDelete = self.cmd('az vmware workload-network port-mirroring delete --resource-group {rg} --private-cloud {privatecloud} --port-mirroring-id {port_mirroring_id}').output
        self.assertEqual(len(portMirroringDelete), 0)
