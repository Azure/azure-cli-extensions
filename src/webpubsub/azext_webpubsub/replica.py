# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.azure_mgmt_webpubsub.models import (
    ResourceSku,
    Replica
)

from .vendored_sdks.azure_mgmt_webpubsub.operations import (
    WebPubSubOperations
)


def webpubsub_replica_list(client: WebPubSubOperations, resource_group_name, webpubsub_name):
    return client.list(resource_group_name, webpubsub_name)


def webpubsub_replica_show(client: WebPubSubOperations, webpubsub_name, replica_name, resource_group_name):
    return client.get(resource_group_name=resource_group_name, resource_name=webpubsub_name, replica_name=replica_name)


def webpubsub_replica_delete(client: WebPubSubOperations, webpubsub_name, replica_name, resource_group_name):
    return client.delete(resource_group_name=resource_group_name, resource_name=webpubsub_name, replica_name=replica_name)


def webpubsub_replica_create(client: WebPubSubOperations, webpubsub_name, replica_name, resource_group_name,
                             sku, unit_count=1, location=None, tags=None):
    sku = ResourceSku(name=sku, capacity=unit_count)
    parameter = Replica(tags=tags,
                        sku=sku,
                        location=location,
                        )

    return client.begin_create_or_update(resource_group_name=resource_group_name, resource_name=webpubsub_name,
                                         replica_name=replica_name, parameters=parameter)
