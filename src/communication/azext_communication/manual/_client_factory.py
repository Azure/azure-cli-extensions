# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# pylint: disable=unused-argument

from azure.cli.core.azclierror import RequiredArgumentMissingError


def cf_communication_identity(cli_ctx, kwargs):
    from azure.communication.identity import CommunicationIdentityClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    client = CommunicationIdentityClient.from_connection_string(connection_string)
    return client


def cf_communication_sms(cli_ctx, kwargs):
    from azure.communication.sms import SmsClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    client = SmsClient.from_connection_string(connection_string)
    return client


def cf_communication_phonenumbers(cli_ctx, kwargs):
    from azure.communication.phonenumbers import PhoneNumbersClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    client = PhoneNumbersClient.from_connection_string(connection_string)
    return client


def cf_communication_chat(cli_ctx, kwargs):
    from azure.communication.chat import ChatClient, CommunicationTokenCredential

    endpoint = kwargs.pop('endpoint', None)
    if endpoint is None:
        raise RequiredArgumentMissingError('Please specify --endpoint, or set AZURE_COMMUNICATION_ENDPOINT.')

    token = kwargs.pop('access_token', None)
    if token is None:
        raise RequiredArgumentMissingError('Please specify --access-token or set AZURE_COMMUNICATION_ACCESS_TOKEN.')

    client = ChatClient(endpoint, CommunicationTokenCredential(token))
    return client
