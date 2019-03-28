# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger

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
def create_azure_firewall(cmd, resource_group_name, azure_firewall_name, location=None, tags=None):
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    AzureFirewall = cmd.get_models('AzureFirewall')
    firewall = AzureFirewall(location=location, tags=tags)
    return client.create_or_update(resource_group_name, azure_firewall_name, firewall)


def update_azure_firewall(instance, tags=None):
    if tags is not None:
        instance.tags = tags
    return instance


def list_azure_firewalls(cmd, resource_group_name=None):
    return _generic_list(cmd.cli_ctx, 'azure_firewalls', resource_group_name)


def create_af_ip_configuration(cmd, resource_group_name, azure_firewall_name, item_name,
                               public_ip_address, virtual_network_name, subnet='AzureFirewallSubnet',  # pylint: disable=unused-argument
                               private_ip_address=None):
    AzureFirewallIPConfiguration, SubResource = cmd.get_models('AzureFirewallIPConfiguration', 'SubResource')
    client = network_client_factory(cmd.cli_ctx).azure_firewalls
    af = client.get(resource_group_name, azure_firewall_name)
    config = AzureFirewallIPConfiguration(
        name=item_name,
        private_ip_address=private_ip_address,
        public_ip_address=SubResource(id=public_ip_address) if public_ip_address else None,
        subnet=SubResource(id=subnet) if subnet else None
    )
    _upsert(af, 'ip_configurations', config, 'name', warn=False)
    poller = client.create_or_update(resource_group_name, azure_firewall_name, af)
    return _get_property(poller.result().ip_configurations, item_name)


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
    collection = getattr(af, collection_param_name)

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
                           source_addresses, destination_addresses, destination_ports, protocols,
                           description=None, priority=None, action=None):
    AzureFirewallNetworkRule, AzureFirewallNetworkRuleCollection = cmd.get_models(
        'AzureFirewallNetworkRule', 'AzureFirewallNetworkRuleCollection')
    params = {
        'name': item_name,
        'description': description,
        'source_addresses': source_addresses,
        'destination_addresses': destination_addresses,
        'destination_ports': destination_ports,
        'protocols': protocols
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
                       source_addresses, destination_addresses, destination_ports, protocols,
                       translated_address, translated_port, description=None, priority=None, action=None):
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
        'translated_port': translated_port
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
                               fqdn_tags=None, priority=None, action=None):
    AzureFirewallApplicationRule, AzureFirewallApplicationRuleCollection = cmd.get_models(
        'AzureFirewallApplicationRule', 'AzureFirewallApplicationRuleCollection')
    params = {
        'name': item_name,
        'description': description,
        'source_addresses': source_addresses,
        'protocols': protocols,
        'target_fqdns': target_fqdns,
        'fqdn_tags': fqdn_tags
    }
    collection_params = {
        'name': collection_name,
        'priority': priority,
        'action': {'type': action}
    }
    return _upsert_af_rule(cmd, resource_group_name, azure_firewall_name,
                           'application_rule_collections', AzureFirewallApplicationRuleCollection,
                           AzureFirewallApplicationRule, item_name, params, collection_params)
# endregion
