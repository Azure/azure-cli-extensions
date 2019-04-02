# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
 
from knack.help_files import helps

from azure.cli.core import AzCommandsLoader


class HelloWorldCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_vm_repair#{}')
        super(HelloWorldCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                       custom_command_type=custom_type)

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, _):
        pass

COMMAND_LOADER_CLS = HelloWorldCommandsLoader
