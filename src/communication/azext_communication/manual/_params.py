# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):
    with self.argument_context('communication update') as c:
        c.argument('location', validator=None)

    with self.argument_context('communication identity issue-access-token') as c:
        c.argument('userid', options_list=['--userid', '-u'], type=str, help='ACS identifier')
        c.argument('scopes', options_list=[
                   '--scope', '-s'], nargs='+', help='list of scopes for an access token ex: chat/voip')

    with self.argument_context('communication sms send-sms') as c:
        c.argument('sender', options_list=['--sender', '-s'], type=str, help='The sender of the SMS')
        c.argument('recipients', options_list=[
                   '--recipient', '-r'], nargs='+', help='The recipient(s) of the SMS')
        c.argument('message', options_list=['--message', '-m'], type=str, help='The message in the SMS')

    with self.argument_context('communication phonenumbers show-phonenumber') as c:
        c.argument('phonenumber', options_list=[
                   '--phonenumber', '-p'], type=str, help='Phone number to get information about')
