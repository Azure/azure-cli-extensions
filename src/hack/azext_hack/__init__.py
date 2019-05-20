# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.command_modules.appservice.commands import ex_handler_factory

class HackExtCommandLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        hack_custom = CliCommandType(operations_tmpl='azext_hack.custom#{}')
        super(HackExtCommandLoader, self).__init__(cli_ctx=cli_ctx,
                                                   custom_command_type=hack_custom,
                                                   min_profile="2017-03-10-profile")
    
    def load_command_table(self, _):
        with self.command_group('hack') as g:
            g.custom_command('up', 'hack_up', exception_handler=ex_handler_factory())
        return self.command_table
    
    def load_arguments(self, _):
        with self.argument_context('hack up') as c:
            c.argument('name', options_list=['--name', '-n'], help='Name of resources')

COMMAND_LOADER_CLS = HackExtCommandLoader
