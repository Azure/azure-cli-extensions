# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    resource_group_name_type,
    get_enum_type,
    get_three_state_flag,
    tags_type)

name_arg_type = CLIArgumentType(metavar='NAME', configured_default='botname')


# pylint: disable=line-too-long,too-many-statements
def load_arguments(self, _):
    with self.argument_context('bot') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type)
        c.argument('resource_name', options_list=['--name', '-n'], help='the Resource Name of the bot.', arg_type=name_arg_type)

    with self.argument_context('bot create') as c:
        c.argument('sku_name', options_list=['--sku'], arg_type=get_enum_type(['F0', 'S1']), help='The Sku of the bot.', arg_group='Registration bot Specific')
        c.argument('kind', options_list=['--kind', '-k'], arg_type=get_enum_type(['registration', 'function', 'webapp']), help='The kind of the bot.')
        c.argument('display_name', help='The display name of the bot. If not specified, defaults to the name of the bot.', arg_group='Registration bot Specific')
        c.argument('description', options_list=['--description', '-d'], help='The description of the bot.', arg_group='Registration bot Specific')
        c.argument('endpoint', options_list=['-e', '--endpoint'], help='The messaging endpoint of the bot.', arg_group='Registration bot Specific')
        c.argument('msa_app_id', options_list=['--appid'], help='The Microsoft account ID (MSA ID) to be used with the bot.')
        c.argument('password', options_list=['-p', '--password'], help='The Microsoft account (MSA) password for the bot.')
        c.argument('storageAccountName', options_list=['-s', '--storage'], help='Storage account name to be used with the bot. If not provided, a new account will be created.', arg_group='Web/Function bot Specific')
        c.argument('tags', arg_type=tags_type)
        c.argument('language', help='The language to be used to create the bot.', options_list=['--lang'], arg_type=get_enum_type(['Csharp', 'Node']), arg_group='Web/Function bot Specific')
        c.argument('appInsightsLocation', help='The location for the app insights to be used with the bot.', options_list=['--insights-location'], arg_group='Web/Function bot Specific',
                   arg_type=get_enum_type(['South Central US', 'East US', 'West US 2', 'North Europe', 'West Europe', 'Southeast Asia']))
        c.argument('version', options_list=['-v', '--version'], help='The Microsoft Bot Builder SDK version to be used to create the bot', arg_type=get_enum_type(['v3', 'v4']), arg_group='Web/Function bot Specific')

    with self.argument_context('bot show') as c:
        c.argument('bot_json', options_list=['--msbot'], help='Show the output as JSON compatible with a .bot file.', arg_type=get_three_state_flag())

    with self.argument_context('bot publish') as c:
        c.argument('code_dir', options_list=['--code-dir'], help='The directory to upload bot code from.')
        c.argument('proj_file', options_list=['--proj-file'], help='The startup project file name (without the .csproj) that needs to be published. Eg: EnterpriseBot.')
        c.argument('sdk_version', options_list=['--sdk-version'], help='The Microsoft Bot Builder SDK version.', arg_type=get_enum_type(['v3', 'v4']))
