# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def list_connectedmachine(client, resource_group_name=None):
    if resource_group_name:
        return client.machines.list_by_resource_group(resource_group_name)
    return client.machines.list_by_subscription()


def show_connectedmachine(client, resource_group_name, name):
    return client.machines.get(resource_group_name, name)


def delete_connectedmachine(client, resource_group_name, name):
    return client.machines.delete(resource_group_name, name)
