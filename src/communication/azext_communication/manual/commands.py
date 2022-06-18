# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azext_communication.manual._client_factory import cf_communication_identity
from azext_communication.manual._client_factory import cf_communication_sms
from azext_communication.manual._client_factory import cf_communication_phonenumbers


def load_command_table(self, _):

    with self.command_group('communication identity', client_factory=cf_communication_identity) as g:
        g.communication_custom_command('issue-access-token', "issue_access_token", client_factory=cf_communication_identity)

    with self.command_group('communication sms', client_factory=cf_communication_sms) as g:
        g.communication_custom_command('send-sms', 'communication_send_sms')

    with self.command_group('communication phonenumbers', client_factory=cf_communication_phonenumbers) as g:
        g.communication_custom_command('list-phonenumbers', 'communication_list_phonenumbers')
        g.communication_custom_command('show-phonenumber', 'communication_show_phonenumber')
