# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from .custom import build_af_rule_list, build_af_rule_show, build_af_rule_delete

from ._client_factory import cf_firewalls, cf_firewall_fqdn_tags
from ._util import (
    list_network_resource_property, get_network_resource_property_entry, delete_network_resource_property_entry)


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_util = CliCommandType(
        operations_tmpl='azext_firewall._util#{}',
        client_factory=None
    )

    network_firewall_sdk = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.operations#AzureFirewallsOperations.{}',
        client_factory=cf_firewalls,
        min_api='2018-08-01'
    )

    network_firewall_fqdn_tags_sdk = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.operations#AzureFirewallFqdnTagsOperations.{}',
        client_factory=cf_firewall_fqdn_tags,
        min_api='2018-08-01'
    )

    # region AzureFirewalls
    with self.command_group('network firewall', network_firewall_sdk) as g:
        g.custom_command('create', 'create_azure_firewall')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_azure_firewalls')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_azure_firewall')

    with self.command_group('network firewall ip-config', network_util) as g:
        g.custom_command('create', 'create_af_ip_configuration')
        g.command('list', list_network_resource_property('azure_firewalls', 'ip_configurations'))
        g.show_command('show', get_network_resource_property_entry('azure_firewalls', 'ip_configurations'))
        g.command('delete', delete_network_resource_property_entry('azure_firewalls', 'ip_configurations'))

    af_rules = {
        'network_rule': 'network-rule',
        'nat_rule': 'nat-rule',
        'application_rule': 'application-rule'
    }
    for rule_type, scope in af_rules.items():
        with self.command_group('network firewall {}'.format(scope), network_firewall_sdk) as g:
            g.custom_command('create', 'create_af_{}'.format(rule_type))
            g.custom_command('list', build_af_rule_list(rule_type, '{}_collections'.format(rule_type)))
            g.custom_command('show', build_af_rule_show(rule_type, '{}_collections'.format(rule_type)))
            g.custom_command('delete', build_af_rule_delete(rule_type, '{}_collections'.format(rule_type)))

    af_collections = {
        'network_rule_collections': 'network-rule collection',
        'nat_rule_collections': 'nat-rule collection',
        'application_rule_collections': 'application-rule collection'
    }
    for subresource, scope in af_collections.items():
        with self.command_group('network firewall {}'.format(scope), network_util) as g:
            g.command('list', list_network_resource_property('azure_firewalls', subresource))
            g.show_command('show', get_network_resource_property_entry('azure_firewalls', subresource))
            g.command('delete', delete_network_resource_property_entry('azure_firewalls', subresource))

    with self.command_group('network firewall', network_firewall_fqdn_tags_sdk) as g:
        g.command('list-fqdn-tags', 'list_all')
    # endregion
