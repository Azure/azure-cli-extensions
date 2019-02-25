# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.log import get_logger
from azext_anf_preview.vendored_sdks.models import NetAppAccountPatch, CapacityPool, Volume, VolumePatch, Snapshot

logger = get_logger(__name__)


def generate_tags(tag):
    if tag is None:
        return None

    tags = {}
    tag_list = tag.split(" ")
    for tag_item in tag_list:
        parts = tag_item.split("=", 1)
        if len(parts) == 2:
            # two parts, everything after first '=' is the tag's value
            tags[parts[0]] = parts[1]
        elif len(parts) == 1:
            # one part, no tag value
            tags[parts[0]] = ""
    return tags


def _update_mapper(existing, new, keys):
    for key in keys:
        existing_value = getattr(existing, key)
        new_value = getattr(new, key)
        setattr(new, key, new_value if new_value is not None else existing_value)


# pylint: disable=unused-argument
def create_account(cmd, client, account_name, resource_group_name, location, tag=None):
    return client.create_or_update(resource_group_name, account_name, location, generate_tags(tag))


# pylint: disable=unused-argument
def update_account(cmd, instance, tag=None):
    params = NetAppAccountPatch(tags=generate_tags(tag))
    return params.tags


def create_pool(cmd, client, account_name, pool_name, resource_group_name, location, size, service_level, tag=None):
    body = CapacityPool(service_level=service_level, size=int(size), location=location, tags=generate_tags(tag))
    return client.create_or_update(body, resource_group_name, account_name, pool_name)


def update_pool(cmd, instance, location=None, size=None, service_level=None, tag=None):
    # put operation to update the record
    if size is not None:
        size = int(size)
    body = CapacityPool(service_level=service_level, size=size, location=location, tags=generate_tags(tag))
    _update_mapper(instance, body, ['location', 'service_level', 'size', 'tags'])
    return body


def create_volume(cmd, client, account_name, pool_name, volume_name, resource_group_name, location, service_level, creation_token, usage_threshold, subnet_id, tag=None):
    body = Volume(
        usage_threshold=int(usage_threshold),
        creation_token=creation_token,
        service_level=service_level,
        location=location,
        subnet_id=subnet_id,
        tags=generate_tags(tag))
    return client.create_or_update(body, resource_group_name, account_name, pool_name, volume_name)


def patch_volume(cmd, instance, service_level=None, usage_threshold=None, tag=None):
    params = VolumePatch(
        usage_threshold=None if usage_threshold is None else int(usage_threshold),
        service_level=service_level,
        tags=generate_tags(tag))
    _update_mapper(instance, params, ['service_level', 'usage_threshold', 'tags'])
    return params


def create_snapshot(cmd, client, account_name, pool_name, volume_name, snapshot_name, file_system_id, resource_group_name, location):
    body = Snapshot(location=location, file_system_id=file_system_id)
    return client.create(body, resource_group_name, account_name, pool_name, volume_name, snapshot_name)
