# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-locals

import re
from subprocess import PIPE, Popen
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.cli.command_modules.acr._constants import get_managed_sku, get_premium_sku
from azure.cli.command_modules.acr._utils import validate_sku_update
from azure.cli.command_modules.acr.custom import acr_update_custom, _check_wincred
from azure.cli.command_modules.acr.network_rule import NETWORK_RULE_NOT_SUPPORTED

from .vendored_sdks.containerregistry.models import (
    NetworkRuleSet,
    Registry,
    RegistryUpdateParameters,
    Sku
)

logger = get_logger(__name__)
ACR_AFEC_REGIONAL_ENDPOINT = "RegionalEndpoint"
ACR_RESOURCE_PROVIDER = "Microsoft.ContainerRegistry"
REGIONAL_ENDPOINTS_NOT_SUPPORTED = "Regional endpoints are only supported for managed registries in Premium SKU."
REGIONAL_ENDPOINTS_NOT_SUPPORTED_FOR_DCT = "Regional endpoints cannot be enabled when Content Trust is enabled. " \
                                           "Please disable Content Trust and try again."


def acr_create_preview(cmd,
                       client,
                       registry_name,
                       resource_group_name,
                       sku,
                       location=None,
                       admin_enabled=False,
                       default_action=None,
                       workspace=None,
                       identity=None,
                       key_encryption_key=None,
                       public_network_enabled=None,
                       zone_redundancy=None,
                       allow_trusted_services=None,
                       allow_exports=None,
                       tags=None,
                       allow_metadata_search=None,
                       dnl_scope=None,
                       role_assignment_mode=None,
                       enable_regional_endpoints=None):
    from azure.cli.command_modules.acr.custom import (
        _configure_cmk, _configure_metadata_search, _configure_public_network_access,
        _configure_domain_name_label_scope, _configure_role_assignment_mode, _handle_export_policy,
        _handle_network_bypass, _create_diagnostic_settings
    )

    if default_action and sku not in get_premium_sku(cmd):
        raise CLIError(NETWORK_RULE_NOT_SUPPORTED)

    if sku not in get_managed_sku(cmd):
        raise CLIError("Classic SKU is no longer supported. Please select a managed SKU.")

    if re.match(r'\w*[A-Z]\w*', registry_name):
        raise InvalidArgumentValueError("argument error: Registry name must use only lowercase.")

    if re.match(r'\w*[-]\w*', registry_name):
        raise InvalidArgumentValueError("argument error: Registry name cannot contain dashes.")

    registry = Registry(location=location, sku=Sku(name=sku), admin_user_enabled=admin_enabled,
                        zone_redundancy=zone_redundancy, tags=tags)

    if default_action:
        registry.network_rule_set = NetworkRuleSet(default_action=default_action)

    if public_network_enabled is not None:
        _configure_public_network_access(cmd, registry, public_network_enabled)

    if identity or key_encryption_key:
        _configure_cmk(cmd, registry, resource_group_name, identity, key_encryption_key)

    if allow_metadata_search is not None:
        _configure_metadata_search(cmd, registry, allow_metadata_search)

    if dnl_scope is not None:
        _configure_domain_name_label_scope(cmd, registry, dnl_scope)

    if role_assignment_mode is not None:
        _configure_role_assignment_mode(cmd, registry, role_assignment_mode)

    if enable_regional_endpoints is not None:
        _configure_regional_endpoint(cmd, registry, sku, enable_regional_endpoints)

    _handle_network_bypass(cmd, registry, allow_trusted_services)
    _handle_export_policy(cmd, registry, allow_exports)

    lro_poller = client.begin_create(resource_group_name, registry_name, registry)

    if workspace:
        from azure.mgmt.core.tools import is_valid_resource_id, resource_id
        from azure.cli.core.commands import LongRunningOperation
        from azure.cli.core.commands.client_factory import get_subscription_id
        acr = LongRunningOperation(cmd.cli_ctx)(lro_poller)
        if not is_valid_resource_id(workspace):
            workspace = resource_id(subscription=get_subscription_id(cmd.cli_ctx),
                                    resource_group=resource_group_name,
                                    namespace='microsoft.OperationalInsights',
                                    type='workspaces',
                                    name=workspace)
        _create_diagnostic_settings(cmd.cli_ctx, acr, workspace)
        return acr

    return lro_poller


def acr_update_custom_preview(cmd,
                              instance,
                              sku=None,
                              admin_enabled=None,
                              default_action=None,
                              data_endpoint_enabled=None,
                              public_network_enabled=None,
                              allow_trusted_services=None,
                              anonymous_pull_enabled=None,
                              allow_exports=None,
                              tags=None,
                              allow_metadata_search=None,
                              role_assignment_mode=None,
                              enable_regional_endpoints=None):
    instance = acr_update_custom(
        cmd,
        instance,
        sku,
        admin_enabled,
        default_action,
        data_endpoint_enabled,
        public_network_enabled,
        allow_trusted_services,
        anonymous_pull_enabled,
        allow_exports,
        tags,
        allow_metadata_search,
        role_assignment_mode
    )

    if enable_regional_endpoints is not None:
        _configure_regional_endpoint(cmd, instance, sku, enable_regional_endpoints)

    return instance


def acr_update_get_preview():
    return RegistryUpdateParameters()


def acr_update_set_preview(cmd, client, registry_name, resource_group_name=None, parameters=None):
    registry, resource_group_name = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)

    if parameters.network_rule_set and registry.sku.name not in get_premium_sku(cmd):
        raise CLIError(NETWORK_RULE_NOT_SUPPORTED)

    if parameters.regional_endpoint_enabled:
        # Regional endpoints require Premium SKU, validate registry tier compatibility
        if registry.sku.name not in get_premium_sku(cmd):
            raise CLIError(REGIONAL_ENDPOINTS_NOT_SUPPORTED)

        # Regional endpoints are incompatible with Docker Content Trust (DCT), check for conflicts
        if registry.policies and registry.policies.trust_policy and registry.policies.trust_policy.status == 'enabled':
            raise CLIError(REGIONAL_ENDPOINTS_NOT_SUPPORTED_FOR_DCT)

        # Recommend enabling data endpoints for optimal performance when using regional endpoints
        if registry.data_endpoint_enabled is False:
            logger.warning(
                "It is recommended to also enable dedicated data endpoints "
                "(--enable-data-endpoint) for optimal in-region performance "
                "when using regional endpoints."
            )

    validate_sku_update(cmd, registry.sku.name, parameters.sku)

    return client.begin_update(resource_group_name, registry_name, parameters)


def acr_show_preview(cmd, client, registry_name, resource_group_name=None):
    from azure.cli.command_modules.acr._utils import get_resource_group_name_by_registry_name
    from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
    resource_group_name = get_resource_group_name_by_registry_name(cmd.cli_ctx, registry_name, resource_group_name)
    try:
        return client.get(resource_group_name, registry_name)
    except (ResourceNotFoundError, HttpResponseError, AttributeError):
        # fallback to vanilla client
        client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_CONTAINERREGISTRY).registries
        return client.get(resource_group_name, registry_name)


def _check_regional_endpoint_afec(cli_ctx):
    """Check if the regional endpoint AFEC is registered for the subscription.
    This check is only needed during the private preview stage.
    """
    feature_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_FEATURES).features
    feature_result = feature_client.get(
        resource_provider_namespace=ACR_RESOURCE_PROVIDER,
        feature_name=ACR_AFEC_REGIONAL_ENDPOINT,
    )
    return feature_result and feature_result.properties and feature_result.properties.state == "Registered"


def _configure_regional_endpoint(cmd, registry, sku, enable_regional_endpoints):
    if not _check_regional_endpoint_afec(cmd.cli_ctx):
        raise CLIError(
            "usage error: The --enable-regional-endpoints parameter is only applicable to"
            " subscriptions registered with feature {}".format(ACR_AFEC_REGIONAL_ENDPOINT)
        )

    if enable_regional_endpoints and sku and sku not in get_premium_sku(cmd):
        raise CLIError(REGIONAL_ENDPOINTS_NOT_SUPPORTED)

    registry.regional_endpoint_enabled = enable_regional_endpoints


def get_registry_by_name(cli_ctx, registry_name, resource_group_name=None):
    """Returns a tuple of Registry object and resource group name.
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    """
    from azure.cli.command_modules.acr._utils import get_resource_group_name_by_registry_name
    resource_group_name = get_resource_group_name_by_registry_name(
        cli_ctx, registry_name, resource_group_name)
    from azext_acrregionalendpoint._client_factory import cf_acrregionalendpoint
    client = cf_acrregionalendpoint(cli_ctx)

    return client.get(resource_group_name, registry_name), resource_group_name


def acr_login_preview(cmd,
                      registry_name,
                      resource_group_name=None,
                      tenant_suffix=None,
                      username=None,
                      password=None,
                      expose_token=False,
                      all_endpoints=False):
    if expose_token and all_endpoints:
        raise CLIError("`--expose-token` cannot be combined with `--all-endpoints`.")

    from azure.cli.command_modules.acr._docker_utils import get_login_credentials, EMPTY_GUID
    if expose_token:
        if username or password:
            raise CLIError("`--expose-token` cannot be combined with `--username` or `--password`.")

        login_server, _, password = get_login_credentials(
            cmd=cmd,
            registry_name=registry_name,
            tenant_suffix=tenant_suffix,
            username=username,
            password=password,
            resource_group_name=resource_group_name)

        logger.warning("Note: The token in both the accessToken and refreshToken fields is "
                       "an ACR Refresh Token, not an ACR Access Token. This ACR Refresh Token cannot be used "
                       "directly to authenticate with registry APIs such as pushing/pulling images and listing "
                       "repositories/tags. This ACR Refresh Token must be subsequently exchanged for an ACR Access."
                       "Please see https://aka.ms/acr/auth/oauth")

        logger.warning("You can perform manual login using the provided refresh token below, "
                       "for example: 'docker login loginServer -u %s -p refreshToken'", EMPTY_GUID)

        token_info = {
            "loginServer": login_server,
            "username": EMPTY_GUID,
            "accessToken": password,
            "refreshToken": password
        }

        return token_info

    tips = "You may want to use 'az acr login -n {} --expose-token' to get a refresh token, " \
           "which does not require Docker to be installed.".format(registry_name)

    from azure.cli.core.util import in_cloud_console
    if in_cloud_console():
        raise CLIError("This command requires running the docker daemon, "
                       "which is not supported in Azure Cloud Shell. " + tips)

    from azure.cli.command_modules.acr.custom import (get_docker_command)
    try:
        docker_command, _ = get_docker_command()
    except CLIError as e:
        logger.warning(tips)
        raise e

    login_server, username, password = get_login_credentials(
        cmd=cmd,
        registry_name=registry_name,
        tenant_suffix=tenant_suffix,
        username=username,
        password=password,
        resource_group_name=resource_group_name)

    # warn casing difference caused by ACR normalizing to lower on login_server
    parts = login_server.split('.')
    if registry_name != parts[0] and registry_name.lower() == parts[0]:
        logger.warning('Uppercase characters are detected in the registry name. When using its server url in '
                       'docker commands, to avoid authentication errors, use all lowercase.')

    if all_endpoints:
        registry, resource_group_name = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)
        if registry.regional_endpoint_enabled and registry.regional_endpoint_host_names:
            login_server_list = [login_server] + registry.regional_endpoint_host_names
            logger.warning("Regional endpoints are enabled. Logging in to %d endpoints.", len(login_server_list))
            for url in login_server_list:
                # Multiple endpoints, show detailed logging for each
                logger.warning("Logging in to %s", url)
                _perform_registry_login(url, docker_command, username, password)
    else:
        _perform_registry_login(login_server, docker_command, username, password)

    return None


def _perform_registry_login(login_server, docker_command, username, password):
    logger.debug("Invoking '%s login --username %s --password <redacted> %s'",
                 docker_command, username, login_server)
    p = Popen([docker_command, "login",
               "--username", username,
               "--password", password,
               login_server], stderr=PIPE)
    _, stderr = p.communicate()
    return_code = p.returncode

    if stderr or return_code != 0:  # when docker command process returns non-zero
        if b'error storing credentials' in stderr and b'stub received bad data' in stderr \
           and _check_wincred(login_server):
            # Retry once after disabling wincred
            p = Popen([docker_command, "login",
                       "--username", username,
                       "--password", password,
                       login_server])
            p.wait()
        else:
            stderr_messages = stderr.decode()
            # Dismiss the '--password-stdin' warning
            if b'--password-stdin' in stderr:
                errors = [err for err in stderr_messages.split('\n') if err and '--password-stdin' not in err]
                # Will not raise CLIError if there is no error other than '--password-stdin'
                if not errors:
                    return None
                stderr_messages = '\n'.join(errors)
            logger.warning(stderr_messages)

            # Raise error only if docker returns non-zero
            if return_code != 0:
                raise CLIError('Login failed.')

    return None


def acr_show_endpoints_preview(cmd,
                               registry_name,
                               resource_group_name=None):
    registry, resource_group_name = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)
    info = {
        'loginServer': registry.login_server,
        'dataEndpoints': []
    }

    if registry.data_endpoint_enabled:
        for host in registry.data_endpoint_host_names:
            info['dataEndpoints'].append({
                'region': host.split('.')[1],
                'endpoint': host,
            })
    else:
        logger.warning('To configure client firewall w/o using wildcard storage blob urls, '
                       'use "az acr update --name %s --data-endpoint-enabled" to enable dedicated '
                       'data endpoints.', registry_name)
        from azure.cli.command_modules.acr._client_factory import cf_acr_replications
        replicate_client = cf_acr_replications(cmd.cli_ctx)
        replicates = list(replicate_client.list(resource_group_name, registry_name))
        for r in replicates:
            info['dataEndpoints'].append({
                'region': r.location,
                'endpoint': '*.blob.' + cmd.cli_ctx.cloud.suffixes.storage_endpoint,
            })
        if not replicates:
            info['dataEndpoints'].append({
                'region': registry.location,
                'endpoint': '*.blob.' + cmd.cli_ctx.cloud.suffixes.storage_endpoint,
            })

    if registry.regional_endpoint_enabled:
        info['regionalEndpoints'] = []
        for host in registry.regional_endpoint_host_names:
            info['regionalEndpoints'].append({
                'region': host.split('.')[1],
                'endpoint': host,
            })

    return info
