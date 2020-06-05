# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from http import HTTPStatus

import requests
from requests import RequestException

import azure.cli.core.telemetry as telemetry

from knack.log import get_logger
from knack.util import CLIError  # pylint: disable=unused-import

from azext_ai_did_you_mean_this.failure_recovery_recommendation import FailureRecoveryRecommendation
from azext_ai_did_you_mean_this._style import style_message
from azext_ai_did_you_mean_this._const import (
    RECOMMENDATION_HEADER_FMT_STR,
    UNABLE_TO_HELP_FMT_STR,
    TELEMETRY_MUST_BE_ENABLED_STR,
    TELEMETRY_MISSING_SUBSCRIPTION_ID_STR,
    TELEMETRY_MISSING_CORRELATION_ID_STR,
    UNABLE_TO_CALL_SERVICE_STR
)
from azext_ai_did_you_mean_this._cmd_table import CommandTable

logger = get_logger(__name__)


# Commands
# note: at least one command is required in order for the CLI to load the extension.
def show_extension_version():
    print('Current version: 0.2.0')


def _log_debug(msg, *args, **kwargs):
    # TODO: see if there's a way to change the log formatter locally without printing to stdout
    msg = f'[Thoth]: {msg}'
    logger.debug(msg, *args, **kwargs)


def get_parameter_table(cmd_table, command, recurse=True):
    az_cli_command = cmd_table.get(command, None)
    parameter_table = az_cli_command.arguments if az_cli_command else None

    # if the specified command was not found and recursive search is enabled...
    if not az_cli_command and recurse:
        # if there are at least two tokens separated by whitespace, remove the last token
        last_delim_idx = command.rfind(' ')
        if last_delim_idx != -1:
            _log_debug('Removing unknown token "%s" from command.', command[last_delim_idx + 1:])
            # try to find the truncated command.
            parameter_table, command = get_parameter_table(cmd_table, command[:last_delim_idx], recurse=False)

    return parameter_table, command


def normalize_and_sort_parameters(cmd_table, command, parameters):
    from knack.deprecation import Deprecated
    _log_debug('normalize_and_sort_parameters: command: "%s", parameters: "%s"', command, parameters)

    parameter_set = set()
    parameter_table, command = get_parameter_table(cmd_table, command)

    if parameters:
        # TODO: Avoid setting rules for global parameters manually.
        rules = {
            '-h': '--help',
            '-o': '--output',
            '--only-show-errors': None,
            '--help': None,
            '--output': None,
            '--query': None,
            '--debug': None,
            '--verbose': None
        }

        blocklisted = {'--debug', '--verbose'}

        if parameter_table:
            for argument in parameter_table.values():
                options = argument.type.settings['options_list']
                # remove deprecated arguments.
                options = (option for option in options if not isinstance(option, Deprecated))

                # attempt to create a rule for each potential parameter.
                try:
                    # sort parameters by decreasing length.
                    sorted_options = sorted(options, key=len, reverse=True)
                    # select the longest parameter as the standard form
                    standard_form = sorted_options[0]

                    for option in sorted_options[1:]:
                        rules[option] = standard_form

                    # don't apply any rules for the parameter's standard form.
                    rules[standard_form] = None
                except TypeError:
                    # ignore cases in which one of the option objects is of an unsupported type.
                    _log_debug('Unexpected argument options `%s` of type `%s`.', options, type(options).__name__)

        for parameter in parameters:
            if parameter in rules:
                # normalize the parameter or do nothing if already normalized
                normalized_form = rules.get(parameter, None) or parameter
                # add the parameter to our result set
                parameter_set.add(normalized_form)
            else:
                # ignore any parameters that we were unable to validate.
                _log_debug('"%s" is an invalid parameter for command "%s".', parameter, command)

        # remove any special global parameters that would typically be removed by the CLI
        parameter_set.difference_update(blocklisted)

    # get the list of parameters as a comma-separated list
    return command, ','.join(sorted(parameter_set))


def recommend_recovery_options(version, command, parameters, extension):
    from timeit import default_timer as timer
    start_time = timer()
    elapsed_time = None

    result = []
    cmd_tbl = CommandTable.CMD_TBL
    _log_debug('recommend_recovery_options: version: "%s", command: "%s", parameters: "%s", extension: "%s"',
               version, command, parameters, extension)

    # if the user doesn't agree to telemetry...
    if not telemetry.is_telemetry_enabled():
        _log_debug(TELEMETRY_MUST_BE_ENABLED_STR)
        return result

    # if the command is empty...
    if not command:
        # try to get the raw command field from telemetry.
        session = telemetry._session  # pylint: disable=protected-access
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

    # perform some rudimentary parsing to extract the parameters and command in a standard form
    command, parameters = normalize_and_sort_parameters(cmd_tbl, command, parameters)
    response = call_aladdin_service(command, parameters, version)

    # only show recommendations when we can contact the service.
    if response and response.status_code == HTTPStatus.OK:
        recommendations = get_recommendations_from_http_response(response)

        if recommendations:
            show_recommendation_header(command)

            for recommendation in recommendations:
                append(f"\t{recommendation}")
        # only prompt user to use "az find" for valid CLI commands
        # note: pylint has trouble resolving statically initialized variables, which is why
        # we need to disable the unsupported membership test rule
        elif any(cmd.startswith(command) for cmd in cmd_tbl.keys()):  # pylint: disable=unsupported-membership-test
            unable_to_help(command)

    elapsed_time = timer() - start_time
    _log_debug('The overall time it took to process failure recovery recommendations was %.2fms.', elapsed_time * 1000)

    return result


def get_recommendations_from_http_response(response):
    recommendations = []

    for suggestion in response.json():
        recommendations.append(FailureRecoveryRecommendation(suggestion))

    return recommendations


def call_aladdin_service(command, parameters, version):
    _log_debug('call_aladdin_service: version: "%s", command: "%s", parameters: "%s"',
               version, command, parameters)

    response = None

    correlation_id = telemetry._session.correlation_id  # pylint: disable=protected-access
    subscription_id = telemetry._get_azure_subscription_id()  # pylint: disable=protected-access

    if subscription_id and correlation_id:
        context = {
            "correlationId": correlation_id,
            "subscriptionId": subscription_id,
            "versionNumber": version
        }

        query = {
            "command": command,
            "parameters": parameters
        }

        api_url = 'https://app.aladdin.microsoft.com/api/v1.0/suggestions'
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.get(
                api_url,
                params={
                    'query': json.dumps(query),
                    'clientType': 'AzureCli',
                    'context': json.dumps(context)
                },
                headers=headers)
        except RequestException as ex:
            _log_debug('requests.get() exception: %s', ex)
    else:
        if subscription_id is None:
            _log_debug(TELEMETRY_MISSING_SUBSCRIPTION_ID_STR)
        if correlation_id is None:
            _log_debug(TELEMETRY_MISSING_CORRELATION_ID_STR)

        _log_debug(UNABLE_TO_CALL_SERVICE_STR)

    return response
