# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from re import match
from ipaddress import ip_network
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.commands.validators import validate_tag
from azure.cli.core.util import CLIError
from msrestazure.tools import is_valid_resource_id
from msrestazure.tools import parse_resource_id
from msrestazure.tools import resource_id
from knack.log import get_logger
from ._utils import ApiType
from ._utils import _get_rg_location

logger = get_logger(__name__)


def validate_env(namespace):
    """ Extracts multiple space-separated envs in key[=value] format """
    if isinstance(namespace.env, list):
        env_dict = {}
        for item in namespace.env:
            env_dict.update(validate_tag(item))
        namespace.env = env_dict


def validate_location(namespace):
    if namespace.location:
        location_slice = namespace.location.split(" ")
        namespace.location = "".join([piece.lower()
                                      for piece in location_slice])


def validate_sku(namespace):
    if namespace.sku is not None:
        namespace.sku = namespace.sku.upper()
        if namespace.sku not in ['BASIC', 'STANDARD']:
            raise CLIError("The pricing tier only accepts value [Basic, Standard]")


def validate_instance_count(namespace):
    if namespace.instance_count is not None:
        if namespace.instance_count < 1:
            raise CLIError("--instance-count must be greater than 0")


def validate_name(namespace):
    namespace.name = namespace.name.lower()
    matchObj = match(r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', namespace.name)
    if matchObj is None:
        raise CLIError(
            '--name should start with lowercase and only contain numbers and lowercases with length [4,31]')


def validate_app_name(namespace):
    if namespace.app is not None:
        namespace.app = namespace.app.lower()
        matchObj = match(r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', namespace.app)
        if matchObj is None:
            raise CLIError(
                '--app should start with lowercase and only contain numbers and lowercases with length [4,31]')


def validate_deployment_name(namespace):
    if namespace.deployment is not None:
        namespace.deployment = namespace.deployment.lower()
        if namespace.deployment is None:
            return

        matchObj = match(
            r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', namespace.deployment)
        if matchObj is None:
            raise CLIError(
                '--deployment should start with lowercase and only contain numbers and lowercases with length [4,31]')


def validate_resource_id(namespace):
    if not is_valid_resource_id(namespace.resource_id):
        raise CLIError("Invalid resource id {}".format(namespace.resource_id))


def validate_cosmos_type(namespace):
    if namespace.api_type is None:
        return
    type = ApiType(namespace.api_type)
    if type in (ApiType.mongo, ApiType.sql, ApiType.gremlin):
        if namespace.database_name is None:
            raise CLIError(
                "Cosmosdb with type {} should specify database name".format(type))

    if type == ApiType.cassandra:
        if namespace.key_space is None:
            raise CLIError(
                "Cosmosdb with type {} should specify key space".format(type))

    if type == ApiType.gremlin:
        if namespace.key_space is None:
            raise CLIError(
                "Cosmosdb with type {} should specify collection name".format(type))


def validate_log_limit(namespace):
    temp_limit = None
    try:
        temp_limit = namespace.limit
    except:
        raise CLIError('--limit must contains only digit')
    if temp_limit < 1:
        raise CLIError('--limit must be in the range [1,2048]')
    if temp_limit > 2048:
        temp_limit = 2048
        logger.error("--limit can not be more than 2048, using 2048 instead")
    namespace.limit = temp_limit * 1024


def validate_log_lines(namespace):
    temp_lines = None
    try:
        temp_lines = namespace.lines
    except:
        raise CLIError('--lines must contains only digit')
    if temp_lines < 1:
        raise CLIError('--lines must be in the range [1,10000]')
    if temp_lines > 10000:
        temp_lines = 10000
        logger.error("--lines can not be more than 10000, using 10000 instead")
    namespace.lines = temp_lines


def validate_log_since(namespace):
    if namespace.since:
        last = namespace.since[-1:]
        try:
            namespace.since = int(
                namespace.since[:-1]) if last in ("hms") else int(namespace.since)
        except:
            raise CLIError("--since contains invalid characters")
        namespace.since *= 60 if last == "m" else 1
        namespace.since *= 3600 if last == "h" else 1
        if namespace.since > 3600:
            raise CLIError("--since can not be more than 1h")


def validate_jvm_options(namespace):
    if namespace.jvm_options is not None:
        namespace.jvm_options = namespace.jvm_options.strip('\'')


def validate_tracing_parameters(namespace):
    if (namespace.app_insights or namespace.app_insights_key) and namespace.disable_distributed_tracing:
        raise CLIError("Conflict detected: '--app-insights' or '--app-insights-key'"
                       "can not be set with '--disable-distributed-tracing'.")
    if namespace.app_insights and namespace.app_insights_key:
        raise CLIError("Conflict detected: '--app-insights' and '--app-insights-key' can not be set at the same time.")


def validate_vnet(cmd, namespace):
    if not namespace.vnet and not namespace.app_subnet and \
       not namespace.service_runtime_subnet and not namespace.reserved_cidr_range:
        return
    validate_vnet_required_parameters(namespace)

    vnet_id = ''
    if namespace.vnet:
        vnet_id = namespace.vnet
        # format the app_subnet and service_runtime_subnet
        if not is_valid_resource_id(vnet_id):
            if vnet_id.count('/') > 0:
                raise CLIError('--vnet {0} is not a valid name or resource ID'.format(vnet_id))
            vnet_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group,
                namespace='Microsoft.Network',
                type='virtualNetworks',
                name=vnet_id
            )
        else:
            vnet = parse_resource_id(vnet_id)
            if vnet['namespace'].lower() != 'microsoft.network' or vnet['type'].lower() != 'virtualnetworks':
                raise CLIError('--vnet {0} is not a valid VirtualNetwork resource ID'.format(vnet_id))
        namespace.app_subnet = _construct_subnet_id(vnet_id, namespace.app_subnet)
        namespace.service_runtime_subnet = _construct_subnet_id(vnet_id, namespace.service_runtime_subnet)
    else:
        app_vnet_id = _parse_vnet_id_from_subnet(namespace.app_subnet)
        service_runtime_vnet_id = _parse_vnet_id_from_subnet(namespace.service_runtime_subnet)
        if app_vnet_id.lower() != service_runtime_vnet_id.lower():
            raise CLIError('--app-subnet and --service-runtime-subnet should be in the same Virtual Networks.')
        vnet_id = app_vnet_id
    if namespace.app_subnet.lower() == namespace.service_runtime_subnet.lower():
        raise CLIError('--app-subnet and --service-runtime-subnet should not be the same.')

    vnet_obj = _get_vnet(cmd, vnet_id)
    instance_location = namespace.location
    if instance_location is None:
        instance_location = _get_rg_location(cmd.cli_ctx, namespace.resource_group)
    else:
        instance_location_slice = instance_location.split(" ")
        instance_location = "".join([piece.lower()
                                     for piece in instance_location_slice])
    if vnet_obj.location.lower() != instance_location.lower():
        raise CLIError('--vnet and Azure Spring Cloud instance should be in the same location.')
    for subnet in vnet_obj.subnets:
        _validate_subnet(namespace, subnet)

    if namespace.reserved_cidr_range:
        _validate_cidr_range(namespace)
    else:
        namespace.reserved_cidr_range = _set_default_cidr_range(vnet_obj.address_space.address_prefixes) if \
            vnet_obj and vnet_obj.address_space and vnet_obj.address_space.address_prefixes \
            else '10.234.0.0/16,10.244.0.0/16,172.17.0.1/16'


def _validate_subnet(namespace, subnet):
    name = ''
    limit = 32
    if subnet.id.lower() == namespace.app_subnet.lower():
        name = 'app-subnet'
        limit = 28
    elif subnet.id.lower() == namespace.service_runtime_subnet.lower():
        name = 'service-runtime-subnet'
        limit = 28
    else:
        return
    if subnet.route_table:
        raise CLIError('--{} with existing route table is not supported. Please remove route table from the subnet,'
                       ' or select another subnet.'.format(name))
    if subnet.ip_configurations:
        raise CLIError('--{} should not have connected device.'.format(name))
    address = ip_network(subnet.address_prefix, strict=False)
    if address.prefixlen > limit:
        raise CLIError('--{0} should contain at least /{1} address, got /{2}'.format(name, limit, address.prefixlen))


def _get_vnet(cmd, vnet_id):
    vnet = parse_resource_id(vnet_id)
    network_client = _get_network_client(cmd.cli_ctx, subscription_id=vnet['subscription'])
    return network_client.virtual_networks.get(vnet['resource_group'], vnet['resource_name'])


def _get_network_client(cli_ctx, subscription_id=None):
    from azure.cli.core.profiles import ResourceType, get_api_version
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx,
                                   ResourceType.MGMT_NETWORK,
                                   subscription_id=subscription_id,
                                   api_version=get_api_version(cli_ctx, ResourceType.MGMT_NETWORK))


def _get_authorization_client(cli_ctx, subscription_id=None):
    from azure.cli.core.profiles import ResourceType
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION, subscription_id=subscription_id)


def _get_graph_rbac_management_client(cli_ctx, subscription_id=None, **_):
    from azure.cli.core.commands.client_factory import configure_common_settings
    from azure.cli.core._profile import Profile
    from azure.graphrbac import GraphRbacManagementClient

    profile = Profile(cli_ctx=cli_ctx)
    cred, subscription_id, tenant_id = profile.get_login_credentials(
        resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id, subscription_id=subscription_id)
    client = GraphRbacManagementClient(
        cred, tenant_id,
        base_url=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    configure_common_settings(cli_ctx, client)
    return client


def _set_default_cidr_range(address_prefixes):
    ip_ranges = [ip_network(x, strict=False) for x in address_prefixes]
    candidates = []
    current = ip_network('10.0.0.0/16')
    while len(candidates) < 3:
        while any(x.overlaps(current) for x in ip_ranges):
            current = _next_range(current, 16)
        candidates.append(current)
        current = _next_range(current, 16)
    # the last one requires x.x.x.1/16 from API side, it is not a strict address
    last = candidates[-1]
    result = [str(x) for x in candidates]
    result[-1] = '{0}/16'.format(str(last[1]))
    return ','.join(result)


def _next_range(ip, prefix):
    try:
        address = ip[-1] + 1
        # should never in 127.0.0.0/8, 169.254.0.0/16, 224.0.0.0/4
        while address.is_loopback:
            address = address + 16777216
        while address.is_link_local:
            address = address + 65536
        while address.is_multicast:
            address = address + 268435456
        return ip_network('{0}/{1}'.format(address, prefix), strict=False)
    except ValueError:
        raise CLIError('Cannot set "reserved-cidr-range" automatically.'
                       'Please specify "--reserved-cidr-range" with 3 unused CIDR ranges in your network environment.')


def _parse_vnet_id_from_subnet(subnet_id):
    if not is_valid_resource_id(subnet_id):
        raise CLIError('{0} is not a valid subnet resource ID'.format(subnet_id))
    subnet = parse_resource_id(subnet_id)
    if subnet['namespace'].lower() != 'microsoft.network' or \
       subnet['type'].lower() != 'virtualnetworks' or \
       'resource_type' not in subnet or subnet['resource_type'].lower() != 'subnets':
        raise CLIError('{0} is not a valid subnet resource ID'.format(subnet_id))
    return resource_id(
        subscription=subnet['subscription'],
        resource_group=subnet['resource_group'],
        namespace=subnet['namespace'],
        type=subnet['type'],
        name=subnet['name']
    )


def _construct_subnet_id(vnet_id, subnet):
    if not is_valid_resource_id(subnet):
        if subnet.count('/'):
            raise CLIError('subnet {0} is not a valid name or resource ID'.format(subnet))
        # subnet name is given
        return vnet_id + '/subnets/' + subnet
    if not subnet.lower().startswith(vnet_id.lower()):
        raise CLIError('subnet {0} is not under virtual network {1}'.format(subnet, vnet_id))
    return subnet


def _validate_cidr_range(namespace):
    ranges = namespace.reserved_cidr_range.split(',')
    ranges = [x for x in ranges if x != '']  # filter out empty ones

    # Not support one /14 range yet
    # if len(ranges) == 1:
    #     _validate_ip(ranges[0], 14)
    #     namespace.reserved_cidr_range = ranges[0]
    #     return
    if len(ranges) != 3:
        raise CLIError('--reserved-cidr-range should be 3 unused /16 IP ranges')
    ipv4 = [_validate_ip(ip, 16) for ip in ranges]
    # check no overlap with each other
    for i, item in enumerate(ipv4):
        for j in range(i + 1, len(ipv4)):
            if item.overlaps(ipv4[j]):
                raise CLIError('--reserved-cidr-range should not overlap each other, but {0} and {1} overlapping.'
                               .format(ranges[i], ranges[j]))
    namespace.reserved_cidr_range = ','.join(ranges)


def _validate_ip(ip, prefix):
    try:
        # Host bits set can be non-zero? Here treat it as valid.
        ip_address = ip_network(ip, strict=False)
        if ip_address.version != 4:
            raise CLIError('{0} is not a valid IPv4 CIDR.'.format(ip))
        if ip_address.prefixlen > prefix:
            raise CLIError(
                '{0} doesn\'t has valid CIDR prefix. '
                ' --reserved-cidr-range should be 3 unused /16 IP ranges.'.format(ip))
        return ip_address
    except ValueError:
        raise CLIError('{0} is not a valid CIDR'.format(ip))


def validate_vnet_required_parameters(namespace):
    # pylint: disable=too-many-boolean-expressions
    if not namespace.app_subnet and \
       not namespace.service_runtime_subnet and \
       not namespace.app_network_resource_group and \
       not namespace.service_runtime_network_resource_group and \
       not namespace.reserved_cidr_range and \
       not namespace.vnet:
        return
    if namespace.sku and namespace.sku.lower() == 'basic':
        raise CLIError('Virtual Network Injection is not supported for Basic tier.')
    if not namespace.app_subnet \
       or not namespace.service_runtime_subnet:
        raise CLIError(
            '--app-subnet, --service-runtime-subnet must be set when deploying to VNet')


def validate_node_resource_group(namespace):
    validate_vnet_required_parameters(namespace)
    _validate_resource_group_name(namespace.service_runtime_network_resource_group,
                                  'service-runtime-network-resource-group')
    _validate_resource_group_name(namespace.app_network_resource_group, 'app-network-resource-group')


def _validate_resource_group_name(name, message_name):
    if not name:
        return
    matchObj = match(r'^[-\w\._\(\)]+$', name)
    if matchObj is None:
        raise CLIError('--{0} must conform to the following pattern: \'^[-\\w\\._\\(\\)]+$\'.'.format(message_name))
