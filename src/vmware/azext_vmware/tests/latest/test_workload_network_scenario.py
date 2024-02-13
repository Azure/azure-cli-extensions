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
            'dhcp': 'dhcp1',
            'display_name': 'testDisplayName',
            'revision': '1',
            'server_address': '40.1.5.1/24',
            'lease_time': '86400',
            'server_addresses': '40.1.5.1/24',
            'dns_service': 'dnsService1',
            'dns_service_ip': '5.5.5.5',
            'default_dns_zone': 'defaultDnsZone1',
            'fqdn_zones': 'fqdnZone1',
            'log_level': 'INFO',
            'dns_zone': 'dnsZone1',
            'domain': 'domain1',
            'dns_server_ips': '1.1.1.1',
            'source_ip': '8.8.8.8',
            'dns_services': '1',
            'port_mirroring': 'portMirroring1',
            'direction': 'BIDIRECTIONAL',
            'source': 'vmGroup1',
            'segment': 'segment1',
            'destination': 'vmGroup2',
            'connected_gateway': '/infra/tier-1s/gateway',
            'dhcp_ranges': '40.20.0.0 40.20.0.1',
            'gateway_address': '40.20.20.20/16',
            'public_ip': 'publicIP1',
            'number_of_public_i_ps': '32',
            'vm_group': 'vmGroup1',
            'members': '564d43da-fefc-2a3b-1d92-42855622fa50',
            'virtual_machine': 'vm1',
            'gateway': 'gateway1'
        })
        
        count = len(self.cmd('az vmware workload-network dhcp list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        dhcpShow = self.cmd('az vmware workload-network dhcp show --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp}').get_output_in_json()
        self.assertEqual(dhcpShow['name'], 'dhcp1')

        dhcpRelayCreate = self.cmd('az vmware workload-network dhcp relay create --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp} --display-name {display_name} --revision {revision} --server-addresses {server_addresses}').get_output_in_json()
        self.assertEqual(dhcpRelayCreate['name'], 'dhcp1')

        dhcpRelayDelete = self.cmd('az vmware workload-network dhcp relay delete --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp} --yes').output
        self.assertEqual(len(dhcpRelayDelete), 0)

        dhcpRelayUpdate = self.cmd('az vmware workload-network dhcp relay update --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp} --display-name {display_name} --revision {revision} --server-addresses {server_addresses}').get_output_in_json()
        self.assertEqual(dhcpRelayUpdate['name'], 'dhcp1')

        dhcpServerCreate = self.cmd('az vmware workload-network dhcp server create --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp} --display-name {display_name} --revision {revision} --server-address {server_address} --lease-time {lease_time}').get_output_in_json()
        self.assertEqual(dhcpServerCreate['name'], 'dhcp1')

        dhcpServerDelete = self.cmd('az vmware workload-network dhcp server delete --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp} --yes').output
        self.assertEqual(len(dhcpServerDelete), 0)

        dhcpServerUpdate = self.cmd('az vmware workload-network dhcp server update --resource-group {rg} --private-cloud {privatecloud} --dhcp {dhcp} --display-name {display_name} --revision {revision} --server-address {server_address} --lease-time {lease_time}').get_output_in_json()
        self.assertEqual(dhcpServerUpdate['name'], 'dhcp1')

        dnsServiceList = self.cmd('az vmware workload-network dns-service list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(dnsServiceList), 1, 'count expected to be 1')

        dnsServiceGet = self.cmd('az vmware workload-network dns-service show --resource-group {rg} --private-cloud {privatecloud} --dns-service {dns_service}').get_output_in_json()
        self.assertEqual(dnsServiceGet['name'], 'portMirroring1')

        dnsServiceCreate = self.cmd('az vmware workload-network dns-service create --resource-group {rg} --private-cloud {privatecloud} --dns-service {dns_service} --display-name {display_name} --dns-service-ip {dns_service_ip} --default-dns-zone {default_dns_zone} --fqdn-zones {fqdn_zones} --log-level {log_level} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsServiceCreate['name'], 'dnsService1')

        dnsServiceUpdate = self.cmd('az vmware workload-network dns-service update --resource-group {rg} --private-cloud {privatecloud} --dns-service {dns_service} --display-name {display_name} --dns-service-ip {dns_service_ip} --default-dns-zone {default_dns_zone} --fqdn-zones {fqdn_zones} --log-level {log_level} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsServiceUpdate['name'], 'dnsService1')

        dnsServiceDelete = self.cmd('az vmware workload-network dns-service delete --resource-group {rg} --private-cloud {privatecloud} --dns-service {dns_service} --yes').output
        self.assertEqual(len(dnsServiceDelete), 0)

        dnsZoneList = self.cmd('az vmware workload-network dns-zone list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(dnsZoneList), 1, 'count expected to be 1')

        dnsZoneGet = self.cmd('az vmware workload-network dns-zone show --resource-group {rg} --private-cloud {privatecloud} --dns-zone {dns_zone}').get_output_in_json()
        self.assertEqual(dnsZoneGet['name'], 'portMirroring1')

        dnsZoneCreate = self.cmd('az vmware workload-network dns-zone create --resource-group {rg} --private-cloud {privatecloud} --dns-zone {dns_zone} --display-name {display_name} --domain {domain} --dns-server-ips {dns_server_ips} --source-ip {source_ip} --dns-services {dns_services} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsZoneCreate['name'], 'dnsZone1')

        dnsZoneUpdate = self.cmd('az vmware workload-network dns-zone update --resource-group {rg} --private-cloud {privatecloud} --dns-zone {dns_zone} --display-name {display_name} --domain {domain} --dns-server-ips {dns_server_ips} --source-ip {source_ip} --dns-services {dns_services} --revision {revision}').get_output_in_json()
        self.assertEqual(dnsZoneUpdate['name'], 'dnsZone1')

        dnsZoneDelete = self.cmd('az vmware workload-network dns-zone delete --resource-group {rg} --private-cloud {privatecloud} --dns-zone {dns_zone} --yes').output
        self.assertEqual(len(dnsZoneDelete), 0)

        portMirroringList = self.cmd('az vmware workload-network port-mirroring list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(portMirroringList), 1, 'count expected to be 1')

        portMirroringGet = self.cmd('az vmware workload-network port-mirroring show --resource-group {rg} --private-cloud {privatecloud} --port-mirroring {port_mirroring}').get_output_in_json()
        self.assertEqual(portMirroringGet['name'], 'portMirroring1')

        portMirroringCreate = self.cmd('az vmware workload-network port-mirroring create --resource-group {rg} --private-cloud {privatecloud} --port-mirroring {port_mirroring} --display-name {display_name} --direction {direction} --source {source} --destination {destination} --revision {revision}').get_output_in_json()
        self.assertEqual(portMirroringCreate['name'], 'portMirroring1')

        portMirroringUpdate = self.cmd('az vmware workload-network port-mirroring update --resource-group {rg} --private-cloud {privatecloud} --port-mirroring {port_mirroring} --display-name {display_name} --direction {direction} --source {source} --destination {destination} --revision {revision}').get_output_in_json()
        self.assertEqual(portMirroringUpdate['name'], 'portMirroring1')

        portMirroringDelete = self.cmd('az vmware workload-network port-mirroring delete --resource-group {rg} --private-cloud {privatecloud} --port-mirroring {port_mirroring} --yes').output
        self.assertEqual(len(portMirroringDelete), 0)

        segmentList = self.cmd('az vmware workload-network segment list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(segmentList), 1, 'count expected to be 1')

        segmentGet = self.cmd('az vmware workload-network segment show --resource-group {rg} --private-cloud {privatecloud} --segment {segment}').get_output_in_json()
        self.assertEqual(segmentGet['name'], 'segment1')

        segmentCreate = self.cmd('az vmware workload-network segment create --resource-group {rg} --private-cloud {privatecloud} --segment {segment} --display-name {display_name} --connected-gateway {connected_gateway} --revision {revision} --dhcp-ranges {dhcp_ranges} --gateway-address {gateway_address}').get_output_in_json()
        self.assertEqual(segmentCreate['name'], 'segment1')

        segmentUpdate = self.cmd('az vmware workload-network segment update --resource-group {rg} --private-cloud {privatecloud} --segment {segment} --display-name {display_name} --connected-gateway {connected_gateway} --revision {revision} --dhcp-ranges {dhcp_ranges} --gateway-address {gateway_address}').get_output_in_json()
        self.assertEqual(segmentUpdate['name'], 'segment1')

        segmentDelete = self.cmd('az vmware workload-network segment delete --resource-group {rg} --private-cloud {privatecloud} --segment {segment} --yes').output
        self.assertEqual(len(segmentDelete), 0)

        publicIpList = self.cmd('az vmware workload-network public-ip list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(publicIpList), 1, 'count expected to be 1')

        publicIpGet = self.cmd('az vmware workload-network public-ip show --resource-group {rg} --private-cloud {privatecloud} --public-ip {public_ip}').get_output_in_json()
        self.assertEqual(publicIpGet['name'], 'publicIP1')

        publicIpCreate = self.cmd('az vmware workload-network public-ip create --resource-group {rg} --private-cloud {privatecloud} --public-ip {public_ip}  --display-name {display_name} --number-of-public-ips {number_of_public_i_ps}').get_output_in_json()
        self.assertEqual(publicIpCreate['name'], 'publicIP1')

        publicIpDelete = self.cmd('az vmware workload-network public-ip delete --resource-group {rg} --private-cloud {privatecloud} --public-ip {public_ip} --yes').output
        self.assertEqual(len(publicIpDelete), 0)

        vmGroupList = self.cmd('az vmware workload-network vm-group list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(vmGroupList), 1, 'count expected to be 1')

        vmGroupGet = self.cmd('az vmware workload-network vm-group show --resource-group {rg} --private-cloud {privatecloud} --vm-group {vm_group}').get_output_in_json()
        self.assertEqual(vmGroupGet['name'], 'cloud1')

        vmGroupCreate = self.cmd('az vmware workload-network vm-group create --resource-group {rg} --private-cloud {privatecloud} --vm-group {vm_group} --display-name {display_name} --members {members} --revision {revision}').get_output_in_json()
        self.assertEqual(vmGroupCreate['name'], 'vmGroup1')

        vmGroupUpdate = self.cmd('az vmware workload-network vm-group update --resource-group {rg} --private-cloud {privatecloud} --vm-group {vm_group} --display-name {display_name} --members {members} --revision {revision}').get_output_in_json()
        self.assertEqual(vmGroupUpdate['name'], 'vmGroup1')

        vmGroupDelete = self.cmd('az vmware workload-network vm-group delete --resource-group {rg} --private-cloud {privatecloud} --vm-group {vm_group} --yes').output
        self.assertEqual(len(vmGroupDelete), 0)

        vmList = self.cmd('az vmware workload-network vm list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(vmList), 1, 'count expected to be 1')

        vmGet = self.cmd('az vmware workload-network vm show --resource-group {rg} --private-cloud {privatecloud} --virtual-machine {virtual_machine}').get_output_in_json()
        self.assertEqual(vmGet['name'], 'vm1')

        gatewayList = self.cmd('az vmware workload-network gateway list --resource-group {rg} --private-cloud {privatecloud}').get_output_in_json()
        self.assertEqual(len(gatewayList), 1, 'count expected to be 1')

        gatewayGet = self.cmd('az vmware workload-network gateway show --resource-group {rg} --private-cloud {privatecloud} --gateway {gateway}').get_output_in_json()
        self.assertEqual(gatewayGet['name'], 'gateway1')