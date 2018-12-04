# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_enum_type)

name_arg_type = CLIArgumentType(metavar='NAME', configured_default='botname')


def load_arguments(self, _):
    with self.argument_context('bot') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('resource_name', options_list=['--name', '-n'], help='the Resource Name of the bot.',
                   arg_type=name_arg_type)

    with self.argument_context('bot publish') as c:
        c.argument('code_dir', options_list=['--code-dir'], help='The directory to upload bot code from.')
        c.argument('proj_name', options_list=['--proj-file'], help='The startup project file name (without the .csproj)'
                                                                   ' that needs to be published. Eg: EnterpriseBot.')
        c.argument('version', options_list=['-v', '--version'], help='The Microsoft Bot Builder SDK version.',
                   arg_type=get_enum_type(['v3', 'v4']))
