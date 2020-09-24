# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from argcomplete.completers import FilesCompleter
from knack.arguments import CLIArgumentType
from azure.cli.core.commands.validators import validate_file_or_dict, get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azext_logic.action import AddIntegrationAccount, AddIntegrationServiceEnvironment


def load_arguments(self, _):

    with self.argument_context('logic workflow list') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument(
            'top', help='The number of items to be included in the result.')
        c.argument('filter', help='The filter to apply on the operation. Options for filters include: State, Trigger, a'
                   'nd ReferencedResourceId.')

    with self.argument_context('logic workflow show') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The workflow name.')

    with self.argument_context('logic workflow create') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The workflow name.')
        c.argument('definition', type=validate_file_or_dict, help='Path to a workflow defintion JSON file (see README.md for more info on this). ' +
                   'This JSON format should match what the logic app design tool exports', completer=FilesCompleter())
        c.argument('location', arg_type=get_location_type(
            self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('integration_account', action=AddIntegrationAccount,
                   nargs='+', help='The integration account.')
        c.argument('integration_service_environment', action=AddIntegrationServiceEnvironment,
                   nargs='+', help='The integration service environment.')
        c.argument('endpoints_configuration', arg_type=CLIArgumentType(options_list=['--endpoints-configuration'],
                                                                       help='The endpoints configuration.'))
        c.argument('access_control', arg_type=CLIArgumentType(options_list=['--access-control'], help='The access contr'
                                                              'ol configuration controls access to this workflow. See README.md for more information'))
        c.argument('state', arg_type=get_enum_type(['NotSpecified', 'Completed', 'Enabled', 'Disabled', 'Deleted', 'Sus'
                                                    'pended']), help='The state.')
        c.argument('tags', tags_type, help='The resource tags.')

    with self.argument_context('logic workflow update') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The workflow name.')
        c.argument('state', arg_type=get_enum_type(['NotSpecified', 'Completed', 'Enabled', 'Disabled', 'Deleted', 'Sus'
                                                    'pended']), help='The state.')
        c.argument('definition', type=validate_file_or_dict, help='Path to a workflow defintion JSON file (see README.md for more info on this). ' +
                   'This JSON format should match what the logic app design tool exports', completer=FilesCompleter())
        c.argument('tags', tags_type, help='The resource tags.')

    with self.argument_context('logic workflow delete') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The workflow name.')

    with self.argument_context('logic integration-account list') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument(
            'top', help='The number of items to be included in the result.')

    with self.argument_context('logic integration-account show') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The integration account name.')

    with self.argument_context('logic integration-account create') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The integration account name.')
        c.argument('location', arg_type=get_location_type(
            self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('sku', type=str, help='The integration account sku.')
        c.argument('integration_service_environment', arg_type=CLIArgumentType(options_list=['--integration-service-env'
                                                                                             'ironment'], help='The integration se'
                                                                               'rvice environment. See README.md For more information'))
        c.argument('state', arg_type=get_enum_type(['NotSpecified', 'Completed', 'Enabled', 'Disabled', 'Deleted', 'Sus'
                                                    'pended']), help='The workflow state.')

    with self.argument_context('logic integration-account update') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The integration account name.')
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('sku', type=str, help='The integration account sku.')
        c.argument('integration_service_environment', arg_type=CLIArgumentType(options_list=['--integration-service-env'
                                                                                             'ironment'], help='The integration se'
                                                                               'rvice environment. See README.md For more information'))
        c.argument('state', arg_type=get_enum_type(['NotSpecified', 'Completed', 'Enabled', 'Disabled', 'Deleted', 'Sus'
                                                    'pended']), help='The workflow state.')

    with self.argument_context('logic integration-account delete') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The integration account name.')

    with self.argument_context('logic integration-account import') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help='The resource group name.')
        c.argument('name', options_list=[
                   '--name', '-n'], help='The integration account name.')
        c.argument('input_path', type=validate_file_or_dict,
                   help='Path to a intergration-account JSON file', completer=FilesCompleter())
        c.argument('location', arg_type=get_location_type(
            self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type, help='The resource tags.')
        c.argument('sku', type=str, help='The integration account sku.')
