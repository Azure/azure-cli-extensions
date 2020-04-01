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


def create_powerbi_embedded_capacity(client,
                                     resource_group_name,
                                     name,
                                     sku_name,
                                     location,
                                     sku_tier=None,
                                     tags=None,
                                     administration_members=None, no_wait=False):
    body = {}
    body.setdefault('sku', {})['name'] = sku_name  # str
    body.setdefault('sku', {})['tier'] = sku_tier  # str
    body['tags'] = tags  # dictionary
    body['location'] = location  # dictionary
    body.setdefault('administration', {})['members'] = None if administration_members is None else administration_members
    return sdk_no_wait(no_wait, client.create, resource_group_name=resource_group_name, dedicated_capacity_name=name, capacity_parameters=body)


def update_powerbi_embedded_capacity(client,
                                     resource_group_name,
                                     name,
                                     sku_name=None,
                                     sku_tier=None,
                                     tags=None,
                                     administration_members=None, no_wait=False):
    body = {}
    if sku_name is not None:
        body.setdefault('sku', {})['name'] = sku_name  # str
    if sku_tier is not None:
        body.setdefault('sku', {})['tier'] = sku_tier  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if administration_members is not None:
        body.setdefault('administration', {})['members'] = None if administration_members is None \
            else administration_members
    return sdk_no_wait(no_wait, client.update, resource_group_name=resource_group_name, dedicated_capacity_name=name,
                       capacity_update_parameters=body)


def delete_powerbi_embedded_capacity(client,
                                     resource_group_name,
                                     name, no_wait=False):
    return sdk_no_wait(no_wait, client.delete, resource_group_name=resource_group_name, dedicated_capacity_name=name)


def get_powerbi_embedded_capacity(client,
                                  resource_group_name,
                                  name):
    return client.get_details(resource_group_name=resource_group_name, dedicated_capacity_name=name)


def list_powerbi_embedded_capacity(client,
                                   resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()
