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


def create_custom_providers_custom_resource_provider(client,
                                                     resource_group_name,
                                                     resource_provider_name,
                                                     location=None,
                                                     tags=None,
                                                     actions=None,
                                                     resource_types=None,
                                                     validations=None,
                                                     no_wait=False):
    body = {'location': location, 'tags': tags,
            'actions': actions, 'resource_types': resource_types,
            'validations': validations}
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name=resource_group_name, resource_provider_name=resource_provider_name, resource_provider=body)


def update_custom_providers_custom_resource_provider(client,
                                                     resource_group_name,
                                                     resource_provider_name,
                                                     tags=None):
    return client.update(resource_group_name=resource_group_name, resource_provider_name=resource_provider_name, tags=tags)


def delete_custom_providers_custom_resource_provider(client,
                                                     resource_group_name,
                                                     resource_provider_name,
                                                     no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, resource_provider_name=resource_provider_name)


def get_custom_providers_custom_resource_provider(client,
                                                  resource_group_name,
                                                  resource_provider_name):
    return client.get(resource_group_name=resource_group_name, resource_provider_name=resource_provider_name)


def list_custom_providers_custom_resource_provider(client,
                                                   resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()
