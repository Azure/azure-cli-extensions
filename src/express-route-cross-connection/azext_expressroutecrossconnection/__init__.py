# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

import azext_expressroutecrossconnection._help  # pylint: disable=unused-import


class ExpressRouteCrossConnectionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        super(ExpressRouteCrossConnectionCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=CliCommandType(operations_tmpl='azext_expressroutecrossconnection.custom#{}')
        )

    def load_command_table(self, _):
        from azext_expressroutecrossconnection.commands import load_command_table
        return self.load_command_table()

    def load_arguments(self, _):
        from azext_expressroutecrossconnection._params import load_arguments
        return self.load_arguments()
        

COMMAND_LOADER_CLS = ExpressRouteCrossConnectionCommandsLoader
