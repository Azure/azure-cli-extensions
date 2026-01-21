# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azext_acrcache._help import helps  # pylint: disable=unused-import


class AcrcacheCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_acrcache._client_factory import cf_acrcache
        acrcache_custom = CliCommandType(
            operations_tmpl='azext_acrcache.cache#{}',
            client_factory=cf_acrcache,
            help_file='azext_acrcache._help',)
        super().__init__(cli_ctx=cli_ctx, custom_command_type=acrcache_custom)

    def load_command_table(self, args):
        from azext_acrcache.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_acrcache._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AcrcacheCommandsLoader
