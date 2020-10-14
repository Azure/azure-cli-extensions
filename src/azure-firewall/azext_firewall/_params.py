# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import argparse

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, tags_type, get_enum_type, get_location_type, zones_type,
    get_three_state_flag)
from azure.cli.core.commands.validators import get_default_location_from_resource_group

from knack.arguments import CLIArgumentType

from ._completers import get_af_subresource_completion_list
from ._validators import (
    get_public_ip_validator, get_subnet_validator, validate_application_rule_protocols,
    validate_firewall_policy, validate_rule_group_collection, process_private_ranges,
    process_threat_intel_allowlist_ip_addresses, process_threat_intel_allowlist_fqdns,
    validate_virtual_hub, get_management_subnet_validator, get_management_public_ip_validator,
    validate_ip_groups)


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def load_arguments(self, _):

    AzureFirewallNetworkRuleProtocol, AzureFirewallRCActionType, AzureFirewallNatRCActionType = self.get_models(
        'AzureFirewallNetworkRuleProtocol', 'AzureFirewallRCActionType', 'AzureFirewallNatRCActionType')

    firewall_name_type = CLIArgumentType(options_list=['--firewall-name', '-f'], metavar='NAME', help='Azure Firewall name.', id_part='name', completer=get_resource_name_completion_list('Microsoft.Network/azureFirewalls'))
    collection_name_type = CLIArgumentType(options_list=['--collection-name', '-c'], help='Name of the rule collection.', id_part='child_name_1')
    virtual_network_name_type = CLIArgumentType(options_list='--vnet-name', metavar='NAME', help='The virtual network (VNet) name.', completer=get_resource_name_completion_list('Microsoft.Network/virtualNetworks'))

    # region AzureFirewalls
    with self.argument_context('network firewall') as c:
        c.argument('azure_firewall_name', firewall_name_type, options_list=['--name', '-n'], id_part='name')
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('description', help='Rule description.')
        c.argument('destination_addresses', nargs='+', help="Space-separated list of destination IP addresses. Use '*' to match all.")
        c.argument('destination_fqdns', nargs='+', help="Space-separated list of destination FQDNs.")
        c.argument('source_addresses', nargs='+', help="Space-separated list of source IP addresses. Use '*' to match all.")
        c.argument('destination_ports', nargs='+', help="Space-separated list of destination ports. Use '*' to match all.")
        c.argument('source_ip_groups', nargs='+', help='Space-separated list of name or resource id of source IpGroups.')
        c.argument('destination_ip_groups', nargs='+', help='Space-separated list of name or resource id of destination IpGroups')
        c.argument('translated_address', help='Translated address for this NAT rule.')
        c.argument('translated_port', help='Translated port for this NAT rule.')
        c.argument('translated_fqdn', help='Translated FQDN for this NAT rule.')
        c.argument('tags', tags_type)
        c.argument('zones', zones_type)
        c.argument('firewall_policy', options_list=['--firewall-policy', '--policy'],
                   help='Name or ID of the firewallPolicy associated with this azure firewall.',
                   validator=validate_firewall_policy)
        c.argument('virtual_hub', options_list=['--virtual-hub', '--vhub'],
                   help='Name or ID of the virtualHub to which the firewall belongs.',
                   validator=validate_virtual_hub)
        c.argument('sku', arg_type=get_enum_type(['AZFW_VNet', 'AZFW_Hub']), help='SKU of Azure firewall. This field cannot be updated after the creation. '
                                                                                  'The default sku in server end is AZFW_VNet. '
                                                                                  'If you want to attach azure firewall to vhub, you should set sku to AZFW_Hub.')
        c.argument('private_ranges', nargs='+', validator=process_private_ranges, help='Space-separated list of SNAT private range. Validate values are single Ip, Ip prefixes or a single special value "IANAPrivateRanges"')
        c.argument('threat_intel_mode', arg_type=get_enum_type(['Alert', 'Deny', 'Off']), help='The operation mode for Threat Intelligence.')
        c.argument('allow_active_ftp', arg_type=get_three_state_flag(),
                   help="Allow Active FTP. By default it is false. It's only allowed for azure firewall on virtual network.")

    with self.argument_context('network firewall', arg_group='Virtual Hub Public Ip') as c:
        c.argument('hub_public_ip_count', options_list=['--public-ip-count', '--count'], type=int,
                   help="Number of Public IP Address associated with azure firewall. "
                        "It's used to add public ip addresses into this firewall.")
        c.argument('hub_public_ip_addresses', nargs='+', options_list=['--public-ips'],
                   help="Space-separated list of Public IP addresses associated with azure firewall. "
                        "It's used to delete public ip addresses from this firewall. ")

    with self.argument_context('network firewall', arg_group='DNS') as c:
        c.argument('dns_servers', nargs='+', help='Space-separated list of DNS server IP addresses')
        c.argument('enable_dns_proxy', arg_type=get_three_state_flag(), help='Enable DNS Proxy')
        c.argument('require_dns_proxy_for_network_rules', arg_type=get_three_state_flag(), help='Requires DNS Proxy functionality for FQDNs within Network Rules')

    with self.argument_context('network firewall threat-intel-allowlist') as c:
        c.argument('ip_addresses', nargs='+', validator=process_threat_intel_allowlist_ip_addresses, help='Space-separated list of IPv4 addresses.')
        c.argument('fqdns', nargs='+', validator=process_threat_intel_allowlist_fqdns, help='Space-separated list of FQDNs.')

    for scope in ['network-rule', 'nat-rule']:
        with self.argument_context('network firewall {}'.format(scope)) as c:
            c.argument('protocols', arg_type=get_enum_type(AzureFirewallNetworkRuleProtocol), nargs='+', help='Space-separated list of protocols.')

    with self.argument_context('network firewall application-rule') as c:
        c.argument('target_fqdns', nargs='+', help='Space-separated list of fully qualified domain names (FDQN).')
        c.argument('fqdn_tags', nargs='+', help='Space-separated list of FQDN tags.')
        c.argument('protocols', nargs='+', validator=validate_application_rule_protocols, help='Space-separated list of protocols and port numbers to use, in PROTOCOL=PORT format. Valid protocols are Http, Https.')

    af_sub_subresources = [
        {'name': 'network-rule', 'display': 'network rule', 'ref': 'network_rule_collections'},
        {'name': 'nat-rule', 'display': 'NAT rule', 'ref': 'nat_rule_collections'},
        {'name': 'application-rule', 'display': 'application rule', 'ref': 'application_rule_collections'},
    ]
    for item in af_sub_subresources:
        with self.argument_context('network firewall {}'.format(item['name'])) as c:
            c.argument('item_name', options_list=['--name', '-n'], help='The name of the {}'.format(item['display']), completer=get_af_subresource_completion_list(item['ref']), id_part='child_name_2')
            c.argument('collection_name', collection_name_type)
            c.argument('firewall_name', firewall_name_type)
            c.argument('azure_firewall_name', firewall_name_type)

        with self.argument_context('network firewall {} list'.format(item['name'])) as c:
            c.argument('item_name', options_list=['--name', '-n'], help='The name of the {}'.format(item['display']), completer=get_af_subresource_completion_list(item['ref']), id_part='child_name_2')
            c.argument('firewall_name', firewall_name_type, id_part=None)

        with self.argument_context('network firewall {} create'.format(item['name']), arg_group='Collection') as c:
            c.argument('collection_name', collection_name_type, help='Name of the collection to create the rule in. Will create the collection if it does not exist.')
            c.argument('priority', help='Priority of the rule collection from 100 (high) to 65000 (low). Supply only if you want to create the collection.', type=int)

        with self.argument_context('network firewall {} collection'.format(item['name'])) as c:
            c.argument('item_name', collection_name_type)
            c.argument('resource_name', firewall_name_type)

        with self.argument_context('network firewall {} collection list'.format(item['name'])) as c:
            c.argument('item_name', collection_name_type)
            c.argument('resource_name', firewall_name_type, id_part=None)

    for scope in ['network-rule', 'application-rule']:
        with self.argument_context('network firewall {}'.format(scope), arg_group='Collection') as c:
            c.argument('action', arg_type=get_enum_type(AzureFirewallRCActionType), help='The action to apply for the rule collection. Supply only if you want to create the collection.')

    with self.argument_context('network firewall nat-rule', arg_group='Collection') as c:
        c.argument('action', arg_type=get_enum_type(AzureFirewallNatRCActionType), help='The action to apply for the rule collection. Supply only if you want to create the collection.')

    with self.argument_context('network firewall ip-config') as c:
        c.argument('item_name', options_list=['--name', '-n'], help='Name of the IP configuration.', id_part='child_name_2')
        c.argument('resource_name', firewall_name_type)
        c.argument('azure_firewall_name', firewall_name_type)
        c.argument('subnet', validator=get_subnet_validator(), help=argparse.SUPPRESS)
        c.argument('virtual_network_name', virtual_network_name_type, help='The virtual network (VNet) name. It should contain one subnet called "AzureFirewallSubnet".')
        c.argument('public_ip_address', help='Name or ID of the public IP to use.', validator=get_public_ip_validator())
        c.argument('private_ip_address', deprecate_info=c.deprecate(expiration='2.3.0'), help='IP address used by the Firewall ILB as the next hop in User Defined Routes.')

    with self.argument_context('network firewall ip-config', arg_group="Management Ip Config") as c:
        c.argument('management_item_name', options_list=['--m-name'],
                   help='Name of the management IP configuration.', is_preview=True)
        c.argument('management_subnet', validator=get_management_subnet_validator(), help=argparse.SUPPRESS, is_preview=True)
        c.argument('management_virtual_network_name', virtual_network_name_type, options_list=['--m-vnet-name'],
                   help='The virtual network (VNet) name for management ip configuation. '
                        'It should contain one subnet called "AzureFirewallManagementSubnet".', is_preview=True)
        c.argument('management_public_ip_address', help='Name or ID of the public IP to use for management ip configuation.',
                   options_list=['--m-public-ip-address'], validator=get_management_public_ip_validator(), is_preview=True)

    with self.argument_context('network firewall management-ip-config') as c:
        c.argument('item_name', options_list=['--name', '-n'], help='Name of the management IP configuration.', id_part='child_name_2')
        c.argument('resource_name', firewall_name_type)
        c.argument('azure_firewall_name', firewall_name_type)
        c.argument('subnet', validator=get_subnet_validator(), help=argparse.SUPPRESS)
        c.argument('virtual_network_name', virtual_network_name_type,
                   help='The virtual network (VNet) name. It should contain one subnet called "AzureFirewallManagementSubnet".')
        c.argument('public_ip_address', help='Name or ID of the public IP to use.', validator=get_public_ip_validator())

    with self.argument_context('network firewall ip-config list') as c:
        c.argument('resource_name', firewall_name_type, id_part=None)

    with self.argument_context('network firewall policy') as c:
        c.argument('firewall_policy_name', options_list=['--name', '-n'], help='The name of the Firewall Policy.')
        c.argument('base_policy', validator=validate_firewall_policy, help='The name or ID of parent firewall policy from which rules are inherited.')
        c.argument('threat_intel_mode', arg_type=get_enum_type(['Alert', 'Deny', 'Off']), help='The operation mode for Threat Intelligence.')

    with self.argument_context('network firewall policy', arg_group='Threat Intel Allowlist') as c:
        c.argument('ip_addresses', nargs='+', help='Space-separated list of IPv4 addresses.')
        c.argument('fqdns', nargs='+', help='Space-separated list of FQDNs.')

    with self.argument_context('network firewall policy rule-collection-group') as c:
        c.argument('firewall_policy_name', options_list=['--policy-name'], help='The name of the Firewall Policy.')
        c.argument('rule_collection_group_name', options_list=['--name', '-n'], help='The name of the Firewall Policy Rule Collection Group.')
        c.argument('priority', type=int, help='Priority of the Firewall Policy Rule Collection Group')

    with self.argument_context('network firewall policy rule-collection-group collection') as c:
        c.argument('rule_collection_group_name', options_list=['--rule-collection-group-name'], help='The name of the Firewall Policy Rule Collection Group.')
        c.argument('rule_collection_name', options_list=['--name', '-n'], help='The name of the collection in Firewall Policy Rule Collection Group.')
        c.argument('rule_priority', options_list=['--collection-priority'], type=int, help='The priority of the rule in Firewall Policy Rule Collection Group')

    with self.argument_context('network firewall policy rule-collection-group collection', arg_group='Common Rule') as c:
        c.argument('description', help='The description of rule.')
        c.argument('destination_addresses', nargs='+', help="Space-separated list of destination IP addresses.")
        c.argument('source_addresses', nargs='+', help="Space-separated list of source IP addresses.")
        c.argument('rule_name', options_list=['--rule-name'], help='The name of rule')
        c.argument('rule_type', options_list=['--rule-type'], arg_type=get_enum_type(["ApplicationRule", "NetworkRule", "NatRule"]), help='The type of rule')
        c.argument('destination_ports', nargs='+', help="Space-separated list of destination ports. This argument is supported for Nat and Network Rule.")
        c.argument('ip_protocols', nargs='+', arg_type=get_enum_type(["TCP", "UDP", "Any", "ICMP"]),
                   help="Space-separated list of IP protocols. This argument is supported for Nat and Network Rule.")
        c.argument('source_ip_groups', nargs='+', validator=validate_ip_groups,
                   help='Space-separated list of name or resource id of source IpGroups.')

    with self.argument_context('network firewall policy rule-collection-group collection', arg_group='Nat Rule') as c:
        c.argument('translated_address', help='Translated address for this NAT rule collection.')
        c.argument('translated_port', help='Translated port for this NAT rule collection.')

    with self.argument_context('network firewall policy rule-collection-group collection', arg_group='Application Rule') as c:
        c.argument('target_fqdns', nargs='+', help='Space-separated list of FQDNs for this rule.', validator=validate_rule_group_collection)
        c.argument('fqdn_tags', nargs='+', help='Space-separated list of FQDN tags for this rule.', validator=validate_rule_group_collection)
        c.argument('protocols', nargs='+', validator=validate_application_rule_protocols, help='Space-separated list of protocols and port numbers to use, in PROTOCOL=PORT format. Valid protocols are Http, Https.')

    with self.argument_context('network firewall policy rule-collection-group collection', arg_group='Network Rule') as c:
        c.argument('destination_ip_groups', nargs='+', validator=validate_ip_groups,
                   help='Space-separated list of name or resource id of destination IpGroups')

    with self.argument_context('network firewall policy rule-collection-group collection add-filter-collection') as c:
        c.argument('filter_action', options_list=['--action'], arg_type=get_enum_type(['Allow', 'Deny']), help='The action type of a rule collection.')

    with self.argument_context('network firewall policy rule-collection-group collection add-nat-collection') as c:
        c.argument('nat_action', options_list=['--action'], arg_type=get_enum_type(['DNAT', 'SNAT']), help='The action type of a rule collection.')

    with self.argument_context('network firewall policy rule-collection-group collection rule') as c:
        c.argument('rule_collection_name', options_list=['--collection-name'], help='The name of the rule collection in Firewall Policy Rule Collection Group.')
        c.argument('rule_name', options_list=['--name', '-n'], arg_group='Common Rule', help='The name of rule')
    # endregion
