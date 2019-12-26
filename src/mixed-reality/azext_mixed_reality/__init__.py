# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_mixed_reality._help import helps  # pylint: disable=unused-import


class MixedRealityClientCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_mixed_reality._client_factory import cf_mixed_reality
        mixed_reality_custom = CliCommandType(
            operations_tmpl='azext_mixed_reality.custom#{}',
            client_factory=cf_mixed_reality)
        super(MixedRealityClientCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                               custom_command_type=mixed_reality_custom)

    def load_command_table(self, args):
        from azext_mixed_reality.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_mixed_reality._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = MixedRealityClientCommandsLoader
