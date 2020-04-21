# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type
)

from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    with self.argument_context('databricks workspace create') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], help='The name of the workspace.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('managed_resource_group', help='The managed resource group to create. It can be either a name or a resource ID.')
        c.argument('custom_virtual_network_id', options_list=['--vnet'], arg_group='Custom VNET', help='Virtual network name or resource ID.')
        c.argument('custom_public_subnet_name', options_list=['--public-subnet'], arg_group='Custom VNET', help='The name of a new public subnet.')
        c.argument('custom_private_subnet_name', options_list=['--private-subnet'], arg_group='Custom VNET', help='The name of a new private subnet.')
        c.argument('sku_name', options_list=['--sku'], arg_type=get_enum_type(['standard', 'premium', 'trial']), help='The SKU tier name.')

    with self.argument_context('databricks workspace update') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')
        c.argument('tags', tags_type)

    with self.argument_context('databricks workspace delete') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')

    with self.argument_context('databricks workspace show') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')

    with self.argument_context('databricks workspace list') as c:
        pass

    with self.argument_context('databricks workspace wait') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')
