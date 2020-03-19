# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from argcomplete.completers import FilesCompleter
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    file_type,
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_logic.action import (
    AddIntegrationAccount,
    AddIntegrationServiceEnvironment,
    AddDefinition,
    AddSku,
    AddKeyVault
)


def load_arguments(self, _):

    with self.argument_context('logic workflow list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.')

    with self.argument_context('logic workflow show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The workflow name.')

    with self.argument_context('logic workflow create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The workflow name.')
        c.argument('input_path', type=file_type, help='Path to a workflow JSON file', completer=FilesCompleter())
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='The resource location.')
        c.argument('tags', tags_type, help='The resource tags.')

    with self.argument_context('logic workflow update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The workflow name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='The resource location.')
        c.argument('tags', tags_type, help='The resource tags.')

    with self.argument_context('logic workflow delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The workflow name.')

    with self.argument_context('logic integration-account list') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('top', help='The number of items to be included in the result.')

    with self.argument_context('logic integration-account show') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The integration account name.')

    with self.argument_context('logic integration-account create') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The integration account name.')
        c.argument('input_path', type=file_type, help='Path to a intergration-account JSON file', completer=FilesCompleter())
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help='The resource location.')
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('sku', type=str, help='The integration account sku.')

    with self.argument_context('logic integration-account update') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('name', help='The integration account name.')
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('sku', type=str, help='The integration account sku.')

    with self.argument_context('logic integration-account delete') as c:
        c.argument('resource_group_name', resource_group_name_type, help='The resource group name.')
        c.argument('_name', help='The integration account name.')
