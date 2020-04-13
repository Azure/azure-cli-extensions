# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_ai_did_you_mean_this._help import helps  # pylint: disable=unused-import

def inject_functions_into_core():
    from azure.cli.core.parser import AzCliCommandParser
    from azext_ai_did_you_mean_this.custom import recommend_recovery_options
    AzCliCommandParser.recommendation_provider = recommend_recovery_options

class AiDidYouMeanThisCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        ai_did_you_mean_this_custom = CliCommandType(
            operations_tmpl='azext_ai_did_you_mean_this.custom#{}')
        super(AiDidYouMeanThisCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                             custom_command_type=ai_did_you_mean_this_custom)

        inject_functions_into_core()

    def load_command_table(self, args):
        from azext_ai_did_you_mean_this.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = AiDidYouMeanThisCommandsLoader
