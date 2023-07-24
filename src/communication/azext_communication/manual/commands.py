# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azext_communication.manual._client_factory import cf_communication_identity
from azext_communication.manual._client_factory import cf_communication_sms
from azext_communication.manual._client_factory import cf_communication_phonenumbers
from azext_communication.manual._client_factory import cf_communication_chat
from azext_communication.manual._client_factory import cf_communication_rooms
from azext_communication.manual._client_factory import cf_communication_email


def load_command_table(self, _):
    _load_identity_token_command_table(self)
    _load_sms_command_table(self)
    _load_phonenumber_command_table(self)
    _load_chat_command_table(self)
    _load_rooms_command_table(self)
    _load_email_command_table(self)


def _load_identity_token_command_table(self):
    identity_arguments = ['connection_string']

    with self.command_group('communication identity user', client_factory=cf_communication_identity,
                            deprecate_info=self.deprecate(target='communication identity user', redirect='communication user-identity user')) as g:
        g.communication_custom_command('create', "communication_identity_create_user", identity_arguments)
        g.communication_custom_command('delete', "communication_identity_delete_user", identity_arguments, confirmation=True)

    with self.command_group('communication identity token', client_factory=cf_communication_identity,
                            deprecate_info=self.deprecate(target='communication identity token', redirect='communication user-identity token')) as g:
        g.communication_custom_command('issue', "communication_identity_issue_access_token", identity_arguments)
        g.communication_custom_command('revoke', "communication_identity_revoke_access_tokens", identity_arguments, confirmation=True)
        g.communication_custom_command('get-for-teams-user', "communication_identity_get_token_for_teams_user", identity_arguments)

    with self.command_group('communication user-identity user', client_factory=cf_communication_identity, is_preview=True) as g:
        g.communication_custom_command('create', "communication_identity_create_user", identity_arguments)
        g.communication_custom_command('delete', "communication_identity_delete_user", identity_arguments, confirmation=True)

    with self.command_group('communication user-identity', client_factory=cf_communication_identity, is_preview=True) as g:
        g.communication_custom_command('issue-access-token', "communication_identity_issue_access_token", identity_arguments,
                                       deprecate_info=self.deprecate(redirect='token issue', hide=True))

    with self.command_group('communication user-identity token', client_factory=cf_communication_identity, is_preview=True) as g:
        g.communication_custom_command('issue', "communication_identity_issue_access_token", identity_arguments)
        g.communication_custom_command('revoke', "communication_identity_revoke_access_tokens", identity_arguments, confirmation=True)
        g.communication_custom_command('get-for-teams-user', "communication_identity_get_token_for_teams_user", identity_arguments)


def _load_sms_command_table(self):
    sms_arguments = ['connection_string']
    with self.command_group('communication sms', client_factory=cf_communication_sms) as g:
        g.communication_custom_command('send', 'communication_send_sms', sms_arguments, is_preview=True)
        g.communication_custom_command('send-sms', 'communication_send_sms', sms_arguments,
                                       deprecate_info=self.deprecate(redirect='send', hide=True))


def _load_phonenumber_command_table(self):
    phonenumber_arguments = ['connection_string']
    with self.command_group('communication phonenumber', client_factory=cf_communication_phonenumbers, is_preview=True) as g:
        g.communication_custom_command('list', 'communication_list_phonenumbers', phonenumber_arguments)
        g.communication_custom_command('show', 'communication_show_phonenumber', phonenumber_arguments)
    with self.command_group('communication phonenumbers', client_factory=cf_communication_phonenumbers,
                            deprecate_info=self.deprecate(redirect='phonenumber', hide=True)) as g:
        g.communication_custom_command('list-phonenumbers', 'communication_list_phonenumbers', phonenumber_arguments,
                                       deprecate_info=self.deprecate(redirect='list', hide=True))
        g.communication_custom_command('show-phonenumber', 'communication_show_phonenumber', phonenumber_arguments,
                                       deprecate_info=self.deprecate(redirect='show', hide=True))


def _load_chat_command_table(self):
    chat_arguments = ['endpoint', 'access_token']
    self.command_group('communication chat', is_preview=True)

    # thread management
    with self.command_group('communication chat thread', client_factory=cf_communication_chat, is_preview=True) as g:
        g.communication_custom_command('list', 'communication_chat_list_threads', chat_arguments)
        g.communication_custom_command('create', 'communication_chat_create_thread', chat_arguments)
        g.communication_custom_command('delete', 'communication_chat_delete_thread', chat_arguments, confirmation=True)
        g.communication_custom_command('update-topic', 'communication_chat_update_topic', chat_arguments)

    # participant management
    with self.command_group('communication chat participant', client_factory=cf_communication_chat, is_preview=True) as g:
        g.communication_custom_command('list', 'communication_chat_list_participants', chat_arguments)
        g.communication_custom_command('add', 'communication_chat_add_participant', chat_arguments)
        g.communication_custom_command('remove', 'communication_chat_remove_participant', chat_arguments, confirmation=True)

    # message management
    with self.command_group('communication chat message', client_factory=cf_communication_chat, is_preview=True) as g:
        g.communication_custom_command('list', 'communication_chat_list_messages', chat_arguments)
        g.communication_custom_command('send', 'communication_chat_send_message', chat_arguments)
        g.communication_custom_command('get', 'communication_chat_get_message', chat_arguments)
        g.communication_custom_command('update', 'communication_chat_update_message', chat_arguments)
        g.communication_custom_command('delete', 'communication_chat_delete_message', chat_arguments, confirmation=True)
    with self.command_group('communication chat message receipt', client_factory=cf_communication_chat, is_preview=True) as g:
        g.communication_custom_command('list', 'communication_chat_list_read_receipts', chat_arguments)
        g.communication_custom_command('send', 'communication_chat_send_read_receipt', chat_arguments)


def _load_rooms_command_table(self):
    rooms_arguments = ['connection_string']
    self.command_group('communication rooms')

    # room management
    with self.command_group('communication rooms', client_factory=cf_communication_rooms) as g:
        g.communication_custom_command('get', 'communication_rooms_get_room', rooms_arguments)
        g.communication_custom_command('create', 'communication_rooms_create_room', rooms_arguments)
        g.communication_custom_command('update', 'communication_rooms_update_room', rooms_arguments)
        g.communication_custom_command('delete', 'communication_rooms_delete_room', rooms_arguments, confirmation=True)
        g.communication_custom_command('list', 'communication_rooms_list_rooms', rooms_arguments)

    # rooms participant management
    with self.command_group('communication rooms participant', client_factory=cf_communication_rooms) as g:
        g.communication_custom_command('get', 'communication_rooms_get_participants', rooms_arguments)
        g.communication_custom_command('add-or-update', 'communication_rooms_add_or_update_participants', rooms_arguments)
        g.communication_custom_command('remove', 'communication_rooms_remove_participants', rooms_arguments, confirmation=True)


def _load_email_command_table(self):
    email_arguments = ['connection_string']
    self.command_group('communication email')

    with self.command_group('communication email', client_factory=cf_communication_email) as g:
        g.communication_custom_command('send', 'communication_email_send', email_arguments)
