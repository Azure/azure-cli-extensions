# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=inconsistent-return-statements

from azext_relay._utils import accessrights_converter

from azext_relay.relay.models import (RelayNamespace, Sku, WcfRelay)


# Namespace Region
def cli_namespace_create(client, resource_group_name, namespace_name, location, tags=None, skutier=None):
    return client.create_or_update(resource_group_name, namespace_name, RelayNamespace(location, tags, Sku(skutier)))


def cli_namespace_list(client, resource_group_name=None):

    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)

    if not resource_group_name:
        return client.list()


# Namespace Authorization rule:
def cli_namespaceautho_create(client, resource_group_name, namespace_name, name, accessrights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, name,
                                                      accessrights_converter(accessrights))


# WcfRelay Region
def cli_wcfrelay_create(client, resource_group_name, namespace_name, name, relay_type=None, requires_client_authorization=None, requires_transport_security=None, user_metadata=None):
    wcfrelayparameter1 = WcfRelay()
    if relay_type:
        wcfrelayparameter1.relay_type = relay_type

    if requires_client_authorization:
        wcfrelayparameter1.requires_client_authorization = requires_client_authorization

    if requires_transport_security:
        wcfrelayparameter1.requires_transport_security = requires_transport_security

    if user_metadata:
        wcfrelayparameter1.user_metadata = user_metadata

    return client.create_or_update(resource_group_name, namespace_name, name, wcfrelayparameter1)


def cli_wcfrelayautho_create(client, resource_group_name, namespace_name, wcfrelay_name, name, access_rights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, wcfrelay_name, name,
                                                      accessrights_converter(access_rights))


def cli_hybridconnectionsautho_create(client, resource_group_name, namespace_name, hybrid_connection_name, name, access_rights=None):
    return client.create_or_update_authorization_rule(resource_group_name, namespace_name, hybrid_connection_name, name,
                                                      accessrights_converter(access_rights))


# pylint: disable=inconsistent-return-statements
def empty_on_404(ex):
    from azext_relay.relay.models import ErrorResponseException
    if isinstance(ex, ErrorResponseException) and ex.response.status_code == 404:
        return None
    raise ex
