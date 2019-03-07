# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core import AzCommandsLoader
import azext_mixed_reality._help  # pylint: disable=unused-import


class MixedRealityCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_command_type = CliCommandType(operations_tmpl='azext_mixed_reality.custom#{}')
        super(MixedRealityCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=custom_command_type)  # pylint: disable=line-too-long

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = MixedRealityCommandsLoader
