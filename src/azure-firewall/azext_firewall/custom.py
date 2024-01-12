# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access, line-too-long, raise-missing-from
# pylint: disable=too-many-lines, too-many-branches, too-many-statements

import copy
from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.aaz import has_value, register_command
from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import UserFault, ServiceError, ValidationError, ArgumentUsageError
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import resource_id
from ._client_factory import network_client_factory
from .aaz.latest.network.firewall import Create as _AzureFirewallCreate, Update as _AzureFirewallUpdate, \
    Show as _AzureFirewallShow
from .aaz.latest.network.firewall.policy import Create as _AzureFirewallPoliciesCreate, \
    Update as _AzureFirewallPoliciesUpdate
from .aaz.latest.network.firewall.policy.rule_collection_group import Create as _RuleCollectionGroupCreate, \
    Update as _RuleCollectionGroupUpdate
from .aaz.latest.network.firewall.policy.intrusion_detection import Show as _IntrusionDetectionShow

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
        from azure.cli.core.aaz import AAZListArg, AAZStrArg, AAZBoolArg, AAZResourceIdArg, AAZResourceIdArgFormat, \
            AAZIntArg, AAZIntArgFormat
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
        args_schema.enable_explicit_proxy = AAZBoolArg(
            options=["--enable-explicit-proxy"],
            arg_group="Explicit Proxy",
            help="When set to true, explicit proxy mode is enabled.",
        )
        args_schema.http_port = AAZIntArg(
            options=["--http-port"],
            arg_group="Explicit Proxy",
            help="Port number for explicit proxy http protocol, cannot be greater than 64000.",
            fmt=AAZIntArgFormat(
                maximum=64000,
                minimum=0,
            ),
        )
        args_schema.https_port = AAZBoolArg(
            options=["--https-port"],
            arg_group="Explicit Proxy",
            help="Port number for explicit proxy https protocol, cannot be greater than 64000.",
            fmt=AAZIntArgFormat(
                maximum=64000,
                minimum=0,
            ),
        )
        args_schema.enable_pac_file = AAZBoolArg(
            options=["--enable-pac-file"],
            arg_group="Explicit Proxy",
            help="When set to true, pac file port and url needs to be provided.",
        )
        args_schema.pac_file_port = AAZIntArg(
            options=["--pac-file-port"],
            arg_group="Explicit Proxy",
            help="Port number for firewall to serve PAC file.",
        )
        args_schema.pac_file = AAZStrArg(
            options=["--pac-file"],
            arg_group="Explicit Proxy",
            help="SAS URL for PAC file.",
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

        if has_value(args.enable_explicit_proxy):
            args.additional_properties['Network.ExplicitProxy.EnableExplicitProxy'] = args.enable_explicit_proxy
        if has_value(args.http_port):
            args.additional_properties['Network.ExplicitProxy.HttpPort'] = args.http_port
        if has_value(args.https_port):
            args.additional_properties['Network.ExplicitProxy.HttpsPort'] = args.https_port
        if has_value(args.enable_pac_file):
            args.additional_properties['Network.ExplicitProxy.EnablePacFile'] = args.enable_pac_file
        if has_value(args.pac_file_port):
            args.additional_properties['Network.ExplicitProxy.PacFilePort'] = args.pac_file_port
        if has_value(args.pac_file):
            args.additional_properties['Network.ExplicitProxy.PacFile'] = args.pac_file


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
            nullable=True, )
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


def update_af_management_ip_configuration(cmd, instance, public_ip_address=None, virtual_network_name=None,
                                          # pylint: disable=unused-argument
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


def delete_af_ip_configuration(cmd, resource_group_name, resource_name, item_name,
                               no_wait=False):  # pylint: disable=unused-argument
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


@register_command(
    "network firewall threat-intel-allowlist create",
    is_preview=True,
)
class ThreatIntelAllowListCreate(_AzureFirewallUpdate):
    """Create an Azure Firewall Threat Intelligence Allow List.

    :example: Create a threat intelligence allow list
        az network firewall threat-intel-allowlist create -g MyResourceGroup -n MyFirewall --ip-addresses 10.0.0.0 10.0.0.1 --fqdns *.microsoft.com www.bing.com *google.com
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._id_part = None
        args_schema.ip_addresses = AAZListArg(
            options=['--ip-addresses'],
            help='Space-separated list of IPv4 addresses.'
        )
        args_schema.ip_addresses.Element = AAZStrArg()
        args_schema.fqdns = AAZListArg(
            options=['--fqdns'],
            help='Space-separated list of FQDNs'
        )
        args_schema.fqdns.Element = AAZStrArg()
        args_schema.firewall_policy._registered = False
        args_schema.threat_intel_mode._registered = False
        args_schema.addresses._registered = False
        args_schema.public_ip_count._registered = False
        args_schema.additional_properties._registered = False
        args_schema.virtual_hub._registered = False
        args_schema.zones._registered = False
        args_schema.tags._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args
        if has_value(args.ip_addresses):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            instance.properties.additional_properties['ThreatIntel.Whitelist.IpAddresses'] = ', '.join(args.ip_addresses.to_serialized_data())
        if has_value(args.fqdns):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            instance.properties.additional_properties['ThreatIntel.Whitelist.FQDNs'] = ', '.join(args.fqdns.to_serialized_data())

    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        output.update({
            **output.pop('additionalProperties')
        })
        return output


@register_command(
    "network firewall threat-intel-allowlist update",
    is_preview=True,
)
class ThreatIntelAllowListUpdate(_AzureFirewallUpdate):
    """Update Azure Firewall Threat Intelligence Allow List.

    :example: Update a threat intelligence allow list
        az network firewall threat-intel-allowlist update -g MyResourceGroup -n MyFirewall --ip-addresses
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZListArg, AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._id_part = None
        args_schema.ip_addresses = AAZListArg(
            options=['--ip-addresses'],
            help='Space-separated list of IPv4 addresses.'
        )
        args_schema.ip_addresses.Element = AAZStrArg()
        args_schema.fqdns = AAZListArg(
            options=['--fqdns'],
            help='Space-separated list of FQDNs'
        )
        args_schema.fqdns.Element = AAZStrArg()
        args_schema.firewall_policy._registered = False
        args_schema.threat_intel_mode._registered = False
        args_schema.addresses._registered = False
        args_schema.public_ip_count._registered = False
        args_schema.additional_properties._registered = False
        args_schema.virtual_hub._registered = False
        args_schema.zones._registered = False
        args_schema.tags._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args
        if has_value(args.ip_addresses):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            instance.properties.additional_properties['ThreatIntel.Whitelist.IpAddresses'] = ', '.join(
                args.ip_addresses.to_serialized_data())
        if has_value(args.fqdns):
            if not has_value(instance.properties.additional_properties):
                instance.properties.additional_properties = {}
            instance.properties.additional_properties['ThreatIntel.Whitelist.FQDNs'] = ', '.join(
                args.fqdns.to_serialized_data())

    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        output.update({
            **output.pop('additionalProperties')
        })
        return output


@register_command(
    "network firewall threat-intel-allowlist show",
    is_preview=True,
)
class ThreatIntelAllowListShow(_AzureFirewallShow):
    """
    Get the details of an Azure Firewall Threat Intelligence Allow List.
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._id_part = None
        return args_schema

    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        return output['additionalProperties']


@register_command(
    "network firewall threat-intel-allowlist delete",
    is_preview=True,
)
class ThreatIntelAllowListDelete(_AzureFirewallUpdate):
    """
    Delete an Azure Firewall Threat Intelligence Allow List.
    """
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._id_part = None
        args_schema.firewall_policy._registered = False
        args_schema.threat_intel_mode._registered = False
        args_schema.addresses._registered = False
        args_schema.public_ip_count._registered = False
        args_schema.additional_properties._registered = False
        args_schema.virtual_hub._registered = False
        args_schema.zones._registered = False
        args_schema.tags._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        if has_value(instance.properties.additional_properties):
            instance.properties.additional_properties._data.pop('ThreatIntel.Whitelist.IpAddresses', None)
            instance.properties.additional_properties._data.pop('ThreatIntel.Whitelist.FQDNs', None)

    def _output(self, *args, **kwargs):
        output = super()._output(*args, **kwargs)
        output.update({
            **output.pop('additionalProperties')
        })
        return output
# endregion


# region AzureFirewallPolicies
# pylint: disable=too-many-locals
class AzureFirewallPoliciesCreate(_AzureFirewallPoliciesCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.identity = AAZResourceIdArg(
            options=['--identity'],
            help="Name or ID of the ManagedIdentity Resource.",
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/"
                         "Microsoft.ManagedIdentity/userAssignedIdentities/{}",
            )
        )
        args_schema.base_policy._fmt = AAZResourceIdArgFormat(
            template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network"
                     "/firewallPolicies/{}",
        )
        args_schema.identity_type._registered = False
        args_schema.user_assigned_identities._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.identity):
            args.identity_type = "UserAssigned"
            args.user_assigned_identities = {args.identity.to_serialized_data(): {}}

        if has_value(args.dns_servers):
            if not has_value(args.enable_dns_proxy):
                args.enable_dns_proxy = False


class AzureFirewallPoliciesUpdate(_AzureFirewallPoliciesUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.identity = AAZResourceIdArg(
            options=['--identity'],
            help="Name or ID of the ManagedIdentity Resource.",
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/"
                         "Microsoft.ManagedIdentity/userAssignedIdentities/{}",
            )
        )
        args_schema.identity_type._registered = False
        args_schema.user_assigned_identities._registered = False
        args_schema.configuration._registered = False

        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.identity):
            args.identity_type = "UserAssigned"
            args.user_assigned_identities = {args.identity.to_serialized_data(): {}}
        elif args.sku == 'Premium':
            args.identity_type = "None"
            args.user_assigned_identities = None


class IntrusionDetectionAdd(_AzureFirewallPoliciesUpdate):
    """
    Add overrided intrusion signature or a bypass rule or private ranges list for intrusion detection
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg, AAZArgEnum, AAZResourceIdArg, AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._options = ['--policy-name']
        args_schema.signature_id = AAZStrArg(
            options=['--signature-id'],
            help="Signature id."
        )
        args_schema.signature_mode = AAZStrArg(
            options=['--mode'],
            help="The signature state"
        )
        args_schema.signature_mode.enum = AAZArgEnum({'Off': 'off', 'Alert': 'Alert', 'Deny': 'Deny'})
        args_schema.bypass_rule_name = AAZStrArg(
            options=['--rule-name'],
            help="Name of the bypass traffic rule"
        )
        args_schema.bypass_rule_description = AAZStrArg(
            options=['--rule-description'],
            help="Description of the bypass traffic rule"
        )
        args_schema.bypass_rule_protocol = AAZStrArg(
            options=['--rule-protocol'],
            help="The rule bypass protocol"
        )
        args_schema.bypass_rule_protocol.enum = AAZArgEnum({'TCP': 'TCP', 'UDP': 'UDP', 'ICMP': 'ICMP', 'Any': 'Any'})
        args_schema.bypass_rule_source_addresses = AAZListArg(
            options=['--rule-src-addresses'],
            help="Space-separated list of source IP addresses or ranges for this rule"
        )
        args_schema.bypass_rule_source_addresses.Element = AAZStrArg()
        args_schema.bypass_rule_destination_addresses = AAZListArg(
            options=['--rule-dest-addresses'],
            help="Space-separated list of destination IP addresses or ranges for this rule"
        )
        args_schema.bypass_rule_destination_addresses.Element = AAZStrArg()
        args_schema.bypass_rule_destination_ports = AAZListArg(
            options=['--rule-dest-ports'],
            help="Space-separated list of destination ports or ranges"
        )
        args_schema.bypass_rule_destination_ports.Element = AAZStrArg()
        args_schema.bypass_rule_source_ip_groups = AAZListArg(
            options=['--rule-src-ip-groups'],
            help="Space-separated list of source IpGroups"
        )
        args_schema.bypass_rule_source_ip_groups.Element = AAZStrArg()
        args_schema.bypass_rule_destination_ip_groups = AAZListArg(
            options=['--rule-dest-ip-groups'],
            help="Space-separated list of destination IpGroups for this rule"
        )
        args_schema.bypass_rule_destination_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.user_assigned_identities._registered = False

        return args_schema

    def pre_instance_update(self, instance):
        from azure.cli.core.azclierror import RequiredArgumentMissingError, InvalidArgumentValueError
        args = self.ctx.args
        if not has_value(instance.properties.intrusion_detection):
            raise RequiredArgumentMissingError(
                'Intrusion detection mode is not set. Setting it by update command first')

        if has_value(args.signature_id) and has_value(args.signature_mode):
            signature_override = {
                'id': args.signature_id,
                'mode': args.signature_mode
            }
            if has_value(instance.properties.intrusion_detection.configuration):
                for overrided_signature in instance.properties.intrusion_detection.configuration.signature_overrides:
                    if overrided_signature.id == args.signature_id:
                        raise InvalidArgumentValueError(
                            f'Signature ID {args.signature_id} exists. Delete it first or try update instead')
                instance.properties.intrusion_detection.configuration.signature_overrides.append(signature_override)
            else:
                instance.properties.intrusion_detection.configuration = {
                    'signatureOverrides': [signature_override]
                }

        if has_value(args.bypass_rule_name):
            bypass_traffic = {
                'name': args.bypass_rule_name,
                'description': args.bypass_rule_description,
                'protocol': args.bypass_rule_protocol,
                'sourceAddresses': args.bypass_rule_source_addresses,
                'destinationAddresses': args.bypass_rule_destination_addresses,
                'destinationPorts': args.bypass_rule_destination_ports,
                'sourceIpGroups': args.bypass_rule_source_ip_groups,
                'destinationIpGroups': args.bypass_rule_destination_ip_groups,
            }
            instance.properties.intrusion_detection.configuration.bypass_traffic_settings.append(bypass_traffic)

        if has_value(args.private_ranges):
            instance.properties.intrusion_detection.configuration.private_ranges = args.private_ranges

    def _output(self, *args, **kwargs):
        return self.deserialize_output(
            self.ctx.vars.instance.properties.intrusion_detection.configuration, client_flatten=True)


@register_command(
    "network firewall policy intrusion-detection list",
    is_preview=True,
)
class IntrusionDetectionList(_IntrusionDetectionShow):
    """
    List all intrusion detection configuration
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._options = ['--policy-name']
        return args_schema

    def _output(self, *args, **kwargs):
        if not has_value(self.ctx.vars.instance.properties.intrusion_detection.configuration):
            return []
        return self.deserialize_output(
            self.ctx.vars.instance.properties.intrusion_detection.configuration, client_flatten=True)


class IntrusionDetectionRemove(_AzureFirewallPoliciesUpdate):
    """
    Remove overrided intrusion signature or a bypass rule
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._options = ['--policy-name']
        args_schema.signature_id = AAZStrArg(
            options=['--signature-id'],
            help="Signature id."
        )
        args_schema.bypass_rule_name = AAZStrArg(
            options=['--rule-name'],
            help="Name of the bypass traffic rule"
        )
        args_schema.user_assigned_identities._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        from azure.cli.core.azclierror import RequiredArgumentMissingError, InvalidArgumentValueError
        args = self.ctx.args
        if not has_value(instance.properties.intrusion_detection):
            raise RequiredArgumentMissingError(
                'Intrusion detection mode is not set. Setting it by update command first')

        if has_value(args.signature_id):
            signatures = instance.properties.intrusion_detection.configuration.signature_overrides
            new_signatures = [s for s in signatures if s.id != args.signature_id]
            if len(signatures) == len(new_signatures):
                raise InvalidArgumentValueError(f"Signature ID {args.signature_id} doesn't exist")
            instance.properties.intrusion_detection.configuration.signature_overrides = new_signatures

        if has_value(args.bypass_rule_name):
            bypass_settings = instance.properties.intrusion_detection.configuration.bypass_traffic_settings
            new_bypass_settings = [s for s in bypass_settings if s.name != args.bypass_rule_name]
            if len(bypass_settings) == len(new_bypass_settings):
                raise InvalidArgumentValueError(f"Bypass rule with name {args.bypass_rule_name} doesn't exist")
            instance.properties.intrusion_detection.configuration.bypass_traffic_settings = new_bypass_settings

    def _output(self, *args, **kwargs):
        return self.deserialize_output(
            self.ctx.vars.instance.properties.intrusion_detection.configuration, client_flatten=True)


class RuleCollectionGroupCreate(_RuleCollectionGroupCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.priority._required = True
        args_schema.rule_collections._registered = False
        return args_schema


class RuleCollectionGroupUpdate(_RuleCollectionGroupUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZDictArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.tags = AAZDictArg(
            options=["--tags"],
            help="Space-separated tags: key[=value] [key[=value] ...].",
        )
        args_schema.tags.Element = AAZStrArg()
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        args = self.ctx.args
        if has_value(args.tags):
            instance.tags = args.tags
        if has_value(args.priority):
            instance.properties.priority = args.priority


@register_command(
    "network firewall policy rule-collection-group collection add-nat-collection",
    is_preview=True,
)
class NatCollectionAdd(_RuleCollectionGroupUpdate):
    """
    Add a NAT collection into an Azure firewall policy rule collection group.

    :example: Add a NAT collection into the rule collection group
        az network firewall policy rule-collection-group collection add-nat-collection -n
        nat_collection --collection-priority 10003 --policy-name {policy} -g {rg} --rule-collection-
        group-name {collectiongroup} --action DNAT --rule-name network_rule --description "test"
        --destination-addresses "202.120.36.15" --source-addresses "202.120.36.13" "202.120.36.14"
        --translated-address 128.1.1.1 --translated-port 1234 --destination-ports 12000 12001 --ip-
        protocols TCP UDP
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg, AAZArgEnum, AAZResourceIdArg, AAZResourceIdArgFormat, \
            AAZIntArg, AAZIntArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._options = ['--name', '-n']
        args_schema.name.help = 'The name of the collection in Firewall Policy Rule Collection Group.'
        args_schema.name._arg_group = ""
        args_schema.name._id_part = None
        args_schema.policy_name._id_part = None
        args_schema.rcg_name = AAZStrArg(
            options=["--rcg-name", "--rule-collection-group-name"],
            help="The name of the Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.collection_priority = AAZIntArg(
            options=["--collection-priority"],
            arg_group="",
            help="The priority of the rule in Firewall Policy Rule Collection Group.",
            required=True,
            fmt=AAZIntArgFormat(
                maximum=65000,
                minimum=100,
            ),
        )
        args_schema.nat_action = AAZStrArg(
            options=["--action"],
            help="The action type of a rule collection.",
        )
        args_schema.nat_action.enum = AAZArgEnum({'DNAT': 'DNAT', 'SNAT': 'SNAT'})
        args_schema.ip_protocols = AAZListArg(
            options=["--ip-protocols"],
            help="Space-separated list of IP protocols. This argument is supported for Nat and Network Rule. ",
            required=True,
            arg_group="Common Rule",
        )
        args_schema.ip_protocols.Element = AAZStrArg()
        args_schema.ip_protocols.enum = AAZArgEnum({'TCP': 'TCP', 'UDP': 'UDP', 'Any': 'Any', 'ICMP': 'ICMP'})
        args_schema.description = AAZStrArg(
            options=["--description"],
            help="The description of rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses = AAZListArg(
            options=["--destination-addresses", "--dest-addr"],
            help="Space-separated list of destination IP addresses.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses.Element = AAZStrArg()
        args_schema.destination_ports = AAZListArg(
            options=["--destination-ports"],
            help="Space-separated list of destination ports. This argument is supported for Nat and Network Rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_ports.Element = AAZStrArg()
        args_schema.rule_name = AAZStrArg(
            options=["--rule-name"],
            help="The name of rule.",
            arg_group="Common Rule"
        )
        args_schema.source_addresses = AAZListArg(
            options=["--source-addresses"],
            help="Space-separated list of source IP ddresses.",
            arg_group="Common Rule"
        )
        args_schema.source_addresses.Element = AAZStrArg()
        args_schema.source_ip_groups = AAZListArg(
            options=["--source-ip-groups"],
            help="Space-separated list of name or resource id of source IpGroups.",
            arg_group="Common Rule"
        )
        args_schema.source_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.translated_address = AAZStrArg(
            options=["--translated-address"],
            help="Translated address for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.translated_fqdn = AAZStrArg(
            options=["--translated-fqdn"],
            help="Translated FQDN for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.translated_port = AAZStrArg(
            options=["--translated-port"],
            help="Translated port for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.rule_collection_name = AAZStrArg(
            help="The name of the rule collection.",
        )
        args_schema.rule_collection_name._registered = False
        args_schema.priority._registered = False
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.rule_collection_name = args.name
        args.name = args.rcg_name

    def pre_instance_update(self, instance):
        args = self.ctx.args
        nat_rule = {
            'name': args.rule_name,
            'description': args.description,
            'rule_type': 'NatRule',
            'ip_protocols': args.ip_protocols,
            'source_addresses': args.source_addresses,
            'destination_addresses': args.destination_addresses,
            'destination_ports': args.destination_ports,
            'translated_address': args.translated_address,
            'translated_fqdn': args.translated_fqdn,
            'translated_port': args.translated_port,
            'source_ip_groups': args.source_ip_groups
        }
        rule_collection = {
            'name': args.rule_collection_name,
            'priority': args.collection_priority,
            'rule_collection_type': 'FirewallPolicyNatRuleCollection',
            'action': {
                'type': args.nat_action
            },
            'rules': [nat_rule]
        }
        instance.properties.rule_collections.append(rule_collection)

    def _output(self, *args, **kwargs):
        return {'ruleCollections': self.deserialize_output(self.ctx.vars.instance.properties.rule_collections,
                                                           client_flatten=True)}


@register_command(
    "network firewall policy rule-collection-group collection add-filter-collection",
    is_preview=True,
)
class FilterCollectionAdd(_RuleCollectionGroupUpdate):
    """
    Add a filter collection into an Azure firewall policy rule collection group.

    :example: Add a filter collection with Network rule into the rule collection group
        az network firewall policy rule-collection-group collection add-filter-collection -g {rg}
        --policy-name {policy} --rule-collection-group-name {collectiongroup} --name
        filter_collection --action Allow --rule-name network_rule --rule-type NetworkRule
        --description "test" --destination-addresses "202.120.36.15" --source-addresses
        "202.120.36.13" "202.120.36.14" --destination-ports 12003 12004 --ip-protocols TCP UDP
        --collection-priority 11002

    :example: Add a filter collection with Application rule into the rule collection group
        az network firewall policy rule-collection-group collection add-filter-collection -g {rg}
        --policy-name {policy} --rule-collection-group-name {collectiongroup} --name
        filter_collection --action Allow --rule-name application_rule --rule-type ApplicationRule
        --description "test" --destination-addresses "202.120.36.15" "202.120.36.16" --source-
        addresses "202.120.36.13" "202.120.36.14" --protocols Http=12800 Https=12801 --fqdn-tags
        AzureBackup HDInsight --collection-priority 11100
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg, AAZArgEnum, AAZBoolArg, AAZDictArg, AAZResourceIdArg, \
            AAZResourceIdArgFormat, AAZIntArg, AAZIntArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._options = ['--name', '-n']
        args_schema.name.help = 'The name of the collection in Firewall Policy Rule Collection Group.'
        args_schema.name._arg_group = ""
        args_schema.name._id_part = None
        args_schema.policy_name._id_part = None
        args_schema.rcg_name = AAZStrArg(
            options=["--rcg-name", "--rule-collection-group-name"],
            help="The name of the Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.collection_priority = AAZIntArg(
            options=["--collection-priority"],
            arg_group="",
            help="The priority of the rule in Firewall Policy Rule Collection Group.",
            required=True,
            fmt=AAZIntArgFormat(
                maximum=65000,
                minimum=100,
            ),
        )
        args_schema.filter_action = AAZStrArg(
            options=["--action"],
            help="The action type of a rule collection.",
        )
        args_schema.filter_action.enum = AAZArgEnum({'Allow': 'Allow', 'Deny': 'Deny'})
        args_schema.ip_protocols = AAZListArg(
            options=["--ip-protocols"],
            help="Space-separated list of IP protocols. This argument is supported for Nat and Network Rule. ",
            arg_group="Common Rule",
        )
        args_schema.ip_protocols.Element = AAZStrArg()
        args_schema.ip_protocols.enum = AAZArgEnum({'TCP': 'TCP', 'UDP': 'UDP', 'Any': 'Any', 'ICMP': 'ICMP'})
        args_schema.description = AAZStrArg(
            options=["--description"],
            help="The description of rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses = AAZListArg(
            options=["--destination-addresses", "--dest-addr"],
            help="Space-separated list of destination IP addresses.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses.Element = AAZStrArg()
        args_schema.destination_ports = AAZListArg(
            options=["--destination-ports"],
            help="Space-separated list of destination ports. This argument is supported for Nat and Network Rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_ports.Element = AAZStrArg()
        args_schema.rule_name = AAZStrArg(
            options=["--rule-name"],
            help="The name of rule.",
            arg_group="Common Rule"
        )
        args_schema.rule_type = AAZStrArg(
            options=["--rule-type"],
            help="The type of rule.",
            arg_group="Common Rule"
        )
        args_schema.rule_type.enum = AAZArgEnum({'ApplicationRule': 'ApplicationRule',
                                                 'NetworkRule': 'NetworkRule',
                                                 'NatRule': 'NatRule'})
        args_schema.source_addresses = AAZListArg(
            options=["--source-addresses"],
            help="Space-separated list of source IP ddresses.",
            arg_group="Common Rule"
        )
        args_schema.source_addresses.Element = AAZStrArg()
        args_schema.source_ip_groups = AAZListArg(
            options=["--source-ip-groups"],
            help="Space-separated list of name or resource id of source IpGroups.",
            arg_group="Common Rule"
        )
        args_schema.source_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.destination_ip_groups = AAZListArg(
            options=['--destination-ip-groups', '--dest-ipg'],
            help="Space-separated list of name or resource id of destination IpGroups.",
            arg_group="Network Rule"
        )
        args_schema.destination_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.destination_fqdns = AAZListArg(
            options=["--destination-fqdns"],
            help="Space-separated list of destination FQDNs.",
            arg_group="Network Rule"
        )
        args_schema.destination_fqdns.Element = AAZStrArg()
        args_schema.enable_tls_inspection = AAZBoolArg(
            options=['--enable-tls-inspection', '--enable-tls-insp'],
            help="Enable flag to terminate TLS connection for this rule",
            default=False,
            is_preview=True,
            arg_group="Application Rule"
        )
        args_schema.fqdn_tags = AAZListArg(
            options=["--fqdn-tags"],
            help="Space-separated list of FQDN tags for this rule.",
            arg_group="Application Rule"
        )
        args_schema.fqdn_tags.Element = AAZStrArg()
        args_schema.protocols = AAZDictArg(
            options=["--protocols"],
            help="Space-separated list of protocols and port numbers to use, in PROTOCOL=PORT format.",
            arg_group="Application Rule"
        )
        args_schema.protocols.Element = AAZStrArg()
        args_schema.target_fqdns = AAZListArg(
            options=["--target-fqdns"],
            help="Space-separated list of FQDNs for this rule.",
            arg_group="Application Rule"
        )
        args_schema.target_fqdns.Element = AAZStrArg()
        args_schema.target_urls = AAZListArg(
            options=["--target-urls"],
            help="Space-separated list of target urls for this rule.",
            is_preview=True,
            arg_group="Application Rule"
        )
        args_schema.target_urls.Element = AAZStrArg()
        args_schema.web_categories = AAZListArg(
            options=["--web-categories"],
            help="Space-separated list of web categories for this rule.",
            arg_group="Application Rule"
        )
        args_schema.web_categories.Element = AAZStrArg()
        args_schema.rule_collection_name = AAZStrArg(
            help="The name of the rule collection.",
        )
        args_schema.rule_collection_name._registered = False
        args_schema.priority._registered = False
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.rule_collection_name = args.name
        args.name = args.rcg_name

    def pre_instance_update(self, instance):
        args = self.ctx.args
        if has_value(args.target_fqdns) and has_value(args.fqdn_tags):
            raise ArgumentUsageError('usage error: --target-fqdns | --fqdn-tags')

        if args.rule_type == 'NetworkRule':
            rule = {
                'name': args.rule_name,
                'description': args.description,
                'rule_type': 'NetworkRule',
                'ip_protocols': args.ip_protocols,
                'source_addresses': args.source_addresses,
                'destination_addresses': args.destination_addresses,
                'destination_ports': args.destination_ports,
                'source_ip_groups': args.source_ip_groups,
                'destination_ip_groups': args.destination_ip_groups,
                'destination_fqdns': args.destination_fqdns
            }
        else:
            protocols = []
            if has_value(args.protocols):
                protocols = list(map(lambda x: {'protocol_type': x[0], 'port': int(x[1])}, args.protocols.to_serialized_data().items()))
            rule = {
                'name': args.rule_name,
                'description': args.description,
                'rule_type': 'ApplicationRule',
                'source_addresses': args.source_addresses,
                'protocols': protocols,
                'destination_addresses': args.destination_addresses,
                'fqdn_tags': args.fqdn_tags,
                'target_fqdns': args.target_fqdns,
                'target_urls': args.target_urls,
                'source_ip_groups': args.source_ip_groups,
                'terminate_tls': args.enable_tls_inspection,
                'web_categories': args.web_categories
            }
        rule_collection = {
            'name': args.rule_collection_name,
            'priority': args.collection_priority,
            'rule_collection_type': 'FirewallPolicyFilterRuleCollection',
            'action': {
                'type': args.filter_action
            },
            'rules': [rule]
        }
        instance.properties.rule_collections.append(rule_collection)

    def _output(self, *args, **kwargs):
        return {'ruleCollections': self.deserialize_output(self.ctx.vars.instance.properties.rule_collections,
                                                           client_flatten=True)}


@register_command(
    "network firewall policy rule-collection-group collection remove",
    is_preview=True,
)
class CollectionRemove(_RuleCollectionGroupUpdate):
    """
    Remove a rule collection from an Azure firewall policy rule collection group.
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name.help = 'The name of the collection in Firewall Policy Rule Collection Group.'
        args_schema.name._arg_group = ""
        args_schema.name._id_part = None
        args_schema.policy_name._id_part = None
        args_schema.rcg_name = AAZStrArg(
            options=["--rcg-name", "--rule-collection-group-name"],
            help="The name of the Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.rule_collection_name = AAZStrArg(
            help="The name of the rule collection.",
        )
        args_schema.rule_collection_name._registered = False
        args_schema.priority._registered = False
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.rule_collection_name = args.name
        args.name = args.rcg_name

    def pre_instance_update(self, instance):
        args = self.ctx.args
        removed_rule_collection = None
        for rule_collection in instance.properties.rule_collections:
            if rule_collection.name == args.rule_collection_name:
                removed_rule_collection = rule_collection

        if removed_rule_collection is not None:
            new_rule_collections = copy.deepcopy(instance.properties.rule_collections.to_serialized_data())
            new_rule_collections.remove(removed_rule_collection.to_serialized_data())
            instance.properties.rule_collections = new_rule_collections

    def _output(self, *args, **kwargs):
        return {'ruleCollections': self.deserialize_output(self.ctx.vars.instance.properties.rule_collections,
                                                           client_flatten=True)}


@register_command(
    "network firewall policy rule-collection-group collection rule add",
    is_preview=True,
)
class FilterRuleAdd(_RuleCollectionGroupUpdate):
    """
    Add a rule into an Azure firewall policy rule collection.
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZListArg, AAZArgEnum, AAZBoolArg, AAZDictArg, AAZResourceIdArg, \
            AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._options = ['--name', '-n']
        args_schema.name.help = 'The name of rule.'
        args_schema.name._arg_group = 'Common Rule'
        args_schema.name._id_part = None
        args_schema.policy_name._id_part = None
        args_schema.collection_name = AAZStrArg(
            options=["--collection-name"],
            help="The name of the rule collection in Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.rcg_name = AAZStrArg(
            options=["--rcg-name", "--rule-collection-group-name"],
            help="The name of the Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.enable_tls_inspection = AAZBoolArg(
            options=['--enable-tls-inspection', '--enable-tls-insp'],
            help="Enable flag to terminate TLS connection for this rule",
            default=False,
            is_preview=True,
            arg_group="Application Rule"
        )
        args_schema.fqdn_tags = AAZListArg(
            options=["--fqdn-tags"],
            help="Space-separated list of FQDN tags for this rule.",
            arg_group="Application Rule"
        )
        args_schema.fqdn_tags.Element = AAZStrArg()
        args_schema.protocols = AAZDictArg(
            options=["--protocols"],
            help="Space-separated list of protocols and port numbers to use, in PROTOCOL=PORT format.",
            arg_group="Application Rule"
        )
        args_schema.protocols.Element = AAZStrArg()
        args_schema.target_fqdns = AAZListArg(
            options=["--target-fqdns"],
            help="Space-separated list of FQDNs for this rule.",
            arg_group="Application Rule"
        )
        args_schema.target_fqdns.Element = AAZStrArg()
        args_schema.target_urls = AAZListArg(
            options=["--target-urls"],
            help="Space-separated list of target urls for this rule.",
            is_preview=True,
            arg_group="Application Rule"
        )
        args_schema.target_urls.Element = AAZStrArg()
        args_schema.web_categories = AAZListArg(
            options=["--web-categories"],
            help="Space-separated list of web categories for this rule.",
            arg_group="Application Rule"
        )
        args_schema.web_categories.Element = AAZStrArg()
        args_schema.ip_protocols = AAZListArg(
            options=["--ip-protocols"],
            help="Space-separated list of IP protocols. This argument is supported for Nat and Network Rule. ",
            arg_group="Common Rule",
        )
        args_schema.ip_protocols.Element = AAZStrArg()
        args_schema.ip_protocols.enum = AAZArgEnum({'TCP': 'TCP', 'UDP': 'UDP', 'Any': 'Any', 'ICMP': 'ICMP'})
        args_schema.description = AAZStrArg(
            options=["--description"],
            help="The description of rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses = AAZListArg(
            options=["--destination-addresses", "--dest-addr"],
            help="Space-separated list of destination IP addresses.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses.Element = AAZStrArg()
        args_schema.destination_ports = AAZListArg(
            options=["--destination-ports"],
            help="Space-separated list of destination ports. This argument is supported for Nat and Network Rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_ports.Element = AAZStrArg()
        args_schema.rule_type = AAZStrArg(
            options=["--rule-type"],
            help="The type of rule.",
            required=True,
            arg_group="Common Rule"
        )
        args_schema.rule_type.enum = AAZArgEnum({'ApplicationRule': 'ApplicationRule',
                                                 'NetworkRule': 'NetworkRule',
                                                 'NatRule': 'NatRule'})
        args_schema.source_addresses = AAZListArg(
            options=["--source-addresses"],
            help="Space-separated list of source IP ddresses.",
            arg_group="Common Rule"
        )
        args_schema.source_addresses.Element = AAZStrArg()
        args_schema.source_ip_groups = AAZListArg(
            options=["--source-ip-groups"],
            help="Space-separated list of name or resource id of source IpGroups.",
            arg_group="Common Rule"
        )
        args_schema.source_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.translated_address = AAZStrArg(
            options=["--translated-address"],
            help="Translated address for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.translated_fqdn = AAZStrArg(
            options=["--translated-fqdn"],
            help="Translated FQDN for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.translated_port = AAZStrArg(
            options=["--translated-port"],
            help="Translated port for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.destination_ip_groups = AAZListArg(
            options=['--destination-ip-groups', '--dest-ipg'],
            help="Space-separated list of name or resource id of destination IpGroups.",
            arg_group="Network Rule"
        )
        args_schema.destination_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.destination_fqdns = AAZListArg(
            options=["--destination-fqdns"],
            help="Space-separated list of destination FQDNs.",
            arg_group="Network Rule"
        )
        args_schema.destination_fqdns.Element = AAZStrArg()
        args_schema.rule_name = AAZStrArg(
            help="The name of rule.",
        )
        args_schema.rule_name._registered = False
        args_schema.priority._registered = False
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.rule_name = args.name
        args.name = args.rcg_name

    def pre_instance_update(self, instance):
        args = self.ctx.args
        target_rule_collection = None
        for rule_collection in instance.properties.rule_collections:
            if rule_collection.name == args.collection_name:
                target_rule_collection = rule_collection

        if target_rule_collection is None:
            raise CLIError("Cannot find corresponding rule.")

        if target_rule_collection.rule_collection_type == "FirewallPolicyFilterRuleCollection" and args.rule_type == 'NatRule':
            raise CLIError("FirewallPolicyFilterRule doesn't support Nat rule.")

        if target_rule_collection.rule_collection_type == "FirewallPolicyNatRuleCollection" and args.rule_type in ['NetworkRule', 'ApplicationRule']:
            raise CLIError("FirewallPolicyNatRule supports neither Network rule nor Application rule.")

        rule = None
        if args.rule_type == "NetworkRule":
            rule = {
                'name': args.rule_name,
                'description': args.description,
                'rule_type': 'NetworkRule',
                'ip_protocols': args.ip_protocols,
                'source_addresses': args.source_addresses,
                'destination_addresses': args.destination_addresses,
                'destination_ports': args.destination_ports,
                'source_ip_groups': args.source_ip_groups,
                'destination_ip_groups': args.destination_ip_groups,
                'destination_fqdns': args.destination_fqdns
            }
        elif args.rule_type == 'ApplicationRule':
            protocols = []
            if has_value(args.protocols):
                protocols = list(
                    map(lambda x: {'protocol_type': x[0], 'port': int(x[1])}, args.protocols.to_serialized_data().items()))
            rule = {
                'name': args.rule_name,
                'description': args.description,
                'rule_type': 'ApplicationRule',
                'source_addresses': args.source_addresses,
                'protocols': protocols,
                'destination_addresses': args.destination_addresses,
                'fqdn_tags': args.fqdn_tags,
                'target_fqdns': args.target_fqdns,
                'target_urls': args.target_urls,
                'source_ip_groups': args.source_ip_groups,
                'terminate_tls': args.enable_tls_inspection,
                'web_categories': args.web_categories
            }

        elif args.rule_type == 'NatRule':
            rule = {
                'name': args.rule_name,
                'description': args.description,
                'rule_type': 'NatRule',
                'ip_protocols': args.ip_protocols,
                'source_addresses': args.source_addresses,
                'destination_addresses': args.destination_addresses,
                'destination_ports': args.destination_ports,
                'translated_address': args.translated_address,
                'translated_fqdn': args.translated_fqdn,
                'translated_port': args.translated_port,
                'source_ip_groups': args.source_ip_groups
            }

        target_rule_collection.rules.append(rule)


@register_command(
    "network firewall policy rule-collection-group collection rule remove",
    is_preview=True,
)
class FilterRuleRemove(_RuleCollectionGroupUpdate):
    """
    Remove a rule from an Azure firewall policy rule collection.
        Filter collection supports having a list of network rules or application rules.
        NatRule collection supports including a list of nat rules.
    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._options = ['--name', '-n']
        args_schema.name.help = 'The name of rule.'
        args_schema.name._arg_group = 'Common Rule'
        args_schema.name._id_part = None
        args_schema.policy_name._id_part = None
        args_schema.collection_name = AAZStrArg(
            options=["--collection-name"],
            help="The name of the rule collection in Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.rcg_name = AAZStrArg(
            options=["--rcg-name", "--rule-collection-group-name"],
            help="The name of the Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.rule_name = AAZStrArg(
            help="The name of rule.",
        )
        args_schema.rule_name._registered = False
        args_schema.priority._registered = False
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.rule_name = args.name
        args.name = args.rcg_name

    def pre_instance_update(self, instance):
        args = self.ctx.args
        target_rule_collection = None
        for rule_collection in instance.properties.rule_collections:
            if rule_collection.name == args.collection_name:
                target_rule_collection = rule_collection

        if target_rule_collection is None:
            raise CLIError("Cannot find corresponding rule collection.")

        removed_rule = None
        for rule in target_rule_collection.rules:
            if rule.name == args.rule_name:
                removed_rule = rule

        if removed_rule is not None:
            new_rules = copy.deepcopy(target_rule_collection.rules.to_serialized_data())
            new_rules.remove(removed_rule.to_serialized_data())
            target_rule_collection.rules = new_rules


@register_command(
    "network firewall policy rule-collection-group collection rule update",
    is_preview=True,
)
class FilterRuleUpdate(_RuleCollectionGroupUpdate):
    """
    Update a rule of an Azure firewall policy rule collection.
        Filter collection supports having a list of network rules or application rules.
        NatRule collection supports including a list of nat rules.

    :example: Update a rule of an Azure firewall policy rule collection.
        az network firewall policy rule-collection-group collection rule update -g {rg} --policy-
        name {policy} --rule-collection-group-name {rcg} --collection-name {cn} -n {rule_name}
        --target-fqdns XXX

    """

    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZStrArg, AAZBoolArg, AAZListArg, AAZDictArg, AAZArgEnum, AAZResourceIdArg, \
            AAZResourceIdArgFormat
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.name._required = True
        args_schema.name._options = ['--name', '-n']
        args_schema.name.help = 'The name of rule.'
        args_schema.name._arg_group = 'Common Rule'
        args_schema.name._id_part = None
        args_schema.policy_name._id_part = None
        args_schema.collection_name = AAZStrArg(
            options=["--collection-name"],
            help="The name of the rule collection in Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.rcg_name = AAZStrArg(
            options=["--rcg-name", "--rule-collection-group-name"],
            help="The name of the Firewall Policy Rule Collection Group.",
            required=True,
            arg_group="",
        )
        args_schema.enable_tls_inspection = AAZBoolArg(
            options=['--enable-tls-inspection', '--enable-tls-insp'],
            help="Enable flag to terminate TLS connection for this rule",
            default=False,
            is_preview=True,
            arg_group="Application Rule"
        )
        args_schema.fqdn_tags = AAZListArg(
            options=["--fqdn-tags"],
            help="Space-separated list of FQDN tags for this rule.",
            arg_group="Application Rule"
        )
        args_schema.fqdn_tags.Element = AAZStrArg()
        args_schema.protocols = AAZDictArg(
            options=["--protocols"],
            help="Space-separated list of protocols and port numbers to use, in PROTOCOL=PORT format.",
            arg_group="Application Rule"
        )
        args_schema.protocols.Element = AAZStrArg()
        args_schema.target_fqdns = AAZListArg(
            options=["--target-fqdns"],
            help="Space-separated list of FQDNs for this rule.",
            arg_group="Application Rule"
        )
        args_schema.target_fqdns.Element = AAZStrArg()
        args_schema.target_urls = AAZListArg(
            options=["--target-urls"],
            help="Space-separated list of target urls for this rule.",
            is_preview=True,
            arg_group="Application Rule"
        )
        args_schema.target_urls.Element = AAZStrArg()
        args_schema.web_categories = AAZListArg(
            options=["--web-categories"],
            help="Space-separated list of web categories for this rule.",
            arg_group="Application Rule"
        )
        args_schema.web_categories.Element = AAZStrArg()
        args_schema.ip_protocols = AAZListArg(
            options=["--ip-protocols"],
            help="Space-separated list of IP protocols. This argument is supported for Nat and Network Rule. ",
            arg_group="Common Rule",
        )
        args_schema.ip_protocols.Element = AAZStrArg()
        args_schema.ip_protocols.enum = AAZArgEnum({'TCP': 'TCP', 'UDP': 'UDP', 'Any': 'Any', 'ICMP': 'ICMP'})
        args_schema.description = AAZStrArg(
            options=["--description"],
            help="The description of rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses = AAZListArg(
            options=["--destination-addresses", "--dest-addr"],
            help="Space-separated list of destination IP addresses.",
            arg_group="Common Rule"
        )
        args_schema.destination_addresses.Element = AAZStrArg()
        args_schema.destination_ports = AAZListArg(
            options=["--destination-ports"],
            help="Space-separated list of destination ports. This argument is supported for Nat and Network Rule.",
            arg_group="Common Rule"
        )
        args_schema.destination_ports.Element = AAZStrArg()
        args_schema.source_addresses = AAZListArg(
            options=["--source-addresses"],
            help="Space-separated list of source IP ddresses.",
            arg_group="Common Rule"
        )
        args_schema.source_addresses.Element = AAZStrArg()
        args_schema.source_ip_groups = AAZListArg(
            options=["--source-ip-groups"],
            help="Space-separated list of name or resource id of source IpGroups.",
            arg_group="Common Rule"
        )
        args_schema.source_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.translated_address = AAZStrArg(
            options=["--translated-address"],
            help="Translated address for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.translated_fqdn = AAZStrArg(
            options=["--translated-fqdn"],
            help="Translated FQDN for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.translated_port = AAZStrArg(
            options=["--translated-port"],
            help="Translated port for this NAT rule collection.",
            arg_group="Nat Rule"
        )
        args_schema.destination_ip_groups = AAZListArg(
            options=['--destination-ip-groups', '--dest-ipg'],
            help="Space-separated list of name or resource id of destination IpGroups.",
            arg_group="Network Rule"
        )
        args_schema.destination_ip_groups.Element = AAZResourceIdArg(
            fmt=AAZResourceIdArgFormat(
                template="/subscriptions/{subscription}/resourceGroups/{resource_group}/providers/Microsoft.Network/ipGroups/{}"
            )
        )
        args_schema.destination_fqdns = AAZListArg(
            options=["--destination-fqdns"],
            help="Space-separated list of destination FQDNs.",
            arg_group="Network Rule"
        )
        args_schema.destination_fqdns.Element = AAZStrArg()
        args_schema.rule_name = AAZStrArg(
            help="The name of rule.",
        )
        args_schema.rule_name._registered = False
        args_schema.priority._registered = False
        args_schema.rule_collections._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        args.rule_name = args.name
        args.name = args.rcg_name

    def pre_instance_update(self, instance):
        args = self.ctx.args
        target_rule_collection = None
        for rule_collection in instance.properties.rule_collections:
            if rule_collection.name == args.collection_name:
                target_rule_collection = rule_collection

        if target_rule_collection is None:
            raise UserFault("Cannot find corresponding rule, please check parameters")

        new_rule = None
        for i, rule in enumerate(target_rule_collection.rules):
            if args.rule_name == rule.name:
                if rule.rule_type == "NetworkRule":
                    new_rule = {
                        'name': args.rule_name,
                        'description': args.description if has_value(args.description) else rule.description,
                        'rule_type': 'NetworkRule',
                        'ip_protocols': args.ip_protocols if has_value(args.ip_protocols) else rule.ip_protocols,
                        'source_addresses': args.source_addresses if has_value(args.source_addresses) else rule.source_addresses,
                        'destination_addresses': args.destination_addresses if has_value(args.destination_addresses) else rule.destination_addresses,
                        'destination_ports': args.destination_ports if has_value(args.destination_ports) else rule.destination_ports,
                        'source_ip_groups': args.source_ip_groups if has_value(args.source_ip_groups) else rule.source_ip_groups,
                        'destination_ip_groups': args.destination_ip_groups if has_value(args.destination_ip_groups) else rule.destination_ip_groups,
                        'destination_fqdns': args.destination_fqdns if has_value(args.destination_fqdns) else rule.destination_fqdns
                    }
                elif rule.rule_type == 'ApplicationRule':
                    protocols = rule.protocols
                    if has_value(args.protocols):
                        protocols = list(
                            map(lambda x: {'protocol_type': x[0], 'port': int(x[1])},
                                args.protocols.to_serialized_data().items()))
                    new_rule = {
                        'name': args.rule_name,
                        'description': args.description if has_value(args.description) else rule.description,
                        'rule_type': 'ApplicationRule',
                        'source_addresses': args.source_addresses if has_value(args.source_addresses) else rule.source_addresses,
                        'protocols': protocols,
                        'destination_addresses': args.destination_addresses if has_value(args.destination_addresses) else rule.destination_addresses,
                        'fqdn_tags': args.fqdn_tags if has_value(args.fqdn_tags) else rule.fqdn_tags,
                        'target_fqdns': args.target_fqdns if has_value(args.target_fqdns) else rule.target_fqdns,
                        'target_urls': args.target_urls if has_value(args.target_urls) else rule.target_urls,
                        'source_ip_groups': args.source_ip_groups if has_value(args.source_ip_groups) else rule.source_ip_groups,
                        'terminate_tls': args.enable_tls_inspection if has_value(args.enable_tls_inspection) else rule.enable_tls_inspection,
                        'web_categories': args.web_categories if has_value(args.web_categories) else rule.web_categories
                    }
                elif rule.rule_type == 'NatRule':
                    new_rule = {
                        'name': args.rule_name,
                        'description': args.description if has_value(args.description) else rule.description,
                        'rule_type': 'NatRule',
                        'ip_protocols': args.ip_protocols if has_value(args.ip_protocols) else rule.ip_protocols,
                        'source_addresses': args.source_addresses if has_value(args.source_addresses) else rule.source_addresses,
                        'destination_addresses': args.destination_addresses if has_value(args.destination_addresses) else rule.destination_addresses,
                        'destination_ports': args.destination_ports if has_value(args.destination_ports) else rule.destination_ports,
                        'translated_address': args.translated_address if has_value(args.translated_address) else rule.translated_address,
                        'translated_fqdn': args.translated_fqdn if has_value(args.translated_fqdn) else rule.translated_fqdn,
                        'translated_port': args.translated_port if has_value(args.translated_port) else rule.translated_port,
                        'source_ip_groups': args.source_ip_groups if has_value(args.source_ip_groups) else rule.source_ip_groups
                    }
                else:
                    raise ServiceError(f'Undefined rule_type : {rule.rule_type}')
                if new_rule is not None:
                    target_rule_collection.rules[i] = new_rule
        if new_rule is None:
            raise UserFault(f'{args.rule_name} does not exist!!!')
# endregion
