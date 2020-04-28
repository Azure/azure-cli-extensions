# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import threading

from azure.cli.core import AzCommandsLoader

from azext_ai_did_you_mean_this._help import helps  # pylint: disable=unused-import
from azext_ai_did_you_mean_this._check_for_updates import is_cli_up_to_date


def inject_functions_into_core():
    from azure.cli.core.parser import AzCliCommandParser
    from azext_ai_did_you_mean_this.custom import recommend_recovery_options
    AzCliCommandParser.recommendation_provider = recommend_recovery_options


def check_if_up_to_date_in_background(*args, **kwargs):
    worker = threading.Thread(target=is_cli_up_to_date, args=args, kwargs=kwargs)
    worker.daemon = True
    worker.start()


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
