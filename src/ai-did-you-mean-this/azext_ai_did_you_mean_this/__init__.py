# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from knack.events import (
    EVENT_INVOKER_CMD_TBL_LOADED
)

from azext_ai_did_you_mean_this._help import helps  # pylint: disable=unused-import
from azext_ai_did_you_mean_this._cmd_table import on_command_table_loaded
from azext_ai_did_you_mean_this._cli_ctx import on_extension_loaded


def inject_functions_into_core():
    from azure.cli.core.parser import AzCliCommandParser
    from azext_ai_did_you_mean_this.custom import recommend_recovery_options
    AzCliCommandParser.recommendation_provider = recommend_recovery_options


class AiDidYouMeanThisCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        ai_did_you_mean_this_custom = CliCommandType(
            operations_tmpl='azext_ai_did_you_mean_this.custom#{}')
        super().__init__(cli_ctx=cli_ctx,
                         custom_command_type=ai_did_you_mean_this_custom)
        self.cli_ctx.register_event(EVENT_INVOKER_CMD_TBL_LOADED, on_command_table_loaded)
        inject_functions_into_core()

    def load_command_table(self, args):
        from azext_ai_did_you_mean_this.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = AiDidYouMeanThisCommandsLoader
