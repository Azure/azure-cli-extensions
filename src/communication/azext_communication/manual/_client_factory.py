# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from azure.cli.core.azclierror import RequiredArgumentMissingError
from ..version import cli_application_id


def cf_communication_identity(cli_ctx, kwargs):
    from azure.communication.identity import CommunicationIdentityClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    args = {'user_agent': cli_application_id()}
    client = CommunicationIdentityClient.from_connection_string(connection_string, **args)

    return client


def cf_communication_sms(cli_ctx, kwargs):
    from azure.communication.sms import SmsClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    args = {'user_agent': cli_application_id()}
    client = SmsClient.from_connection_string(connection_string, **args)

    return client


def cf_communication_phonenumbers(cli_ctx, kwargs):
    from azure.communication.phonenumbers import PhoneNumbersClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    args = {'user_agent': cli_application_id()}
    client = PhoneNumbersClient.from_connection_string(connection_string, **args)

    return client


def cf_communication_chat(cli_ctx, kwargs):
    from azure.communication.chat import ChatClient, CommunicationTokenCredential

    endpoint = kwargs.pop('endpoint', None)
    if endpoint is None:
        raise RequiredArgumentMissingError('Please specify --endpoint, or set AZURE_COMMUNICATION_ENDPOINT.')

    token = kwargs.pop('access_token', None)
    if token is None:
        raise RequiredArgumentMissingError('Please specify --access-token or set AZURE_COMMUNICATION_ACCESS_TOKEN.')

    args = {'user_agent': cli_application_id()}
    client = ChatClient(endpoint, CommunicationTokenCredential(token), **args)

    return client


def cf_communication_rooms(cli_ctx, kwargs):
    from azure.communication.rooms import RoomsClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    args = {'user_agent': cli_application_id()}
    client = RoomsClient.from_connection_string(connection_string, **args)
    return client


def cf_communication_email(cli_ctx, kwargs):
    from azure.communication.email import EmailClient

    connection_string = kwargs.pop('connection_string', None)
    if connection_string is None:
        error_msg = 'Please specify --connection-string, or set AZURE_COMMUNICATION_CONNECTION_STRING.'
        raise RequiredArgumentMissingError(error_msg)

    args = {'user_agent': cli_application_id()}
    client = EmailClient.from_connection_string(connection_string, **args)
    return client
