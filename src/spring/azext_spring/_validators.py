# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from re import match
from re import search
from ipaddress import ip_network
import zipfile
from azure.cli.core import telemetry
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.commands.validators import validate_tag
from azure.cli.core.azclierror import ArgumentUsageError, InvalidArgumentValueError
from knack.validators import DefaultStr
from azure.mgmt.core.tools import is_valid_resource_id
from azure.mgmt.core.tools import parse_resource_id
from azure.mgmt.core.tools import resource_id
from knack.log import get_logger
from ._clierror import NotSupportedPricingTierError
from ._utils import (ApiType, _get_rg_location, _get_file_type, _get_sku_name, _java_runtime_in_number)
from ._util_enterprise import is_enterprise_tier
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from ._constant import (MARKETPLACE_OFFER_ID, MARKETPLACE_PLAN_ID, MARKETPLACE_PUBLISHER_ID)

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


def validate_sku(cmd, namespace):
    if not namespace.sku:
        return
    if namespace.sku.lower() == 'enterprise':
        _validate_saas_provider(cmd, namespace)
        _validate_terms(cmd, namespace)
    else:
        _check_saas_not_set(cmd, namespace)
        _check_tanzu_components_not_enable(cmd, namespace)
    normalize_sku(cmd, namespace)


def normalize_sku(cmd, namespace):
    if namespace.sku:
        namespace.sku = models.Sku(name=_get_sku_name(namespace.sku), tier=namespace.sku)


def _check_saas_not_set(cmd, namespace):
    if namespace.marketplace_plan_id:
        raise InvalidArgumentValueError('--marketplace-plan-id is supported only when --sku=Enterprise')


def _validate_saas_provider(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).providers
    if client.get('Microsoft.SaaS').registration_state != 'Registered':
        raise InvalidArgumentValueError('Microsoft.SaaS resource provider is not registered.\n'
                                        'Run "az provider register -n Microsoft.SaaS" to register.')


def _validate_terms(cmd, namespace):
    from azure.mgmt.marketplaceordering import MarketplaceOrderingAgreements
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    client = get_mgmt_service_client(cmd.cli_ctx, MarketplaceOrderingAgreements).marketplace_agreements
    plan_id = namespace.marketplace_plan_id or MARKETPLACE_PLAN_ID
    term = client.get(offer_type="virtualmachine",
                      publisher_id=MARKETPLACE_PUBLISHER_ID,
                      offer_id=MARKETPLACE_OFFER_ID,
                      plan_id=plan_id)
    if not term.accepted:
        raise InvalidArgumentValueError('Terms for Azure Spring Apps Enterprise is not accepted.\n'
                                        'Run "az term accept --publisher {} '
                                        '--product {} '
                                        '--plan {}" to accept the term.'.format(MARKETPLACE_PUBLISHER_ID,
                                                                                MARKETPLACE_OFFER_ID,
                                                                                plan_id))


def _check_tanzu_components_not_enable(cmd, namespace):
    suffix = 'can only be used for Azure Spring Apps Enterprise. Please add --sku="Enterprise" to create Enterprise instance.'
    if namespace.enable_application_configuration_service:
        raise ArgumentUsageError('--enable-application-configuration-service {}'.format(suffix))
    if namespace.enable_service_registry:
        raise ArgumentUsageError('--enable-service-registry {}'.format(suffix))
    if namespace.enable_gateway:
        raise ArgumentUsageError('--enable-gateway {}'.format(suffix))
    if namespace.enable_api_portal:
        raise ArgumentUsageError('--enable-api-portal {}'.format(suffix))
    if namespace.enable_application_live_view:
        raise ArgumentUsageError('--enable-application-live-view {}'.format(suffix))
    if namespace.enable_application_accelerator:
        raise ArgumentUsageError('--enable-application-accelerator {}'.format(suffix))
    if namespace.application_configuration_service_generation:
        raise ArgumentUsageError('--application-configuration-service-generation {}'.format(suffix))


def validate_instance_count(namespace):
    if namespace.instance_count is not None:
        if namespace.instance_count < 1:
            raise InvalidArgumentValueError("--instance-count must be greater than 0")


def validate_instance_not_existed(client, name, location):
    availability_parameters = models.NameAvailabilityParameters(type="Microsoft.AppPlatform/Spring", name=name)
    name_availability = client.services.check_name_availability(location, availability_parameters)
    if not name_availability.name_available and name_availability.reason == "AlreadyExists":
        raise InvalidArgumentValueError("The service name '{}' is already taken.".format(name))


def validate_name(namespace):
    namespace.name = namespace.name.lower()
    matchObj = match(r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', namespace.name)
    if matchObj is None:
        raise InvalidArgumentValueError(
            '--name should start with lowercase and only contain numbers and lowercases with length [4,31]')


def validate_app_name(namespace):
    if namespace.app is not None:
        namespace.app = namespace.app.lower()
        matchObj = match(r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', namespace.app)
        if matchObj is None:
            raise InvalidArgumentValueError(
                '--app should start with lowercase and only contain numbers and lowercases with length [4,31]')


def validate_deployment_name(namespace):
    if namespace.deployment is not None:
        namespace.deployment = namespace.deployment.lower()
        if namespace.deployment is None:
            return

        matchObj = match(
            r'^[a-z][a-z0-9-]{2,30}[a-z0-9]$', namespace.deployment)
        if matchObj is None:
            raise InvalidArgumentValueError(
                '--deployment should start with lowercase and only contain numbers and lowercases with length [4,31]')


def validate_resource_id(namespace):
    if not is_valid_resource_id(namespace.resource_id):
        raise InvalidArgumentValueError("Invalid resource id {}".format(namespace.resource_id))


def validate_cosmos_type(namespace):
    if namespace.api_type is None:
        return
    type = ApiType(namespace.api_type)
    if type in (ApiType.mongo, ApiType.sql, ApiType.gremlin):
        if namespace.database_name is None:
            raise InvalidArgumentValueError(
                "Cosmosdb with type {} should specify database name".format(type))

    if type == ApiType.cassandra:
        if namespace.key_space is None:
            raise InvalidArgumentValueError(
                "Cosmosdb with type {} should specify key space".format(type))

    if type == ApiType.gremlin:
        if namespace.key_space is None:
            raise InvalidArgumentValueError(
                "Cosmosdb with type {} should specify collection name".format(type))


def validate_jvm_options(namespace):
    if namespace.jvm_options is not None:
        namespace.jvm_options = namespace.jvm_options.strip('\'')


def validate_ingress_timeout(namespace):
    if namespace.ingress_read_timeout is not None and (namespace.ingress_read_timeout < 1 or
                                                       namespace.ingress_read_timeout > 1800):
        raise InvalidArgumentValueError("Invalid value: Ingress read timeout must be in the range [1,1800].")


def validate_remote_debugging_port(namespace):
    if namespace.remote_debugging_port is not None and (namespace.remote_debugging_port < 1024 or
                                                        namespace.remote_debugging_port > 65535):
        raise InvalidArgumentValueError("Invalid value: remote debugging port must be in the range [1024,65535].")


def validate_ingress_send_timeout(namespace):
    if namespace.ingress_send_timeout is not None and (namespace.ingress_send_timeout < 1 or
                                                       namespace.ingress_send_timeout > 1800):
        raise InvalidArgumentValueError("Invalid value: Ingress send timeout must be in the range [1,1800].")


def validate_ingress_session_max_age(namespace):
    if namespace.session_max_age is not None \
            and (namespace.session_max_age < 0 or namespace.session_max_age > 7 * 24 * 3600):
        raise InvalidArgumentValueError("Invalid value: Ingress session max-age must between 0 seconds and 7 days.")


def validate_ingress_client_auth_certificates(namespace):
    if namespace.client_auth_certs is not None:
        namespace.client_auth_certs = namespace.client_auth_certs.split()


def validate_tracing_parameters_asc_create(namespace):
    if (namespace.app_insights or namespace.app_insights_key or namespace.sampling_rate is not None) \
            and namespace.disable_app_insights:
        raise InvalidArgumentValueError(
            "Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
            "can not be set with '--disable-app-insights'.")
    _validate_app_insights_parameters(namespace)


def validate_dataplane_public_endpoint(namespace):
    if namespace.enable_log_stream_public_endpoint is not None and namespace.enable_dataplane_public_endpoint is not None:
        if namespace.enable_log_stream_public_endpoint != namespace.enable_dataplane_public_endpoint:
            raise InvalidArgumentValueError("The value of enable_log_stream_public_endpoint and "
                                            "enable_dataplane_public_endpoint should be the same, "
                                            "you cannot set one to false and another to true.")


def validate_tracing_parameters_asc_update(namespace):
    if (namespace.app_insights or namespace.app_insights_key) and namespace.disable_app_insights:
        raise InvalidArgumentValueError(
            "Conflict detected: '--app-insights' or '--app-insights-key' "
            "can not be set with '--disable-app-insights'.")
    if namespace.app_insights and namespace.app_insights_key:
        raise InvalidArgumentValueError(
            "Conflict detected: '--app-insights' and '--app-insights-key' can not be set at the same time.")
    if namespace.app_insights == "":
        raise InvalidArgumentValueError("Conflict detected: '--app-insights' can not be empty.")


def validate_java_agent_parameters(namespace):
    """TODO (jiec) Deco this function when 'enable-java-agent' is decommissioned.
    """
    if namespace.disable_app_insights and namespace.enable_java_agent:
        raise InvalidArgumentValueError(
            "Conflict detected: '--enable-java-agent' and '--disable-app-insights' "
            "can not be set at the same time.")


def validate_app_insights_parameters(cmd, namespace):
    if (namespace.app_insights or namespace.app_insights_key or namespace.sampling_rate is not None) \
            and namespace.disable:
        raise InvalidArgumentValueError(
            "Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
            "can not be set with '--disable'.")
    if not namespace.app_insights \
            and not namespace.app_insights_key \
            and namespace.sampling_rate is None \
            and not namespace.disable:
        raise InvalidArgumentValueError("Invalid value: nothing is updated for application insights.")
    _validate_app_insights_parameters(namespace)
    validate_app_insights_command_not_supported_tier(cmd, namespace)


def _validate_app_insights_parameters(namespace):
    if namespace.app_insights and namespace.app_insights_key:
        raise InvalidArgumentValueError(
            "Conflict detected: '--app-insights' and '--app-insights-key' can not be set at the same time.")
    if namespace.app_insights == "":
        raise InvalidArgumentValueError("Invalid value: '--app-insights' can not be empty.")
    if namespace.app_insights_key == "":
        raise InvalidArgumentValueError("Invalid value: '--app-insights-key' can not be empty.")
    if namespace.sampling_rate is not None and (namespace.sampling_rate < 0 or namespace.sampling_rate > 100):
        raise InvalidArgumentValueError("Invalid value: Sampling Rate must be in the range [0,100].")


def validate_app_insights_command_not_supported_tier(cmd, namespace):
    if is_enterprise_tier(cmd, namespace.resource_group, namespace.name):
        raise NotSupportedPricingTierError("Enterprise tier service instance {} in group {} is not supported in this command, ".format(namespace.name, namespace.resource_group) +
                                           "please refer to 'az spring build-service builder buildpack-binding' command group.")


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
                raise InvalidArgumentValueError('--vnet {0} is not a valid name or resource ID'.format(vnet_id))
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
                raise InvalidArgumentValueError('--vnet {0} is not a valid VirtualNetwork resource ID'.format(vnet_id))
        namespace.app_subnet = _construct_subnet_id(vnet_id, namespace.app_subnet)
        namespace.service_runtime_subnet = _construct_subnet_id(vnet_id, namespace.service_runtime_subnet)
    else:
        app_vnet_id = _parse_vnet_id_from_subnet(namespace.app_subnet)
        service_runtime_vnet_id = _parse_vnet_id_from_subnet(namespace.service_runtime_subnet)
        if app_vnet_id.lower() != service_runtime_vnet_id.lower():
            raise InvalidArgumentValueError('--app-subnet and --service-runtime-subnet should be in the same Virtual Networks.')
        vnet_id = app_vnet_id
    if namespace.app_subnet.lower() == namespace.service_runtime_subnet.lower():
        raise InvalidArgumentValueError('--app-subnet and --service-runtime-subnet should not be the same.')

    vnet_obj = _get_vnet(cmd, vnet_id)
    instance_location = namespace.location
    if instance_location is None:
        instance_location = _get_rg_location(cmd.cli_ctx, namespace.resource_group)
    else:
        instance_location_slice = instance_location.split(" ")
        instance_location = "".join([piece.lower()
                                     for piece in instance_location_slice])
    if vnet_obj["location"].lower() != instance_location.lower():
        raise InvalidArgumentValueError('--vnet and Azure Spring Apps instance should be in the same location.')
    for subnet in vnet_obj["subnets"]:
        _validate_subnet(namespace, subnet)
    _validate_route_table(namespace, vnet_obj)

    if namespace.reserved_cidr_range:
        _validate_cidr_range(namespace)
    else:
        namespace.reserved_cidr_range = _set_default_cidr_range(vnet_obj["addressSpace"]["addressPrefixes"]) if \
            vnet_obj and vnet_obj.get("addressSpace", None) and vnet_obj["addressSpace"].get("addressPrefixes", None) \
            else '10.234.0.0/16,10.244.0.0/16,172.17.0.1/16'


def _validate_subnet(namespace, subnet):
    name = ''
    limit = 32
    if subnet["id"].lower() == namespace.app_subnet.lower():
        name = 'app-subnet'
        limit = 28
    elif subnet["id"].lower() == namespace.service_runtime_subnet.lower():
        name = 'service-runtime-subnet'
        limit = 28
    else:
        return
    if subnet.get("ipConfigurations", None):
        raise InvalidArgumentValueError('--{} should not have connected device.'.format(name))
    address = ip_network(subnet["addressPrefix"], strict=False)
    if address.prefixlen > limit:
        raise InvalidArgumentValueError('--{0} should contain at least /{1} address, got /{2}'.format(name, limit, address.prefixlen))


def _get_vnet(cmd, vnet_id):
    vnet = parse_resource_id(vnet_id)
    from .aaz.latest.network.vnet import Show as _VirtualNetworkShow

    class VirtualNetworkShow(_VirtualNetworkShow):
        @classmethod
        def _build_arguments_schema(cls, *args, **kwargs):
            from azure.cli.core.aaz import AAZStrArg
            args_schema = super()._build_arguments_schema(*args, **kwargs)
            args_schema.subscription_id = AAZStrArg()
            return args_schema

        def pre_operations(self):
            from azure.cli.core.aaz import has_value
            args = self.ctx.args
            if has_value(args.subscription_id):
                self.ctx._subscription_id = args.subscription_id.to_serialized_data()
    get_args = {
        'name': vnet['resource_name'],
        'subscription_id': vnet['subscription'],
        'resource_group': vnet['resource_group']
    }
    return VirtualNetworkShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)


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
        raise InvalidArgumentValueError('Cannot set "reserved-cidr-range" automatically.'
                                        'Please specify "--reserved-cidr-range" with 3 unused CIDR ranges in your '
                                        'network environment.')


def _parse_vnet_id_from_subnet(subnet_id):
    if not is_valid_resource_id(subnet_id):
        raise InvalidArgumentValueError('{0} is not a valid subnet resource ID'.format(subnet_id))
    subnet = parse_resource_id(subnet_id)
    if subnet['namespace'].lower() != 'microsoft.network' or \
       subnet['type'].lower() != 'virtualnetworks' or \
       'resource_type' not in subnet or subnet['resource_type'].lower() != 'subnets':
        raise InvalidArgumentValueError('{0} is not a valid subnet resource ID'.format(subnet_id))
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
            raise InvalidArgumentValueError('subnet {0} is not a valid name or resource ID'.format(subnet))
        # subnet name is given
        return vnet_id + '/subnets/' + subnet
    if not subnet.lower().startswith(vnet_id.lower()):
        raise InvalidArgumentValueError('subnet {0} is not under virtual network {1}'.format(subnet, vnet_id))
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
        raise InvalidArgumentValueError('--reserved-cidr-range should be 3 unused /16 IP ranges')
    ipv4 = [_validate_ip(ip, 16) for ip in ranges]
    # check no overlap with each other
    for i, item in enumerate(ipv4):
        for j in range(i + 1, len(ipv4)):
            if item.overlaps(ipv4[j]):
                raise InvalidArgumentValueError(
                    '--reserved-cidr-range should not overlap each other, but {0} and {1} overlapping.'
                    .format(ranges[i], ranges[j]))
    namespace.reserved_cidr_range = ','.join(ranges)


def _validate_ip(ip, prefix):
    try:
        # Host bits set can be non-zero? Here treat it as valid.
        ip_address = ip_network(ip, strict=False)
        if ip_address.version != 4:
            raise InvalidArgumentValueError('{0} is not a valid IPv4 CIDR.'.format(ip))
        if ip_address.prefixlen > prefix:
            raise InvalidArgumentValueError(
                '{0} doesn\'t has valid CIDR prefix. '
                ' --reserved-cidr-range should be 3 unused /16 IP ranges.'.format(ip))
        return ip_address
    except ValueError:
        raise InvalidArgumentValueError('{0} is not a valid CIDR'.format(ip))


def validate_vnet_required_parameters(namespace):
    # pylint: disable=too-many-boolean-expressions
    if not namespace.app_subnet and \
       not namespace.service_runtime_subnet and \
       not namespace.app_network_resource_group and \
       not namespace.service_runtime_network_resource_group and \
       not namespace.reserved_cidr_range and \
       not namespace.vnet:
        return
    if namespace.sku and _parse_sku_name(namespace.sku) == 'basic':
        raise InvalidArgumentValueError('Virtual Network Injection is not supported for Basic tier.')
    if not namespace.app_subnet \
       or not namespace.service_runtime_subnet:
        raise InvalidArgumentValueError(
            '--app-subnet, --service-runtime-subnet must be set when deploying to VNet')


def validate_node_resource_group(namespace):
    validate_vnet_required_parameters(namespace)
    _validate_resource_group_name(namespace.service_runtime_network_resource_group,
                                  'service-runtime-network-resource-group')
    _validate_resource_group_name(namespace.app_network_resource_group, 'app-network-resource-group')


def _parse_sku_name(sku):
    if not sku:
        return 'standard'
    if type(sku) is str or type(sku) is DefaultStr:
        return sku.lower()
    return sku.tier.lower()


def _validate_resource_group_name(name, message_name):
    if not name:
        return
    matchObj = match(r'^[-\w\._\(\)]+$', name)
    if matchObj is None:
        raise InvalidArgumentValueError('--{0} must conform to the following pattern: \'^[-\\w\\._\\(\\)]+$\'.'.format(message_name))


def _validate_route_table(namespace, vnet_obj):
    app_route_table_id = ""
    runtime_route_table_id = ""
    for subnet in vnet_obj["subnets"]:
        if subnet["id"].lower() == namespace.app_subnet.lower() and subnet.get("routeTable", None):
            app_route_table_id = subnet["routeTable"]["id"]
        if subnet["id"].lower() == namespace.service_runtime_subnet.lower() and subnet.get("routeTable", None):
            runtime_route_table_id = subnet["routeTable"]["id"]

    if app_route_table_id and runtime_route_table_id:
        if app_route_table_id == runtime_route_table_id:
            raise InvalidArgumentValueError('--service-runtime-subnet and --app-subnet should associate with different route tables.')
    if (app_route_table_id and not runtime_route_table_id) \
            or (not app_route_table_id and runtime_route_table_id):
        raise InvalidArgumentValueError(
            '--service-runtime-subnet and --app-subnet should both associate with different route tables or neither.')


def validate_jar(namespace):
    server_runtime_version = _get_server_runtime(namespace)
    cmd_runtime_version = namespace.runtime_version
    runtime_version = cmd_runtime_version if cmd_runtime_version is not None else server_runtime_version
    if namespace.disable_validation:
        telemetry.set_user_fault("jar validation is disabled")
        return
    file_type = _get_file_type(runtime_version, namespace.artifact_path)
    if file_type != "Jar":
        return
    values = _parse_jar_file(namespace.artifact_path)
    if values is None:
        # ignore jar_file check
        return

    tips = ", if you choose to ignore these errors, turn validation off with --disable-validation"
    if not values["has_jar"] and not values["has_class"]:
        telemetry.set_user_fault("invalid_jar_no_class_jar")
        raise InvalidArgumentValueError(
            "Do not find any class or jar file, please check if your artifact is a valid fat jar" + tips)
    if not values["has_manifest"]:
        telemetry.set_user_fault("invalid_jar_no_manifest")
        raise InvalidArgumentValueError(
            "Do not find MANIFEST.MF, please check if your artifact is a valid fat jar" + tips)
    if values["file_size"] / 1024 / 1024 < 10:
        telemetry.set_user_fault("invalid_jar_thin_jar")
        raise InvalidArgumentValueError("Thin jar detected, please check if your artifact is a valid fat jar" + tips)
    version_number = int(runtime_version[len("Java_"):])
    if values["jdk_version"] not in _java_runtime_in_number():
        raise InvalidArgumentValueError("Your java application is compiled with {}, currently the supported "
                                        "java version is Java_8, Java_11, Java_17 and Java_21, you can configure the java runtime "
                                        "with --runtime-version".format("Java_" + str(values["jdk_version"])) + tips)
    if values["jdk_version"] > version_number:
        telemetry.set_user_fault("invalid_java_runtime")
        raise InvalidArgumentValueError("Invalid java runtime, the runtime you configured is {}, the jar you use is "
                                        "compiled with {}, you can configure the java runtime with --runtime-version".
                                        format(runtime_version, "Java_" + str(values["jdk_version"])) + tips)
    # validate spring boot version
    if values["spring_boot_version"] and values["spring_boot_version"].startswith('1'):
        telemetry.set_user_fault("old_spring_boot_version")
        raise InvalidArgumentValueError(
            "The spring boot {} you are using is not supported. To get the latest supported "
            "versions please refer to: https://aka.ms/ascspringversion".format(values["spring_boot_version"]) + tips)

    # old spring cloud version, need to import ms sdk <= 2.2.1
    if values["spring_cloud_version"]:
        if values["spring_cloud_version"] < "2.2.5":
            if not values["ms_sdk_version"] or values["ms_sdk_version"] > "2.2.1":
                telemetry.set_user_fault("old_spring_cloud_version")
                raise InvalidArgumentValueError(
                    "The spring cloud {} you are using is not supported. To get the latest supported "
                    "versions please refer to: https://aka.ms/ascspringversion".format(values["spring_cloud_version"]) + tips)
        else:
            if values["ms_sdk_version"] and values["ms_sdk_version"] <= "2.2.1":
                telemetry.set_user_fault("old_ms_sdk_version")
                raise InvalidArgumentValueError(
                    "The spring-cloud-starter-azure-spring-cloud-client version {} is no longer "
                    "supported, please remove it or upgrade to a higher version, to get the latest "
                    "supported versions please refer to: "
                    "https://mvnrepository.com/artifact/com.microsoft.azure/spring-cloud-starter-azure"
                    "-spring-cloud-client".format(values["ms_sdk_version"]) + tips)

    if not values["has_actuator"]:
        telemetry.set_user_fault("no_spring_actuator")
        logger.warning(
            "Seems you do not import spring actuator, thus metrics are not enabled, please refer to "
            "https://aka.ms/ascdependencies for more details")


def _get_server_runtime(namespace):
    try:
        return namespace.deployment.properties.source.runtime_version
    except:
        return None


def _parse_jar_file(artifact_path):
    file_size = 0
    spring_boot_version = ""
    spring_cloud_version = ""
    has_actuator = False
    has_manifest = False
    has_jar = False
    has_class = False
    ms_sdk_version = ""
    jdk_version = ""

    spring_boot_pattern = "/spring-boot-[0-9].*jar"
    spring_boot_actuator_pattern = "/spring-boot-actuator-[0-9].*jar"
    ms_sdk_pattern = "/spring-cloud-starter-azure-spring-cloud-client-[0-9].*jar"
    spring_cloud_config_pattern = "/spring-cloud-config-client-[0-9].*jar"
    spring_cloud_eureka_pattern = "/spring-cloud-netflix-eureka-client-[0-9].*jar"

    try:
        with zipfile.ZipFile(artifact_path, 'r') as zf:
            files = zf.infolist()
            for file in files:
                file_size += file.file_size
                file_name = file.filename

                if file_name.lower().endswith('.jar'):
                    has_jar = True
                if file_name.lower().endswith('.class'):
                    has_class = True
                    binary_content = zf.open(file_name)
                    binary_content.read(4)
                    binary_content.read(2)
                    major_version = int.from_bytes(binary_content.read(2), byteorder='big')
                    # refers to https://www.baeldung.com/java-find-class-version#class-version-in-java
                    jdk_version = major_version - 44
                if file_name.upper().endswith('MANIFEST.MF'):
                    has_manifest = True
                if search(spring_boot_pattern, file_name):
                    prefix = 'spring-boot-'
                    spring_boot_version = file_name[file_name.index(prefix) + len(prefix):file_name.index('.jar')]
                if search(spring_boot_actuator_pattern, file_name):
                    has_actuator = True
                if search(ms_sdk_pattern, file_name):
                    prefix = 'spring-cloud-starter-azure-spring-cloud-client-'
                    ms_sdk_version = file_name[file_name.index(prefix) + len(prefix):file_name.index('.jar')]
                if search(spring_cloud_config_pattern, file_name):
                    prefix = 'spring-cloud-config-client-'
                    spring_cloud_version = file_name[file_name.index(prefix) + len(prefix):file_name.index('.jar')]
                if search(spring_cloud_eureka_pattern, file_name):
                    prefix = 'spring-cloud-netflix-eureka-client-'
                    spring_cloud_version = file_name[file_name.index(prefix) + len(prefix):file_name.index('.jar')]
        return dict(file_size=file_size, spring_boot_version=spring_boot_version,
                    spring_cloud_version=spring_cloud_version, has_actuator=has_actuator,
                    has_manifest=has_manifest, has_jar=has_jar, has_class=has_class,
                    ms_sdk_version=ms_sdk_version, jdk_version=jdk_version)
    except Exception as err:  # pylint: disable=broad-except
        telemetry.set_exception("parse user jar file failed, " + str(err))
        return None


def validate_config_server_ssh_or_warn(namespace):
    private_key = namespace.private_key
    host_key = namespace.host_key
    host_key_algorithm = namespace.host_key_algorithm
    strict_host_key_checking = namespace.strict_host_key_checking
    if private_key or host_key or host_key_algorithm or strict_host_key_checking:
        logger.warning("SSH authentication only supports SHA-1 signature under Config Server restriction. "
                       "Please refer to https://aka.ms/asa-configserver-ssh to understand how to use SSH under this restriction.")


def validate_managed_environment(namespace):
    managed_environment_id = namespace.managed_environment
    if managed_environment_id:
        if not is_valid_resource_id(managed_environment_id):
            raise InvalidArgumentValueError('--managed-environment {0} is not a valid Container App Environment resource ID'.format(managed_environment_id))
        managed_environment = parse_resource_id(managed_environment_id)
        if managed_environment['namespace'].lower() != 'microsoft.app' or managed_environment['type'].lower() != 'managedenvironments':
            raise InvalidArgumentValueError('--managed-environment {0} is not a valid Container App Environment resource ID'.format(managed_environment_id))


def validate_server_version(cmd, namespace):
    if namespace.server_version and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ArgumentUsageError("'--server-version' only supports for Standard/Basic tier Spring instance.")


def validate_planned_maintenance(namespace):
    if namespace.enable_planned_maintenance is True \
            and (namespace.planned_maintenance_day is None or namespace.planned_maintenance_start_hour is None):
        raise InvalidArgumentValueError("Invalid value: --planned-maintenance-day and --planned-maintenance-start-hour must be set when --enable-planned-maintenance is set.")
    if namespace.enable_planned_maintenance is False \
            and (namespace.planned_maintenance_day is not None or namespace.planned_maintenance_start_hour is not None):
        raise InvalidArgumentValueError("Invalid value: --planned-maintenance-day and --planned-maintenance-start-hour can only be set when --enable-planned-maintenance is set.")
    if namespace.planned_maintenance_start_hour is not None \
            and (namespace.planned_maintenance_start_hour < 0 or namespace.planned_maintenance_start_hour > 23):
        raise InvalidArgumentValueError("Invalid value: planned maintenance start hour must be in the range [0,23].")
