# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import hashlib
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


def new_examples(help_file):
    try:
        examples = replace_examples(help_file.command)
    except requests.exceptions.ConnectionError:
        examples = []

    if examples:
        help_file.examples = examples


# Replace built in examples with Aladdin ones
def replace_examples(command):
    # Specify az to coerce the examples to be for the exact command
    lookup_term = "az " + command
    return get_generated_examples(lookup_term)


# Support functions
def get_generated_examples(cli_term):
    examples = []
    response = call_aladdin_service(cli_term)

    if response.status_code == 200:
        for answer in json.loads(response.content):
            # Ignore pruned responses
            if answer['source'] != 'pruned':
                examples.append(clean_from_http_answer(answer))

    return examples


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
    version = str(parse_version(core_version))
    correlation_id = telemetry_core._session.correlation_id   # pylint: disable=protected-access
    subscription_id = telemetry_core._get_azure_subscription_id()  # pylint: disable=protected-access

    # Used for DDOS protection and rate limiting
    user_id = telemetry_core._get_installation_id()  # pylint: disable=protected-access
    hashed_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()

    context = {
        "versionNumber": version,
    }

    # Only pull in the contextual values if we have consent
    if telemetry_core.is_telemetry_enabled():
        context['correlationId'] = correlation_id

    if telemetry_core.is_telemetry_enabled() and subscription_id is not None:
        context['subscriptionId'] = subscription_id

    api_url = 'https://app.aladdin.microsoft.com/api/v1.0/examples'
    headers = {
        'Content-Type': 'application/json',
        'X-UserId': hashed_user_id
    }

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
