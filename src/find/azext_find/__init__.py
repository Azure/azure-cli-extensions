# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.help_files import helps

helps['find'] = """
    type: command
    short-summary: Ask a question about Azure CLI.
"""


class FindCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        processquery_custom = CliCommandType(
            operations_tmpl='azext_find.custom#{}')
        super(FindCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=processquery_custom)
        # print(cli_ctx.__dict__)
        # print(cli_ctx.invocation.parser = newParser)

    def load_command_table(self, _):
        with self.command_group('') as g:
            # print(args) #passed as argument
            g.custom_command('find', 'processquery')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('find') as c:
            c.argument('question', options_list=['-q', '--question'], help='Questions about Azure CLI commands.')


COMMAND_LOADER_CLS = FindCommandsLoader
