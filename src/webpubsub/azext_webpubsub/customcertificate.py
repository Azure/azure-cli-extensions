# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.azure_mgmt_webpubsub.models import (
    CustomCertificate,
)

from .vendored_sdks.azure_mgmt_webpubsub.operations import (
    WebPubSubCustomCertificatesOperations,
)


def custom_certificate_list(client: WebPubSubCustomCertificatesOperations, resource_group_name, webpubsub_name):
    return client.list(resource_group_name, webpubsub_name)


def custom_certificate_show(client: WebPubSubCustomCertificatesOperations, resource_group_name, webpubsub_name, certificate_name):
    return client.get(resource_group_name, webpubsub_name, certificate_name)


def custom_certificate_get(client: WebPubSubCustomCertificatesOperations, resource_group_name, webpubsub_name, certificate_name):
    return client.get(resource_group_name, webpubsub_name, certificate_name)


def custom_certificate_create(client: WebPubSubCustomCertificatesOperations, resource_group_name, webpubsub_name, certificate_name, key_vault_base_uri, key_vault_secret_name, key_vault_secret_version=None):
    parameters = CustomCertificate(key_vault_base_uri=key_vault_base_uri,
                                   key_vault_secret_name=key_vault_secret_name,
                                   key_vault_secret_version=key_vault_secret_version)
    return client.begin_create_or_update(resource_group_name, webpubsub_name, certificate_name, parameters)


def custom_certificate_delete(client: WebPubSubCustomCertificatesOperations, resource_group_name, webpubsub_name, certificate_name):
    return client.delete(resource_group_name, webpubsub_name, certificate_name)
