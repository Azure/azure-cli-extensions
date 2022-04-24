# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from re import match
from azure.cli.core.commands.validators import validate_tag
from azure.core.exceptions import ResourceNotFoundError
from azure.cli.core.azclierror import (ArgumentUsageError, ClientRequestError,
                                       InvalidArgumentValueError,
                                       MutuallyExclusiveArgumentError)
from azure.core.exceptions import ResourceNotFoundError
from knack.log import get_logger

from ._resource_quantity import validate_cpu as validate_and_normalize_cpu
from ._resource_quantity import \
    validate_memory as validate_and_normalize_memory
from ._util_enterprise import (
    is_enterprise_tier, get_client
)
from ._validators import (validate_instance_count, _parse_sku_name)
from .buildpack_binding import (DEFAULT_BUILD_SERVICE_NAME)

logger = get_logger(__name__)


def only_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and not is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' only supports for Enterprise tier Spring instance.".format(namespace.command))


def not_support_enterprise(cmd, namespace):
    if namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ClientRequestError("'{}' doesn't support for Enterprise tier Spring instance.".format(namespace.command))


def validate_build_env(cmd, namespace):
    if namespace.build_env is not None and namespace.resource_group and namespace.service and not is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ArgumentUsageError("'--build-env' only supports for Enterprise tier Spring instance.")
    else:
        if isinstance(namespace.build_env, list):
            env_dict = {}
            for item in namespace.build_env:
                env_dict.update(validate_tag(item))
            namespace.build_env = env_dict


def validate_target_module(cmd, namespace):
    if namespace.target_module is not None and namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ArgumentUsageError("'--target-module' doesn't support for Enterprise tier Spring instance.")


def validate_runtime_version(cmd, namespace):
    if namespace.runtime_version is not None and namespace.resource_group and namespace.service and is_enterprise_tier(cmd, namespace.resource_group, namespace.service):
        raise ArgumentUsageError("'--runtime-version' doesn't support for Enterprise tier Spring instance.")


def validate_builder_create(cmd, namespace):
    client = get_client(cmd)
    try:
        builder = client.build_service_builder.get(namespace.resource_group,
                                                   namespace.service,
                                                   DEFAULT_BUILD_SERVICE_NAME,
                                                   namespace.name)
        if builder is not None:
            raise ClientRequestError('Builder {} already exists.'.format(namespace.name))
    except ResourceNotFoundError:
        pass


def validate_builder_update(cmd, namespace):
    client = get_client(cmd)
    try:
        client.build_service_builder.get(namespace.resource_group,
                                         namespace.service,
                                         DEFAULT_BUILD_SERVICE_NAME,
                                         namespace.name)
    except ResourceNotFoundError:
        raise ClientRequestError('Builder {} does not exist.'.format(namespace.name))


def validate_builder_resource(namespace):
    if namespace.builder_json is not None and namespace.builder_file is not None:
        raise ClientRequestError("You can only specify either --builder-json or --builder-file.")
    if namespace.builder_json is None and namespace.builder_file is None:
        raise ClientRequestError("--builder-json or --builder-file is required.")


def validate_build_pool_size(namespace):
    if _parse_sku_name(namespace.sku) == 'enterprise':
        if namespace.build_pool_size is None:
            namespace.build_pool_size = 'S1'
    else:
        if namespace.build_pool_size is not None:
            raise ClientRequestError("You can only specify --build-pool-size with enterprise tier.")


def validate_cpu(namespace):
    namespace.cpu = validate_and_normalize_cpu(namespace.cpu)


def validate_memory(namespace):
    namespace.memory = validate_and_normalize_memory(namespace.memory)


def validate_git_uri(namespace):
    uri = namespace.uri
    if uri and (not uri.startswith("https://")) and (not uri.startswith("git@")):
        raise InvalidArgumentValueError("Git URI should start with \"https://\" or \"git@\"")


def validate_config_file_patterns(namespace):
    if namespace.config_file_patterns:
        _validate_patterns(namespace.config_file_patterns)


def validate_acs_patterns(namespace):
    if namespace.patterns:
        _validate_patterns(namespace.patterns)


def _validate_patterns(patterns):
    pattern_list = patterns.split(',')
    invalid_list = [p for p in pattern_list if not _is_valid_pattern(p)]
    if len(invalid_list) > 0:
        logger.warning("Patterns '%s' are invalid.", ','.join(invalid_list))
        raise InvalidArgumentValueError("Patterns should be the collection of patterns separated by comma, each pattern in the format of 'application' or 'application/profile'")


def _is_valid_pattern(pattern):
    return _is_valid_app_name(pattern) or _is_valid_app_and_profile_name(pattern)


def _is_valid_app_name(pattern):
    return match(r"^[a-zA-Z][-_a-zA-Z0-9]*$", pattern) is not None


def _is_valid_profile_name(profile):
    return profile == "*" or _is_valid_app_name(profile)


def _is_valid_app_and_profile_name(pattern):
    parts = pattern.split('/')
    return len(parts) == 2 and _is_valid_app_name(parts[0]) and _is_valid_profile_name(parts[1])


def validate_gateway_update(namespace):
    _validate_sso(namespace)
    validate_cpu(namespace)
    validate_memory(namespace)
    validate_instance_count(namespace)


def validate_api_portal_update(namespace):
    _validate_sso(namespace)
    validate_instance_count(namespace)


def _validate_sso(namespace):
    all_provided = namespace.scope is not None and namespace.client_id is not None and namespace.client_secret is not None and namespace.issuer_uri is not None
    none_provided = namespace.scope is None and namespace.client_id is None and namespace.client_secret is None and namespace.issuer_uri is None
    if not all_provided and not none_provided:
        raise ArgumentUsageError("Single Sign On configurations '--scope --client-id --client-secret --issuer-uri' should be all provided or none provided.")
    if namespace.scope is not None:
        namespace.scope = namespace.scope.split(",") if namespace.scope else []


def validate_routes(namespace):
    if namespace.routes_json is not None and namespace.routes_file is not None:
        raise MutuallyExclusiveArgumentError("You can only specify either --routes-json or --routes-file.")


def validate_gateway_instance_count(namespace):
    if namespace.gateway_instance_count is not None:
        if namespace.enable_gateway is False:
            raise ArgumentUsageError("--gateway-instance-count can only be set when enable gateway.")
        if namespace.gateway_instance_count < 1:
            raise ArgumentUsageError("--gateway-instance-count must be greater than 0")


def validate_api_portal_instance_count(namespace):
    if namespace.api_portal_instance_count is not None:
        if namespace.enable_api_portal is False:
            raise ArgumentUsageError("--api-portal-instance-count can only be set when enable API portal.")
        if namespace.api_portal_instance_count < 1:
            raise ArgumentUsageError("--api-portal-instance-count must be greater than 0")


def validate_buildpack_binding_properties(namespace):
    """ Extracts multiple space-separated properties in key[=value] format """
    if isinstance(namespace.properties, list):
        properties_dict = {}
        for item in namespace.properties:
            properties_dict.update(validate_tag(item))
        namespace.properties = properties_dict


def validate_buildpack_binding_secrets(namespace):
    """ Extracts multiple space-separated secrets in key[=value] format """
    if isinstance(namespace.secrets, list):
        secrets_dict = {}
        for item in namespace.secrets:
            secrets_dict.update(validate_tag(item))
        namespace.secrets = secrets_dict


def validate_buildpack_binding_not_exist(cmd, namespace):
    client = get_client(cmd)
    try:
        binding_resource = client.buildpack_binding.get(namespace.resource_group,
                                                        namespace.service,
                                                        DEFAULT_BUILD_SERVICE_NAME,
                                                        namespace.builder_name,
                                                        namespace.name)
        if binding_resource is not None:
            raise ClientRequestError('buildpack Binding {} in builder {} already exists '
                                     'in resource group {}, service {}. You can edit it by set command.'
                                     .format(namespace.name, namespace.resource_group, namespace.service, namespace.builder_name))
    except ResourceNotFoundError:
        # Excepted case
        pass


def validate_buildpack_binding_exist(cmd, namespace):
    client = get_client(cmd)
    # If not exists exception will be raised
    client.buildpack_binding.get(namespace.resource_group,
                                 namespace.service,
                                 DEFAULT_BUILD_SERVICE_NAME,
                                 namespace.builder_name,
                                 namespace.name)
