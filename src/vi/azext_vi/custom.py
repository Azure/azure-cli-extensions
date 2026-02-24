# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from .k8s_utils import troubleshoot_k8s_extension


def _get_vi_extension(client, resource_group_name, connected_cluster):
    extension = client.extensions.get_vi_extension(
        resource_group=resource_group_name,
        connected_cluster=connected_cluster)
    if not extension:
        raise CLIError(
            f'VI Extension not found in connected cluster "{connected_cluster}" '
            f'under resource group "{resource_group_name}".')
    return extension


def show_vi_extension(client, resource_group_name, connected_cluster):
    extension = _get_vi_extension(client, resource_group_name, connected_cluster)
    return extension


def troubleshoot_vi_extension(cmd, client, resource_group_name, connected_cluster):
    extension = _get_vi_extension(client, resource_group_name, connected_cluster)
    namespace = extension.get("properties", {}).get("scope", {}).get("cluster", {}).get("releaseNamespace")
    if not namespace:
        raise CLIError(
            f'Unable to determine namespace for VI Extension in connected cluster "{connected_cluster}".')

    troubleshoot_k8s_extension(cmd=cmd, name=extension.get("name"), namespace_list=namespace)


def add_camera(client, resource_group_name, connected_cluster, camera_name, rtsp_url, ignore_certificate=False):
    extension = _get_vi_extension(client, resource_group_name, connected_cluster)
    response = client.cameras.add_camera(extension=extension,
                                         camera_name=camera_name,
                                         rtsp_url=rtsp_url,
                                         ignore_certificate=ignore_certificate)
    return response


def list_cameras(client, resource_group_name, connected_cluster, ignore_certificate=False):
    extension = _get_vi_extension(client, resource_group_name, connected_cluster)
    response = client.cameras.list_cameras(extension=extension, ignore_certificate=ignore_certificate)
    cameras = response.get('results', [])
    return cameras
