# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.help_files import helps

helps['?'] = """
    type: command
    short-summary: Ask a question about Azure CLI.
    parameters:
        - query: -q
          type: string
          short-summary: Question to ask Aladdin.
"""

class AladdinCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        processquery_custom = CliCommandType(
            operations_tmpl='azext_aladdin.custom#{}')
        super(AladdinCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=processquery_custom)
        #print(cli_ctx.__dict__)
        #print(cli_ctx.invocation.parser = newParser)

    def load_command_table(self, args):
        with self.command_group('?') as g:
            #print(args)
            g.custom_command('', 'processquery')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('?') as c:
            c.argument('query', options_list=['-q'], help='Question to ask Aladdin.')

COMMAND_LOADER_CLS = AladdinCommandsLoader
