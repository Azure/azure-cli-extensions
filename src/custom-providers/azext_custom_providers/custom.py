# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_custom_providers_custom_resource_provider(cmd, client,
                                                     resource_group,
                                                     name,
                                                     location,
                                                     tags=None,
                                                     actions=None,
                                                     resource_types=None,
                                                     validations=None):
    body = {}
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['actions'] = actions
    body['resource_types'] = resource_types
    body['validations'] = validations
    return client.create_or_update(resource_group_name=resource_group, resource_provider_name=name, resource_provider=body)


def update_custom_providers_custom_resource_provider(cmd, client,
                                                     resource_group,
                                                     name,
                                                     location=None,
                                                     tags=None,
                                                     actions=None,
                                                     resource_types=None,
                                                     validations=None):
    body = {}
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if actions is not None:
        body['actions'] = actions
    if resource_types is not None:
        body['resource_types'] = resource_types
    if validations is not None:
        body['validations'] = validations
    return client.create_or_update(resource_group_name=resource_group, resource_provider_name=name, resource_provider=body)


def delete_custom_providers_custom_resource_provider(cmd, client,
                                                     resource_group,
                                                     name):
    return client.delete(resource_group_name=resource_group, resource_provider_name=name)


def get_custom_providers_custom_resource_provider(cmd, client,
                                                  resource_group,
                                                  name):
    return client.get(resource_group_name=resource_group, resource_provider_name=name)


def list_custom_providers_custom_resource_provider(cmd, client,
                                                   resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list_by_subscription()
