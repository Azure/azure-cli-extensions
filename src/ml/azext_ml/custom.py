# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
import json


def create_ml(cmd, client,
              resource_group,
              name,
              location,
              tags=None,
              sku=None,
              workspace_state=None,
              key_vault_identifier_id=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['sku'] = json.loads(sku) if isinstance(sku, str) else sku
    body['workspace_state'] = workspace_state  # str
    body['key_vault_identifier_id'] = key_vault_identifier_id  # str
    return client.create_or_update(resource_group_name=resource_group, workspace_name=name, parameters=body)


def update_ml(cmd, client,
              resource_group,
              name,
              location=None,
              tags=None,
              sku=None,
              workspace_state=None,
              key_vault_identifier_id=None):
    body = client.get(resource_group_name=resource_group, workspace_name=name).as_dict()
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if sku is not None:
        body['sku'] = json.loads(sku) if isinstance(sku, str) else sku
    if workspace_state is not None:
        body['workspace_state'] = workspace_state  # str
    if key_vault_identifier_id is not None:
        body['key_vault_identifier_id'] = key_vault_identifier_id  # str
    return client.create_or_update(resource_group_name=resource_group, workspace_name=name, parameters=body)


def delete_ml(cmd, client,
              resource_group,
              name):
    return client.delete(resource_group_name=resource_group, workspace_name=name)


def get_ml(cmd, client,
           resource_group,
           name):
    return client.get(resource_group_name=resource_group, workspace_name=name)


def list_ml(cmd, client,
            resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()


def resync_storage_keys_ml(cmd, client,
                           resource_group,
                           name):
    return client.resync_storage_keys(resource_group_name=resource_group, workspace_name=name)


def list_workspace_keys_ml(cmd, client,
                           resource_group,
                           name):
    return client.list_workspace_keys(resource_group_name=resource_group, workspace_name=name)
