# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core import AzCommandsLoader
from ._validators import validate_name


class HackExtCommandLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        hack_custom = CliCommandType(operations_tmpl='azext_hack.custom#{}')
        super(HackExtCommandLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=hack_custom)

    def load_command_table(self, _):
        with self.command_group('hack') as g:
            g.custom_command('up', 'hack_up')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('hack up') as c:
            c.argument('name',
                       options_list=['--name', '-n'],
                       help='Name of resources',
                       validator=validate_name,
                       type=str.lower)
            c.argument('database',
                       options_list=['--database', '-d'],
                       help='Database type - { sql | mysql | cosmosdb }',
                       choices=['sql', 'mysql', 'cosmosdb'],
                       default='sql',
                       type=str.lower)
            c.argument('runtime',
                       options_list=['--runtime', '-r'],
                       help='Runtime',
                       choices=['php', 'node', 'tomcat',
                                'jetty', 'python', 'aspnet'],
                       type=str.lower)
            c.argument('ai',
                       help='Enable Azure Cognitive Services',
                       options_list=['--ai', '-ai'],
                       default=None,
                       action='store_true')


COMMAND_LOADER_CLS = HackExtCommandLoader
