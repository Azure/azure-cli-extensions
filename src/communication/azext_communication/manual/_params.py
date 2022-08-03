# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):
    with self.argument_context('communication update') as c:
        c.argument('location', validator=None)

    _load_identity_arguments(self)
    _load_sms_arguments(self)
    _load_phonenumber_arguments(self)
    _load_chat_arguments(self)


def _load_identity_arguments(self):
    with self.argument_context('communication identity issue-access-token') as c:
        c.argument('userid', options_list=['--userid', '-u'],
                   type=str, help='ACS identifier')
        c.argument('scopes', options_list=['--scope', '-s'],
                   nargs='+', help='list of scopes for an access token ex: chat/voip')
    with self.argument_context('communication identity revoke-access-tokens') as c:
        c.argument('userid', options_list=['--userid', '-u'], type=str, help='ACS identifier')


def _load_sms_arguments(self):
    with self.argument_context('communication sms send-sms') as c:
        c.argument('sender', options_list=['--sender', '-s'],
                   type=str, help='The sender of the SMS')
        c.argument('recipients', options_list=['--recipient', '-r'],
                   nargs='+', help='The recipient(s) of the SMS')
        c.argument('message', options_list=['--message', '-m'],
                   type=str, help='The message in the SMS')


def _load_phonenumber_arguments(self):
    with self.argument_context('communication phonenumbers show-phonenumber') as c:
        c.argument('phonenumber', options_list=['--phonenumber', '-p'],
                   type=str, help='Phone number to get information about')


def _load_chat_arguments(self):
    _load_chat_thread_management(self)
    _load_chat_participant_management(self)
    _load_chat_message_management(self)


def _load_chat_thread_management(self):
    with self.argument_context('communication chat list-threads') as c:
        c.argument('start_time', options_list=['--start-time', '-s'],
                   type=str, help='Start time in ISO8601 format, ex: 2022-07-14T10:21')

    with self.argument_context('communication chat create-thread') as c:
        c.argument('topic', options_list=['--topic', '-p'],
                   type=str, help='Chat topic')
        c.argument('idempotency_token', options_list=['--idempotency-token'],
                   type=str, help='Idempotency token')

    with self.argument_context('communication chat delete-thread') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')


def _load_chat_participant_management(self):
    with self.argument_context('communication chat list-participants') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('skip', options_list=['--skip'],
                   type=str, help='Number of participants to skip')

    with self.argument_context('communication chat add-participant') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('user_id', options_list=['--user-id', '-u'],
                   type=str, help='Chat participant identifier')
        c.argument('display_name', options_list=['--display-name', '-d'],
                   type=str, help='Chat participant display name')
        c.argument('start_time', options_list=['--start-time', '-s'],
                   type=str, help='Start time to share history in ISO8601 format, ex: 2022-07-14T10:21')

    with self.argument_context('communication chat remove-participant') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('user_id', options_list=['--user-id', '-u'],
                   type=str, help='Chat participant identifier')


def _load_chat_message_management(self):
    with self.argument_context('communication chat send-message') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('display_name', options_list=['--display-name', '-d'],
                   type=str, help='Sender''s display name')
        c.argument('message_content', options_list=['--content', '-c'],
                   type=str, help='Chat message content')
        c.argument('message_type', options_list=['--message-type', '-y'],
                   type=str, help='Content type, can be text or html')

    with self.argument_context('communication chat list-messages') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('start_time', options_list=['--start-time', '-s'],
                   type=str, help='Start time in ISO8601 format, ex: 2022-07-14T10:21')

    with self.argument_context('communication chat get-message') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id', '-i'],
                   type=str, help='Message id')

    with self.argument_context('communication chat update-message') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id', '-i'],
                   type=str, help='Message id')
        c.argument('message_content', options_list=['--content', '-c'],
                   type=str, help='Chat message content')

    with self.argument_context('communication chat delete-message') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id', '-i'],
                   type=str, help='Message id')

    with self.argument_context('communication chat update-topic') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('topic', options_list=['--topic', '-p'],
                   type=str, help='Chat topic')

    with self.argument_context('communication chat list-read-receipts') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('skip', options_list=['--skip'],
                   type=str, help='Number of read receipts to skip')

    with self.argument_context('communication chat send-read-receipt') as c:
        c.argument('thread_id', options_list=['--thread-id', '-t'],
                   type=str, help='Thread id')
        c.argument('message_id', options_list=['--message-id', '-i'],
                   type=str, help='Message id')
