# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.aaz import has_value
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import UserFault, ServiceError, ValidationError
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import resource_id
from ._client_factory import network_client_factory
from .aaz.latest.network.firewall import Create as _AzureFirewallCreate, Update as _AzureFirewallUpdate

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
        raise CLIError(f"Property '{name}' does not exist")
    return result


def _upsert(parent, collection_name, obj_to_add, key_name, warn=True):
    if not getattr(parent, collection_name, None):
        setattr(parent, collection_name, [])
    collection = getattr(parent, collection_name, None)

    value = getattr(obj_to_add, key_name)
    if value is None:
        raise CLIError(
            f"Unable to resolve a value for key '{key_name}' with which to match.")
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
            raise CLIError(f"unable to find '{comp}'...")
    return curr_item


# region AzureFirewall
class AzureFirewallCreate(_AzureFirewallCreate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg, AAZBoolArg, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.private_ranges = AAZListArg(
            options=['--private-ranges'],
            help="Space-separated list of SNAT privaterange. Validate values are single Ip, "
                 "Ipprefixes or a single special value \"IANAPrivateRanges\".")
        args_schema.private_ranges.Element = AAZStrArg()
        args_schema.allow_active_ftp = AAZBoolArg(
            options=['--allow-active-ftp'],
            help="Allow Active FTP. By default it is false. It's only allowed for azure firewall on virtual network.")
        args_schema.enable_fat_flow_logging = AAZBoolArg(
            options=['--enable-fat-flow-logging', '--fat-flow-logging'],
            help="Allow fat flow logging. By default it is false.")
        args_schema.enable_udp_log_optimization = AAZBoolArg(
            options=['--enable-udp-log-optimization', '--udp-log-optimization'],
            help="Allow UDP log optimization. By default it is false.")
        args_schema.dns_servers = AAZListArg(
            options=['--dns-servers'],
            arg_group="DNS",
            help="Space-separated list of DNS server IP addresses.")
        args_schema.dns_servers.Element = AAZStrArg()
        args_schema.enable_dns_proxy = AAZBoolArg(
            options=['--enable-dns-proxy'],
            arg_group="DNS",
            help="Enable DNS Proxy.")
        args_schema.route_server_id = AAZStrArg(
            options=['--route-server-id'],
            help="The Route Server Id for the firewall.")
        args_schema.conf_name = AAZStrArg(
            options=["--conf-name"],
            arg_group="Data Traffic IP Configuration",
            help="Name of the IP configuration.",
        )
        args_schema.vnet_name = AAZStrArg(
            options=["--vnet-name"],
            arg_group="Data Traffic IP Configuration",
            help="The virtual network (VNet) name. It should contain one subnet called \"AzureFirewallSubnet\".",
        )
        args_schema.public_ip = AAZResourceIdArg(
            options=["--public-ip"],
            arg_group="Data Traffic IP Configuration",
            help="Name or ID of the public IP to use.",
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/publicIPAddresses/{}"
            ),
        )
        args_schema.m_public_ip._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                     "/publicIPAddresses/{}",
        )
        args_schema.firewall_policy._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                     "/firewallPolicies/{}",
        )
        args_schema.virtual_hub._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                     "/virtualHubs/{}",
        )
        args_schema.additional_properties._registered = False
        args_schema.ip_configurations._registered = False
        args_schema.mgmt_ip_conf_subnet._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.sku):
            sku = args.sku.to_serialized_data()
            if sku.lower() == 'azfw_hub' and not all([args.virtual_hub, args.public_ip_count]):
                raise CLIError(
                    'usage error: virtual hub and hub ip addresses are mandatory for azure firewall on virtual hub.')
            if sku.lower() == 'azfw_hub' and has_value(args.allow_active_ftp):
                raise CLIError('usage error: allow active ftp is not allowed for azure firewall on virtual hub.')
        if has_value(args.firewall_policy) and any([args.enable_dns_proxy, args.dns_servers]):
            raise CLIError('usage error: firewall policy and dns settings cannot co-exist.')

        # validate basic sku firewall
        if has_value(args.tier) and has_value(args.sku):
            tier = args.tier.to_serialized_data()
            if tier.lower() == 'basic' and sku.lower() == 'azfw_vnet' \
                    and not all([args.m_conf_name, args.m_public_ip]):
                err_msg = "When creating Basic SKU firewall, both --m-conf-name and --m-public-ip-address should be provided."
                raise ValidationError(err_msg)

        args.additional_properties = {}
        if has_value(args.private_ranges):
            private_ranges = args.private_ranges.to_serialized_data()
            args.additional_properties['Network.SNAT.PrivateRanges'] = ', '.join(private_ranges)

        if not has_value(args.sku) or sku.lower() == 'azfw_vnet':
            if not has_value(args.firewall_policy):
                if has_value(args.enable_dns_proxy):
                    # service side requires lowercase
                    if args.enable_dns_proxy:
                        args.additional_properties['Network.DNS.EnableProxy'] = 'true'
                    else:
                        args.additional_properties['Network.DNS.EnableProxy'] = 'false'
                if has_value(args.dns_servers):
                    dns_servers = args.dns_servers.to_serialized_data()
                    args.additional_properties['Network.DNS.Servers'] = ','.join(dns_servers or '')

        if has_value(args.allow_active_ftp) and args.allow_active_ftp:
            args.additional_properties['Network.FTP.AllowActiveFTP'] = 'true'

        if has_value(args.enable_fat_flow_logging) and args.enable_fat_flow_logging:
            args.additional_properties['Network.AdditionalLogs.EnableFatFlowLogging'] = 'true'

        if has_value(args.enable_udp_log_optimization) and args.enable_udp_log_optimization:
            args.additional_properties['Network.AdditionalLogs.EnableUdpLogOptimization'] = 'true'

        if has_value(args.route_server_id):
            args.additional_properties['Network.RouteServerInfo.RouteServerID'] = args.route_server_id

        if has_value(args.conf_name):
            subnet_id = resource_id(
                subscription=get_subscription_id(self.cli_ctx),
                resource_group=args.resource_group,
                namespace='Microsoft.Network',
                type='virtualNetworks',
                name=args.vnet_name,
                child_type_1='subnets',
                child_name_1='AzureFirewallSubnet'
            )
            args.ip_configurations = [{"name": args.conf_name,
                                       "subnet": subnet_id if has_value(subnet_id) else None,
                                       "public_ip_address": args.public_ip if has_value(args.public_ip) else None}]

        if has_value(args.tier) and has_value(args.sku):
            if tier.lower() == 'basic' and sku.lower() == 'azfw_vnet':
                management_subnet_id = resource_id(
                    subscription=get_subscription_id(self.cli_ctx),
                    resource_group=args.resource_group,
                    namespace='Microsoft.Network',
                    type='virtualNetworks',
                    name=args.vnet_name,
                    child_type_1='subnets',
                    child_name_1='AzureFirewallManagementSubnet'
                )
                args.mgmt_ip_conf_subnet = management_subnet_id


# pylint: disable=too-many-branches disable=too-many-statements
class AzureFirewallUpdate(_AzureFirewallUpdate):

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg, AAZBoolArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.private_ranges = AAZListArg(
            options=['--private-ranges'],
            help="Space-separated list of SNAT privaterange. Validate values are single Ip, "
                 "Ipprefixes or a single special value \"IANAPrivateRanges\".",
            nullable=True)
        args_schema.private_ranges.Element = AAZStrArg(nullable=True)
        args_schema.allow_active_ftp = AAZBoolArg(
            options=['--allow-active-ftp'],
            help="Allow Active FTP. By default it is false. It's only allowed for azure firewall on virtual network.",
            nullable=True,)
        args_schema.enable_fat_flow_logging = AAZBoolArg(
            options=['--enable-fat-flow-logging', '--fat-flow-logging'],
            help="Allow fat flow logging. By default it is false.",
            nullable=True)
        args_schema.enable_udp_log_optimization = AAZBoolArg(
            options=['--enable-udp-log-optimization', '--udp-log-optimization'],
            help="Allow UDP log optimization. By default it is false.",
            nullable=True)
        args_schema.dns_servers = AAZListArg(
            options=['--dns-servers'],
            arg_group="DNS",
            help="Space-separated list of DNS server IP addresses.",
            nullable=True)
        args_schema.dns_servers.Element = AAZStrArg(nullable=True)
        args_schema.enable_dns_proxy = AAZBoolArg(
            options=['--enable-dns-proxy'],
            arg_group="DNS",
            help="Enable DNS Proxy.",
            nullable=True)
        args_schema.public_ips = AAZListArg(
            options=['--public-ips'],
            arg_group="Virtual Hub Public Ip",
            help="Space-separated list of Public IP addresses associated with azure firewall. "
                 "It's used to delete public ip addresses from this firewall.",
            nullable=True)
        args_schema.public_ips.Element = AAZStrArg(nullable=True)
        # "Network.RouteServerInfo.RouteServerID"
        args_schema.route_server_id = AAZStrArg(
            options=['--route-server-id'],
            help="The Route Server Id for the firewall.",
            nullable=True)
        args_schema.virtual_hub._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                     "/virtualHubs/{}",
        )
        args_schema.addresses._registered = False
        args_schema.additional_properties._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.firewall_policy) and any([args.enable_dns_proxy, args.dns_servers]):
            raise CLIError('usage error: firewall policy and dns settings cannot co-exist.')
        if all([args.public_ips, args.public_ip_count]):
            raise CLIError('Cannot add and remove public ip addresses at same time.')

        if has_value(args.virtual_hub):
            if args.virtual_hub == '':
                args.virtual_hub = None

    def pre_instance_update(self, instance):
        args = self.ctx.args
        if has_value(args.private_ranges):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            private_ranges = args.private_ranges.to_serialized_data()
            instance.properties.additional_properties['Network.SNAT.PrivateRanges'] = ', '.join(private_ranges)

        if has_value(args.enable_dns_proxy):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            # service side requires lowercase
            if args.enable_dns_proxy:
                instance.properties.additional_properties['Network.DNS.EnableProxy'] = 'true'
            else:
                instance.properties.additional_properties['Network.DNS.EnableProxy'] = 'false'

        if has_value(args.dns_servers):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            dns_servers = args.dns_servers.to_serialized_data()
            instance.properties.additional_properties['Network.DNS.Servers'] = ','.join(dns_servers or '')

        if has_value(args.route_server_id):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            instance.properties.additional_properties['Network.RouteServerInfo.RouteServerID'] = args.route_server_id

        if has_value(args.public_ips):
            try:
                if instance.hub_ip_addresses is not None:
                    pass
            except AttributeError:
                raise CLIError('Cannot delete public ip addresses from vhub without creation.')
        if has_value(args.public_ip_count):
            try:
                if has_value(instance.hub_ip_addresses.public_i_ps.count) and \
                        args.public_ip_count.to_serialized_data() > \
                        instance.hub_ip_addresses.public_i_ps.count.to_serialized_data():  # pylint: disable=line-too-long
                    instance.hub_ip_addresses.public_i_ps.count = args.public_ip_count
                else:
                    raise CLIError('Cannot decrease the count of hub ip addresses through --count.')
            except AttributeError:
                pass

        if has_value(args.public_ips):
            try:
                if len(args.public_ips.to_serialized_data()) > \
                        instance.hub_ip_addresses.public_i_ps.count.to_serialized_data():
                    raise CLIError('Number of public ip addresses must be less than or equal to existing ones.')
                from azure.cli.core.aaz.utils import assign_aaz_list_arg
                args.addresses = assign_aaz_list_arg(
                    args.addresses,
                    args.public_ips,
                    element_transformer=lambda _, public_ip: {"address": public_ip}
                )
                args.public_ip_count = len(args.public_ips.to_serialized_data())
                # instance.hub_ip_addresses.public_i_ps.addresses = [{"address": ip} for ip in args.hub_public_ip_addresses]  # pylint: disable=line-too-long
                # instance.hub_ip_addresses.public_i_ps.count = len(args.hub_public_ip_addresses.to_serialized_data())
            except AttributeError as err:
                raise CLIError('Public Ip addresses must exist before deleting them.') from err

        if has_value(args.allow_active_ftp):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            if args.allow_active_ftp:
                instance.properties.additional_properties['Network.FTP.AllowActiveFTP'] = 'true'
            elif 'Network.FTP.AllowActiveFTP' in instance.properties.additional_properties:
                del instance.properties.additional_properties['Network.FTP.AllowActiveFTP']

        if has_value(args.enable_fat_flow_logging):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            if args.enable_fat_flow_logging:
                instance.properties.additional_properties['Network.AdditionalLogs.EnableFatFlowLogging'] = 'true'
            elif 'Network.AdditionalLogs.EnableFatFlowLogging' in instance.properties.additional_properties:
                del instance.properties.additional_properties['Network.AdditionalLogs.EnableFatFlowLogging']

        if has_value(args.enable_udp_log_optimization):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            if args.enable_udp_log_optimization:
                instance.properties.additional_properties['Network.AdditionalLogs.EnableUdpLogOptimization'] = 'true'
            elif 'Network.AdditionalLogs.EnableUdpLogOptimization' in instance.properties.additional_properties:
                del instance.properties.additional_properties['Network.AdditionalLogs.EnableUdpLogOptimization']


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
    poller = client.begin_create_or_update(resource_group_name, azure_firewall_name, af)
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
        result = sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, resource_name, af).result()
        if next((x for x in getattr(result, 'ip_configurations') if x.name.lower() == item_name.lower()), None):
            raise CLIError(f"Failed to delete '{item_name}' on '{resource_name}'")


def build_af_rule_list(item_param_name, collection_param_name):
    import sys

    def list_func(cmd, resource_group_name, firewall_name, collection_name):
        client = network_client_factory(cmd.cli_ctx).azure_firewalls
        af = client.get(resource_group_name, firewall_name)
        return _find_item_at_path(af, f'{collection_param_name}.{collection_name}')

    func_name = f'list_af_{item_param_name}s'
    setattr(sys.modules[__name__], func_name, list_func)
    return func_name


def build_af_rule_show(item_param_name, collection_param_name):
    import sys

    def show_func(cmd, resource_group_name, firewall_name, collection_name, item_name):
        client = network_client_factory(cmd.cli_ctx).azure_firewalls
        af = client.get(resource_group_name, firewall_name)
        return _find_item_at_path(af, f'{collection_param_name}.{collection_name}.rules.{item_name}')

    func_name = f'show_af_{item_param_name}'
    setattr(sys.modules[__name__], func_name, show_func)
    return func_name


def build_af_rule_delete(item_param_name, collection_param_name):
    import sys

    def delete_func(cmd, resource_group_name, firewall_name, collection_name, item_name):
        client = network_client_factory(cmd.cli_ctx).azure_firewalls
        af = client.get(resource_group_name, firewall_name)
        collection = _find_item_at_path(af, f'{collection_param_name}.{collection_name}')
        collection.rules = [rule for rule in collection.rules if rule.name != item_name]
        client.begin_create_or_update(resource_group_name, firewall_name, af)

    func_name = f'delete_af_{item_param_name}'
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
    af = client.begin_create_or_update(resource_group_name, firewall_name, af).result()
    return _find_item_at_path(af, f'{collection_param_name}.{collection_name}.rules.{item_name}')


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
    return client.begin_create_or_update(resource_group_name, azure_firewall_name, firewall)


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
    return client.begin_create_or_update(resource_group_name, azure_firewall_name, firewall)
# endregion


# region AzureFirewallPolicies
# pylint: disable=too-many-locals
def create_azure_firewall_policies(cmd, resource_group_name, firewall_policy_name, base_policy=None,
                                   threat_intel_mode=None, location=None, tags=None, ip_addresses=None,
                                   fqdns=None,
                                   dns_servers=None, enable_dns_proxy=None,
                                   sku=None, intrusion_detection_mode=None, sql=None,
                                   key_vault_secret_id=None, certificate_name=None, user_assigned_identity=None):
    client = network_client_factory(cmd.cli_ctx).firewall_policies
    (FirewallPolicy,
     SubResource,
     FirewallPolicyThreatIntelWhitelist,
     DnsSettings,
     FirewallPolicySku,
     ManagedServiceIdentityUserAssignedIdentitiesValue,
     ManagedServiceIdentity) = cmd.get_models('FirewallPolicy',
                                              'SubResource',
                                              'FirewallPolicyThreatIntelWhitelist',
                                              'DnsSettings',
                                              'FirewallPolicySku',
                                              # pylint: disable=line-too-long
                                              'Components1Jq1T4ISchemasManagedserviceidentityPropertiesUserassignedidentitiesAdditionalproperties',
                                              'ManagedServiceIdentity')
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
    if cmd.supported_api_version(min_api='2021-08-01'):
        if sku is not None:
            firewall_policy.sku = FirewallPolicySku(tier=sku)

        if intrusion_detection_mode is not None:
            (FirewallPolicyIntrusionDetection,
             FirewallPolicyIntrusionDetectionConfiguration) = \
                cmd.get_models('FirewallPolicyIntrusionDetection',
                               'FirewallPolicyIntrusionDetectionConfiguration')
            firewall_policy.intrusion_detection = FirewallPolicyIntrusionDetection(
                mode=intrusion_detection_mode,
                configuration=FirewallPolicyIntrusionDetectionConfiguration()
            )

        if certificate_name is not None and key_vault_secret_id is not None:
            FirewallPolicyTransportSecurity, FirewallPolicyCertificateAuthority = \
                cmd.get_models('FirewallPolicyTransportSecurity', 'FirewallPolicyCertificateAuthority')
            certificate_auth = FirewallPolicyCertificateAuthority(key_vault_secret_id=key_vault_secret_id,
                                                                  name=certificate_name)
            firewall_policy.transport_security = FirewallPolicyTransportSecurity(certificate_authority=certificate_auth)

    if cmd.supported_api_version(min_api='2021-03-01'):
        if sql is not None:
            FirewallPolicySQL = cmd.get_models('FirewallPolicySQL')
            firewall_policy.sql = FirewallPolicySQL(allow_sql_redirect=sql)

    # identity
    if user_assigned_identity is not None:
        user_assigned_indentity_instance = ManagedServiceIdentityUserAssignedIdentitiesValue()
        user_assigned_identities_instance = {}
        user_assigned_identities_instance[user_assigned_identity] = user_assigned_indentity_instance
        identity_instance = ManagedServiceIdentity(
            type="UserAssigned",
            user_assigned_identities=user_assigned_identities_instance
        )
        firewall_policy.identity = identity_instance

    return client.begin_create_or_update(resource_group_name, firewall_policy_name, firewall_policy)


# pylint: disable=too-many-locals
def update_azure_firewall_policies(cmd,
                                   instance, tags=None, threat_intel_mode=None, ip_addresses=None,
                                   fqdns=None,
                                   dns_servers=None, enable_dns_proxy=None,
                                   sku=None, intrusion_detection_mode=None, sql=None,
                                   key_vault_secret_id=None, certificate_name=None, user_assigned_identity=None):

    (FirewallPolicyThreatIntelWhitelist, FirewallPolicySku) = cmd.get_models('FirewallPolicyThreatIntelWhitelist',
                                                                             'FirewallPolicySku')
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
    if cmd.supported_api_version(min_api='2021-08-01'):
        if sku is not None:
            instance.sku = FirewallPolicySku(tier=sku)

        if intrusion_detection_mode is not None:
            if instance.intrusion_detection is not None:
                instance.intrusion_detection.mode = intrusion_detection_mode
            else:
                (FirewallPolicyIntrusionDetection, FirewallPolicyIntrusionDetectionConfiguration) = \
                    cmd.get_models('FirewallPolicyIntrusionDetection', 'FirewallPolicyIntrusionDetectionConfiguration')
                instance.intrusion_detection = FirewallPolicyIntrusionDetection(
                    mode=intrusion_detection_mode,
                    configuration=FirewallPolicyIntrusionDetectionConfiguration()
                )
        if certificate_name is not None and key_vault_secret_id is not None:
            FirewallPolicyTransportSecurity, FirewallPolicyCertificateAuthority = \
                cmd.get_models('FirewallPolicyTransportSecurity', 'FirewallPolicyCertificateAuthority')
            certificate_auth = FirewallPolicyCertificateAuthority(key_vault_secret_id=key_vault_secret_id,
                                                                  name=certificate_name)
            instance.transport_security = FirewallPolicyTransportSecurity(certificate_authority=certificate_auth)

    if cmd.supported_api_version(min_api='2021-03-01'):
        if sql is not None:
            FirewallPolicySQL = cmd.get_models('FirewallPolicySQL')
            instance.sql = FirewallPolicySQL(allow_sql_redirect=sql)

    # identity
    (ManagedServiceIdentityUserAssignedIdentitiesValue,
     ManagedServiceIdentity) = cmd.get_models('Components1Jq1T4ISchemasManagedserviceidentity\
         PropertiesUserassignedidentitiesAdditionalproperties',
                                              'ManagedServiceIdentity')
    if user_assigned_identity is not None:
        user_assigned_indentity_instance = ManagedServiceIdentityUserAssignedIdentitiesValue()
        user_assigned_identities_instance = {}
        user_assigned_identities_instance[user_assigned_identity] = user_assigned_indentity_instance
        identity_instance = ManagedServiceIdentity(
            type="UserAssigned",
            user_assigned_identities=user_assigned_identities_instance
        )
        instance.identity = identity_instance

    return instance


def set_azure_firewall_policies(cmd, resource_group_name, firewall_policy_name, parameters):
    if parameters.identity is None and parameters.sku.tier == 'Premium':
        ManagedServiceIdentity = cmd.get_models('ManagedServiceIdentity')

        identity = ManagedServiceIdentity(type="None", user_assigned_identities=None)
        parameters.identity = identity

    client = network_client_factory(cmd.cli_ctx).firewall_policies
    return client.begin_create_or_update(resource_group_name, firewall_policy_name, parameters)


def list_azure_firewall_policies(cmd, resource_group_name=None):
    client = network_client_factory(cmd.cli_ctx).firewall_policies
    if resource_group_name is not None:
        return client.list(resource_group_name)
    return client.list_all()


def add_firewall_policy_intrusion_detection_config(cmd,
                                                   resource_group_name,
                                                   firewall_policy_name,
                                                   private_ranges=None,
                                                   signature_id=None,
                                                   signature_mode=None,
                                                   bypass_rule_name=None,
                                                   bypass_rule_description=None,
                                                   bypass_rule_protocol=None,
                                                   bypass_rule_source_addresses=None,
                                                   bypass_rule_destination_addresses=None,
                                                   bypass_rule_destination_ports=None,
                                                   bypass_rule_source_ip_groups=None,
                                                   bypass_rule_destination_ip_groups=None):

    from azure.cli.core.azclierror import RequiredArgumentMissingError, InvalidArgumentValueError

    client = network_client_factory(cmd.cli_ctx).firewall_policies
    firewall_policy = client.get(resource_group_name, firewall_policy_name)

    if firewall_policy.intrusion_detection is None:
        raise RequiredArgumentMissingError('Intrusion detection mode is not set. Setting it by update command first')

    if signature_id is not None and signature_mode is not None:
        for overrided_signature in firewall_policy.intrusion_detection.configuration.signature_overrides:
            if overrided_signature.id == signature_id:
                raise InvalidArgumentValueError(
                    f'Signature ID {signature_id} exists. Delete it first or try update instead')

        FirewallPolicyIntrusionDetectionSignatureSpecification = \
            cmd.get_models('FirewallPolicyIntrusionDetectionSignatureSpecification')
        signature_override = FirewallPolicyIntrusionDetectionSignatureSpecification(
            id=signature_id,
            mode=signature_mode
        )
        firewall_policy.intrusion_detection.configuration.signature_overrides.append(signature_override)

    if bypass_rule_name is not None:
        FirewallPolicyIntrusionDetectionBypassTrafficSpecifications = \
            cmd.get_models('FirewallPolicyIntrusionDetectionBypassTrafficSpecifications')
        bypass_traffic = FirewallPolicyIntrusionDetectionBypassTrafficSpecifications(
            name=bypass_rule_name,
            description=bypass_rule_description,
            protocol=bypass_rule_protocol,
            source_addresses=bypass_rule_source_addresses,
            destination_addresses=bypass_rule_destination_addresses,
            destination_ports=bypass_rule_destination_ports,
            source_ip_groups=bypass_rule_source_ip_groups,
            destination_ip_groups=bypass_rule_destination_ip_groups,
        )
        firewall_policy.intrusion_detection.configuration.bypass_traffic_settings.append(bypass_traffic)

    if private_ranges is not None:
        __private_ranges = [x.strip() for x in private_ranges.split(",")]
        firewall_policy.intrusion_detection.configuration.private_ranges = __private_ranges

    result = sdk_no_wait(False,
                         client.begin_create_or_update,
                         resource_group_name,
                         firewall_policy_name,
                         firewall_policy).result()
    return result.intrusion_detection.configuration


def list_firewall_policy_intrusion_detection_config(cmd, resource_group_name, firewall_policy_name):
    client = network_client_factory(cmd.cli_ctx).firewall_policies
    firewall_policy = client.get(resource_group_name, firewall_policy_name)

    if firewall_policy.intrusion_detection is None:
        return []

    return firewall_policy.intrusion_detection.configuration


def remove_firewall_policy_intrusion_detection_config(cmd,
                                                      resource_group_name,
                                                      firewall_policy_name,
                                                      signature_id=None,
                                                      bypass_rule_name=None):
    from azure.cli.core.azclierror import RequiredArgumentMissingError, InvalidArgumentValueError

    client = network_client_factory(cmd.cli_ctx).firewall_policies
    firewall_policy = client.get(resource_group_name, firewall_policy_name)

    if firewall_policy.intrusion_detection is None:
        raise RequiredArgumentMissingError('Intrusion detection mode is not set. Setting it by update command first')

    if signature_id is not None:
        signatures = firewall_policy.intrusion_detection.configuration.signature_overrides
        new_signatures = [s for s in signatures if s.id != signature_id]
        if len(signatures) == len(new_signatures):
            raise InvalidArgumentValueError(f"Signature ID {signature_id} doesn't exist")
        firewall_policy.intrusion_detection.configuration.signature_overrides = new_signatures

    if bypass_rule_name is not None:
        bypass_settings = firewall_policy.intrusion_detection.configuration.bypass_traffic_settings
        new_bypass_settings = [s for s in bypass_settings if s.name != bypass_rule_name]
        if len(bypass_settings) == len(new_bypass_settings):
            raise InvalidArgumentValueError(f"Bypass rule with name {signature_id} doesn't exist")
        firewall_policy.intrusion_detection.configuration.bypass_traffic_settings = new_bypass_settings

    result = sdk_no_wait(False,
                         client.begin_create_or_update,
                         resource_group_name,
                         firewall_policy_name,
                         firewall_policy).result()
    return result.intrusion_detection.configuration


def create_azure_firewall_policy_rule_collection_group(cmd, resource_group_name, firewall_policy_name,
                                                       rule_collection_group_name, priority):
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    FirewallPolicyRuleCollectionGroup = cmd.get_models('FirewallPolicyRuleCollectionGroup')
    rule_group = FirewallPolicyRuleCollectionGroup(priority=priority,
                                                   name=rule_collection_group_name)
    return client.begin_create_or_update(resource_group_name,
                                         firewall_policy_name, rule_collection_group_name, rule_group)


def update_azure_firewall_policy_rule_collection_group(instance, priority=None, tags=None):
    if tags is not None:
        instance.tags = tags
    if priority is not None:
        instance.priority = priority
    return instance


def add_azure_firewall_policy_nat_rule_collection(cmd, resource_group_name, firewall_policy_name,
                                                  rule_collection_group_name, ip_protocols,
                                                  rule_collection_name, rule_priority, translated_address=None,
                                                  translated_fqdn=None, translated_port=None, nat_action=None,
                                                  rule_name=None, description=None,
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
    return client.begin_create_or_update(resource_group_name, firewall_policy_name,
                                         rule_collection_group_name, rule_collection_group)


# pylint: disable=too-many-locals
def add_azure_firewall_policy_filter_rule_collection(cmd, resource_group_name, firewall_policy_name,
                                                     rule_collection_group_name, rule_collection_name,
                                                     rule_priority, filter_action=None, rule_name=None,
                                                     rule_type=None, description=None, ip_protocols=None,
                                                     source_addresses=None, destination_addresses=None,
                                                     destination_ports=None,
                                                     protocols=None, fqdn_tags=None, target_fqdns=None,
                                                     source_ip_groups=None, destination_ip_groups=None,
                                                     destination_fqdns=None,
                                                     target_urls=None,
                                                     enable_tls_inspection=False, web_categories=None):
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
                           destination_ip_groups=destination_ip_groups,
                           destination_fqdns=destination_fqdns)
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
                               target_urls=target_urls,
                               source_ip_groups=source_ip_groups,
                               terminate_tls=enable_tls_inspection,
                               web_categories=web_categories)
    filter_rule_collection = FirewallPolicyFilterRuleCollection(name=rule_collection_name,
                                                                priority=rule_priority,
                                                                rule_collection_type="FirewallPolicyFilterRule",
                                                                action=FirewallPolicyFilterRuleCollectionAction(
                                                                    type=filter_action
                                                                ),
                                                                rules=[rule])
    rule_collection_group.rule_collections.append(filter_rule_collection)
    return client.begin_create_or_update(resource_group_name, firewall_policy_name,
                                         rule_collection_group_name, rule_collection_group)


def remove_azure_firewall_policy_rule_collection(cmd, resource_group_name, firewall_policy_name,
                                                 rule_collection_group_name, rule_collection_name):
    client = network_client_factory(cmd.cli_ctx).firewall_policy_rule_collection_groups
    rule_collection_group = client.get(resource_group_name, firewall_policy_name, rule_collection_group_name)
    for rule_collection in rule_collection_group.rule_collections:
        if rule_collection.name == rule_collection_name:
            rule_collection_group.rule_collections.remove(rule_collection)
    return client.begin_create_or_update(resource_group_name, firewall_policy_name,
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
                                          source_ip_groups=None, destination_ip_groups=None, destination_fqdns=None,
                                          translated_address=None, translated_port=None, translated_fqdn=None,
                                          target_urls=None, enable_tls_inspection=False, web_categories=None):
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
                           destination_ip_groups=destination_ip_groups,
                           destination_fqdns=destination_fqdns)
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
                               target_urls=target_urls,
                               source_ip_groups=source_ip_groups,
                               terminate_tls=enable_tls_inspection,
                               web_categories=web_categories)
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
                       source_ip_groups=source_ip_groups,
                       translated_fqdn=translated_fqdn)
    target_rule_collection.rules.append(rule)
    return client.begin_create_or_update(resource_group_name, firewall_policy_name,
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
    return client.begin_create_or_update(resource_group_name, firewall_policy_name,
                                         rule_collection_group_name, rule_collection_group)


# pylint: disable=too-many-locals
def update_azure_firewall_policy_filter_rule(cmd, instance, rule_collection_name, rule_name,
                                             description=None, ip_protocols=None, source_addresses=None,
                                             destination_addresses=None, destination_ports=None,
                                             protocols=None, fqdn_tags=None, target_fqdns=None,
                                             source_ip_groups=None, destination_ip_groups=None, destination_fqdns=None,
                                             translated_address=None, translated_port=None, translated_fqdn=None,
                                             target_urls=None, enable_tls_inspection=None, web_categories=None):
    (NetworkRule,
     FirewallPolicyRuleApplicationProtocol,
     ApplicationRule,
     NatRule) = cmd.get_models('NetworkRule', 'FirewallPolicyRuleApplicationProtocol',
                               'ApplicationRule', 'NatRule')
    target_rule_collection = None
    for rule_collection in instance.rule_collections:
        if rule_collection.name == rule_collection_name:
            target_rule_collection = rule_collection

    if target_rule_collection is None:
        raise UserFault("Cannot find corresponding rule, please check parameters")

    for i, rule in enumerate(target_rule_collection.rules):
        if rule_name == rule.name:
            new_rule = {}
            if rule.rule_type == "NetworkRule":
                new_rule = NetworkRule(name=rule_name,
                                       description=(description or rule.description),
                                       rule_type=rule.rule_type,
                                       ip_protocols=(ip_protocols or rule.ip_protocols),
                                       source_addresses=(source_addresses or rule.source_addresses),
                                       destination_addresses=(destination_addresses or rule.destination_addresses),
                                       destination_ports=(destination_ports or rule.destination_ports),
                                       source_ip_groups=(source_ip_groups or rule.source_ip_groups),
                                       destination_ip_groups=(destination_ip_groups or rule.destination_ip_groups),
                                       destination_fqdns=(destination_fqdns or rule.destination_fqdns))
            elif rule.rule_type == 'ApplicationRule':
                def map_application_rule_protocol(item):
                    return FirewallPolicyRuleApplicationProtocol(protocol_type=item['protocol_type'],
                                                                 port=int(item['port']))

                protocols = list(map(map_application_rule_protocol, protocols))
                new_rule = ApplicationRule(name=rule_name,
                                           description=(description or rule.description),
                                           rule_type=rule.rule_type,
                                           source_addresses=(source_addresses or rule.source_addresses),
                                           protocols=(protocols or rule.protocols),
                                           destination_addresses=(destination_addresses or rule.destination_addresses),
                                           fqdn_tags=(fqdn_tags or rule.fqdn_tags),
                                           target_fqdns=(target_fqdns or rule.target_fqdns),
                                           target_urls=(target_urls or rule.target_urls),
                                           source_ip_groups=(source_ip_groups or rule.source_ip_groups),
                                           terminate_tls=(enable_tls_inspection or rule.terminate_tls),
                                           web_categories=(web_categories or rule.web_categories))
            elif rule.rule_type == 'NatRule':
                new_rule = NatRule(name=rule_name,
                                   description=(description or rule.description),
                                   rule_type=rule.rule_type,
                                   ip_protocols=(ip_protocols or rule.ip_protocols),
                                   source_addresses=(source_addresses or rule.source_addresses),
                                   destination_addresses=(destination_addresses or rule.destination_addresses),
                                   destination_ports=(destination_ports or rule.destination_ports),
                                   translated_address=(translated_address or rule.translated_address),
                                   translated_port=(translated_port or rule.translated_port),
                                   translated_fqdn=(translated_fqdn or rule.translated_fqdn),
                                   source_ip_groups=(source_ip_groups or rule.source_ip_groups))
            if new_rule:
                target_rule_collection.rules[i] = copy.deepcopy(new_rule)
                return instance
            raise ServiceError(f'Undefined rule_type : {rule.rule_type}')

    raise UserFault(f'{rule_name} does not exist!!!')
# endregion
