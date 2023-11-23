# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import get_enum_type, get_three_state_flag


def load_arguments(self, _):
    with self.argument_context('communication update') as c:
        c.argument('location', validator=None)

    _load_user_identity_arguments(self)
    _load_legacy_identity_arguments(self)
    _load_sms_arguments(self)
    _load_phonenumber_arguments(self)
    _load_chat_arguments(self)
    _load_rooms_arguments(self)
    _load_email_arguments(self)


def _load_user_identity_arguments(self):
    self.argument_context('communication user-identity user create')

    with self.argument_context('communication user-identity user delete') as c:
        c.argument('user_id', options_list=['--user'], type=str, help='ACS identifier')

    with self.argument_context('communication user-identity issue-access-token') as c:
        c.argument('user_id', options_list=['--userid', '-u'], type=str, help='ACS identifier')
        c.argument('scopes', options_list=['--scope', '-s'],
                   nargs='+', help='list of scopes for an access token ex: chat/voip')

    with self.argument_context('communication user-identity token issue') as c:
        c.argument('user_id', options_list=['--user'], type=str, help='ACS identifier')
        c.argument('scopes', options_list=['--scope'], nargs='+',
                   help='list of scopes for an access token ex: chat/voip')

    with self.argument_context('communication user-identity token revoke') as c:
        c.argument('user_id', options_list=['--user'], type=str, help='ACS identifier')

    with self.argument_context('communication user-identity token get-for-teams-user') as c:
        c.argument('aad_token', options_list=['--aad-token'], type=str, help='Azure AD access token of a Teams User')
        c.argument('client_id', options_list=['--client'], type=str, help='Client ID of an Azure AD application'
                   'to be verified against the appId claim in the Azure AD access token')
        c.argument('user_object_id', options_list=['--aad-user'], type=str, help='Object ID of an Azure AD user'
                   '(Teams User) to be verified against the OID claim in the Azure AD access token')


def _load_legacy_identity_arguments(self):
    self.argument_context('communication identity user create')

    with self.argument_context('communication identity user delete') as c:
        c.argument('user_id', options_list=['--user'], type=str, help='ACS identifier')

    with self.argument_context('communication identity token issue') as c:
        c.argument('user_id', options_list=['--user'], type=str, help='ACS identifier')
        c.argument('scopes', options_list=['--scope'], nargs='+',
                   help='list of scopes for an access token ex: chat/voip')

    with self.argument_context('communication identity token revoke') as c:
        c.argument('user_id', options_list=['--user'], type=str, help='ACS identifier')

    with self.argument_context('communication identity token get-for-teams-user') as c:
        c.argument('aad_token', options_list=['--aad-token'], type=str, help='Azure AD access token of a Teams User')
        c.argument('client_id', options_list=['--client'], type=str, help='Client ID of an Azure AD application'
                   'to be verified against the appId claim in the Azure AD access token')
        c.argument('user_object_id', options_list=['--aad-user'], type=str, help='Object ID of an Azure AD user'
                   '(Teams User) to be verified against the OID claim in the Azure AD access token')


def _load_sms_arguments(self):
    with self.argument_context('communication sms send-sms') as c:
        c.argument('sender', options_list=['--sender', '-s'],
                   type=str, help='The sender of the SMS')
        c.argument('recipients', options_list=['--recipient', '-r'],
                   nargs='+', help='The recipient(s) of the SMS')
        c.argument('message', options_list=['--message', '-m'],
                   type=str, help='The message in the SMS')
    with self.argument_context('communication sms send') as c:
        c.argument('sender', options_list=['--sender'],
                   type=str, help='The sender of the SMS')
        c.argument('recipients', options_list=['--recipient'],
                   nargs='+', help='The recipient(s) of the SMS')
        c.argument('message', options_list=['--message'],
                   type=str, help='The message in the SMS')


def _load_phonenumber_arguments(self):
    with self.argument_context('communication phonenumbers show-phonenumber') as c:
        c.argument('phonenumber', options_list=['--phonenumber', '-p'],
                   type=str, help='Phone number to get information about')
    with self.argument_context('communication phonenumber show') as c:
        c.argument('phonenumber', options_list=['--phonenumber'],
                   type=str, help='Phone number to get information about')


def _load_chat_arguments(self):
    _load_chat_thread_management(self)
    _load_chat_participant_management(self)
    _load_chat_message_management(self)


def _load_chat_thread_management(self):
    with self.argument_context('communication chat thread list') as c:
        c.argument('start_time', options_list=['--start-time'],
                   type=str, help='Start time in ISO8601 format, ex: 2022-07-14T10:21')

    with self.argument_context('communication chat thread create') as c:
        c.argument('topic', options_list=['--topic'],
                   type=str, help='Chat topic')
        c.argument('idempotency_token', options_list=['--idempotency-token'],
                   type=str, help='Idempotency token')

    with self.argument_context('communication chat thread delete') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')

    with self.argument_context('communication chat thread update-topic') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('topic', options_list=['--topic'],
                   type=str, help='Chat topic')


def _load_chat_participant_management(self):
    with self.argument_context('communication chat participant list') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('skip', options_list=['--skip'],
                   type=str, help='Number of participants to skip')

    with self.argument_context('communication chat participant add') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('user_id', options_list=['--user'],
                   type=str, help='Chat participant identifier')
        c.argument('display_name', options_list=['--display-name'],
                   type=str, help='Chat participant display name')
        c.argument('start_time', options_list=['--start-time'],
                   type=str, help='Start time to share history in ISO8601 format, ex: 2022-07-14T10:21')

    with self.argument_context('communication chat participant remove') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('user_id', options_list=['--user'],
                   type=str, help='Chat participant identifier')


def _load_chat_message_management(self):
    with self.argument_context('communication chat message send') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('display_name', options_list=['--display-name'],
                   type=str, help='Sender''s display name')
        c.argument('message_content', options_list=['--content'],
                   type=str, help='Chat message content')
        c.argument('message_type', options_list=['--message-type'],
                   type=str, help='Content type, can be text or html')

    with self.argument_context('communication chat message list') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('start_time', options_list=['--start-time'],
                   type=str, help='Start time in ISO8601 format, ex: 2022-07-14T10:21')

    with self.argument_context('communication chat message get') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id'],
                   type=str, help='Message id')

    with self.argument_context('communication chat message update') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id'],
                   type=str, help='Message id')
        c.argument('message_content', options_list=['--content'],
                   type=str, help='Chat message content')

    with self.argument_context('communication chat message delete') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id'],
                   type=str, help='Message id')

    with self.argument_context('communication chat message receipt list') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('skip', options_list=['--skip'],
                   type=str, help='Number of read receipts to skip')

    with self.argument_context('communication chat message receipt send') as c:
        c.argument('thread_id', options_list=['--thread', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id'],
                   type=str, help='Message id')


def _load_rooms_arguments(self):
    with self.argument_context('communication rooms get') as c:
        c.argument('room_id', options_list=['--room'],
                   type=str, help='Room Id')

    with self.argument_context('communication rooms create') as c:
        c.argument('valid_from',
                   help='The timestamp from when the room is open for joining, '
                   'in in ISO8601 format, ex: 2023-03-31T10:21. Optional.')
        c.argument('valid_until',
                   help='The timestamp from when the room can no longer be joined,'
                   ' in ISO8601 format, ex: 2023-06-31T10:21. Optional.')
        c.argument('pstn_dial_out_enabled',
                   help='Set this flag to true if, at the time of the call, '
                   'dial out to a PSTN number is enabled in a particular room. '
                   'By default, this flag is set to false. Optional.')
        c.argument('presenters', options_list=['--presenter-participants'],
                   nargs='+', help='Collection of identities to be invited to the room as presenter. Optional.')
        c.argument('attendees', options_list=['--attendee-participants'],
                   nargs='+', help='Collection of identities to be invited to the room as attendee. Optional.')
        c.argument('consumers', options_list=['--consumer-participants'],
                   nargs='+', help='Collection of identities to be invited to the room as consumer. Optional.')

    with self.argument_context('communication rooms delete') as c:
        c.argument('room_id', options_list=['--room'],
                   type=str, help='Room Id')

    with self.argument_context('communication rooms update') as c:
        c.argument('room_id', options_list=['--room'], type=str, help='Room Id')
        c.argument('valid_from',
                   help='The timestamp from when the room is open for joining, in in ISO8601 format, '
                   'ex: 2023-03-31T10:21. Should be used together with --valid-until. Optional.')
        c.argument('valid_until',
                   help='The timestamp from when the room can no longer be joined, in ISO8601 format, '
                   'ex: 2023-06-31T10:21. Should be used together with --valid-from. Optional.')
        c.argument('pstn_dial_out_enabled',
                   help='Set this flag to true if, at the time of the call, '
                   'dial out to a PSTN number is enabled in a particular room. '
                   'By default, this flag is set to false. Optional.')

    with self.argument_context('communication rooms participant get') as c:
        c.argument('room_id', options_list=['--room'],
                   type=str, help='Room Id')

    with self.argument_context('communication rooms participant add-or-update') as c:
        c.argument('room_id', options_list=['--room'],
                   type=str, help='Room Id')
        c.argument('presenters', options_list=['--presenter-participants'],
                   nargs='+', help='Collection of identities to be added to the room as presenter.')
        c.argument('attendees', options_list=['--attendee-participants'],
                   nargs='+', help='Collection of identities to be added to the room as attendee.')
        c.argument('consumers', options_list=['--consumer-participants'],
                   nargs='+', help='Collection of identities to be added to the room as consumer.')

    with self.argument_context('communication rooms participant remove') as c:
        c.argument('room_id', options_list=['--room'],
                   type=str, help='Room Id')
        c.argument('participants', options_list=['--participants'],
                   nargs='+', help='Collection of identities that will be removed from the room.')


def _load_email_arguments(self):
    with self.argument_context('communication email send') as c:
        c.argument('sender', options_list=['--sender'], type=str, help='Sender email address from a verified domain.')
        c.argument('subject', options_list=['--subject'], type=str, help='Subject of the email message.')
        c.argument('text', options_list=['--text'], type=str, help='Plain text version of the email message. Optional.')
        c.argument('html', options_list=['--html'], type=str,
                   help='Html version of the email message. Optional.')
        c.argument('recipients_to', options_list=['--to'], nargs='+',
                   help='Recepients email addresses comma seperated if more than one.')
        c.argument('importance', options_list=['--importance'], arg_type=get_enum_type(['normal', 'low', 'high']),
                   help='The importance type for the email. Known values are: high,'
                   ' normal, and low. Default is normal. Optional')
        c.argument('recipients_cc', options_list=['--cc'], nargs='+', help='Carbon copy email addresses.')
        c.argument('recipients_bcc', options_list=['--bcc'], nargs='+', help='Blind carbon copy email addresses.')
        c.argument('reply_to', options_list=['--reply-to'], type=str, help='Reply-to email address. Optional.')
        c.argument('disable_tracking', options_list=['--disable-tracking'],
                   arg_type=get_three_state_flag(),
                   help='Indicates whether user engagement tracking should be disabled for this specific request. '
                   'This is only applicable if the resource-level user engagement '
                   'tracking setting was already enabled in control plane. Optional.')
        c.argument('attachments', options_list=['--attachments'], nargs='+',
                   help='List of email attachments. Optional.')
        c.argument('attachment_types', options_list=['--attachment-types'], nargs='+',
                   help='List of email attachment types, in the same order of attachments.'
                   ' Required for each attachment. Known values are: avi, bmp, doc, docm,'
                   ' docx, gif, jpeg, mp3, one, pdf, png, ppsm, ppsx, ppt, pptm, pptx,'
                   ' pub, rpmsg, rtf, tif, txt, vsd, wav, wma, xls, xlsb, xlsm, and xlsx')
