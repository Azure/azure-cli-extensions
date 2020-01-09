# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from knack.util import CLIError


def create_powerbiembedded_workspace_collection(cmd, client,
                                                resource_group_name,
                                                name,
                                                location=None,
                                                tags=None):
    exist = client.check_name_availability(location=location, name=name).name_available
    if exist:
        return client.create(resource_group_name=resource_group_name, workspace_collection_name=name, location=location, tags=tags)
    raise CLIError("{} already exists. Please use another name.".format(name))


def update_powerbiembedded_workspace_collection(cmd, client,
                                                resource_group_name,
                                                name,
                                                tags=None):
    return client.update(resource_group_name=resource_group_name, workspace_collection_name=name, tags=tags)


def delete_powerbiembedded_workspace_collection(cmd, client,
                                                resource_group_name,
                                                name):
    return client.delete(resource_group_name=resource_group_name, workspace_collection_name=name)


def get_powerbiembedded_workspace_collection(cmd, client,
                                             resource_group_name,
                                             name):
    return client.get_by_name(resource_group_name=resource_group_name, workspace_collection_name=name)


def list_powerbiembedded_workspace_collection(cmd, client,
                                              resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def get_access_keys_powerbiembedded_workspace_collection(cmd, client,
                                                         resource_group_name,
                                                         name):
    return client.get_access_keys(resource_group_name=resource_group_name, workspace_collection_name=name)


def regenerate_key_powerbiembedded_workspace_collection(cmd, client,
                                                        resource_group_name,
                                                        name,
                                                        key_name='key1'):
    return client.regenerate_key(resource_group_name=resource_group_name, workspace_collection_name=name, key_name=key_name)


def list_powerbiembedded_workspace_collection_workspace(cmd, client,
                                                        resource_group_name,
                                                        workspace_collection_name):
    return client.list(resource_group_name=resource_group_name, workspace_collection_name=workspace_collection_name)
