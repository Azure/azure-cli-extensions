# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def create_databricks_workspace(cmd, client,
                                resource_group,
                                name,
                                location,
                                managed_resource_group_id,
                                aml_workspace_id_value,
                                custom_virtual_network_id_value,
                                custom_public_subnet_name_value,
                                custom_private_subnet_name_value,
                                enable_no_public_ip_value,
                                load_balancer_backend_pool_name_value,
                                load_balancer_id_value,
                                relay_namespace_name_value,
                                storage_account_name_value,
                                storage_account_sku_name_value,
                                resource_tags_value,
                                vnet_address_prefix_value,
                                sku_name,
                                tags=None,
                                aml_workspace_id_type=None,
                                custom_virtual_network_id_type=None,
                                custom_public_subnet_name_type=None,
                                custom_private_subnet_name_type=None,
                                enable_no_public_ip_type=None,
                                load_balancer_backend_pool_name_type=None,
                                load_balancer_id_type=None,
                                relay_namespace_name_type=None,
                                storage_account_name_type=None,
                                storage_account_sku_name_type=None,
                                resource_tags_type=None,
                                vnet_address_prefix_type=None,
                                ui_definition_uri=None,
                                authorizations=None,
                                sku_tier=None):
    body = {}
    body['tags'] = tags  # dictionary
    body['location'] = location  # str
    body['managed_resource_group_id'] = managed_resource_group_id  # str
    body.setdefault('parameters', {}).setdefault('aml_workspace_id', {})['type'] = aml_workspace_id_type  # str
    body.setdefault('parameters', {}).setdefault('aml_workspace_id', {})['value'] = aml_workspace_id_value  # str
    body.setdefault('parameters', {}).setdefault('custom_virtual_network_id', {})['type'] = custom_virtual_network_id_type  # str
    body.setdefault('parameters', {}).setdefault('custom_virtual_network_id', {})['value'] = custom_virtual_network_id_value  # str
    body.setdefault('parameters', {}).setdefault('custom_public_subnet_name', {})['type'] = custom_public_subnet_name_type  # str
    body.setdefault('parameters', {}).setdefault('custom_public_subnet_name', {})['value'] = custom_public_subnet_name_value  # str
    body.setdefault('parameters', {}).setdefault('custom_private_subnet_name', {})['type'] = custom_private_subnet_name_type  # str
    body.setdefault('parameters', {}).setdefault('custom_private_subnet_name', {})['value'] = custom_private_subnet_name_value  # str
    body.setdefault('parameters', {}).setdefault('enable_no_public_ip', {})['type'] = enable_no_public_ip_type  # str
    body.setdefault('parameters', {}).setdefault('enable_no_public_ip', {})['value'] = enable_no_public_ip_value  # boolean
    body.setdefault('parameters', {}).setdefault('load_balancer_backend_pool_name', {})['type'] = load_balancer_backend_pool_name_type  # str
    body.setdefault('parameters', {}).setdefault('load_balancer_backend_pool_name', {})['value'] = load_balancer_backend_pool_name_value  # str
    body.setdefault('parameters', {}).setdefault('load_balancer_id', {})['type'] = load_balancer_id_type  # str
    body.setdefault('parameters', {}).setdefault('load_balancer_id', {})['value'] = load_balancer_id_value  # str
    body.setdefault('parameters', {}).setdefault('relay_namespace_name', {})['type'] = relay_namespace_name_type  # str
    body.setdefault('parameters', {}).setdefault('relay_namespace_name', {})['value'] = relay_namespace_name_value  # str
    body.setdefault('parameters', {}).setdefault('storage_account_name', {})['type'] = storage_account_name_type  # str
    body.setdefault('parameters', {}).setdefault('storage_account_name', {})['value'] = storage_account_name_value  # str
    body.setdefault('parameters', {}).setdefault('storage_account_sku_name', {})['type'] = storage_account_sku_name_type  # str
    body.setdefault('parameters', {}).setdefault('storage_account_sku_name', {})['value'] = storage_account_sku_name_value  # str
    body.setdefault('parameters', {}).setdefault('resource_tags', {})['type'] = resource_tags_type  # str
    body.setdefault('parameters', {}).setdefault('resource_tags', {})['value'] = resource_tags_value  # unknown-primary[object]
    body.setdefault('parameters', {}).setdefault('vnet_address_prefix', {})['type'] = vnet_address_prefix_type  # str
    body.setdefault('parameters', {}).setdefault('vnet_address_prefix', {})['value'] = vnet_address_prefix_value  # str
    body['ui_definition_uri'] = ui_definition_uri  # str
    body['authorizations'] = authorizations
    body.setdefault('sku', {})['name'] = sku_name  # str
    body.setdefault('sku', {})['tier'] = sku_tier  # str
    return client.create_or_update(resource_group_name=resource_group, workspace_name=name, parameters=body)


def update_databricks_workspace(cmd, client,
                                resource_group,
                                name,
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
                                sku_name=None,
                                sku_tier=None):
    body = {}
    if tags is not None:
        body['tags'] = tags  # dictionary
    if location is not None:
        body['location'] = location  # str
    if managed_resource_group_id is not None:
        body['managed_resource_group_id'] = managed_resource_group_id  # str
    if aml_workspace_id_type is not None:
        body.setdefault('parameters', {}).setdefault('aml_workspace_id', {})['type'] = aml_workspace_id_type  # str
    if aml_workspace_id_value is not None:
        body.setdefault('parameters', {}).setdefault('aml_workspace_id', {})['value'] = aml_workspace_id_value  # str
    if custom_virtual_network_id_type is not None:
        body.setdefault('parameters', {}).setdefault('custom_virtual_network_id', {})['type'] = custom_virtual_network_id_type  # str
    if custom_virtual_network_id_value is not None:
        body.setdefault('parameters', {}).setdefault('custom_virtual_network_id', {})['value'] = custom_virtual_network_id_value  # str
    if custom_public_subnet_name_type is not None:
        body.setdefault('parameters', {}).setdefault('custom_public_subnet_name', {})['type'] = custom_public_subnet_name_type  # str
    if custom_public_subnet_name_value is not None:
        body.setdefault('parameters', {}).setdefault('custom_public_subnet_name', {})['value'] = custom_public_subnet_name_value  # str
    if custom_private_subnet_name_type is not None:
        body.setdefault('parameters', {}).setdefault('custom_private_subnet_name', {})['type'] = custom_private_subnet_name_type  # str
    if custom_private_subnet_name_value is not None:
        body.setdefault('parameters', {}).setdefault('custom_private_subnet_name', {})['value'] = custom_private_subnet_name_value  # str
    if enable_no_public_ip_type is not None:
        body.setdefault('parameters', {}).setdefault('enable_no_public_ip', {})['type'] = enable_no_public_ip_type  # str
    if enable_no_public_ip_value is not None:
        body.setdefault('parameters', {}).setdefault('enable_no_public_ip', {})['value'] = enable_no_public_ip_value  # boolean
    if load_balancer_backend_pool_name_type is not None:
        body.setdefault('parameters', {}).setdefault('load_balancer_backend_pool_name', {})['type'] = load_balancer_backend_pool_name_type  # str
    if load_balancer_backend_pool_name_value is not None:
        body.setdefault('parameters', {}).setdefault('load_balancer_backend_pool_name', {})['value'] = load_balancer_backend_pool_name_value  # str
    if load_balancer_id_type is not None:
        body.setdefault('parameters', {}).setdefault('load_balancer_id', {})['type'] = load_balancer_id_type  # str
    if load_balancer_id_value is not None:
        body.setdefault('parameters', {}).setdefault('load_balancer_id', {})['value'] = load_balancer_id_value  # str
    if relay_namespace_name_type is not None:
        body.setdefault('parameters', {}).setdefault('relay_namespace_name', {})['type'] = relay_namespace_name_type  # str
    if relay_namespace_name_value is not None:
        body.setdefault('parameters', {}).setdefault('relay_namespace_name', {})['value'] = relay_namespace_name_value  # str
    if storage_account_name_type is not None:
        body.setdefault('parameters', {}).setdefault('storage_account_name', {})['type'] = storage_account_name_type  # str
    if storage_account_name_value is not None:
        body.setdefault('parameters', {}).setdefault('storage_account_name', {})['value'] = storage_account_name_value  # str
    if storage_account_sku_name_type is not None:
        body.setdefault('parameters', {}).setdefault('storage_account_sku_name', {})['type'] = storage_account_sku_name_type  # str
    if storage_account_sku_name_value is not None:
        body.setdefault('parameters', {}).setdefault('storage_account_sku_name', {})['value'] = storage_account_sku_name_value  # str
    if resource_tags_type is not None:
        body.setdefault('parameters', {}).setdefault('resource_tags', {})['type'] = resource_tags_type  # str
    if resource_tags_value is not None:
        body.setdefault('parameters', {}).setdefault('resource_tags', {})['value'] = resource_tags_value  # unknown-primary[object]
    if vnet_address_prefix_type is not None:
        body.setdefault('parameters', {}).setdefault('vnet_address_prefix', {})['type'] = vnet_address_prefix_type  # str
    if vnet_address_prefix_value is not None:
        body.setdefault('parameters', {}).setdefault('vnet_address_prefix', {})['value'] = vnet_address_prefix_value  # str
    if ui_definition_uri is not None:
        body['ui_definition_uri'] = ui_definition_uri  # str
    if authorizations is not None:
        body['authorizations'] = authorizations
    if sku_name is not None:
        body.setdefault('sku', {})['name'] = sku_name  # str
    if sku_tier is not None:
        body.setdefault('sku', {})['tier'] = sku_tier  # str
    return client.create_or_update(resource_group_name=resource_group, workspace_name=name, parameters=body)


def delete_databricks_workspace(cmd, client,
                                resource_group,
                                name):
    return client.delete(resource_group_name=resource_group, workspace_name=name)


def get_databricks_workspace(cmd, client,
                             resource_group,
                             name):
    return client.get(resource_group_name=resource_group, workspace_name=name)


def list_databricks_workspace(cmd, client,
                              resource_group=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list_by_subscription()


def list_databricks_operation(cmd, client):
    return client.list()
