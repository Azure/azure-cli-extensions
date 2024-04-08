# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

import os
from re import match
from azure.cli.core import telemetry
from azure.cli.core.commands.validators import validate_tag
from azure.core.exceptions import ResourceNotFoundError
from azure.cli.core.azclierror import (ArgumentUsageError, ClientRequestError,
                                       InvalidArgumentValueError,
                                       MutuallyExclusiveArgumentError)
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger
from .vendored_sdks.appplatform.v2024_05_01_preview.models import (ApmReference, CertificateReference)
from .vendored_sdks.appplatform.v2024_05_01_preview.models._app_platform_management_client_enums import (ApmType, ConfigurationServiceGeneration)

from ._gateway_constant import (GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE, GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE,
                                GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE, GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE)
from ._resource_quantity import validate_cpu as validate_and_normalize_cpu
from ._resource_quantity import \
    validate_memory as validate_and_normalize_memory
from ._util_enterprise import (
    is_enterprise_tier, get_client
)
from ._validators import (validate_instance_count, _parse_sku_name, _parse_jar_file)
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
                if item:
                    comps = item.split('=', 1)
                    if len(comps) <= 1:
                        raise ArgumentUsageError("The value of env {} should not be empty.".format(item))
                    else:
                        if match(r"^[-._a-zA-Z][-._a-zA-Z0-9]*$", comps[0]):
                            result = {}
                            result = {comps[0]: comps[1]}
                            env_dict.update(result)
                        else:
                            raise ArgumentUsageError("The env name {} is not allowed. The valid env name should follow the pattern '[-._a-zA-Z][-._a-zA-Z0-9]*'(For example, BP_JVM_VERSION).".format(comps[0]))
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
        if namespace.build_pool_size is None and not namespace.disable_build_service:
            namespace.build_pool_size = 'S1'
        elif namespace.build_pool_size is not None and namespace.disable_build_service:
            raise InvalidArgumentValueError("Conflict detected: '--build-pool-size' can not be set with '--disable-build-service'.")
    else:
        if namespace.build_pool_size is not None:
            raise ClientRequestError("You can only specify --build-pool-size with enterprise tier.")


def validate_build_service(namespace):
    if _parse_sku_name(namespace.sku) == 'enterprise':
        if (namespace.registry_server or namespace.registry_username or namespace.registry_password is not None) \
                and ((namespace.registry_server is None) or (namespace.registry_username is None) or (namespace.registry_password is None)):
            raise InvalidArgumentValueError(
                "The'--registry-server', '--registry-username' and '--registry-password' should be specified together.")
        if (namespace.registry_server or namespace.registry_username or namespace.registry_password is not None) \
                and namespace.disable_build_service:
            raise InvalidArgumentValueError(
                "Conflict detected: '--registry-server', '--registry-username' and '--registry-password' "
                "can not be set with '--disable-build-service'.")
    else:
        if namespace.disable_build_service or namespace.registry_server or namespace.registry_username or namespace.registry_password is not None:
            raise InvalidArgumentValueError("The build service is only supported with enterprise tier.")


def validate_build_create(cmd, namespace):
    client = get_client(cmd)
    try:
        build = client.build_service.get_build(namespace.resource_group,
                                               namespace.service,
                                               DEFAULT_BUILD_SERVICE_NAME,
                                               namespace.name)
        if build is not None:
            raise ClientRequestError('Build {} already exists.'.format(namespace.name))
    except ResourceNotFoundError:
        pass


def validate_build_update(cmd, namespace):
    client = get_client(cmd)
    try:
        build = client.build_service.get_build(namespace.resource_group,
                                               namespace.service,
                                               DEFAULT_BUILD_SERVICE_NAME,
                                               namespace.name)
        if namespace.builder is None:
            namespace.builder = build.properties.builder.split("/")[-1]
        if namespace.build_cpu is None:
            namespace.build_cpu = build.properties.resource_requests.cpu
        if namespace.build_memory is None:
            namespace.build_memory = build.properties.resource_requests.memory
        if namespace.build_env is None:
            namespace.build_env = build.properties.env
    except ResourceNotFoundError:
        raise ClientRequestError('Build {} does not exist.'.format(namespace.name))


def validate_central_build_instance(cmd, namespace):
    only_support_enterprise(cmd, namespace)
    client = get_client(cmd)
    try:
        build_service = client.build_service.get_build_service(namespace.resource_group,
                                                               namespace.service,
                                                               DEFAULT_BUILD_SERVICE_NAME)
        if not build_service.properties.container_registry:
            raise ClientRequestError('The command is only supported when using your own container registry.')
    except ResourceNotFoundError:
        raise ClientRequestError('Build Service is not enabled.')


def validate_source_path(namespace):
    arguments = [namespace.artifact_path, namespace.source_path]
    if all(not x for x in arguments):
        raise InvalidArgumentValueError('One of --artifact-path, --source-path must be provided.')
    valued_args = [x for x in arguments if x]
    if len(valued_args) > 1:
        raise InvalidArgumentValueError('At most one of --artifact-path, --source-path must be provided.')


def validate_artifact_path(namespace):
    if namespace.disable_validation:
        telemetry.set_user_fault("jar validation is disabled")
        return
    if namespace.artifact_path is None or os.path.splitext(namespace.artifact_path)[-1] != "jar":
        return
    values = _parse_jar_file(namespace.artifact_path)
    if values is None:
        # ignore jar_file check
        return
    file_size, spring_boot_version, spring_cloud_version, has_actuator, has_manifest, has_jar, has_class, ms_sdk_version, jdk_version = values

    tips = ", if you choose to ignore these errors, turn validation off with --disable-validation"
    if not has_jar and not has_class:
        telemetry.set_user_fault("invalid_jar_no_class_jar")
        raise InvalidArgumentValueError(
            "Do not find any class or jar file, please check if your artifact is a valid fat jar" + tips)
    if not has_manifest:
        telemetry.set_user_fault("invalid_jar_no_manifest")
        raise InvalidArgumentValueError(
            "Do not find MANIFEST.MF, please check if your artifact is a valid fat jar" + tips)
    if file_size / 1024 / 1024 < 10:
        telemetry.set_user_fault("invalid_jar_thin_jar")
        raise InvalidArgumentValueError("Thin jar detected, please check if your artifact is a valid fat jar" + tips)

    # validate spring boot version
    if spring_boot_version and spring_boot_version.startswith('1'):
        telemetry.set_user_fault("old_spring_boot_version")
        raise InvalidArgumentValueError(
            "The spring boot {} you are using is not supported. To get the latest supported "
            "versions please refer to: https://aka.ms/ascspringversion".format(spring_boot_version) + tips)

    # old spring cloud version, need to import ms sdk <= 2.2.1
    if spring_cloud_version:
        if spring_cloud_version < "2.2.5":
            if not ms_sdk_version or ms_sdk_version > "2.2.1":
                telemetry.set_user_fault("old_spring_cloud_version")
                raise InvalidArgumentValueError(
                    "The spring cloud {} you are using is not supported. To get the latest supported "
                    "versions please refer to: https://aka.ms/ascspringversion".format(spring_cloud_version) + tips)
        else:
            if ms_sdk_version and ms_sdk_version <= "2.2.1":
                telemetry.set_user_fault("old_ms_sdk_version")
                raise InvalidArgumentValueError(
                    "The spring-cloud-starter-azure-spring-cloud-client version {} is no longer "
                    "supported, please remove it or upgrade to a higher version, to get the latest "
                    "supported versions please refer to: "
                    "https://mvnrepository.com/artifact/com.microsoft.azure/spring-cloud-starter-azure"
                    "-spring-cloud-client".format(ms_sdk_version) + tips)

    if not has_actuator:
        telemetry.set_user_fault("no_spring_actuator")
        logger.warning(
            "Seems you do not import spring actuator, thus metrics are not enabled, please refer to "
            "https://aka.ms/ascdependencies for more details")


def validate_container_registry_update(cmd, namespace):
    validate_container_registry(namespace)
    client = get_client(cmd)
    try:
        client.container_registries.get(namespace.resource_group, namespace.service, namespace.name)
    except ResourceNotFoundError:
        raise ClientRequestError('Container Registry {} does not exist.'.format(namespace.name))


def validate_container_registry_create(cmd, namespace):
    validate_container_registry(namespace)
    client = get_client(cmd)
    try:
        container_registry = client.container_registries.get(namespace.resource_group, namespace.service, namespace.name)
        if container_registry is not None:
            raise ClientRequestError('Container Registry {} already exists.'.format(namespace.name))
    except ResourceNotFoundError:
        pass


def validate_container_registry(namespace):
    if not namespace.name or not namespace.username or not namespace.password or not namespace.server:
        raise InvalidArgumentValueError('The --name, --server, --username and --password must be provided.')


def validate_cpu(namespace):
    namespace.cpu = validate_and_normalize_cpu(namespace.cpu)


def validate_memory(namespace):
    namespace.memory = validate_and_normalize_memory(namespace.memory)


def validate_git_uri(namespace):
    uri = namespace.uri
    if uri and (not uri.startswith("https://")) and (not uri.startswith("git@")):
        raise InvalidArgumentValueError("Git URI should start with \"https://\" or \"git@\"")


def validate_acc_git_url(namespace):
    url = namespace.git_url
    if not url:
        raise ArgumentUsageError("Git Repository configurations '--git-url' should be all provided.")
    if url and (not url.startswith("https://")) and (not url.startswith("ssh://")):
        raise InvalidArgumentValueError("Git URL should start with \"https://\" or \"ssh://\"")


def validate_acc_git_refs(namespace):
    args = [namespace.git_branch, namespace.git_commit, namespace.git_tag]
    if all(x is None for x in args):
        raise ArgumentUsageError("Git Repository configurations at least one of '--git-branch --git-commit --git-tag' should be all provided.")


def validate_git_interval(namespace):
    if namespace.git_interval is not None:
        if namespace.git_interval < 1:
            raise InvalidArgumentValueError("--git-interval must be greater than 0")


def validate_acs_ssh_or_warn(namespace):
    private_key = namespace.private_key
    host_key = namespace.host_key
    host_key_algorithm = namespace.host_key_algorithm
    host_key_check = namespace.host_key_check
    if private_key or host_key or host_key_algorithm or host_key_check:
        logger.warning("SSH authentication only supports SHA-1 signature under ACS restriction. "
                       "Please refer to https://aka.ms/asa-acs-ssh to understand how to use SSH under this restriction.")


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


def validate_pattern_for_show_acs_configs(namespace):
    if namespace.config_file_pattern:
        if not _is_valid_pattern(namespace.config_file_pattern):
            raise InvalidArgumentValueError("Pattern should be in the format of 'application' or 'application/profile'")
        if _is_valid_app_and_profile_name(namespace.config_file_pattern):
            parts = namespace.config_file_pattern.split('/')
            if parts[1] == '*':
                namespace.config_file_pattern = f"{parts[0]}/default"
        elif _is_valid_app_name(namespace.config_file_pattern):
            namespace.config_file_pattern = f"{namespace.config_file_pattern}/default"


def _is_valid_pattern(pattern):
    return _is_valid_app_name(pattern) or _is_valid_app_and_profile_name(pattern)


def _is_valid_app_name(pattern):
    return match(r"^[a-zA-Z][-_a-zA-Z0-9]*$", pattern) is not None


def _is_valid_profile_name(profile):
    return profile == "*" or _is_valid_app_name(profile)


def _is_valid_app_and_profile_name(pattern):
    parts = pattern.split('/')
    return len(parts) == 2 and _is_valid_app_name(parts[0]) and _is_valid_profile_name(parts[1])


def validate_acs_create(namespace):
    if namespace.application_configuration_service_generation is not None:
        if namespace.enable_application_configuration_service is False:
            raise ArgumentUsageError("--application-configuration-service-generation can only be set when enable application configuration service.")


def validate_refresh_interval(namespace):
    if namespace.refresh_interval:
        if not isinstance(namespace.refresh_interval, int):
            raise InvalidArgumentValueError("--refresh-interval should be a number.")

        if namespace.refresh_interval < 0:
            raise ArgumentUsageError("--refresh-interval must be greater than or equal to 0.")


def validate_gateway_update(cmd, namespace):
    _validate_gateway_response_cache(namespace)
    _validate_sso(namespace)
    validate_cpu(namespace)
    validate_memory(namespace)
    validate_instance_count(namespace)
    _validate_gateway_apm_types(namespace)
    _validate_gateway_envs(namespace)
    _validate_gateway_secrets(namespace)
    validate_apm_reference(cmd, namespace)


def validate_api_portal_update(namespace):
    _validate_sso(namespace)
    validate_instance_count(namespace)


def validate_dev_tool_portal(namespace):
    args = [namespace.scopes, namespace.client_id, namespace.client_secret, namespace.metadata_url]
    if not all(args) and not all(x is None for x in args):
        raise ArgumentUsageError("Single Sign On configurations '--scopes --client-id --client-secret --metadata-url' should be all provided or none provided.")
    if namespace.scopes is not None:
        namespace.scopes = namespace.scopes.split(",") if namespace.scopes else []


def _validate_sso(namespace):
    all_provided = namespace.scope is not None and namespace.client_id is not None and namespace.client_secret is not None and namespace.issuer_uri is not None
    none_provided = namespace.scope is None and namespace.client_id is None and namespace.client_secret is None and namespace.issuer_uri is None
    if not all_provided and not none_provided:
        raise ArgumentUsageError("Single Sign On configurations '--scope --client-id --client-secret --issuer-uri' should be all provided or none provided.")
    if namespace.scope is not None:
        namespace.scope = namespace.scope.split(",") if namespace.scope else []


def _validate_gateway_apm_types(namespace):
    if namespace.apm_types is None:
        return
    for type in namespace.apm_types:
        if (type not in list(ApmType)):
            raise InvalidArgumentValueError("Allowed APM types are: " + ', '.join(list(ApmType)))


def _validate_gateway_envs(namespace):
    """ Extracts multiple space-separated properties in key[=value] format """
    if isinstance(namespace.properties, list):
        properties_dict = {}
        for item in namespace.properties:
            properties_dict.update(validate_tag(item))
        namespace.properties = properties_dict


def _validate_gateway_secrets(namespace):
    """ Extracts multiple space-separated secrets in key[=value] format """
    if isinstance(namespace.secrets, list):
        secrets_dict = {}
        for item in namespace.secrets:
            secrets_dict.update(validate_tag(item))
        namespace.secrets = secrets_dict


def _validate_gateway_response_cache(namespace):
    _validate_gateway_response_cache_exclusive(namespace)
    _validate_gateway_response_cache_scope(namespace)
    _validate_gateway_response_cache_size(namespace)
    _validate_gateway_response_cache_ttl(namespace)


def _validate_gateway_response_cache_exclusive(namespace):
    if namespace.enable_response_cache is not None and namespace.enable_response_cache is False \
        and (namespace.response_cache_scope is not None
             or namespace.response_cache_size is not None
             or namespace.response_cache_ttl is not None):
        raise InvalidArgumentValueError(
            "Conflict detected: Parameters in ['--response-cache-scope', '--response-cache-scope', '--response-cache-ttl'] "
            "cannot be set together with '--enable-response-cache false'.")


def _validate_gateway_response_cache_scope(namespace):
    scope = namespace.response_cache_scope
    if (scope is not None and not isinstance(scope, str)):
        raise InvalidArgumentValueError("The allowed values for '--response-cache-scope' are [{}, {}]".format(
            GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE, GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE
        ))
    if (scope is not None and isinstance(scope, str)):
        scope = scope.lower()
        if GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE.lower() != scope \
                and GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE.lower() != scope:
            raise InvalidArgumentValueError("The allowed values for '--response-cache-scope' are [{}, {}]".format(
                GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE, GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE
            ))
        # Normalize input
        if GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE.lower() == scope:
            namespace.response_cache_scope = GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE
        else:
            namespace.response_cache_scope = GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE


def _validate_gateway_response_cache_size(namespace):
    if namespace.response_cache_size is not None:
        size = namespace.response_cache_size
        if not isinstance(size, str):
            raise InvalidArgumentValueError('--response-cache-size should be a string')
        if GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE.lower() == size.lower():
            # Normalize the input
            namespace.response_cache_size = GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE
        else:
            pattern = r"^[1-9][0-9]{0,9}(GB|MB|KB)$"
            if not match(pattern, size):
                raise InvalidArgumentValueError(
                    "Invalid response cache size '{}', the regex used to validate is '{}'".format(size, pattern))


def _validate_gateway_response_cache_ttl(namespace):
    if namespace.response_cache_ttl is not None:
        ttl = namespace.response_cache_ttl
        if not isinstance(ttl, str):
            raise InvalidArgumentValueError('--response-cache-ttl should be a string')
        if GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE.lower() == ttl.lower():
            # Normalize the input
            namespace.response_cache_ttl = GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE
        else:
            pattern = r"^[1-9][0-9]{0,9}(h|m|s)$"
            if not match(pattern, ttl):
                raise InvalidArgumentValueError(
                    "Invalid response cache ttl '{}', the regex used to validate is '{}'".format(ttl, pattern))


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


def validate_customized_accelerator(namespace):
    validate_acc_git_url(namespace)
    validate_acc_git_refs(namespace)
    if namespace.accelerator_tags is not None:
        namespace.accelerator_tags = namespace.accelerator_tags.split(",") if namespace.accelerator_tags else []


def validate_apm_properties(namespace):
    """ Extracts multiple space-separated properties in key[=value] format """
    if isinstance(namespace.properties, list):
        properties_dict = {}
        for item in namespace.properties:
            properties_dict.update(validate_tag(item))
        namespace.properties = properties_dict


def validate_apm_secrets(namespace):
    """ Extracts multiple space-separated secrets in key[=value] format """
    if isinstance(namespace.secrets, list):
        secrets_dict = {}
        for item in namespace.secrets:
            secrets_dict.update(validate_tag(item))
        namespace.secrets = secrets_dict


def validate_apm_not_exist(cmd, namespace):
    client = get_client(cmd)
    try:
        apm_resource = client.apms.get(namespace.resource_group, namespace.service, namespace.name)
        if apm_resource is not None:
            raise ClientRequestError('APM {} already exists '
                                     'in resource group {}, service {}. You can edit it by update command.'
                                     .format(namespace.name, namespace.resource_group, namespace.service))
    except ResourceNotFoundError:
        # Excepted case
        pass


def validate_apm_update(cmd, namespace):
    client = get_client(cmd)
    try:
        client.apms.get(namespace.resource_group, namespace.service, namespace.name)
    except ResourceNotFoundError:
        raise ClientRequestError('APM {} does not exist.'.format(namespace.name))


def validate_apm_reference(cmd, namespace):
    apm_names = namespace.apms

    if not apm_names:
        return

    service_resource_id = get_service_resource_id(cmd, namespace)

    result = []
    for apm_name in apm_names:
        if apm_name != "":
            resource_id = '{}/apms/{}'.format(service_resource_id, apm_name)
            apm_reference = ApmReference(resource_id=resource_id)
            result.append(apm_reference)

    namespace.apms = result


def validate_apm_reference_and_enterprise_tier(cmd, namespace):
    if namespace.apms is not None and namespace.resource_group and namespace.service and not is_enterprise_tier(
            cmd, namespace.resource_group, namespace.service):
        raise ArgumentUsageError("'--apms' only supports for Enterprise tier Spring instance.")

    validate_apm_reference(cmd, namespace)


def get_service_resource_id(cmd, namespace):
    subscription = get_subscription_id(cmd.cli_ctx)
    service_resource_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}'.format(
        subscription, namespace.resource_group, namespace.service)
    return service_resource_id


def validate_cert_reference(cmd, namespace):
    cert_names = namespace.certificates

    if not cert_names:
        return

    result = []
    get_cert_resource_id(cert_names, cmd, namespace, result)

    namespace.certificates = result


def get_cert_resource_id(cert_names, cmd, namespace, result):
    service_resource_id = get_service_resource_id(cmd, namespace)
    for cert_name in cert_names:
        resource_id = '{}/certificates/{}'.format(service_resource_id, cert_name)
        cert_reference = CertificateReference(resource_id=resource_id)
        result.append(cert_reference)


def validate_build_cert_reference(cmd, namespace):
    cert_names = namespace.build_certificates
    if cert_names is not None and namespace.resource_group and namespace.service and not is_enterprise_tier(
            cmd, namespace.resource_group, namespace.service):
        raise ArgumentUsageError("'--build-certificates' only supports for Enterprise tier Spring instance.")

    if not cert_names:
        return

    result = []
    get_cert_resource_id(cert_names, cmd, namespace, result)

    namespace.build_certificates = result


def validate_create_app_binding_default_service_registry(cmd, namespace):
    if namespace.bind_service_registry:
        namespace.bind_service_registry = _get_eactly_one_service_registry_resource_id(cmd,
                                                                                       namespace.resource_group,
                                                                                       namespace.service)


def _get_eactly_one_service_registry_resource_id(cmd, resource_group, service):
    client = get_client(cmd)
    service_registry_resources = list(client.service_registries.list(resource_group, service))
    if len(service_registry_resources) == 0:
        raise ClientRequestError('App cannot bind to service registry because it is not configured.')
    if len(service_registry_resources) > 1:
        raise ClientRequestError('App cannot bind to multiple service registries.')
    return service_registry_resources[0].id


def validate_create_app_binding_default_application_configuration_service(cmd, namespace):
    if namespace.bind_application_configuration_service:
        namespace.bind_application_configuration_service \
            = _get_eactly_one_application_configuration_service_resource_id(cmd,
                                                                            namespace.resource_group,
                                                                            namespace.service)


def _get_eactly_one_application_configuration_service_resource_id(cmd, resource_group, service):
    client = get_client(cmd)
    acs_resources = list(client.configuration_services.list(resource_group, service))
    if len(acs_resources) == 0:
        raise ClientRequestError('App cannot bind to application configuration service '
                                 'because it is not configured.')
    if len(acs_resources) > 1:
        raise ClientRequestError('App cannot bind to multiple application configuration services.')
    return acs_resources[0].id
