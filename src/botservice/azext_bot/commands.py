# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.command_modules.botservice._client_factory import (
    get_botservice_management_client)
from azure.cli.command_modules.botservice._exception_handler import bot_exception_handler


def load_command_table(self, _):
    botOperations_commandType = CliCommandType(
        operations_tmpl='azext_bot.botservice.operations.bots_operations#BotsOperations.{}',
        client_factory=get_botservice_management_client,
        exception_handler=bot_exception_handler
    )

    with self.command_group('bot', botOperations_commandType) as g:
        g.custom_command('publish', 'publish_app')
