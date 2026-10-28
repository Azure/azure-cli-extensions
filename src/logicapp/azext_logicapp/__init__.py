# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import,import-outside-toplevel,import-error,no-name-in-module

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import CliCommandType
from azure.cli.core.profiles import ResourceType

import azext_logicapp._help


class LogicAppExtCommandLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        logicapp_custom = CliCommandType(operations_tmpl='azext_logicapp.custom#{}')
        super(LogicAppExtCommandLoader, self).__init__(
            cli_ctx=cli_ctx,
            custom_command_type=logicapp_custom,
            resource_type=ResourceType.MGMT_APPSERVICE)

    def load_command_table(self, args):
        from azext_logicapp.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, args):
        from azext_logicapp._params import load_arguments
        load_arguments(self, args)


COMMAND_LOADER_CLS = LogicAppExtCommandLoader
