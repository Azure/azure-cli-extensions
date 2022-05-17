# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ClientRequestError

from .vendored_sdks.appplatform.v2022_01_01_preview import models

DEFAULT_NAME = "default"


def api_portal_show(cmd, client, resource_group, service):
    return client.api_portals.get(resource_group, service, DEFAULT_NAME)


def api_portal_update(cmd, client, resource_group, service,
                      instance_count=None,
                      assign_endpoint=None,
                      https_only=None,
                      scope=None,
                      client_id=None,
                      client_secret=None,
                      issuer_uri=None):
    api_portal = client.api_portals.get(resource_group, service, DEFAULT_NAME)

    sso_properties = api_portal.properties.sso_properties
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

    properties = models.ApiPortalProperties(
        public=assign_endpoint if assign_endpoint is not None else api_portal.properties.public,
        https_only=https_only if https_only is not None else api_portal.properties.https_only,
        gateway_ids=api_portal.properties.gateway_ids,
        sso_properties=sso_properties
    )

    sku = models.Sku(name=api_portal.sku.name, tier=api_portal.sku.tier,
                     capacity=instance_count or api_portal.sku.capacity)

    if sku.capacity > 1 and properties.sso_properties:
        raise ClientRequestError("API Portal doesn't support to configure SSO with multiple replicas for now.")

    api_portal_resource = models.ApiPortalResource(
        properties=properties, sku=sku)
    return client.api_portals.begin_create_or_update(resource_group, service, DEFAULT_NAME, api_portal_resource)


def api_portal_clear(cmd, client, resource_group, service):
    api_portal = client.api_portals.get(resource_group, service, DEFAULT_NAME)
    properties = models.ApiPortalProperties(
        gateway_ids=api_portal.properties.gateway_ids
    )

    sku = models.Sku(name=api_portal.sku.name, tier=api_portal.sku.tier)
    api_portal_resource = models.ApiPortalResource(properties=properties, sku=sku)
    return client.api_portals.begin_create_or_update(resource_group, service, DEFAULT_NAME, api_portal_resource)


def api_portal_custom_domain_show(cmd, client, resource_group, service, domain_name):
    return client.api_portal_custom_domains.get(resource_group, service, DEFAULT_NAME, domain_name)


def api_portal_custom_domain_list(cmd, client, resource_group, service):
    return client.api_portal_custom_domains.list(resource_group, service, DEFAULT_NAME)


def api_portal_custom_domain_update(cmd, client, resource_group, service,
                                    domain_name,
                                    certificate=None):
    properties = models.ApiPortalCustomDomainProperties()
    if certificate is not None:
        certificate_response = client.certificates.get(
            resource_group, service, certificate)
        properties = models.ApiPortalCustomDomainProperties(
            thumbprint=certificate_response.properties.thumbprint
        )

    custom_domain_resource = models.ApiPortalCustomDomainResource(
        properties=properties)
    return client.api_portal_custom_domains.begin_create_or_update(resource_group, service, DEFAULT_NAME,
                                                                   domain_name, custom_domain_resource)


def api_portal_custom_domain_unbind(cmd, client, resource_group, service, domain_name):
    client.api_portal_custom_domains.get(resource_group, service,
                                         DEFAULT_NAME, domain_name)
    return client.api_portal_custom_domains.begin_delete(resource_group, service, DEFAULT_NAME, domain_name)
