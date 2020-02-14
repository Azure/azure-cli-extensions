# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_powerbi_embedded_capacity(cmd, client,
                                     resource_group_name,
                                     name,
                                     sku_name,
                                     location=None,
                                     sku_tier=None,
                                     tags=None,
                                     administration_members=None):
    body = {}
    body.setdefault('sku', {})['name'] = sku_name  # str
    body.setdefault('sku', {})['tier'] = sku_tier  # str
    body['tags'] = tags  # dictionary
    body['location'] = location  # dictionary
    body.setdefault('administration', {})['members'] = None if administration_members is None else administration_members
    return client.create(resource_group_name=resource_group_name, dedicated_capacity_name=name, capacity_parameters=body)


def update_powerbi_embedded_capacity(cmd, client,
                                     resource_group,
                                     name,
                                     sku_name=None,
                                     sku_tier=None,
                                     tags=None,
                                     administration_members=None):
    body = {}
    if sku_name is not None:
        body.setdefault('sku', {})['name'] = sku_name  # str
    if sku_tier is not None:
        body.setdefault('sku', {})['tier'] = sku_tier  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if administration_members is not None:
        body.setdefault('administration', {})['members'] = None if administration_members is None else administration_members
    return client.create(resource_group_name=resource_group, dedicated_capacity_name=name, capacity_parameters=body)


def delete_powerbi_embedded_capacity(cmd, client,
                                     resource_group,
                                     name):
    return client.delete(resource_group_name=resource_group, dedicated_capacity_name=name)


def get_powerbi_embedded_capacity(cmd, client,
                                  resource_group,
                                  name):
    return client.get_details(resource_group_name=resource_group, dedicated_capacity_name=name)


def list_powerbi_embedded_capacity(cmd, client,
                                   resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()
