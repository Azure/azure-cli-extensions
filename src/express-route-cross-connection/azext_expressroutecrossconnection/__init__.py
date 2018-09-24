# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader
from azure.cli.core.profiles import register_resource_type

import azext_expressroutecrossconnection._help  # pylint: disable=unused-import


class ExpressRouteCrossConnectionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from .profiles import CUSTOM_ER_CC
        register_resource_type('latest', CUSTOM_ER_CC, '2018-04-01')
        super(ExpressRouteCrossConnectionCommandsLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=CliCommandType(operations_tmpl='azext_expressroutecrossconnection.custom#{}'),
            resource_type=CUSTOM_ER_CC
        )

    def load_command_table(self, args):
        from .commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, args):
        from ._params import load_arguments
        load_arguments(self, args)


COMMAND_LOADER_CLS = ExpressRouteCrossConnectionCommandsLoader
