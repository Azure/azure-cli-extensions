# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_asc._help import helps  # pylint: disable=unused-import


class AscCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_asc._client_factory import cf_asc
        asc_custom = CliCommandType(
            operations_tmpl='azext_asc.custom#{}',
            client_factory=cf_asc)
        super(AscCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=asc_custom)

    def load_command_table(self, args):
        from azext_asc.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_asc._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = AscCommandsLoader
