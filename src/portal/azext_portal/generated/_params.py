# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type,
    file_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    with self.argument_context('portal dashboard list') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The name of the resource group.')

    with self.argument_context('portal dashboard show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('name', options_list=[
                   '--name', '-n'], help='The name of the dashboard.')

    with self.argument_context('portal dashboard create') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The name of the resource group.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The name of the dashboard.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('input_path', type=file_type,
                   help='The path to the dashboard properties JSON file.', completer=FilesCompleter())

    with self.argument_context('portal dashboard update') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The name of the resource group.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The name of the dashboard.')
        c.argument('input_path', type=file_type,
                   help='The path to the dashboard properties JSON file.', completer=FilesCompleter())

    with self.argument_context('portal dashboard delete') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The name of the resource group.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The name of the dashboard.')

    with self.argument_context('portal dashboard import') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The name of the resource group.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The name of the dashboard.')
        c.argument('input_path', type=file_type,
                   help='The path to the dashboard json file.', completer=FilesCompleter())
