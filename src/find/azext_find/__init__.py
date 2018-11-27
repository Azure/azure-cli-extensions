# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from knack.help_files import helps

helps['find'] = """
    type: command
    short-summary: I'm an AI robot, my advice is based on our Azure documentation as well as the usage patterns of Azure CLI and Azure ARM users. Using me improves Azure products and documentation.
    examples:
        - name: Give me any Azure CLI command or group and I’ll show the most popular commands and parameters.
          text: |
            az find 'az [group]'           : az find 'az storage'
            az find 'az [group] [command]' : az find 'az monitor activity-log list'
        - name: You can also enter a search term, and I'll try to help find the best commands.
          text: |
            az find '[query]' : az find 'arm template'
"""


class FindCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        process_query_custom = CliCommandType(
            operations_tmpl='azext_find.custom#{}')
        super(FindCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=process_query_custom)

    def load_command_table(self, _):
        with self.command_group('') as g:
            g.custom_command('find', 'process_query')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('find') as c:
            c.positional('cli_term', help='An Azure CLI command or group for which you need an example.')


COMMAND_LOADER_CLS = FindCommandsLoader
