# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait

from ._client_factory import network_client_factory, network_client_policy_factory

logger = get_logger(__name__)


def _generic_list(cli_ctx, operation_name, resource_group_name):
    ncf = network_client_factory(cli_ctx)
    operation_group = getattr(ncf, operation_name)
    if resource_group_name:
        return operation_group.list(resource_group_name)

    return operation_group.list_all()


def _get_property(items, name):
    result = next((x for x in items if x.name.lower() == name.lower()), None)
    if not result:
        raise CLIError("Property '{}' does not exist".format(name))
    return result


def _upsert(parent, collection_name, obj_to_add, key_name, warn=True):
    if not getattr(parent, collection_name, None):
        setattr(parent, collection_name, [])
    collection = getattr(parent, collection_name, None)

    value = getattr(obj_to_add, key_name)
    if value is None:
        raise CLIError(
            "Unable to resolve a value for key '{}' with which to match.".format(key_name))
    match = next((x for x in collection if getattr(x, key_name, None) == value), None)
    if match:
        if warn:
            logger.warning("Item '%s' already exists. Replacing with new values.", value)
        collection.remove(match)

    collection.append(obj_to_add)


def _find_item_at_path(instance, path):
    # path accepts the pattern property/name/property/name
    curr_item = instance
    path_comps = path.split('.')
    for i, comp in enumerate(path_comps):
        if i % 2:
            # name
            curr_item = next((x for x in curr_item if x.name == comp), None)
        else:
            # property
            curr_item = getattr(curr_item, comp, None)
        if not curr_item:
            raise CLIError("unable to find '{}'...".format(comp))
    return curr_item


# region AzureFirewall
def create_azure_firewall(cmd, resource_group_name, azure_firewall_name, location=None,
                          tags=None, zones=None, private_ranges=None, firewall_policy=None,
                          virtual_hub=None, sku=None,
                          dns_servers=None, enable_dns_proxy=None, require_dns_proxy_for_network_rules=None):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    AzureFirewall, SubResource, AzureFirewallSku = cmd.get_models('AzureFirewall', 'SubResource', 'AzureFirewallSku')
    sku_instance = AzureFirewallSku(name=sku, tier='Standard')
    firewall = AzureFirewall(location=location,
                             tags=tags,
                             zones=zones,
                             additional_properties={},
                             virtual_hub=SubResource(id=virtual_hub) if virtual_hub is not None else None,
                             firewall_policy=SubResource(id=firewall_policy) if firewall_policy is not None else None,
                             sku=sku_instance if sku is not None else None)
    if private_ranges is not None:
        if firewall.additional_properties is None:
            firewall.additional_properties = {}
        firewall.additional_properties['Network.SNAT.PrivateRanges'] = private_ranges

    firewall.additional_properties['DNSEnableProxy'] = enable_dns_proxy if enable_dns_proxy is not None else False
    firewall.additional_properties['DNSRequireProxyForNetworkRules'] = \
        require_dns_proxy_for_network_rules if require_dns_proxy_for_network_rules is not None else True
    firewall.additional_properties['DNSServer'] = dns_servers

    return client.create_or_update(resource_group_name, azure_firewall_name, firewall)


def update_azure_firewall(cmd, instance, tags=None, zones=None, private_ranges=None,
                          firewall_policy=None, virtual_hub=None,
                          dns_servers=None, enable_dns_proxy=None, require_dns_proxy_for_network_rules=None):
    SubResource = cmd.get_models('SubResource')
    if tags is not None:
        instance.tags = tags
    if zones is not None:
        instance.zones = zones
    if private_ranges is not None:
        if instance.additional_properties is None:
            instance.additional_properties = {}
        instance.additional_properties['Network.SNAT.PrivateRanges'] = private_ranges
    if firewall_policy is not None:
        instance.firewall_policy = SubResource(id=firewall_policy)
    if virtual_hub is not None:
        if virtual_hub == '':
            instance.virtual_hub = None
        else:
            instance.virtual_hub = SubResource(id=virtual_hub)

    if enable_dns_proxy is not None:
        instance.additional_properties['DNSEnableProxy'] = enable_dns_proxy
    if require_dns_proxy_for_network_rules is not None:
        instance.additional_properties['DNSRequireProxyForNetworkRules'] = require_dns_proxy_for_network_rules
    if dns_servers is not None:
        instance.additional_properties['DNSServer'] = dns_servers

    return instance


def list_azure_firewalls(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'azure_firewalls', resource_group_name)


# pylint: disable=unused-argument
def create_af_ip_configuration(cmd, resource_group_name, azure_firewall_name, item_name,
                               public_ip_address, virtual_network_name=None, subnet='AzureFirewallSubnet',
                               management_item_name=None, management_public_ip_address=None,
                               management_virtual_network_name=None, management_subnet='AzureFirewallManagementSubnet'):
    AzureFirewallIPConfiguration, SubResource = cmd.get_models('AzureFirewallIPConfiguration', 'SubResource')
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, azure_firewall_name)
    config = AzureFirewallIPConfiguration(
        name=item_name,
        public_ip_address=SubResource(id=public_ip_address) if public_ip_address else None,
        subnet=SubResource(id=subnet) if subnet else None
    )
    _upsert(af, 'ip_configurations', config, 'name', warn=False)
    if management_item_name is not None:
        management_config = AzureFirewallIPConfiguration(
            name=management_item_name,
            public_ip_address=SubResource(id=management_public_ip_address) if management_public_ip_address else None,
            subnet=SubResource(id=management_subnet) if management_subnet else None
        )
        af.management_ip_configuration = management_config
    poller = client.create_or_update(resource_group_name, azure_firewall_name, af)
    return _get_property(poller.result().ip_configurations, item_name)


def create_af_management_ip_configuration(cmd, resource_group_name, azure_firewall_name, item_name,
                                          public_ip_address, virtual_network_name,  # pylint: disable=unused-argument
                                          subnet='AzureFirewallManagementSubnet'):
    AzureFirewallIPConfiguration, SubResource = cmd.get_models('AzureFirewallIPConfiguration', 'SubResource')
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, azure_firewall_name)
    config = AzureFirewallIPConfiguration(
        name=item_name,
        public_ip_address=SubResource(id=public_ip_address) if public_ip_address else None,
        subnet=SubResource(id=subnet) if subnet else None
    )
    af.management_ip_configuration = config
    poller = client.create_or_update(resource_group_name, azure_firewall_name, af)
    return poller.result().management_ip_configuration


def update_af_management_ip_configuration(cmd, instance, public_ip_address=None, virtual_network_name=None,  # pylint: disable=unused-argument
                                          subnet='AzureFirewallManagementSubnet'):
    SubResource = cmd.get_models('SubResource')
    if public_ip_address is not None:
        instance.management_ip_configuration.public_ip_address = SubResource(id=public_ip_address)
    if subnet is not None:
        instance.management_ip_configuration.subnet = SubResource(id=subnet)
    return instance


def set_af_management_ip_configuration(cmd, resource_group_name, azure_firewall_name, parameters):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    poller = client.create_or_update(resource_group_name, azure_firewall_name, parameters)
    return poller.result().management_ip_configuration


def show_af_management_ip_configuration(cmd, resource_group_name, azure_firewall_name):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, azure_firewall_name)
    return af.management_ip_configuration


def delete_af_management_ip_configuration(cmd, resource_group_name, azure_firewall_name):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, azure_firewall_name)
    af.management_ip_configuration = None
    poller = client.create_or_update(resource_group_name, azure_firewall_name, af)
    return poller.result().management_ip_configuration


def delete_af_ip_configuration(cmd, resource_group_name, resource_name, item_name, no_wait=False):  # pylint: disable=unused-argument
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, resource_name)
    keep_items = \
        [x for x in af.ip_configurations if x.name.lower() != item_name.lower()]
    af.ip_configurations = keep_items if keep_items else None
    if not keep_items:
        if af.management_ip_configuration is not None:
            logger.warning('Management ip configuration cannot exist without regular ip config. Delete it as well.')
            af.management_ip_configuration = None
    if no_wait:
        sdk_no_wait(no_wait, client.create_or_update, resource_group_name, resource_name, af)
    else:
        result = sdk_no_wait(no_wait, client.create_or_update, resource_group_name, resource_name, af).result()
        if next((x for x in getattr(result, 'ip_configurations') if x.name.lower() == item_name.lower()), None):
            raise CLIError("Failed to delete '{}' on '{}'".format(item_name, resource_name))


def build_af_rule_list(item_param_name, collection_param_name):
    import sys

    def list_func(cmd, resource_group_name, firewall_name, collection_name):
        client = network_client_factory(cmd.cli_ctx).azure_firewalls
        af = client.get(resource_group_name, firewall_name)
        return _find_item_at_path(af, '{}.{}'.format(collection_param_name, collection_name))

    func_name = 'list_af_{}s'.format(item_param_name)
    setattr(sys.modules[__name__], func_name, list_func)
    return func_name


def build_af_rule_show(item_param_name, collection_param_name):
    import sys

    def show_func(cmd, resource_group_name, firewall_name, collection_name, item_name):
        client = network_client_factory(cmd.cli_ctx).azure_firewalls
        af = client.get(resource_group_name, firewall_name)
        return _find_item_at_path(af, '{}.{}.rules.{}'.format(collection_param_name, collection_name, item_name))

    func_name = 'show_af_{}'.format(item_param_name)
    setattr(sys.modules[__name__], func_name, show_func)
    return func_name


def build_af_rule_delete(item_param_name, collection_param_name):
    import sys

    def delete_func(cmd, resource_group_name, firewall_name, collection_name, item_name):
        client = network_client_factory(cmd.cli_ctx).azure_firewalls
        af = client.get(resource_group_name, firewall_name)
        collection = _find_item_at_path(af, '{}.{}'.format(collection_param_name, collection_name))
        collection.rules = [rule for rule in collection.rules if rule.name != item_name]
        client.create_or_update(resource_group_name, firewall_name, af)

    func_name = 'delete_af_{}'.format(item_param_name)
    setattr(sys.modules[__name__], func_name, delete_func)
    return func_name


def _upsert_af_rule(cmd, resource_group_name, firewall_name, collection_param_name, collection_class,
                    item_class, item_name, params, collection_params):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, firewall_name)
    collection = getattr(af, collection_param_name, [])

    collection_name = collection_params.get('name', '')
    priority = collection_params.get('priority', None)
    action = collection_params.get('action', None)

    collection_match = next((x for x in collection if x.name.lower() == collection_name.lower()), None)

    usage_error = CLIError("usage error: --collection-name EXISTING_NAME | --collection-name NEW_NAME --priority"
                           " INT --action ACTION")
    if collection_match:
        if any([priority, action['type']]):
            logger.warning("Rule collection '%s' already exists.", collection_params['name'])
            raise usage_error
    else:
        if not all([priority, action['type']]):
            logger.warning("Rule collection '%s' does not exist and needs to be created.", collection_params['name'])
            raise usage_error
        # create new collection
        logger.warning("Creating rule collection '%s'.", collection_params['name'])
        collection_match = collection_class(**collection_params)
        collection_match.rules = []

    collection_match.rules.append(item_class(**params))
    _upsert(af, collection_param_name, collection_match, 'name', warn=False)
    af = client.create_or_update(resource_group_name, firewall_name, af).result()
    return _find_item_at_path(af, '{}.{}.rules.{}'.format(collection_param_name, collection_name, item_name))


def create_af_network_rule(cmd, resource_group_name, azure_firewall_name, collection_name, item_name,
                           destination_ports, protocols, destination_fqdns=None, source_addresses=None,
                           destination_addresses=None, description=None, priority=None, action=None,
                           source_ip_groups=None, destination_ip_groups=None):
    AzureFirewallNetworkRule, AzureFirewallNetworkRuleCollection = cmd.get_models(
        'AzureFirewallNetworkRule', 'AzureFirewallNetworkRuleCollection')
    params = {
        'name': item_name,
        'description': description,
        'source_addresses': source_addresses,
        'destination_addresses': destination_addresses,
        'destination_ports': destination_ports,
        'destination_fqdns': destination_fqdns,
        'protocols': protocols,
        'destination_ip_groups': destination_ip_groups,
        'source_ip_groups': source_ip_groups
    }
    collection_params = {
        'name': collection_name,
        'priority': priority,
        'action': {'type': action}
    }
    return _upsert_af_rule(cmd, resource_group_name, azure_firewall_name,
                           'network_rule_collections', AzureFirewallNetworkRuleCollection, AzureFirewallNetworkRule,
                           item_name, params, collection_params)


def create_af_nat_rule(cmd, resource_group_name, azure_firewall_name, collection_name, item_name,
                       destination_addresses, destination_ports, protocols, translated_port, source_addresses=None,
                       translated_address=None, translated_fqdn=None, description=None, priority=None, action=None,
                       source_ip_groups=None):
    AzureFirewallNatRule, AzureFirewallNatRuleCollection = cmd.get_models(
        'AzureFirewallNatRule', 'AzureFirewallNatRuleCollection')
    params = {
        'name': item_name,
        'description': description,
        'source_addresses': source_addresses,
        'destination_addresses': destination_addresses,
        'destination_ports': destination_ports,
        'protocols': protocols,
        'translated_address': translated_address,
        'translated_port': translated_port,
        'translated_fqdn': translated_fqdn,
        'source_ip_groups': source_ip_groups
    }
    collection_params = {
        'name': collection_name,
        'priority': priority,
        'action': {'type': action}
    }
    return _upsert_af_rule(cmd, resource_group_name, azure_firewall_name,
                           'nat_rule_collections', AzureFirewallNatRuleCollection, AzureFirewallNatRule,
                           item_name, params, collection_params)


def create_af_application_rule(cmd, resource_group_name, azure_firewall_name, collection_name, item_name,
                               protocols, description=None, source_addresses=None, target_fqdns=None,
                               fqdn_tags=None, priority=None, action=None, source_ip_groups=None):
    AzureFirewallApplicationRule, AzureFirewallApplicationRuleCollection = cmd.get_models(
        'AzureFirewallApplicationRule', 'AzureFirewallApplicationRuleCollection')
    params = {
        'name': item_name,
        'description': description,
        'source_addresses': source_addresses,
        'protocols': protocols,
        'target_fqdns': target_fqdns,
        'fqdn_tags': fqdn_tags,
        'source_ip_groups': source_ip_groups
    }
    collection_params = {
        'name': collection_name,
        'priority': priority,
        'action': {'type': action}
    }
    return _upsert_af_rule(cmd, resource_group_name, azure_firewall_name,
                           'application_rule_collections', AzureFirewallApplicationRuleCollection,
                           AzureFirewallApplicationRule, item_name, params, collection_params)


def create_azure_firewall_threat_intel_whitelist(cmd, resource_group_name, azure_firewall_name,
                                                 ip_addresses=None, fqdns=None):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    firewall = client.get(resource_group_name=resource_group_name, azure_firewall_name=azure_firewall_name)
    if ip_addresses is not None:
        if firewall.additional_properties is None:
            firewall.additional_properties = {}
        firewall.additional_properties['ThreatIntel.Whitelist.IpAddresses'] = ip_addresses
    if fqdns is not None:
        if firewall.additional_properties is None:
            firewall.additional_properties = {}
        firewall.additional_properties['ThreatIntel.Whitelist.FQDNs'] = fqdns
    return client.create_or_update(resource_group_name, azure_firewall_name, firewall)


def update_azure_firewall_threat_intel_whitelist(instance, ip_addresses=None, fqdns=None):
    if ip_addresses is not None:
        if instance.additional_properties is None:
            instance.additional_properties = {}
        instance.additional_properties['ThreatIntel.Whitelist.IpAddresses'] = ip_addresses
    if fqdns is not None:
        if instance.additional_properties is None:
            instance.additional_properties = {}
        instance.additional_properties['ThreatIntel.Whitelist.FQDNs'] = fqdns
    return instance


def show_azure_firewall_threat_intel_whitelist(cmd, resource_group_name, azure_firewall_name):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    firewall = client.get(resource_group_name=resource_group_name, azure_firewall_name=azure_firewall_name)
    if firewall.additional_properties is None:
        firewall.additional_properties = {}
    return firewall.additional_properties


def delete_azure_firewall_threat_intel_whitelist(cmd, resource_group_name, azure_firewall_name):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    firewall = client.get(resource_group_name=resource_group_name, azure_firewall_name=azure_firewall_name)
    if firewall.additional_properties is not None:
        firewall.additional_properties.pop('ThreatIntel.Whitelist.IpAddresses', None)
        firewall.additional_properties.pop('ThreatIntel.Whitelist.FQDNs', None)
    return client.create_or_update(resource_group_name, azure_firewall_name, firewall)
# endregion


# region AzureFirewallPolicies
def create_azure_firewall_policies(cmd, resource_group_name, firewall_policy_name, base_policy=None,
                                   threat_intel_mode=None, location=None, tags=None):
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policies
    FirewallPolicy, SubResource = cmd.get_models('FirewallPolicy', 'SubResource')
    fire_wall_policy = FirewallPolicy(base_policy=SubResource(id=base_policy) if base_policy is not None else None,
                                      threat_intel_mode=threat_intel_mode,
                                      location=location,
                                      tags=tags)
    return client.create_or_update(resource_group_name, firewall_policy_name, fire_wall_policy)


def update_azure_firewall_policies(instance, tags=None, threat_intel_mode=None):
    if tags is not None:
        instance.tags = tags
    if threat_intel_mode is not None:
        instance.threat_intel_mode = threat_intel_mode
    return instance


def list_azure_firewall_policies(cmd, resource_group_name=None):
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policies
    if resource_group_name is not None:
        return client.list(resource_group_name)
    return client.list_all()


def create_azure_firewall_policy_rule_collection_group(cmd, resource_group_name, firewall_policy_name,
                                                       rule_collection_group_name, priority):
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    FirewallPolicyRuleCollectionGroup = cmd.get_models('FirewallPolicyRuleCollectionGroup')
    rule_group = FirewallPolicyRuleCollectionGroup(priority=priority,
                                                   name=rule_collection_group_name)
    return client.create_or_update(resource_group_name, firewall_policy_name, rule_collection_group_name, rule_group)


def update_azure_firewall_policy_rule_collection_group(instance, priority=None, tags=None):
    if tags is not None:
        instance.tags = tags
    if priority is not None:
        instance.priority = priority
    return instance


def add_azure_firewall_policy_nat_rule_collection(cmd, resource_group_name, firewall_policy_name,
                                                  rule_collection_group_name,
                                                  rule_collection_name, rule_priority, translated_address=None,
                                                  translated_port=None, nat_action=None,
                                                  condition_name=None, description=None, ip_protocols=None,
                                                  source_addresses=None, destination_addresses=None,
                                                  destination_ports=None, source_ip_groups=None):
    FirewallPolicyNatRuleCollection, FirewallPolicyNatRuleCollectionAction, \
        NatRule, FirewallPolicyRuleNetworkProtocol = \
        cmd.get_models('FirewallPolicyNatRuleCollection', 'FirewallPolicyNatRuleCollectionAction',
                       'NatRule', 'FirewallPolicyRuleNetworkProtocol')
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    ip_protocols = list(map(FirewallPolicyRuleNetworkProtocol, ip_protocols))
    nat_rule = NatRule(name=condition_name,
                       description=description,
                       rule_type="NatRule",
                       ip_protocols=ip_protocols,
                       source_addresses=source_addresses,
                       destination_addresses=destination_addresses,
                       destination_ports=destination_ports,
                       translated_address=translated_address,
                       translated_port=translated_port,
                       source_ip_groups=source_ip_groups)
    nat_rule_collection = FirewallPolicyNatRuleCollection(name=rule_collection_name,
                                                          priority=rule_priority,
                                                          rule_collection_type="FirewallPolicyNatRuleCollection",
                                                          action=FirewallPolicyNatRuleCollectionAction(
                                                              type=nat_action
                                                          ),
                                                          rules=[nat_rule])
    rule_collection_group.rule_collections.append(nat_rule_collection)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)


# pylint: disable=too-many-locals
def add_azure_firewall_policy_filter_rule_collection(cmd, resource_group_name, firewall_policy_name,
                                                     rule_collection_group_name, rule_collection_name,
                                                     rule_priority, filter_action=None, condition_name=None,
                                                     condition_type=None, description=None, ip_protocols=None,
                                                     source_addresses=None, destination_addresses=None,
                                                     destination_ports=None,
                                                     protocols=None, fqdn_tags=None, target_fqdns=None):
    NetworkRule, FirewallPolicyRuleApplicationProtocol,\
        ApplicationRule, FirewallPolicyFilterRuleCollectionAction, FirewallPolicyFilterRuleCollection =\
        cmd.get_models('NetworkRule', 'FirewallPolicyRuleApplicationProtocol',
                       'ApplicationRule', 'FirewallPolicyFilterRuleCollectionAction',
                       'FirewallPolicyFilterRuleCollection')
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    rule = None
    if condition_type == "NetworkRule":
        rule = NetworkRule(name=condition_name,
                           description=description,
                           rule_type=condition_type,
                           ip_protocols=ip_protocols,
                           source_addresses=source_addresses,
                           destination_addresses=destination_addresses,
                           destination_ports=destination_ports)
    else:
        def map_application_rule_protocol(item):
            return FirewallPolicyRuleApplicationProtocol(protocol_type=item['protocol_type'],
                                                         port=int(item['port']))
        protocols = list(map(map_application_rule_protocol, protocols))
        rule = ApplicationRule(name=condition_name,
                               description=description,
                               rule_type=condition_type,
                               source_addresses=source_addresses,
                               protocols=protocols,
                               destination_addresses=destination_addresses,
                               destination_ports=destination_ports,
                               fqdn_tags=fqdn_tags,
                               target_fqdns=target_fqdns)
    filter_rule_collection = FirewallPolicyFilterRuleCollection(name=rule_collection_name,
                                                                priority=rule_priority,
                                                                rule_collection_type="FirewallPolicyFilterRule",
                                                                action=FirewallPolicyFilterRuleCollectionAction(
                                                                    type=filter_action
                                                                ),
                                                                rules=[rule])
    rule_collection_group.rule_collections.append(filter_rule_collection)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)


def remove_azure_firewall_policy_rule_collection(cmd, resource_group_name, firewall_policy_name,
                                                 rule_collection_group_name, rule_collection_name):
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            rule_collection_group.rule_collections.remove(rule_collection)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)


def list_azure_firewall_policy_rule_collection(cmd, resource_group_name,
                                               firewall_policy_name, rule_collection_group_name):
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    return rule_collection_group.rule_collections


# pylint: disable=too-many-locals
def add_azure_firewall_policy_filter_rule(cmd, resource_group_name, firewall_policy_name,
                                          rule_collection_group_name,
                                          rule_collection_name, condition_name, condition_type,
                                          description=None, ip_protocols=None, source_addresses=None,
                                          destination_addresses=None, destination_ports=None,
                                          protocols=None, fqdn_tags=None, target_fqdns=None):
    NetworkRule, FirewallPolicyRuleApplicationProtocol, ApplicationRule = \
        cmd.get_models('NetworkRule', 'FirewallPolicyRuleApplicationProtocol',
                       'ApplicationRule')
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    target_rule_collection = None
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            target_rule_collection = rule_collection

    if target_rule_collection is None:
        raise CLIError("Cannot find corresponding rule.")

    rule = None
    if condition_type == "NetworkRule":
        rule = NetworkRule(name=condition_name,
                           description=description,
                           rule_condition_type=condition_type,
                           ip_protocols=ip_protocols,
                           source_addresses=source_addresses,
                           destination_addresses=destination_addresses,
                           destination_ports=destination_ports)
    else:
        def map_application_rule_protocol(item):
            return FirewallPolicyRuleApplicationProtocol(protocol_type=item['protocol_type'],
                                                         port=int(item['port']))

        protocols = list(map(map_application_rule_protocol, protocols))
        rule = ApplicationRule(name=condition_name,
                               description=description,
                               rule_condition_type=condition_type,
                               source_addresses=source_addresses,
                               protocols=protocols,
                               destination_addresses=destination_addresses,
                               destination_ports=destination_ports,
                               fqdn_tags=fqdn_tags,
                               target_fqdns=target_fqdns)
    target_rule_collection.rules.append(rule)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)


def remove_azure_firewall_policy_filter_rule(cmd, resource_group_name, firewall_policy_name,
                                             rule_collection_group_name,
                                             rule_collection_name, condition_name):
    client = network_client_policy_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    target_rule_collection = None
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            target_rule_collection = rule_collection

    if target_rule_collection is None:
        raise CLIError("Cannot find corresponding rule collection.")

    for rule in target_rule_collection.rules:
        if rule.name == condition_name:
            target_rule_collection.rules.remove(rule)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)
# endregion
