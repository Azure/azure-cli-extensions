# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.azure_messaging_webpubsubservice import (
    WebPubSubServiceClient
)


def broadcast(client, resource_group_name, webpubsub_name, hub_name, payload):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.send_to_all(message=payload, content_type='text/plain')


def check_connection_exists(client, resource_group_name, webpubsub_name, hub_name, connection_id):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    return service_client.connection_exists(connection_id)


def close_connection(client, resource_group_name, webpubsub_name, hub_name, connection_id):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.close_connection(connection_id)


def send_connection(client, resource_group_name, webpubsub_name, hub_name, connection_id, payload):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.send_to_connection(connection_id, message=payload, content_type='text/plain')


def add_connection_to_group(client, resource_group_name, webpubsub_name, hub_name, connection_id, group_name):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.add_connection_to_group(group_name, connection_id)


def remove_connection_from_group(client, resource_group_name, webpubsub_name, hub_name, connection_id, group_name):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.remove_connection_from_group(group_name, connection_id)


def send_group(client, resource_group_name, webpubsub_name, hub_name, group_name, payload):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.send_to_group(group_name, payload, content_type='text/plain')


def check_user_exists(client, resource_group_name, webpubsub_name, hub_name, user_id):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    return service_client.user_exists(user_id)


def send_user(client, resource_group_name, webpubsub_name, hub_name, user_id, payload):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.send_to_user(user_id, payload, content_type='text/plain')


def add_user_to_group(client, resource_group_name, webpubsub_name, hub_name, user_id, group_name):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.add_user_to_group(group_name, user_id)


def remove_user_from_group(client, resource_group_name, webpubsub_name, hub_name, user_id, group_name=None):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    if group_name:
        service_client.remove_user_from_group(group_name, user_id)
    else:
        service_client.remove_user_from_all_groups(user_id)


def grant_permission(client, resource_group_name, webpubsub_name, hub_name, connection_id, permission, group_name):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.grant_permission(permission, connection_id, target_name=group_name)


def revoke_permission(client, resource_group_name, webpubsub_name, hub_name, connection_id, permission, group_name):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    service_client.revoke_permission(permission, connection_id, target_name=group_name)


def check_permission(client, resource_group_name, webpubsub_name, hub_name, connection_id, permission, group_name):
    service_client = _get_service_client(client, resource_group_name, webpubsub_name, hub_name)
    return service_client.has_permission(permission, connection_id, target_name=group_name)


def _get_service_client(client, resource_group_name, webpubsub_name, hub) -> WebPubSubServiceClient:
    keys = client.list_keys(resource_group_name, webpubsub_name)
    return WebPubSubServiceClient.from_connection_string(keys.primary_connection_string, hub)
