# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import json
import re
import requests
from pkg_resources import parse_version

from azure.cli.core import telemetry as telemetry_core
from azure.cli.core import __version__ as core_version
from azure.cli.core._help import HelpExample


# Commands
def check_connection_aladdin():
    response = ping_aladdin_service()
    if response.status_code == 200:
        print('Connection was successful')
    else:
        print('Connection failed')


# Replacements for core functions
def provide_examples(help_file):
    return replace_examples(help_file)


# Provide two options for changing the examples

# Replace built in examples wirh Aladdin ones
def replace_examples(help_file):
    # Specify az to coerce the examples to be for the exact command
    lookup_term = "az " + help_file.command
    return get_generated_examples(lookup_term)


# Append Aladdin examples to the built in ones
def append_examples(help_file):
    # Specify az to coerce the examples to be for the exact command
    lookup_term = "az " + help_file.command
    aladdin_examples = get_generated_examples(lookup_term)
    return concat_unique_examples(help_file.examples, aladdin_examples)


# Support functions
def get_generated_examples(cli_term):
    examples = []
    response = call_aladdin_service(cli_term)

    if response.status_code == 200:
        for answer in json.loads(response.content):
            examples.append(clean_from_http_answer(answer))

    return examples


def concat_unique_examples(first_list, second_list):
    for first_item in first_list:
        for second_item in second_list:
            if are_examples_equal(first_item, second_item):
                second_list.remove(second_item)
    return first_list + second_list


def are_examples_equal(first, second):
    return clean_string(first.short_summary) == clean_string(second.short_summary) \
        or clean_string(first.command) == clean_string(second.command)


def clean_string(text):
    return text.strip()


def clean_from_http_answer(http_answer):
    example = HelpExample()
    example.short_summary = http_answer['title'].strip()
    example.command = http_answer['snippet'].strip()
    if example.short_summary.startswith("az "):
        example.short_summary, example.command = example.command, example.short_summary
        example.short_summary = example.short_summary.split('\r\n')[0]
    elif '```azurecli\r\n' in example.command:
        start_index = example.command.index('```azurecli\r\n') + len('```azurecli\r\n')
        example.command = example.command[start_index:]
    example.command = example.command.replace('```', '').replace(example.short_summary, '').strip()
    example.command = re.sub(r'\[.*\]', '', example.command).strip()
    # Add a '\n' to comply with the existing examples format
    example.command = example.command + '\n'
    return example


# HTTP calls
def ping_aladdin_service():
    api_url = 'https://app.aladdin.microsoft.com/api/v1.0/monitor'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(
        api_url,
        headers=headers)

    return response


def call_aladdin_service(query):
    client_request_id = ''
    if telemetry_core._session.application:  # pylint: disable=protected-access
        client_request_id = telemetry_core._session.application.data['headers']['x-ms-client-request-id']  # pylint: disable=protected-access

    session_id = telemetry_core._session._get_base_properties()['Reserved.SessionId']  # pylint: disable=protected-access
    subscription_id = telemetry_core._get_azure_subscription_id()  # pylint: disable=protected-access
    client_request_id = client_request_id  # pylint: disable=protected-access
    installation_id = telemetry_core._get_installation_id()  # pylint: disable=protected-access
    version = str(parse_version(core_version))

    context = {
        "sessionId": session_id,
        "subscriptionId": subscription_id,
        "clientRequestId": client_request_id,
        "installationId": installation_id,
        "versionNumber": version
    }

    api_url = 'https://app.aladdin.microsoft.com/api/v1.0/examples'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(
        api_url,
        params={
            'query': query,
            'clientType': 'AzureCli',
            'context': json.dumps(context),
            'commandOnly': True,
            'numberOfExamples': 5
        },
        headers=headers)

    return response
