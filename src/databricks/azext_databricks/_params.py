# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_databricks.action import (
    PeeringAddAuthorizations
)


def load_arguments(self, _):

    with self.argument_context('databricks workspace create') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the workspace.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('managed_resource_group_id', id_part=None, help='The managed resource group Id.')
        c.argument('aml_workspace_id_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('aml_workspace_id_value', id_part=None, help='The value which should be used for this field.')
        c.argument('custom_virtual_network_id_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('custom_virtual_network_id_value', id_part=None, help='The value which should be used for this field.')
        c.argument('custom_public_subnet_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('custom_public_subnet_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('custom_private_subnet_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('custom_private_subnet_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('enable_no_public_ip_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('enable_no_public_ip_value', arg_type=get_three_state_flag(), id_part=None, help='The value which should be used for this field.')
        c.argument('load_balancer_backend_pool_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('load_balancer_backend_pool_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('load_balancer_id_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('load_balancer_id_value', id_part=None, help='The value which should be used for this field.')
        c.argument('relay_namespace_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('relay_namespace_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('storage_account_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('storage_account_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('storage_account_sku_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('storage_account_sku_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('resource_tags_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('resource_tags_value', id_part=None, help='The value which should be used for this field.')
        c.argument('vnet_address_prefix_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('vnet_address_prefix_value', id_part=None, help='The value which should be used for this field.')
        c.argument('ui_definition_uri', id_part=None, help='The blob URI where the UI definition file is located.')
        c.argument('authorizations', id_part=None, help='The workspace provider authorizations.', action=PeeringAddAuthorizations, nargs='+')
        c.argument('sku_name', id_part=None, help='The SKU name.')
        c.argument('sku_tier', id_part=None, help='The SKU tier.')

    with self.argument_context('databricks workspace update') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the workspace.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('managed_resource_group_id', id_part=None, help='The managed resource group Id.')
        c.argument('aml_workspace_id_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('aml_workspace_id_value', id_part=None, help='The value which should be used for this field.')
        c.argument('custom_virtual_network_id_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('custom_virtual_network_id_value', id_part=None, help='The value which should be used for this field.')
        c.argument('custom_public_subnet_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('custom_public_subnet_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('custom_private_subnet_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('custom_private_subnet_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('enable_no_public_ip_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('enable_no_public_ip_value', arg_type=get_three_state_flag(), id_part=None, help='The value which should be used for this field.')
        c.argument('load_balancer_backend_pool_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('load_balancer_backend_pool_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('load_balancer_id_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('load_balancer_id_value', id_part=None, help='The value which should be used for this field.')
        c.argument('relay_namespace_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('relay_namespace_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('storage_account_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('storage_account_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('storage_account_sku_name_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('storage_account_sku_name_value', id_part=None, help='The value which should be used for this field.')
        c.argument('resource_tags_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('resource_tags_value', id_part=None, help='The value which should be used for this field.')
        c.argument('vnet_address_prefix_type', arg_type=get_enum_type(['Bool', 'Object', 'String']), id_part=None, help='The type of variable that this is')
        c.argument('vnet_address_prefix_value', id_part=None, help='The value which should be used for this field.')
        c.argument('ui_definition_uri', id_part=None, help='The blob URI where the UI definition file is located.')
        c.argument('authorizations', id_part=None, help='The workspace provider authorizations.', action=PeeringAddAuthorizations, nargs='+')
        c.argument('sku_name', id_part=None, help='The SKU name.')
        c.argument('sku_tier', id_part=None, help='The SKU tier.')

    with self.argument_context('databricks workspace delete') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the workspace.')

    with self.argument_context('databricks workspace show') as c:
        c.argument('resource_group', resource_group_name_type)
        c.argument('name', id_part=None, help='The name of the workspace.')

    with self.argument_context('databricks workspace list') as c:
        c.argument('resource_group', resource_group_name_type)
