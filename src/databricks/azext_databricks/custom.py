# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


from azure.cli.core.util import sdk_no_wait


def create_databricks_workspace(cmd, client,
                                resource_group_name,
                                workspace_name,
                                location,
                                sku_name,
                                managed_resource_group=None,
                                custom_virtual_network_id=None,
                                custom_public_subnet_name=None,
                                custom_private_subnet_name=None,
                                tags=None,
                                no_wait=False):
    body = {}
    body['tags'] = tags  # dictionary
    body['location'] = location  # str
    body['managed_resource_group_id'] = managed_resource_group  # str
    body.setdefault('sku', {})['name'] = sku_name  # str

    parameters = {}
    if custom_virtual_network_id is not None:
        _set_parameter_value(parameters, 'custom_virtual_network_id', custom_virtual_network_id)  # str
    if custom_public_subnet_name is not None:
        _set_parameter_value(parameters, 'custom_public_subnet_name', custom_public_subnet_name)  # str
    if custom_private_subnet_name is not None:
        _set_parameter_value(parameters, 'custom_private_subnet_name', custom_private_subnet_name)  # str
    body['parameters'] = parameters

    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       parameters=body)


def _set_parameter_value(parameters, field, value):
    parameters.setdefault(field, {})['value'] = value


def update_databricks_workspace(cmd, client,  # pylint: disable=too-many-branches
                                resource_group_name,
                                workspace_name,
                                tags=None,
                                no_wait=False):
    return sdk_no_wait(no_wait, client.update,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       tags=tags)


def delete_databricks_workspace(cmd, client, resource_group_name,
                                workspace_name,
                                no_wait=False):
    return sdk_no_wait(no_wait, client.delete,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name)


def get_databricks_workspace(cmd, client, resource_group_name, workspace_name):
    return client.get(resource_group_name=resource_group_name,
                      workspace_name=workspace_name)


def list_databricks_workspace(cmd, client, resource_group_name=None):
    if not resource_group_name:
        return client.list_by_subscription()  # todo service 502
    return client.list_by_resource_group(resource_group_name=resource_group_name)
