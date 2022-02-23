# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import sdk_no_wait
from knack.log import get_logger

from .custom import LOG_RUNNING_PROMPT
from .vendored_sdks.appplatform.v2022_01_01_preview import models

logger = get_logger(__name__)
DEFAULT_NAME = "default"


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
                   allowed_origins=None,
                   allowed_methods=None,
                   allowed_headers=None,
                   max_age=None,
                   allow_credentials=None,
                   exposed_headers=None,
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
        gateway.properties.cors_properties, allowed_origins, allowed_methods, allowed_headers, max_age, allow_credentials, exposed_headers)

    resource_requests = models.GatewayResourceRequests(
        cpu=cpu or gateway.properties.resource_requests.cpu,
        memory=memory or gateway.properties.resource_requests.memory
    )

    properties = models.GatewayProperties(
        public=assign_endpoint if assign_endpoint is not None else gateway.properties.public,
        https_only=https_only if https_only is not None else gateway.properties.https_only,
        sso_properties=sso_properties,
        api_metadata_properties=api_metadata_properties,
        cors_properties=cors_properties,
        resource_requests=resource_requests)

    sku = models.Sku(name=gateway.sku.name, tier=gateway.sku.tier,
                     capacity=instance_count or gateway.sku.capacity)

    gateway_resource = models.GatewayResource(properties=properties, sku=sku)

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
    _validate_route_config_exist(client, resource_group, service, name)

    app_resource_id = _update_app_resource_id(client, resource_group, service, app_name, None)
    routes = _update_routes(routes_file, routes_json, [])

    return _create_or_update_gateway_route_configs(client, resource_group, service, name, app_resource_id, routes)


def gateway_route_config_update(cmd, client, resource_group, service, name,
                                app_name=None,
                                routes_json=None,
                                routes_file=None):
    gateway_route_config = client.gateway_route_configs.get(
        resource_group, service, DEFAULT_NAME, name)

    app_resource_id = _update_app_resource_id(client, resource_group, service, app_name, gateway_route_config.properties.app_resource_id)
    routes = _update_routes(routes_file, routes_json, gateway_route_config.properties.routes)

    return _create_or_update_gateway_route_configs(client, resource_group, service, name, app_resource_id, routes)


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


def _update_cors(existing, allowed_origins, allowed_methods, allowed_headers, max_age, allow_credentials, exposed_headers):
    if allowed_origins is None and allowed_methods is None and allowed_headers is None and max_age is None and allow_credentials is None and exposed_headers is None:
        return existing
    cors = existing if existing is not None else models.GatewayCorsProperties()
    if allowed_origins is not None:
        cors.allowed_origins = allowed_origins.split(",") if allowed_origins else None
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


def _validate_route_config_exist(client, resource_group, service, name):
    route_configs = client.gateway_route_configs.list(
        resource_group, service, DEFAULT_NAME)
    if name in (route_config.name for route_config in list(route_configs)):
        raise InvalidArgumentValueError("Route config " + name + " already exists")


def _update_app_resource_id(client, resource_group, service, app_name, app_resource_id):
    if app_name is not None:
        app_resource = client.apps.get(resource_group, service, app_name)
        app_resource_id = app_resource.id
    return app_resource_id


def _update_routes(routes_file, routes_json, routes):
    if routes_file is not None:
        with open(routes_file, 'r') as json_file:
            routes = json.load(json_file)

    if routes_json is not None:
        routes = json.loads(routes_json)
    return routes


def _create_or_update_gateway_route_configs(client, resource_group, service, name, app_resource_id, routes):
    properties = models.GatewayRouteConfigProperties(
        app_resource_id=app_resource_id, routes=routes)
    route_config_resource = models.GatewayRouteConfigResource(
        properties=properties)
    return client.gateway_route_configs.begin_create_or_update(resource_group, service, DEFAULT_NAME, name, route_config_resource)
