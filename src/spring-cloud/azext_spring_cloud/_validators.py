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


def validate_vnet(cmd, namespace):
    if not namespace.vnet and not namespace.app_subnet and \
        not namespace.service_runtime_subnet and not namespace.reserved_cidr_range:
        return
    validate_vnet_required_parameters(namespace)
    _validate_cidr_range(namespace.reserved_cidr_range)

    if namespace.vnet:
        vnet = namespace.vnet
        # format the app_subnet and service_runtime_subnet
        if not is_valid_resource_id(vnet):
            if vnet.count('/') > 0:
                raise CLIError('vnet {0} is not a valid name or resource ID'.format(vnet))
            vnet = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group,
                namespace='Microsoft.Network',
                type='virtualNetworks',
                name=vnet
            )
        namespace.app_subnet = _parse_subnet(vnet, namespace.app_subnet)
        namespace.service_runtime_subnet = _parse_subnet(vnet, namespace.service_runtime_subnet)
    else:
        app_vnet_id = _validate_subnet_id(namespace.app_subnet)
        service_runtime_vnet_id = _validate_subnet_id(namespace.service_runtime_subnet)
        if app_vnet_id.lower() != service_runtime_vnet_id.lower():
            raise CLIError('--app-subnet and --service-runtime-subnet should be in the same Virtual Networks.')
    if namespace.app_subnet.lower() == namespace.service_runtime_subnet.lower():
        raise CLIError('--app-subnet and --service-runtime-subnet should not be the same.')

def _validate_subnet_id(subnet_id):
    if not is_valid_resource_id(subnet_id):
        raise CLIError('subnet {0} is not a valid resource ID'.format(subnet_id))
    subnet = parse_resource_id(subnet_id)
    return resource_id(
        subscription=subnet['subscription'],
        resource_group=subnet['resource_group'],
        namespace=subnet['namespace'],
        type=subnet['type'],
        name=subnet['name']
    )

def _parse_subnet(vnet_id, subnet):
    if not is_valid_resource_id(subnet):
        if subnet.count('/'):
            raise CLIError('subnet {0} is not a valid name or resource ID'.format(subnet))
        # subnet name is given
        return vnet_id + '/subnets/' + subnet
    if not subnet.lower().startswith(vnet_id.lower()):
        raise CLIError('subnet {0} is not under virtual network {1}'.format(subnet, vnet_id))
    return subnet

def _validate_cidr_range(ranges):
    if isinstance(ranges, list):
        if len(ranges) != 3:
            raise CLIError('--reserved-cidr-range should be 1 unused /14 IP range, or 3 unused /16 IP rangeds')
        for ip in ranges:
            _validate_ip(ip, 16)
    else:
        _validate_ip(ranges, 14)

def _validate_ip(ip, prefix):
    try:
        # Host bits set can be non-zero? Here treat it as valid.
        ip_address = ip_network(ip, strict=False)
        if ip_address.version != 4:
            raise CLIError('{0} is not a valid CIDR.'.format(ip))
        if ip_address.prefixlen > prefix:
            raise CLIError(
                '{0} is not valid.'
                ' --reserved-cidr-range should be 1 unused /14 IP range, or 3 unused /16 IP rangeds.'.format(ip))
    except ValueError:
        raise CLIError('{0} is not a valid CIDR'.format(ip))

def validate_vnet_required_parameters(namespace):
    if not namespace.reserved_cidr_range or not namespace.app_subnet or not namespace.service_runtime_subnet:
        raise CLIError(
            '--reserved-cidr-range, --app-subnet, --service-runtime-subnet must be set when deploying to VNet')
