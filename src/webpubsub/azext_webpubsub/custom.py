# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_webpubsub.vendored_sdks.azure_mgmt_webpubsub.models._models_py3 import WebPubSubSocketIOSettings
from .vendored_sdks.azure_mgmt_webpubsub.models import (
    ResourceSku,
    WebPubSubResource
)

from .vendored_sdks.azure_mgmt_webpubsub.operations import (
    UsagesOperations,
    WebPubSubOperations
)


def webpubsub_create(client: WebPubSubOperations, resource_group_name, webpubsub_name, sku,
                     unit_count=1, location=None, tags=None, kind=None, service_mode=None):
    socketio = None
    if kind is not None and kind.casefold() == "socketio".casefold():
        socketio = WebPubSubSocketIOSettings(service_mode=service_mode)
    sku = ResourceSku(name=sku, capacity=unit_count)
    parameter = WebPubSubResource(
        sku=sku,
        location=location,
        tags=tags,
        kind=kind,
        socket_io=socketio
    )

    return client.begin_create_or_update(resource_group_name, webpubsub_name, parameter)


def webpubsub_list(client, resource_group_name=None):
    if not resource_group_name:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name)


def webpubsub_delete(client, webpubsub_name, resource_group_name):
    return client.begin_delete(resource_group_name, webpubsub_name)


def webpubsub_show(client, webpubsub_name, resource_group_name):
    return client.get(resource_group_name, webpubsub_name)


def webpubsub_restart(client, webpubsub_name, resource_group_name):
    return client.begin_restart(resource_group_name, webpubsub_name)


def webpubsub_get(client, webpubsub_name, resource_group_name):
    return client.get(resource_group_name, webpubsub_name)


def webpubsub_set(client, webpubsub_name, resource_group_name, parameters):
    return client.begin_update(resource_group_name, webpubsub_name, parameters)


def update_webpubsub(instance, tags=None, sku=None, unit_count=None, service_mode=None):
    if service_mode is not None and instance.kind is not None and instance.kind.casefold() == "socketio".casefold():
        instance.socket_io = WebPubSubSocketIOSettings(service_mode=service_mode)
    sku = sku if sku else instance.sku.name
    unit_count = unit_count if unit_count else instance.sku.capacity
    instance.sku = ResourceSku(name=sku, capacity=unit_count)

    if tags is not None:
        instance.tags = tags

    return instance


def webpubsub_usage(client: UsagesOperations, location):
    return client.list(location)


def webpubsub_skus(client: WebPubSubOperations, resource_group_name, webpubsub_name):
    return client.list_skus(resource_group_name, webpubsub_name).value
