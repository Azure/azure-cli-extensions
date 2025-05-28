# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger

from .custom import LOG_RUNNING_PROMPT
from .vendored_sdks.appplatform.v2024_05_01_preview import models
from ._gateway_constant import (GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE, GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE,
                                GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE, GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE)
from ._utils import get_spring_sku

logger = get_logger(__name__)
DEFAULT_NAME = "default"


def gateway_create(cmd, client, service, resource_group, instance_count=None):
    sku = get_spring_sku(client, resource_group, service)
    gateway_resource = models.GatewayResource()
    if instance_count and sku:
        gateway_resource.sku = models.Sku(name=sku.name, tier=sku.tier, capacity=instance_count)
    return client.gateways.begin_create_or_update(resource_group, service, DEFAULT_NAME, gateway_resource)


def gateway_delete(cmd, client, service, resource_group):
    return client.gateways.begin_delete(resource_group, service, DEFAULT_NAME)


def gateway_update(cmd, client, resource_group, service,
                   cpu=None,
                   memory=None,
                   instance_count=None,
                   assign_endpoint=None,
                   https_only=None,
                   scope=None,
                   client_id=None,
                   client_secret=None,
                   issuer_uri=None,
                   api_title=None,
                   api_description=None,
                   api_doc_location=None,
                   api_version=None,
                   server_url=None,
                   apm_types=None,
                   properties=None,
                   secrets=None,
                   allowed_origins=None,
                   allowed_origin_patterns=None,
                   allowed_methods=None,
                   allowed_headers=None,
                   max_age=None,
                   allow_credentials=None,
                   exposed_headers=None,
                   enable_certificate_verification=None,
                   certificate_names=None,
                   addon_configs_json=None,
                   addon_configs_file=None,
                   apms=None,
                   enable_response_cache=None,
                   response_cache_scope=None,
                   response_cache_size=None,
                   response_cache_ttl=None,
                   no_wait=False
                   ):
    gateway = client.gateways.get(resource_group, service, DEFAULT_NAME)

    sso_properties = gateway.properties.sso_properties
    if scope is not None and client_id is not None and client_secret is not None and issuer_uri is not None:
        if not client_id and not client_secret and not issuer_uri:
            # clear SSO properties
            sso_properties = None
        else:
            sso_properties = models.SsoProperties(
                scope=scope,
                client_id=client_id,
                client_secret=client_secret,
                issuer_uri=issuer_uri,
            )

    api_metadata_properties = _update_api_metadata(
        gateway.properties.api_metadata_properties, api_title, api_description, api_doc_location, api_version, server_url)

    cors_properties = _update_cors(
        gateway.properties.cors_properties, allowed_origins, allowed_origin_patterns, allowed_methods, allowed_headers, max_age, allow_credentials, exposed_headers)

    client_auth = _update_client_auth(client, resource_group, service,
                                      gateway.properties.client_auth, enable_certificate_verification, certificate_names)

    resource_requests = models.GatewayResourceRequests(
        cpu=cpu or gateway.properties.resource_requests.cpu,
        memory=memory or gateway.properties.resource_requests.memory
    )

    update_apm_types = apm_types if apm_types is not None else gateway.properties.apm_types
    environment_variables = _update_envs(gateway.properties.environment_variables, properties, secrets)

    addon_configs = _update_addon_configs(gateway.properties.addon_configs, addon_configs_json, addon_configs_file)

    apms = _update_apms(client, resource_group, service, gateway.properties.apms, apms)

    response_cache = _update_response_cache(client,
                                            resource_group,
                                            service,
                                            gateway.properties.response_cache_properties,
                                            enable_response_cache,
                                            response_cache_scope,
                                            response_cache_size,
                                            response_cache_ttl)

    model_properties = models.GatewayProperties(
        public=assign_endpoint if assign_endpoint is not None else gateway.properties.public,
        https_only=https_only if https_only is not None else gateway.properties.https_only,
        sso_properties=sso_properties,
        api_metadata_properties=api_metadata_properties,
        cors_properties=cors_properties,
        apm_types=update_apm_types,
        apms=apms,
        environment_variables=environment_variables,
        client_auth=client_auth,
        addon_configs=addon_configs,
        resource_requests=resource_requests,
        response_cache_properties=response_cache)

    sku = models.Sku(name=gateway.sku.name, tier=gateway.sku.tier,
                     capacity=instance_count or gateway.sku.capacity)

    gateway_resource = models.GatewayResource(properties=model_properties, sku=sku)

    logger.warning(LOG_RUNNING_PROMPT)
    return sdk_no_wait(no_wait, client.gateways.begin_create_or_update,
                       resource_group, service, DEFAULT_NAME, gateway_resource)


def gateway_show(cmd, client, resource_group, service):
    return client.gateways.get(resource_group, service, DEFAULT_NAME)


def gateway_clear(cmd, client, resource_group, service, no_wait=False):
    gateway = client.gateways.get(resource_group, service, DEFAULT_NAME)
    properties = models.GatewayProperties()
    sku = models.Sku(name=gateway.sku.name, tier=gateway.sku.tier)
    gateway_resource = models.GatewayResource(properties=properties, sku=sku)

    logger.warning(LOG_RUNNING_PROMPT)
    return sdk_no_wait(no_wait, client.gateways.begin_create_or_update,
                       resource_group, service, DEFAULT_NAME, gateway_resource)


def gateway_restart(cmd, client, service, resource_group, no_wait=False):
    return client.gateways.begin_restart(resource_group, service, DEFAULT_NAME)


def gateway_sync_cert(cmd, client, service, resource_group, no_wait=False):
    return client.gateways.begin_restart(resource_group, service, DEFAULT_NAME)


def gateway_custom_domain_show(cmd, client, resource_group, service, domain_name):
    return client.gateway_custom_domains.get(resource_group, service, DEFAULT_NAME, domain_name)


def gateway_custom_domain_list(cmd, client, resource_group, service):
    return client.gateway_custom_domains.list(resource_group, service, DEFAULT_NAME)


def gateway_custom_domain_update(cmd, client, resource_group, service,
                                 domain_name,
                                 certificate=None):
    properties = models.GatewayCustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(
            resource_group, service, certificate)
        properties.thumbprint = certificate_response.properties.thumbprint

    custom_domain_resource = models.GatewayCustomDomainResource(
        properties=properties)
    return client.gateway_custom_domains.begin_create_or_update(resource_group, service, DEFAULT_NAME,
                                                                domain_name, custom_domain_resource)


def gateway_custom_domain_unbind(cmd, client, resource_group, service, domain_name):
    client.gateway_custom_domains.get(resource_group, service,
                                      DEFAULT_NAME, domain_name)
    return client.gateway_custom_domains.begin_delete(resource_group, service, DEFAULT_NAME, domain_name)


def gateway_route_config_show(cmd, client, resource_group, service, name):
    return client.gateway_route_configs.get(resource_group, service, DEFAULT_NAME, name)


def gateway_route_config_list(cmd, client, resource_group, service):
    return client.gateway_route_configs.list(resource_group, service, DEFAULT_NAME)


def gateway_route_config_create(cmd, client, resource_group, service, name,
                                app_name=None,
                                routes_json=None,
                                routes_file=None):
    _validate_route_config_not_exist(client, resource_group, service, name)
    route_properties = models.GatewayRouteConfigProperties()
    return _create_or_update_gateway_route_configs(client, resource_group, service, name, route_properties,
                                                   app_name, routes_file, routes_json)


def gateway_route_config_update(cmd, client, resource_group, service, name,
                                app_name=None,
                                routes_json=None,
                                routes_file=None):
    _validate_route_config_exist(client, resource_group, service, name)
    route_properties = client.gateway_route_configs.get(
        resource_group, service, DEFAULT_NAME, name).properties
    return _create_or_update_gateway_route_configs(client, resource_group, service, name, route_properties,
                                                   app_name, routes_file, routes_json)


def gateway_route_config_remove(cmd, client, resource_group, service, name):
    return client.gateway_route_configs.begin_delete(resource_group, service, DEFAULT_NAME, name)


def _update_api_metadata(existing, api_title, api_description, api_documentation_location, version, server_url):
    if api_title is None and api_description is None and api_documentation_location is None and version is None and server_url is None:
        return existing
    api_metadata = models.GatewayApiMetadataProperties() if existing is None else existing
    if api_title is not None:
        api_metadata.title = api_title
    if api_description is not None:
        api_metadata.description = api_description
    if api_documentation_location is not None:
        api_metadata.documentation = api_documentation_location
    if version is not None:
        api_metadata.version = version
    if server_url is not None:
        api_metadata.server_url = server_url
    return api_metadata


def _update_cors(existing, allowed_origins, allowed_origin_patterns, allowed_methods, allowed_headers, max_age, allow_credentials, exposed_headers):
    if allowed_origins is None and allowed_origin_patterns is None and allowed_methods is None and allowed_headers is None and max_age is None and allow_credentials is None and exposed_headers is None:
        return existing
    cors = existing if existing is not None else models.GatewayCorsProperties()
    if allowed_origins is not None:
        cors.allowed_origins = allowed_origins.split(",") if allowed_origins else None
    if allowed_origin_patterns is not None:
        cors.allowed_origin_patterns = allowed_origin_patterns.split(",") if allowed_origin_patterns else None
    if allowed_methods is not None:
        cors.allowed_methods = allowed_methods.split(",") if allowed_methods else None
    if allowed_headers is not None:
        cors.allowed_headers = allowed_headers.split(",") if allowed_headers else None
    if max_age:
        cors.max_age = max_age
    if allow_credentials is not None:
        cors.allow_credentials = allow_credentials
    if exposed_headers is not None:
        cors.exposed_headers = exposed_headers.split(",") if exposed_headers else None
    return cors


def _update_envs(existing, envs_dict, secrets_dict):
    if envs_dict is None and secrets_dict is None:
        return existing
    envs = existing if existing is not None else models.GatewayPropertiesEnvironmentVariables()
    if envs_dict is not None:
        envs.properties = envs_dict
    if secrets_dict is not None:
        envs.secrets = secrets_dict
    return envs


def _update_client_auth(client, resource_group, service, existing, enable_certificate_verification, certificate_names):
    if enable_certificate_verification is None and certificate_names is None:
        return existing
    client_auth = existing if existing is not None else models.GatewayPropertiesClientAuth()
    if enable_certificate_verification is not None:
        client_auth.certificate_verification = models.GatewayCertificateVerification.ENABLED if enable_certificate_verification else models.GatewayCertificateVerification.DISABLED
    if certificate_names is not None:
        client_auth.certificates = []
        if certificate_names == "":
            # Clear certificates
            return client_auth
        certs_in_asa = client.certificates.list(resource_group, service)
        certs_array = certificate_names.split(",")
        for name in certs_array:
            cert_in_asa = next((c for c in certs_in_asa if c.name == name), None)
            if cert_in_asa:
                client_auth.certificates.append(cert_in_asa.id)
            else:
                raise InvalidArgumentValueError(f"Certificate {name} not found in Azure Spring Apps.")
    return client_auth


def _update_apms(client, resource_group, service, existing, apms):
    if apms is None:
        return existing
    return apms


def _update_addon_configs(existing, addon_configs_json, addon_configs_file):
    if addon_configs_file is None and addon_configs_json is None:
        return existing

    raw_json = {}
    if addon_configs_file is not None:
        with open(addon_configs_file, 'r') as json_file:
            raw_json = json.load(json_file)

    if addon_configs_json is not None:
        raw_json = json.loads(addon_configs_json)

    return raw_json


def _validate_route_config_not_exist(client, resource_group, service, name):
    route_configs = client.gateway_route_configs.list(
        resource_group, service, DEFAULT_NAME)
    if name in (route_config.name for route_config in list(route_configs)):
        raise InvalidArgumentValueError("Route config " + name + " already exists")


def _validate_route_config_exist(client, resource_group, service, name):
    route_configs = client.gateway_route_configs.list(
        resource_group, service, DEFAULT_NAME)
    if name not in (route_config.name for route_config in list(route_configs)):
        raise InvalidArgumentValueError("Route config " + name + " doesn't exist")


def _create_or_update_gateway_route_configs(client, resource_group, service, name, route_properties,
                                            app_name, routes_file, routes_json):
    app_resource_id = _get_app_resource_id_by_name(client, resource_group, service, app_name)
    route_properties = _create_or_update_routes_properties(routes_file, routes_json, route_properties)

    if app_resource_id is not None:
        route_properties.app_resource_id = app_resource_id
    route_config_resource = models.GatewayRouteConfigResource(
        properties=route_properties)
    return client.gateway_route_configs.begin_create_or_update(resource_group, service, DEFAULT_NAME, name, route_config_resource)


def _get_app_resource_id_by_name(client, resource_group, service, app_name):
    if app_name is not None:
        app_resource = client.apps.get(resource_group, service, app_name)
        return app_resource.id
    return None


def _create_or_update_routes_properties(routes_file, routes_json, route_properties):
    if routes_file is None and routes_json is None:
        return route_properties

    route_properties = models.GatewayRouteConfigProperties()
    if routes_file is not None:
        with open(routes_file, 'r') as json_file:
            raw_json = json.load(json_file)

    if routes_json is not None:
        raw_json = json.loads(routes_json)

    if isinstance(raw_json, list):
        route_properties.routes = raw_json
    else:
        raw_json = _route_config_property_convert(raw_json)
        route_properties = models.GatewayRouteConfigProperties(**raw_json)
    return route_properties


# Convert camelCase to snake_case to align with backend
def _route_config_property_convert(raw_json):
    if raw_json is None:
        return raw_json

    convert_raw_json = {}
    for key in raw_json:
        if key == "routes":
            convert_raw_json[key] = list(map(lambda v: _route_config_property_convert(v), raw_json[key]))
        else:
            replaced_key = re.sub('(?<!^)(?=[A-Z])', '_', key).lower()
            convert_raw_json[replaced_key] = raw_json[key]
    return convert_raw_json


def _update_response_cache(client, resource_group, service, existing_response_cache=None,
                           enable_response_cache=None,
                           response_cache_scope=None,
                           response_cache_size=None,
                           response_cache_ttl=None):
    if existing_response_cache is None and not enable_response_cache:
        if response_cache_scope is not None or response_cache_size is not None or response_cache_ttl is not None:
            raise InvalidArgumentValueError("Response cache is not enabled. "
                                            "Please use --enable-response-cache together to configure it.")

    if existing_response_cache is None and enable_response_cache:
        if response_cache_scope is None:
            raise InvalidArgumentValueError("--response-cache-scope is required when enable response cache.")

    # enable_response_cache can be None, which can still mean to enable response cache
    if enable_response_cache is False:
        return None

    target_cache_scope = _get_target_cache_scope(response_cache_scope, existing_response_cache)
    target_cache_size = _get_target_cache_size(response_cache_size, existing_response_cache)
    target_cache_ttl = _get_target_cache_ttl(response_cache_ttl, existing_response_cache)

    if target_cache_scope is None:
        if target_cache_size is None and target_cache_ttl is None:
            return None
        else:
            raise InvalidArgumentValueError("--response-cache-scope is required when enable response cache.")

    if target_cache_scope == GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE:
        return models.GatewayLocalResponseCachePerRouteProperties(
            size=target_cache_size, time_to_live=target_cache_ttl)
    else:
        return models.GatewayLocalResponseCachePerInstanceProperties(
            size=target_cache_size, time_to_live=target_cache_ttl)


def _get_target_cache_scope(response_cache_scope, existing_response_cache):
    if response_cache_scope is not None:
        return response_cache_scope

    if existing_response_cache is None:
        return None

    if isinstance(existing_response_cache, models.GatewayLocalResponseCachePerRouteProperties):
        return GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE

    if isinstance(existing_response_cache, models.GatewayLocalResponseCachePerInstanceProperties):
        return GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE


def _get_target_cache_size(size, existing_response_cache):
    if size is not None:
        if size == GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE:
            return None
        else:
            return size

    if existing_response_cache is None or existing_response_cache.size is None:
        return None
    else:
        return existing_response_cache.size


def _get_target_cache_ttl(ttl, existing_response_cache):
    if ttl is not None:
        if ttl == GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE:
            return None
        else:
            return ttl

    if existing_response_cache is None or existing_response_cache.time_to_live is None:
        return None
    else:
        return existing_response_cache.time_to_live
