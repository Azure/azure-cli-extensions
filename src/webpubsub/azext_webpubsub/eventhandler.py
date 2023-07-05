# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.azure_mgmt_webpubsub.models import (
    WebPubSubHubProperties,
    WebPubSubHub,
)
from .vendored_sdks.azure_mgmt_webpubsub.operations import (
    WebPubSubHubsOperations
)


def hub_create(client: WebPubSubHubsOperations, resource_group_name, webpubsub_name, hub_name, event_handler=None, allow_anonymous=False):
    anonymous_connect_policy = 'allow' if allow_anonymous else 'deny'
    properties = WebPubSubHubProperties(anonymous_connect_policy=anonymous_connect_policy, event_handlers=event_handler)
    parameters = WebPubSubHub(properties=properties)
    return client.begin_create_or_update(hub_name, resource_group_name, webpubsub_name, parameters)


def hub_delete(client: WebPubSubHubsOperations, resource_group_name, webpubsub_name, hub_name):
    return client.begin_delete(hub_name, resource_group_name, webpubsub_name)


def hub_show(client: WebPubSubHubsOperations, resource_group_name, webpubsub_name, hub_name):
    return client.get(hub_name, resource_group_name, webpubsub_name)


def hub_list(client: WebPubSubHubsOperations, resource_group_name, webpubsub_name):
    return client.list(resource_group_name, webpubsub_name)


def get_hub(client: WebPubSubHubsOperations, resource_group_name, webpubsub_name, hub_name):
    return client.get(hub_name, resource_group_name, webpubsub_name)


def set_hub(client: WebPubSubHubsOperations, resource_group_name, webpubsub_name, hub_name, parameters):
    return client.begin_create_or_update(hub_name, resource_group_name, webpubsub_name, parameters)


def update(instance: WebPubSubHub, event_handler=None, allow_anonymous=None):
    if allow_anonymous is not None:
        instance.properties.anonymous_connect_policy = 'allow' if allow_anonymous else 'deny'
    if event_handler is not None:
        instance.properties.event_handlers = event_handler
    return instance
