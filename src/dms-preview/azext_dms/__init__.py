# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_dms._help  # pylint: disable=unused-import


class DmsCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azure.cli.command_modules.dms.commands import dms_api_exception_handler
        dms_custom = CliCommandType(operations_tmpl='azext_dms.custom#{}',
                                    exception_handler=dms_api_exception_handler)
        super(DmsCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                custom_command_type=dms_custom)

    def load_command_table(self, args):
        from azext_dms.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_dms._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = DmsCommandsLoader
