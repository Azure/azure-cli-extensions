# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.util import sdk_no_wait

from ._client_factory import network_client_factory

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
                          dns_servers=None, enable_dns_proxy=None,
                          threat_intel_mode=None, hub_public_ip_count=None, allow_active_ftp=None):
    if firewall_policy and any([enable_dns_proxy, dns_servers]):
        raise CLIError('usage error: firewall policy and dns settings cannot co-exist.')
    if sku and sku.lower() == 'azfw_hub' and not all([virtual_hub, hub_public_ip_count]):
        raise CLIError('usage error: virtual hub and hub ip addresses are mandatory for azure firewall on virtual hub.')
    if sku and sku.lower() == 'azfw_hub' and allow_active_ftp:
        raise CLIError('usage error: allow active ftp is not allowed for azure firewall on virtual hub.')
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    (AzureFirewall,
     SubResource,
     AzureFirewallSku,
     HubIPAddresses,
     HubPublicIPAddresses) = cmd.get_models('AzureFirewall',
                                            'SubResource',
                                            'AzureFirewallSku',
                                            'HubIPAddresses',
                                            'HubPublicIPAddresses')
    sku_instance = AzureFirewallSku(name=sku, tier='Standard')
    firewall = AzureFirewall(location=location,
                             tags=tags,
                             zones=zones,
                             additional_properties={},
                             virtual_hub=SubResource(id=virtual_hub) if virtual_hub is not None else None,
                             firewall_policy=SubResource(id=firewall_policy) if firewall_policy is not None else None,
                             sku=sku_instance if sku is not None else None,
                             threat_intel_mode=threat_intel_mode,
                             hub_ip_addresses=HubIPAddresses(
                                 public_ips=HubPublicIPAddresses(
                                     count=hub_public_ip_count
                                 )
                             ) if hub_public_ip_count is not None else None)
    if private_ranges is not None:
        if firewall.additional_properties is None:
            firewall.additional_properties = {}
        firewall.additional_properties['Network.SNAT.PrivateRanges'] = private_ranges
    if sku is None or sku.lower() == 'azfw_vnet':
        if firewall_policy is None:
            if firewall.additional_properties is None:
                firewall.additional_properties = {}
            if enable_dns_proxy is not None:
                # service side requires lowercase
                firewall.additional_properties['Network.DNS.EnableProxy'] = str(enable_dns_proxy).lower()
            if dns_servers is not None:
                firewall.additional_properties['Network.DNS.Servers'] = ','.join(dns_servers or '')

    if allow_active_ftp:
        if firewall.additional_properties is None:
            firewall.additional_properties = {}
        firewall.additional_properties['Network.FTP.AllowActiveFTP'] = "true"

    return client.create_or_update(resource_group_name, azure_firewall_name, firewall)


# pylint: disable=too-many-branches
def update_azure_firewall(cmd, instance, tags=None, zones=None, private_ranges=None,
                          firewall_policy=None, virtual_hub=None,
                          dns_servers=None, enable_dns_proxy=None,
                          threat_intel_mode=None, hub_public_ip_addresses=None,
                          hub_public_ip_count=None, allow_active_ftp=None):
    if firewall_policy and any([enable_dns_proxy, dns_servers]):
        raise CLIError('usage error: firewall policy and dns settings cannot co-exist.')
    if all([hub_public_ip_addresses, hub_public_ip_count]):
        raise CLIError('Cannot add and remove public ip addresses at same time.')
    (SubResource,
     AzureFirewallPublicIPAddress,
     HubIPAddresses,
     HubPublicIPAddresses) = cmd.get_models('SubResource',
                                            'AzureFirewallPublicIPAddress',
                                            'HubIPAddresses',
                                            'HubPublicIPAddresses')
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
        # service side requires lowercase
        instance.additional_properties['Network.DNS.EnableProxy'] = str(enable_dns_proxy).lower()
    if dns_servers is not None:
        instance.additional_properties['Network.DNS.Servers'] = ','.join(dns_servers or '')
    if threat_intel_mode is not None:
        instance.threat_intel_mode = threat_intel_mode

    if instance.hub_ip_addresses is None and hub_public_ip_addresses is not None:
        raise CLIError('Cannot delete public ip addresses from vhub without creation.')
    if hub_public_ip_count is not None:
        try:
            if instance.hub_ip_addresses.public_ips.count is not None and hub_public_ip_count > instance.hub_ip_addresses.public_ips.count:  # pylint: disable=line-too-long
                instance.hub_ip_addresses.public_ips.count = hub_public_ip_count
            else:
                raise CLIError('Cannot decrease the count of hub ip addresses through --count.')
        except AttributeError:
            instance.hub_ip_addresses = HubIPAddresses(
                public_ips=HubPublicIPAddresses(
                    count=hub_public_ip_count
                )
            )

    if hub_public_ip_addresses is not None:
        try:
            if len(hub_public_ip_addresses) > instance.hub_ip_addresses.public_ips.count:
                raise CLIError('Number of public ip addresses must be less than or equal to existing ones.')
            instance.hub_ip_addresses.public_ips.addresses = [AzureFirewallPublicIPAddress(address=ip) for ip in hub_public_ip_addresses]  # pylint: disable=line-too-long
            instance.hub_ip_addresses.public_ips.count = len(hub_public_ip_addresses)
        except AttributeError:
            raise CLIError('Public Ip addresses must exist before deleting them.')

    if allow_active_ftp is not None:
        if instance.additional_properties is None:
            instance.additional_properties = {}
        if allow_active_ftp:
            instance.additional_properties['Network.FTP.AllowActiveFTP'] = "true"
        elif 'Network.FTP.AllowActiveFTP' in instance.additional_properties:
            del instance.additional_properties['Network.FTP.AllowActiveFTP']

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


def create_azure_firewall_threat_intel_allowlist(cmd, resource_group_name, azure_firewall_name,
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


def update_azure_firewall_threat_intel_allowlist(instance, ip_addresses=None, fqdns=None):
    if ip_addresses is not None:
        if instance.additional_properties is None:
            instance.additional_properties = {}
        instance.additional_properties['ThreatIntel.Whitelist.IpAddresses'] = ip_addresses
    if fqdns is not None:
        if instance.additional_properties is None:
            instance.additional_properties = {}
        instance.additional_properties['ThreatIntel.Whitelist.FQDNs'] = fqdns
    return instance


def show_azure_firewall_threat_intel_allowlist(cmd, resource_group_name, azure_firewall_name):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    firewall = client.get(resource_group_name=resource_group_name, azure_firewall_name=azure_firewall_name)
    if firewall.additional_properties is None:
        firewall.additional_properties = {}
    return firewall.additional_properties


def delete_azure_firewall_threat_intel_allowlist(cmd, resource_group_name, azure_firewall_name):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    firewall = client.get(resource_group_name=resource_group_name, azure_firewall_name=azure_firewall_name)
    if firewall.additional_properties is not None:
        firewall.additional_properties.pop('ThreatIntel.Whitelist.IpAddresses', None)
        firewall.additional_properties.pop('ThreatIntel.Whitelist.FQDNs', None)
    return client.create_or_update(resource_group_name, azure_firewall_name, firewall)
# endregion


# region AzureFirewallPolicies
def create_azure_firewall_policies(cmd, resource_group_name, firewall_policy_name, base_policy=None,
                                   threat_intel_mode=None, location=None, tags=None, ip_addresses=None,
                                   fqdns=None,
                                   dns_servers=None, enable_dns_proxy=None):
    client = network_client_factory(cmd.cli_ctx).firewall_policies
    (FirewallPolicy,
     SubResource,
     FirewallPolicyThreatIntelWhitelist,
     DnsSettings) = cmd.get_models('FirewallPolicy',
                                   'SubResource',
                                   'FirewallPolicyThreatIntelWhitelist',
                                   'DnsSettings')
    firewall_policy = FirewallPolicy(base_policy=SubResource(id=base_policy) if base_policy is not None else None,
                                     threat_intel_mode=threat_intel_mode,
                                     location=location,
                                     tags=tags)

    threat_intel_allowlist = FirewallPolicyThreatIntelWhitelist(ip_addresses=ip_addresses,
                                                                fqdns=fqdns) if ip_addresses and fqdns else None
    firewall_policy.threat_intel_whitelist = threat_intel_allowlist

    if cmd.supported_api_version(min_api='2020-05-01'):
        if any([dns_servers, enable_dns_proxy]):
            dns_settings = DnsSettings(servers=dns_servers,
                                       enable_proxy=enable_dns_proxy or False)
            firewall_policy.dns_settings = dns_settings

    return client.create_or_update(resource_group_name, firewall_policy_name, firewall_policy)


def update_azure_firewall_policies(cmd,
                                   instance, tags=None, threat_intel_mode=None, ip_addresses=None,
                                   fqdns=None,
                                   dns_servers=None, enable_dns_proxy=None):

    (FirewallPolicyThreatIntelWhitelist) = cmd.get_models('FirewallPolicyThreatIntelWhitelist')
    if tags is not None:
        instance.tags = tags
    if threat_intel_mode is not None:
        instance.threat_intel_mode = threat_intel_mode

    if cmd.supported_api_version(min_api='2020-05-01'):
        if instance.dns_settings is None and any([dns_servers, enable_dns_proxy]):
            DnsSettings = cmd.get_models('DnsSettings')
            instance.dns_settings = DnsSettings()
        if dns_servers is not None:
            instance.dns_settings.servers = dns_servers
        if enable_dns_proxy is not None:
            instance.dns_settings.enable_proxy = enable_dns_proxy

    if instance.threat_intel_whitelist is None and any([ip_addresses, fqdns]):
        instance.threat_intel_whitelist = FirewallPolicyThreatIntelWhitelist(ip_addresses=ip_addresses,
                                                                             fqnds=fqdns)
    if ip_addresses is not None:
        instance.threat_intel_whitelist.ip_addresses = ip_addresses
    if fqdns is not None:
        instance.threat_intel_whitelist.fqdns = fqdns
    return instance


def list_azure_firewall_policies(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).firewall_policies
    if resource_group_name is not None:
        return client.list(resource_group_name)
    return client.list_all()


def create_azure_firewall_policy_rule_collection_group(cmd, resource_group_name, firewall_policy_name,
                                                       rule_collection_group_name, priority):
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
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
                                                  translated_fqdn=None, translated_port=None, nat_action=None,
                                                  rule_name=None, description=None, ip_protocols=None,
                                                  source_addresses=None, destination_addresses=None,
                                                  destination_ports=None, source_ip_groups=None):
    FirewallPolicyNatRuleCollection, FirewallPolicyNatRuleCollectionAction, \
        NatRule, FirewallPolicyRuleNetworkProtocol = \
        cmd.get_models('FirewallPolicyNatRuleCollection', 'FirewallPolicyNatRuleCollectionAction',
                       'NatRule', 'FirewallPolicyRuleNetworkProtocol')
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    ip_protocols = list(map(FirewallPolicyRuleNetworkProtocol, ip_protocols))
    nat_rule = NatRule(name=rule_name,
                       description=description,
                       rule_type="NatRule",
                       ip_protocols=ip_protocols,
                       source_addresses=source_addresses,
                       destination_addresses=destination_addresses,
                       destination_ports=destination_ports,
                       translated_address=translated_address,
                       translated_fqdn=translated_fqdn,
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
                                                     rule_priority, filter_action=None, rule_name=None,
                                                     rule_type=None, description=None, ip_protocols=None,
                                                     source_addresses=None, destination_addresses=None,
                                                     destination_ports=None,
                                                     protocols=None, fqdn_tags=None, target_fqdns=None,
                                                     source_ip_groups=None, destination_ip_groups=None):
    NetworkRule, FirewallPolicyRuleApplicationProtocol,\
        ApplicationRule, FirewallPolicyFilterRuleCollectionAction, FirewallPolicyFilterRuleCollection =\
        cmd.get_models('NetworkRule', 'FirewallPolicyRuleApplicationProtocol',
                       'ApplicationRule', 'FirewallPolicyFilterRuleCollectionAction',
                       'FirewallPolicyFilterRuleCollection')
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    rule = None
    if rule_type == "NetworkRule":
        rule = NetworkRule(name=rule_name,
                           description=description,
                           rule_type=rule_type,
                           ip_protocols=ip_protocols,
                           source_addresses=source_addresses,
                           destination_addresses=destination_addresses,
                           destination_ports=destination_ports,
                           source_ip_groups=source_ip_groups,
                           destination_ip_groups=destination_ip_groups)
    else:
        def map_application_rule_protocol(item):
            return FirewallPolicyRuleApplicationProtocol(protocol_type=item['protocol_type'],
                                                         port=int(item['port']))
        protocols = list(map(map_application_rule_protocol, protocols))
        rule = ApplicationRule(name=rule_name,
                               description=description,
                               rule_type=rule_type,
                               source_addresses=source_addresses,
                               protocols=protocols,
                               destination_addresses=destination_addresses,
                               fqdn_tags=fqdn_tags,
                               target_fqdns=target_fqdns,
                               source_ip_groups=source_ip_groups)
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
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            rule_collection_group.rule_collections.remove(rule_collection)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)


def list_azure_firewall_policy_rule_collection(cmd, resource_group_name,
                                               firewall_policy_name, rule_collection_group_name):
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    return rule_collection_group.rule_collections


# pylint: disable=too-many-locals
def add_azure_firewall_policy_filter_rule(cmd, resource_group_name, firewall_policy_name,
                                          rule_collection_group_name,
                                          rule_collection_name, rule_name, rule_type,
                                          description=None, ip_protocols=None, source_addresses=None,
                                          destination_addresses=None, destination_ports=None,
                                          protocols=None, fqdn_tags=None, target_fqdns=None,
                                          source_ip_groups=None, destination_ip_groups=None,
                                          translated_address=None, translated_port=None):
    (NetworkRule,
     FirewallPolicyRuleApplicationProtocol,
     ApplicationRule,
     NatRule) = cmd.get_models('NetworkRule', 'FirewallPolicyRuleApplicationProtocol',
                               'ApplicationRule', 'NatRule')
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    target_rule_collection = None
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            target_rule_collection = rule_collection

    if target_rule_collection is None:
        raise CLIError("Cannot find corresponding rule.")

    if target_rule_collection.rule_collection_type == "FirewallPolicyFilterRule" and rule_type == 'NatRule':
        raise CLIError("FirewallPolicyFilterRule doesn't support Nat rule.")

    if target_rule_collection.rule_collection_type == "FirewallPolicyNatRule" and rule_type in ['NetworkRule',
                                                                                                'ApplicationRule']:
        raise CLIError("FirewallPolicyNatRule supports neither Network rule nor Application rule.")

    rule = None
    if rule_type == "NetworkRule":
        rule = NetworkRule(name=rule_name,
                           description=description,
                           rule_type=rule_type,
                           ip_protocols=ip_protocols,
                           source_addresses=source_addresses,
                           destination_addresses=destination_addresses,
                           destination_ports=destination_ports,
                           source_ip_groups=source_ip_groups,
                           destination_ip_groups=destination_ip_groups)
    elif rule_type == 'ApplicationRule':
        def map_application_rule_protocol(item):
            return FirewallPolicyRuleApplicationProtocol(protocol_type=item['protocol_type'],
                                                         port=int(item['port']))

        protocols = list(map(map_application_rule_protocol, protocols))
        rule = ApplicationRule(name=rule_name,
                               description=description,
                               rule_type=rule_type,
                               source_addresses=source_addresses,
                               protocols=protocols,
                               destination_addresses=destination_addresses,
                               fqdn_tags=fqdn_tags,
                               target_fqdns=target_fqdns,
                               source_ip_groups=source_ip_groups)
    elif rule_type == 'NatRule':
        rule = NatRule(name=rule_name,
                       description=description,
                       rule_type="NatRule",
                       ip_protocols=ip_protocols,
                       source_addresses=source_addresses,
                       destination_addresses=destination_addresses,
                       destination_ports=destination_ports,
                       translated_address=translated_address,
                       translated_port=translated_port,
                       source_ip_groups=source_ip_groups)
    target_rule_collection.rules.append(rule)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)


def remove_azure_firewall_policy_filter_rule(cmd, resource_group_name, firewall_policy_name,
                                             rule_collection_group_name,
                                             rule_collection_name, rule_name):
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups

    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    target_rule_collection = None
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            target_rule_collection = rule_collection

    if target_rule_collection is None:
        raise CLIError("Cannot find corresponding rule collection.")

    for rule in target_rule_collection.rules:
        if rule.name == rule_name:
            target_rule_collection.rules.remove(rule)
    return client.create_or_update(resource_group_name, firewall_policy_name,
                                   rule_collection_group_name, rule_collection_group)
# endregion
