# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
# pylint: disable=unused-import
import azext_db_up._help


class RdbmsUpCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        db_up_custom = CliCommandType(
            operations_tmpl='azext_db_up.custom#{}')
        super(RdbmsUpCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=db_up_custom,
                                                    min_profile="2017-03-10-profile")

    def load_command_table(self, args):
        super(RdbmsUpCommandsLoader, self).load_command_table(args)
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        super(RdbmsUpCommandsLoader, self).load_arguments(command)
        from ._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = RdbmsUpCommandsLoader
