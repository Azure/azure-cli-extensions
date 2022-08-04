# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azext_communication.manual._client_factory import cf_communication_identity
from azext_communication.manual._client_factory import cf_communication_sms
from azext_communication.manual._client_factory import cf_communication_phonenumbers
from azext_communication.manual._client_factory import cf_communication_chat


def load_command_table(self, _):

    identity_arguments = ['connection_string']
    with self.command_group('communication identity', client_factory=cf_communication_identity, is_preview=True) as g:
        g.communication_custom_command('issue-access-token', "communication_issue_access_token", identity_arguments, client_factory=cf_communication_identity)
        g.communication_custom_command('revoke-access-tokens', "communication_revoke_access_tokens", identity_arguments, client_factory=cf_communication_identity)

    sms_arguments = ['connection_string']
    with self.command_group('communication sms', client_factory=cf_communication_sms, is_preview=True) as g:
        g.communication_custom_command('send-sms', 'communication_send_sms', sms_arguments)

    phonenumber_arguments = ['connection_string']
    with self.command_group('communication phonenumbers', client_factory=cf_communication_phonenumbers, is_preview=True) as g:
        g.communication_custom_command('list-phonenumbers', 'communication_list_phonenumbers', phonenumber_arguments)
        g.communication_custom_command('show-phonenumber', 'communication_show_phonenumber', phonenumber_arguments)

    chat_arguments = ['endpoint', 'access_token']
    with self.command_group('communication chat', client_factory=cf_communication_chat, is_preview=True) as g:
        # thread management
        g.communication_custom_command('list-threads', 'communication_chat_list_threads', chat_arguments)
        g.communication_custom_command('create-thread', 'communication_chat_create_thread', chat_arguments)
        g.communication_custom_command('delete-thread', 'communication_chat_delete_thread', chat_arguments)

        # participant management
        g.communication_custom_command('list-participants', 'communication_chat_list_participants', chat_arguments)
        g.communication_custom_command('add-participant', 'communication_chat_add_participant', chat_arguments)
        g.communication_custom_command('remove-participant', 'communication_chat_remove_participant', chat_arguments)

        # message management
        g.communication_custom_command('list-messages', 'communication_chat_list_messages', chat_arguments)
        g.communication_custom_command('send-message', 'communication_chat_send_message', chat_arguments)
        g.communication_custom_command('get-message', 'communication_chat_get_message', chat_arguments)
        g.communication_custom_command('update-message', 'communication_chat_update_message', chat_arguments)
        g.communication_custom_command('delete-message', 'communication_chat_delete_message', chat_arguments)
        g.communication_custom_command('update-topic', 'communication_chat_update_topic', chat_arguments)
        g.communication_custom_command('list-read-receipts', 'communication_chat_list_read_receipts', chat_arguments)
        g.communication_custom_command('send-read-receipt', 'communication_chat_send_read_receipt', chat_arguments)
