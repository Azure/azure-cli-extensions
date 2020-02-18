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


def create_databricks_workspace(
    cmd,
    client,
    resource_group_name,
    workspace_name,
    location,
    sku_name,
    tags=None,
    managed_resource_group=None,
    aml_workspace_id=None,
    custom_virtual_network_id=None,
    custom_public_subnet_name=None,
    custom_private_subnet_name=None,
    enable_no_public_ip=None,
    load_balancer_backend_pool_name=None,
    load_balancer_id=None,
    relay_namespace_name=None,
    storage_account_name=None,
    storage_account_sku_name=None,
    # resource_tags=None,
    vnet_address_prefix=None,
    authorizations=None):
    from azure.cli.core.commands.client_factory import get_subscription_id
    random_id = id_generator()
    parameters = {
        "enable_no_public_ip": None,
        "relay_namespace_name": "dbrelay{}".format(random_id),
        "storage_account_name": "dbstorage{}".format(random_id),
        "storage_account_sku_name": "Standard_GRS",
        "vnet_address_prefix": "10.139"
    }
    parameters['aml_workspace_id'] = aml_workspace_id  # str
    parameters['custom_virtual_network_id'] = custom_virtual_network_id  # str
    parameters['custom_public_subnet_name'] = custom_public_subnet_name  # str
    parameters['custom_private_subnet_name'] = custom_private_subnet_name  # str
    parameters['load_balancer_backend_pool_name'] = load_balancer_backend_pool_name  # str
    parameters['load_balancer_id'] = load_balancer_id  # str

    if enable_no_public_ip is not None:
        parameters['enable_no_public_ip'] = enable_no_public_ip  # str
    if relay_namespace_name is not None:
        parameters['relay_namespace_name'] = relay_namespace_name  # str
    if storage_account_name is not None:
        parameters['storage_account_name'] = storage_account_name  # str
    if storage_account_sku_name is not None:
        parameters['storage_account_sku_name'] = storage_account_sku_name  # str
    if vnet_address_prefix is not None:
        parameters['vnet_address_prefix'] = vnet_address_prefix  # str

    body = {}
    body['parameters'] = parameters
    body['tags'] = tags  # dictionary
    body['location'] = location  # str
    managed_resource_group_id = '/subscriptions/' + get_subscription_id(
        cmd.cli_ctx) + '/resourceGroups/' + managed_resource_group
    body['managed_resource_group_id'] = managed_resource_group_id  # str
    # "managedResourceGroupId": "[concat('/subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/databricks-rg-', parameters('workspaces_feng_workspace_name'), '-2dmcpf2mtjrsa')]",

    body['authorizations'] = authorizations
    body.setdefault('sku', {})['name'] = sku_name  # str
    # body.setdefault('sku', {})['tier'] = sku_tier  # str
    print(body)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   workspace_name=workspace_name,
                                   parameters=body)


def update_databricks_workspace(
    cmd,
    client,  # pylint: disable=too-many-branches
    resource_group_name,
    workspace_name,
    tags=None,
    location=None,
    managed_resource_group_id=None,
    aml_workspace_id_type=None,
    aml_workspace_id_value=None,
    custom_virtual_network_id_type=None,
    custom_virtual_network_id_value=None,
    custom_public_subnet_name_type=None,
    custom_public_subnet_name_value=None,
    custom_private_subnet_name_type=None,
    custom_private_subnet_name_value=None,
    enable_no_public_ip_type=None,
    enable_no_public_ip_value=None,
    load_balancer_backend_pool_name_type=None,
    load_balancer_backend_pool_name_value=None,
    load_balancer_id_type=None,
    load_balancer_id_value=None,
    relay_namespace_name_type=None,
    relay_namespace_name_value=None,
    storage_account_name_type=None,
    storage_account_name_value=None,
    storage_account_sku_name_type=None,
    storage_account_sku_name_value=None,
    resource_tags_type=None,
    resource_tags_value=None,
    vnet_address_prefix_type=None,
    vnet_address_prefix_value=None,
    ui_definition_uri=None,
    authorizations=None,
    sku_name=None):
    body = {}
    if tags is not None:
        body['tags'] = tags  # dictionary
    if location is not None:
        body['location'] = location  # str
    if managed_resource_group_id is not None:
        body['managed_resource_group_id'] = managed_resource_group_id  # str
    if aml_workspace_id_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'aml_workspace_id', {})['value'] = aml_workspace_id_value  # str
    if custom_virtual_network_id_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'custom_virtual_network_id',
            {})['value'] = custom_virtual_network_id_value  # str
    if custom_public_subnet_name_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'custom_public_subnet_name',
            {})['value'] = custom_public_subnet_name_value  # str
    if custom_private_subnet_name_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'custom_private_subnet_name',
            {})['value'] = custom_private_subnet_name_value  # str
    if enable_no_public_ip_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'enable_no_public_ip',
            {})['value'] = enable_no_public_ip_value  # boolean
    if load_balancer_backend_pool_name_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'load_balancer_backend_pool_name',
            {})['value'] = load_balancer_backend_pool_name_value  # str
    if load_balancer_id_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'load_balancer_id', {})['value'] = load_balancer_id_value  # str
    if relay_namespace_name_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'relay_namespace_name',
            {})['value'] = relay_namespace_name_value  # str
    if storage_account_name_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'storage_account_name',
            {})['value'] = storage_account_name_value  # str
    if storage_account_sku_name_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'storage_account_sku_name',
            {})['value'] = storage_account_sku_name_value  # str
    if resource_tags_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'resource_tags',
            {})['value'] = resource_tags_value  # unknown-primary[object]
    if vnet_address_prefix_value is not None:
        body.setdefault('parameters', {}).setdefault(
            'vnet_address_prefix',
            {})['value'] = vnet_address_prefix_value  # str
    if authorizations is not None:
        body['authorizations'] = authorizations
    if sku_name is not None:
        body.setdefault('sku', {})['name'] = sku_name  # str
    return client.update(resource_group_name=resource_group_name,
                         workspace_name=workspace_name,
                         parameters=body)


def delete_databricks_workspace(cmd, client, resource_group_name,
                                workspace_name):
    return client.delete(resource_group_name=resource_group_name,
                         workspace_name=workspace_name)


def get_databricks_workspace(cmd, client, resource_group_name, workspace_name):
    return client.get(resource_group_name=resource_group_name,
                      workspace_name=workspace_name)


def list_databricks_workspace(cmd, client, resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(
            resource_group_name=resource_group)
    return client.list_by_subscription()
