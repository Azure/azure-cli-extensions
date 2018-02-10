# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

# pylint: disable=unused-import
# pylint: disable=line-too-long

from ._help import helps


class RelayCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        relay_custom = CliCommandType(operations_tmpl='azext_relay.custom#{}')
        super(RelayCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=relay_custom, min_profile="2017-03-10-profile")

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from ._params import load_arguments_relayparams
        load_arguments_relayparams(self, command)


COMMAND_LOADER_CLS = RelayCommandsLoader
