# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_bot._client_factory import (
    get_botservice_management_client,
    get_botChannels_client)
from azext_bot._exception_handler import bot_exception_handler


def load_command_table(self, _):
    botOperations_commandType = CliCommandType(
        operations_tmpl='azext_bot.botservice.operations.bots_operations#BotsOperations.{}',  # pylint: disable=line-too-long
        client_factory=get_botservice_management_client,
        exception_handler=bot_exception_handler
    )

    channelOperations_commandType = CliCommandType(
        operations_tmpl='azext_bot.custom#channelOperationsInstance.{}',  # pylint: disable=line-too-long
        client_factory=get_botChannels_client,
        exception_handler=bot_exception_handler
    )

    updateBotService_commandType = CliCommandType(
        operations_tmpl='azext_bot.custom#{}',
        client_factory=get_botservice_management_client,
        exception_handler=bot_exception_handler
    )

    with self.command_group('bot', botOperations_commandType) as g:
        g.custom_command('create', 'create')
        g.custom_command('publish', 'publish_app')
        g.custom_command('download', 'download_app')
        g.custom_command('show', 'get_bot')
        g.custom_command('delete', 'delete_bot')
        g.generic_update_command('update', setter_name='update', setter_type=updateBotService_commandType)

    with self.command_group('bot connection', botOperations_commandType) as g:
        g.custom_command('list', 'get_connections')
        g.custom_command('show', 'get_connection')
        g.custom_command('create', 'create_connection')
        g.custom_command('delete', 'delete_connection')
        g.custom_command('list-providers', 'get_service_providers')

    for channel in ['facebook', 'email', 'msteams', 'skype', 'kik', 'webchat', 'directline', 'telegram', 'sms',
                    'slack']:
        with self.command_group('bot {}'.format(channel), channelOperations_commandType) as g:
            g.custom_command('create', '{}_create'.format(channel))
            g.command('show', '{}_get'.format(channel))
            g.command('delete', '{}_delete'.format(channel))
