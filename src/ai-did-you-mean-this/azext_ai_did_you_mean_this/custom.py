# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from http import HTTPStatus
from pkg_resources import parse_version

import requests

import azure.cli.core.telemetry as telemetry_core

from knack.log import get_logger
from knack.util import CLIError  # pylint: disable=unused-import

from azext_ai_did_you_mean_this.failure_recovery_recommendation import FailureRecoveryRecommendation
from azext_ai_did_you_mean_this._style import style_message
from azext_ai_did_you_mean_this._check_for_updates import CliStatus, is_cli_up_to_date

logger = get_logger(__name__)

UPDATE_RECOMMENDATION_STR = (
    "Better failure recovery recommendations are available from the latest version of the CLI. "
    "Please update for the best experience.\n"
)

UNABLE_TO_HELP_FMT_STR = (
    '\nSorry I am not able to help with [{command}]'
    '\nTry running [az find "az {command}"] to see examples of [{command}] from other users.'
)

RECOMMENDATION_HEADER_FMT_STR = (
    '\nHere are the most common ways users succeeded after [{command}] failed:'
)

CLI_CHECK_IF_UP_TO_DATE = False


# Commands
def show_extension_version():
    print(f'Current version: 0.1.0')


def _log_debug(msg, *args, **kwargs):
    # TODO: see if there's a way to change the log formatter locally without printing to stdout
    msg = f'[Thoth]: {msg}'
    logger.debug(msg, *args, **kwargs)


def normalize_and_sort_parameters(parameters):
    # When an error occurs, global parameters are not filtered out. Repeat that logic here.
    # TODO: Consider moving this list to a connstant in azure.cli.core.commands
    parameters = [param for param in parameters if param not in ['--debug', '--verbose']]
    return ','.join(sorted(parameters))


def recommend_recovery_options(version, command, parameters, extension):
    result = []
    _log_debug('recommend_recovery_options: version: "%s", command: "%s", parameters: "%s", extension: "%s"',
               version, command, parameters, extension)

    # if the command is empty...
    if not command:
        # try to get the raw command field from telemetry.
        session = telemetry_core._session  # pylint: disable=protected-access
        # get the raw command parsed by the CommandInvoker object.
        command = session.raw_command
        if command:
            _log_debug(f'Setting command to [{command}] from telemtry.')

    def append(line):
        result.append(line)

    def unable_to_help(command):
        msg = UNABLE_TO_HELP_FMT_STR.format(command=command)
        append(msg)

    def show_recommendation_header(command):
        msg = RECOMMENDATION_HEADER_FMT_STR.format(command=command)
        append(style_message(msg))

    if extension:
        _log_debug('Detected extension. No action to perform.')
    if not command:
        _log_debug('Command is empty. No action to perform.')

    # if an extension is in-use or the command is empty...
    if extension or not command:
        return result

    parameters = normalize_and_sort_parameters(parameters)
    response = call_aladdin_service(command, parameters, '2.3.1')

    if response.status_code == HTTPStatus.OK:
        recommendations = get_recommendations_from_http_response(response)

        if recommendations:
            show_recommendation_header(command)

            for recommendation in recommendations:
                append(f"\t{recommendation}")
        else:
            unable_to_help(command)
    else:
        unable_to_help(command)

    if CLI_CHECK_IF_UP_TO_DATE:
        cli_status = is_cli_up_to_date()

        if cli_status == CliStatus.OUTDATED:
            append(style_message(UPDATE_RECOMMENDATION_STR))
    else:
        _log_debug('Skipping CLI version check.')

    return result


def get_recommendations_from_http_response(response):
    recommendations = []

    for suggestion in json.loads(response.content):
        recommendations.append(FailureRecoveryRecommendation(suggestion))

    return recommendations


def call_aladdin_service(command, parameters, core_version):
    _log_debug('call_aladdin_service: version: "%s", command: "%s", parameters: "%s"',
               core_version, command, parameters)

    session_id = telemetry_core._session._get_base_properties()['Reserved.SessionId']  # pylint: disable=protected-access
    subscription_id = telemetry_core._get_azure_subscription_id()  # pylint: disable=protected-access
    version = str(parse_version(core_version))

    context = {
        "sessionId": session_id,
        "subscriptionId": subscription_id,
        "versionNumber": version
    }

    query = {
        "command": command,
        "parameters": parameters
    }

    api_url = 'https://app.aladdindev.microsoft.com/api/v1.0/suggestions'
    headers = {'Content-Type': 'application/json'}

    response = requests.get(
        api_url,
        params={
            'query': json.dumps(query),
            'clientType': 'AzureCli',
            'context': json.dumps(context)
        },
        headers=headers)

    return response
