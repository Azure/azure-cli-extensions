# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
)
from azext_portal.action import AddMetadata


def load_arguments(self, _):

    with self.argument_context('portal dashboard list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group.')

    with self.argument_context('portal dashboard show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group.')
        c.argument('name', help='The name of the dashboard.')

    with self.argument_context('portal dashboard create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group.')
        c.argument('name', help='The name of the dashboard.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='Resource location')
        c.argument('tags', tags_type, help='Resource tags')
        c.argument('properties_lenses', arg_type=CLIArgumentType(options_list=['--properties-lenses'], help='The dashboard lenses.'))
        c.argument('properties_metadata', action=AddMetadata, nargs='+', help='The dashboard metadata.')

    with self.argument_context('portal dashboard update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group.')
        c.argument('name', help='The name of the dashboard.')
        c.argument('tags', tags_type, help='Resource tags')
        c.argument('properties_lenses', arg_type=CLIArgumentType(options_list=['--properties-lenses'], help='The dashboard lenses.'))
        c.argument('properties_metadata', action=AddMetadata, nargs='+', help='The dashboard metadata.')

    with self.argument_context('portal dashboard delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The name of the resource group.')
        c.argument('name', help='The name of the dashboard.')
