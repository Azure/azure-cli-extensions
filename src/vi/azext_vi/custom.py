# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from .k8s_utils import troubleshoot_k8s_extension
from .cameras_utils import format_cameras

def my_vi_command(client):
    return {"message": "This is my custom VI command!"}


def show_vi_extension(client, resource_group_name, connected_cluster):
    extension = client.extensions.get_vi_extension(
        resource_group=resource_group_name,
        connected_cluster=connected_cluster)
    if not extension:
        raise CLIError(
            f'VI Extension not found in connected cluster "{connected_cluster}" '
            f'under resource group "{resource_group_name}".')
    return extension


def update_vi_extension(client, resource_group_name, connected_cluster):
    extension = client.extensions.get_vi_extension(
        resource_group=resource_group_name,
        connected_cluster=connected_cluster)
    if not extension:
        raise CLIError(
            f'VI Extension not found in connected cluster "{connected_cluster}" '
            f'under resource group "{resource_group_name}".')
    return extension


def troubleshoot_vi_extension(cmd, client, resource_group_name, connected_cluster):
    extension = client.extensions.get_vi_extension(
        resource_group=resource_group_name,
        connected_cluster=connected_cluster)
    if not extension:
        raise CLIError(
            f'VI Extension not found in connected cluster "{connected_cluster}" '
            f'under resource group "{resource_group_name}".')

    namespace = extension.get("properties", {}).get("scope", {}).get("cluster", {}).get("releaseNamespace")
    if not namespace:
        raise CLIError(
            f'Unable to determine namespace for VI Extension in connected cluster "{connected_cluster}".')

    troubleshoot_k8s_extension(cmd=cmd, name=extension.get("name"), namespace_list=namespace)


def list_cameras(client, resource_group_name, connected_cluster):
    extension = client.extensions.get_vi_extension(
        resource_group=resource_group_name,
        connected_cluster=connected_cluster)
    if not extension:
        raise CLIError(
            f'VI Extension not found in connected cluster "{connected_cluster}" '
            f'under resource group "{resource_group_name}". '
            f'Please ensure the VI Extension is installed before listing cameras.')

    response = client.cameras.list_cameras(extension=extension)
    cameras = response.get('results')
    format_cameras(cameras)
    return cameras


def list_vi(cmd, resource_group_name=None):
    raise CLIError('TODO: Implement `vi list`')


def update_vi(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance
