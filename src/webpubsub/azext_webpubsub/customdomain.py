# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.azure_mgmt_webpubsub.models import (
    CustomDomain,
    ResourceReference
)

from .vendored_sdks.azure_mgmt_webpubsub.operations import (
    WebPubSubCustomDomainsOperations,
)


def custom_domain_list(client: WebPubSubCustomDomainsOperations, resource_group_name, webpubsub_name):
    return client.list(resource_group_name, webpubsub_name)


def custom_domain_show(client: WebPubSubCustomDomainsOperations, resource_group_name, webpubsub_name, name):
    return client.get(resource_group_name, webpubsub_name, name)


def custom_domain_get(client: WebPubSubCustomDomainsOperations, resource_group_name, webpubsub_name, name):
    return client.get(resource_group_name, webpubsub_name, name)


def custom_domain_create(client: WebPubSubCustomDomainsOperations, resource_group_name, webpubsub_name, name, domain_name, certificate_resource_id):
    resource_reference = ResourceReference(id=certificate_resource_id)
    custom_domain = CustomDomain(domain_name=domain_name, custom_certificate=resource_reference)

    return client.begin_create_or_update(resource_group_name, webpubsub_name, name, custom_domain)


def custom_domain_delete(client: WebPubSubCustomDomainsOperations, resource_group_name, webpubsub_name, name):
    return client.begin_delete(resource_group_name, webpubsub_name, name)
