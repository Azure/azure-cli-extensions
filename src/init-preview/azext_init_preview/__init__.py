# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from ._help import helps  # pylint: disable=unused-import


class InitCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        super(InitCommandsLoader, self).__init__(cli_ctx=cli_ctx
                                                 )

    def load_command_table(self, args):
        from azure.cli.core.commands import CliCommandType

        custom_init = CliCommandType(operations_tmpl='azext_init_preview.custom#{}')

        with self.command_group('storage', custom_init) as g:
            g.command('init', 'storage_init', is_preview=True)

        return self.command_table


COMMAND_LOADER_CLS = InitCommandsLoader
