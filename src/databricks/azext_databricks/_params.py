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
from ._validators import validate_encryption_values


def load_arguments(self, _):

    with self.argument_context('databricks workspace create') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], help='The name of the workspace.')
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('managed_resource_group', help='The managed resource group to create. It can be either a name or a resource ID.')
        c.argument('custom_virtual_network_id', options_list=['--vnet'], arg_group='Custom VNET', help='Virtual Network name or resource ID.')
        c.argument('custom_public_subnet_name', options_list=['--public-subnet'], arg_group='Custom VNET', help='The name of a Public Subnet within the Virtual Network.')
        c.argument('custom_private_subnet_name', options_list=['--private-subnet'], arg_group='Custom VNET', help='The name of a Private Subnet within the Virtual Network.')
        c.argument('sku_name', options_list=['--sku'], arg_type=get_enum_type(['standard', 'premium', 'trial']), help='The SKU tier name.')
        c.argument('prepare_encryption', action='store_true', help='Flag to enable the Managed Identity for managed storage account to prepare for CMK encryption.')

    with self.argument_context('databricks workspace update') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')
        c.argument('tags', tags_type)
        c.argument('prepare_encryption', action='store_true', help='Flag to enable the Managed Identity for managed storage account to prepare for CMK encryption.')
        c.argument('encryption_key_source', options_list=['--key-source'], arg_group='Encryption', arg_type=get_enum_type(['Default', 'Microsoft.Keyvault']), validator=validate_encryption_values, help='The encryption key source (provider).')
        c.argument('encryption_key_name', options_list=['--key-name'], arg_group='Encryption', help='The name of KeyVault key.')
        c.argument('encryption_key_version', options_list=['--key-version'], arg_group='Encryption', help='The version of KeyVault key.')
        c.argument('encryption_key_vault', options_list=['--key-vault'], arg_group='Encryption', help='The Uri of KeyVault.')

    with self.argument_context('databricks workspace delete') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')

    with self.argument_context('databricks workspace show') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')

    with self.argument_context('databricks workspace list') as c:
        pass

    with self.argument_context('databricks workspace wait') as c:
        c.argument('workspace_name', options_list=['--name', '-n'], id_part='name', help='The name of the workspace.')
