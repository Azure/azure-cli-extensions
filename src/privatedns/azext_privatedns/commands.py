# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azure.cli.core.util import empty_on_404
from azext_privatedns._client_factory import (cf_privatedns_mgmt_zones, cf_privatedns_mgmt_virtual_network_links, cf_privatedns_mgmt_record_sets)
from azext_privatedns._format import (transform_privatedns_zone_table_output, transform_privatedns_link_table_output, transform_privatedns_record_set_output, transform_privatedns_record_set_table_output)


def load_command_table(self, _):

    network_privatedns_zone_sdk = CliCommandType(
        operations_tmpl='azext_privatedns.privatedns.operations.private_zones_operations#PrivateZonesOperations.{}',
        client_factory=cf_privatedns_mgmt_zones
    )

    network_privatedns_virtual_network_link_sdk = CliCommandType(
        operations_tmpl='azext_privatedns.privatedns.operations.virtual_network_links_operations#VirtualNetworkLinksOperations.{}',
        client_factory=cf_privatedns_mgmt_virtual_network_links
    )

    network_privatedns_record_set_sdk = CliCommandType(
        operations_tmpl='azext_privatedns.privatedns.operations.record_sets_operations#RecordSetsOperations.{}',
        client_factory=cf_privatedns_mgmt_record_sets
    )

    with self.command_group('network privatedns zone', network_privatedns_zone_sdk) as g:
        g.command('delete', 'delete', confirmation=True, supports_no_wait=True)
        g.show_command('show', 'get', table_transformer=transform_privatedns_zone_table_output, exception_handler=empty_on_404)
        g.custom_command('list', 'list_privatedns_zones', client_factory=cf_privatedns_mgmt_zones, table_transformer=transform_privatedns_zone_table_output)
        g.custom_command('create', 'create_privatedns_zone', client_factory=cf_privatedns_mgmt_zones, supports_no_wait=True)
        g.generic_update_command('update', setter_name='update', custom_func_name='update_privatedns_zone', supports_no_wait=True)
        g.wait_command('wait')

    with self.command_group('network privatedns link', network_privatedns_virtual_network_link_sdk) as g:
        g.command('delete', 'delete', confirmation=True, supports_no_wait=True)
        g.show_command('show', 'get', table_transformer=transform_privatedns_link_table_output, exception_handler=empty_on_404)
        g.command('list', 'list', table_transformer=transform_privatedns_link_table_output)
        g.custom_command('create', 'create_privatedns_link', client_factory=cf_privatedns_mgmt_virtual_network_links, supports_no_wait=True)
        g.generic_update_command('update', setter_name='update', custom_func_name='update_privatedns_link', supports_no_wait=True)
        g.wait_command('wait')

    # supported_records = ['a', 'aaaa', 'mx', 'ptr', 'srv', 'txt']
    # for record in supported_records:
    #     with self.command_group('network privatedns record-set {}'.format(record), network_privatedns_record_set_sdk) as g:
    #         g.show_command('show', 'get', transform=transform_privatedns_record_set_output)
    #         g.command('delete', 'delete', confirmation=True)
    #         g.custom_command('list', 'list_dns_record_set', client_factory=cf_privatedns_mgmt_record_sets, transform=transform_privatedns_record_set_output, table_transformer=transform_dns_record_set_table_output)
    #         g.custom_command('create', 'create_dns_record_set', transform=transform_dns_record_set_output, doc_string_source=dns_doc_string)
    #         g.custom_command('add-record', 'add_dns_{}_record'.format(record), transform=transform_dns_record_set_output)
    #         g.custom_command('remove-record', 'remove_dns_{}_record'.format(record), transform=transform_dns_record_set_output)
    #         g.generic_update_command('update', custom_func_name='update_dns_record_set', transform=transform_dns_record_set_output)

    # with self.command_group('network privatedns record-set soa', network_dns_record_set_sdk) as g:
    #     g.show_command('show', 'get', transform=transform_dns_record_set_output)
    #     g.custom_command('update', 'update_dns_soa_record', transform=transform_dns_record_set_output)

    # with self.command_group('network privatedns record-set cname', network_dns_record_set_sdk) as g:
    #     g.show_command('show', 'get', transform=transform_dns_record_set_output)
    #     g.command('delete', 'delete')
    #     g.custom_command('list', 'list_dns_record_set', client_factory=cf_dns_mgmt_record_sets, transform=transform_dns_record_set_output, table_transformer=transform_dns_record_set_table_output)
    #     g.custom_command('create', 'create_dns_record_set', transform=transform_dns_record_set_output, doc_string_source=dns_doc_string)
    #     g.custom_command('set-record', 'add_dns_cname_record', transform=transform_dns_record_set_output)
    #     g.custom_command('remove-record', 'remove_dns_cname_record', transform=transform_dns_record_set_output)
