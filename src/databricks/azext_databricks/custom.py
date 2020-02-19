# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

import random
import string


def id_generator(size=13, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_databricks_workspace(cmd, client,
                                resource_group_name,
                                workspace_name,
                                location,
                                managed_resource_group,
                                sku_name,
                                aml_workspace_id=None,
                                custom_virtual_network_id=None,
                                custom_public_subnet_name=None,
                                custom_private_subnet_name=None,
                                enable_no_public_ip=False,
                                load_balancer_backend_pool_name=None,
                                load_balancer_id=None,
                                relay_namespace_name=None,
                                storage_account_name=None,
                                storage_account_sku_name=None,
                                vnet_address_prefix=None,
                                tags=None):
    body = {}
    body['tags'] = tags  # dictionary
    body['location'] = location  # str
    body['managed_resource_group_id'] = managed_resource_group  # str

    random_id = id_generator()

    body.setdefault('parameters', {}).setdefault('enable_no_public_ip', {})['value'] = enable_no_public_ip  # boolean
    if aml_workspace_id is not None:
        body.setdefault('parameters', {}).setdefault('aml_workspace_id', {})['value'] = aml_workspace_id  # str
    if custom_virtual_network_id is not None:
        body.setdefault('parameters', {}).setdefault('custom_virtual_network_id', {})['value'] = custom_virtual_network_id  # str
    if custom_public_subnet_name is not None:
        body.setdefault('parameters', {}).setdefault('custom_public_subnet_name', {})['value'] = custom_public_subnet_name  # str
    if custom_private_subnet_name is not None:
        body.setdefault('parameters', {}).setdefault('custom_private_subnet_name', {})['value'] = custom_private_subnet_name  # str
    if load_balancer_backend_pool_name is not None:
        body.setdefault('parameters', {}).setdefault('load_balancer_backend_pool_name', {})['value'] = load_balancer_backend_pool_name  # str
    if load_balancer_id is not None:
        body.setdefault('parameters', {}).setdefault('load_balancer_id', {})['value'] = load_balancer_id  # str

    # set default values, same as what portal does
    body.setdefault('parameters', {}).setdefault('relay_namespace_name', {})['value'] = "dbrelay{}".format(random_id) if relay_namespace_name is None else relay_namespace_name  # str
    body.setdefault('parameters', {}).setdefault('storage_account_name', {})['value'] = "dbstorage{}".format(random_id) if storage_account_name is None else storage_account_name  # str
    body.setdefault('parameters', {}).setdefault('storage_account_sku_name', {})['value'] = "Standard_GRS" if storage_account_sku_name is None else storage_account_sku_name  # str
    body.setdefault('parameters', {}).setdefault('vnet_address_prefix', {})['value'] = "10.139" if vnet_address_prefix is None else vnet_address_prefix  # str

    body.setdefault('sku', {})['name'] = sku_name  # str
    print(body)
    return client.create_or_update(resource_group_name=resource_group_name, workspace_name=workspace_name, parameters=body)


def update_databricks_workspace(cmd, client,  # pylint: disable=too-many-branches
                                resource_group_name,
                                workspace_name,
                                tags=None):
    return client.update(resource_group_name=resource_group_name,
                         workspace_name=workspace_name,
                         tags=tags)


def delete_databricks_workspace(cmd, client, resource_group_name,
                                workspace_name):
    return client.delete(resource_group_name=resource_group_name,
                         workspace_name=workspace_name)


def get_databricks_workspace(cmd, client, resource_group_name, workspace_name):
    return client.get(resource_group_name=resource_group_name,
                      workspace_name=workspace_name)


def list_databricks_workspace(cmd, client, resource_group_name=None, list_all=None):
    if list_all or resource_group_name is None:
        return client.list_by_subscription()
    return client.list_by_resource_group(resource_group_name=resource_group_name)
