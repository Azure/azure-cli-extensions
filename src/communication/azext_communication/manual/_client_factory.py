# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-argument
def cf_communication_identity(cli_ctx, kwargs):
    from azure.communication.identity import CommunicationIdentityClient
    connection_string = kwargs.pop('connection_string', None)
    client = CommunicationIdentityClient.from_connection_string(connection_string)
    return client


def cf_communication_sms(cli_ctx, kwargs):
    from azure.communication.sms import SmsClient
    connection_string = kwargs.pop('connection_string', None)
    client = SmsClient.from_connection_string(connection_string)
    return client


def cf_communication_phonenumbers(cli_ctx, kwargs):
    from azure.communication.phonenumbers import PhoneNumbersClient
    connection_string = kwargs.pop('connection_string', None)
    client = PhoneNumbersClient.from_connection_string(connection_string)
    return client
