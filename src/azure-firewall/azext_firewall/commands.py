# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from .custom import build_af_rule_list, build_af_rule_show, build_af_rule_delete
from .profiles import CUSTOM_FIREWALL

from ._client_factory import cf_firewalls, cf_firewall_fqdn_tags, cf_firewall_policies, cf_firewall_policy_rule_collection_groups
from ._util import (
    list_network_resource_property, get_network_resource_property_entry, delete_network_resource_property_entry)

from ._validators import validate_af_network_rule, validate_af_nat_rule, validate_af_application_rule


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    network_util = CliCommandType(
        operations_tmpl='azext_firewall._util#{}',
        client_factory=None
    )

    network_firewall_sdk = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.v2020_05_01.operations#AzureFirewallsOperations.{}',
        client_factory=cf_firewalls,
        resource_type=CUSTOM_FIREWALL,
        min_api='2018-08-01'
    )

    network_firewall_fqdn_tags_sdk = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.v2020_05_01.operations#AzureFirewallFqdnTagsOperations.{}',
        client_factory=cf_firewall_fqdn_tags,
        resource_type=CUSTOM_FIREWALL,
        min_api='2018-08-01'
    )

    network_firewall_policies_sdk = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.v2020_05_01.operations#FirewallPoliciesOperations.{}',
        client_factory=cf_firewall_policies,
        resource_type=CUSTOM_FIREWALL,
        min_api='2019-07-01'
    )

    network_firewall_policy_rule_groups = CliCommandType(
        operations_tmpl='azext_firewall.vendored_sdks.v2020_05_01.operations#FirewallPolicyRuleCollectionGroupsOperations.{}',
        client_factory=cf_firewall_policy_rule_collection_groups,
        resource_type=CUSTOM_FIREWALL,
        min_api='2019-07-01'
    )

    # region AzureFirewalls
    with self.command_group('network firewall', network_firewall_sdk) as g:
        g.custom_command('create', 'create_azure_firewall')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_azure_firewalls')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_azure_firewall')

    with self.command_group('network firewall threat-intel-whitelist', network_firewall_sdk, is_preview=True, min_api='2019-09-01') as g:
        g.custom_command('create', 'create_azure_firewall_threat_intel_whitelist')
        g.custom_command('delete', 'delete_azure_firewall_threat_intel_whitelist')
        g.custom_show_command('show', 'show_azure_firewall_threat_intel_whitelist')
        g.generic_update_command('update', custom_func_name='update_azure_firewall_threat_intel_whitelist')

    with self.command_group('network firewall ip-config', network_util) as g:
        g.custom_command('create', 'create_af_ip_configuration')
        g.command('list', list_network_resource_property('azure_firewalls', 'ip_configurations'))
        g.show_command('show', get_network_resource_property_entry('azure_firewalls', 'ip_configurations'))
        g.custom_command('delete', 'delete_af_ip_configuration')

    with self.command_group('network firewall management-ip-config', network_util, is_preview=True) as g:
        # https://github.com/Azure/azure-cli-extensions/issues/1270
        # disable it by service limitation.
        # g.custom_command('create', 'create_af_management_ip_configuration')
        g.custom_show_command('show', 'show_af_management_ip_configuration')
        g.generic_update_command('update', command_type=network_firewall_sdk,
                                 custom_func_name='update_af_management_ip_configuration',
                                 setter_type=CliCommandType(operations_tmpl='azext_firewall.custom#{}'),
                                 setter_name='set_af_management_ip_configuration')
        # Discussed with service team to hide this command for now.
        # g.custom_command('delete', 'delete_af_management_ip_configuration')

    af_rules = {
        'network_rule': {'scope': 'network-rule', 'validator': validate_af_network_rule},
        'nat_rule': {'scope': 'nat-rule', 'validator': validate_af_nat_rule},
        'application_rule': {'scope': 'application-rule', 'validator': validate_af_application_rule}
    }

    for rule_type, af_rule in af_rules.items():
        with self.command_group('network firewall {}'.format(af_rule['scope']), network_firewall_sdk) as g:
            g.custom_command('create', 'create_af_{}'.format(rule_type), validator=af_rule['validator'])
            g.custom_command('list', build_af_rule_list(rule_type, '{}_collections'.format(rule_type)))
            g.custom_show_command('show', build_af_rule_show(rule_type, '{}_collections'.format(rule_type)))
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

    # region AzureFirewallPolicies
    with self.command_group('network firewall policy', network_firewall_policies_sdk, resource_type=CUSTOM_FIREWALL, is_preview=True, min_api='2019-07-01') as g:
        g.custom_command('create', 'create_azure_firewall_policies')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_azure_firewall_policies')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_azure_firewall_policies')

    with self.command_group('network firewall policy rule-collection-group', network_firewall_policy_rule_groups, resource_type=CUSTOM_FIREWALL, is_preview=True) as g:
        g.custom_command('create', 'create_azure_firewall_policy_rule_collection_group')
        g.generic_update_command('update', custom_func_name='update_azure_firewall_policy_rule_collection_group')
        g.command('delete', 'delete')
        g.show_command('show')
        g.command('list', 'list')

    with self.command_group('network firewall policy rule-collection-group collection', network_firewall_policy_rule_groups, resource_type=CUSTOM_FIREWALL, is_preview=True) as g:
        g.custom_command('add-nat-collection', 'add_azure_firewall_policy_nat_rule_collection')
        g.custom_command('add-filter-collection', 'add_azure_firewall_policy_filter_rule_collection')
        g.custom_command('remove', 'remove_azure_firewall_policy_rule_collection')
        g.custom_command('list', 'list_azure_firewall_policy_rule_collection')

    with self.command_group('network firewall policy rule-collection-group collection rule', network_firewall_policy_rule_groups, resource_type=CUSTOM_FIREWALL, is_preview=True) as g:
        g.custom_command('add', 'add_azure_firewall_policy_filter_rule')
        g.custom_command('remove', 'remove_azure_firewall_policy_filter_rule')
    # endregion
