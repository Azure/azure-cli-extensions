# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from http import HTTPStatus

import azure.cli.core.telemetry as telemetry
import requests
from requests import RequestException

from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this._command import Command
from azext_ai_did_you_mean_this._const import (
    RECOMMEND_RECOVERY_OPTIONS_LOG_FMT_STR, RECOMMENDATION_HEADER_FMT_STR,
    RECOMMENDATION_PROCESSING_TIME_FMT_STR, SERVICE_CONNECTION_TIMEOUT,
    TELEMETRY_IS_DISABLED_STR, TELEMETRY_IS_ENABLED_STR,
    TELEMETRY_MISSING_CORRELATION_ID_STR,
    TELEMETRY_MISSING_SUBSCRIPTION_ID_STR, UNABLE_TO_HELP_FMT_STR)
from azext_ai_did_you_mean_this._logging import get_logger
from azext_ai_did_you_mean_this._style import style_message
from azext_ai_did_you_mean_this.suggestion import Suggestion
from azext_ai_did_you_mean_this.telemetry import (FaultType,
                                                  NoRecommendationReason,
                                                  TelemetryProperty,
                                                  extension_telemetry_session,
                                                  get_correlation_id,
                                                  get_subscription_id,
                                                  set_exception,
                                                  set_properties, set_property)
from azext_ai_did_you_mean_this.timer import Timer
from azext_ai_did_you_mean_this.version import VERSION

logger = get_logger(__name__)


# Commands
# note: at least one command is required in order for the CLI to load the extension.
def show_extension_version():
    print(f'Current version: {VERSION}')


def normalize_and_sort_parameters(command_table, command, parameters):
    logger.debug('normalize_and_sort_parameters: command: "%s", parameters: "%s"', command, parameters)

    _command, parsed_command = Command.parse(command_table, command)
    _parameteters, unrecognized_parameters = Command.normalize(_command, *parameters)
    normalized_parameters = ','.join(sorted(set(_parameteters)))

    set_properties({
        TelemetryProperty.RawCommand: command,
        TelemetryProperty.Command: parsed_command,
        TelemetryProperty.RawParameters: ','.join(parameters),
        TelemetryProperty.Parameters: normalized_parameters,
        TelemetryProperty.UnrecognizedParameters: ','.join(sorted(set(unrecognized_parameters)))
    })

    return parsed_command, normalized_parameters


def recommend_recovery_options(version, command, parameters, extension):
    result = []
    execution_time = Timer()

    with extension_telemetry_session():
        with execution_time:
            cmd_tbl = CommandTable.CMD_TBL
            logger.debug(RECOMMEND_RECOVERY_OPTIONS_LOG_FMT_STR,
                         version, command, parameters, extension)

            set_properties({
                TelemetryProperty.CoreVersion: version,
                TelemetryProperty.ExtensionVersion: VERSION,
                TelemetryProperty.InferredExtension: extension
            })

            # if the command is empty...
            if not command:
                # try to get the raw command field from telemetry.
                session = telemetry._session  # pylint: disable=protected-access
                # get the raw command parsed by the CommandInvoker object.
                command = session.raw_command
                if command:
                    logger.debug(f'Setting command to [{command}] from telemtry.')

            def append(line):
                result.append(line)

            def unable_to_help(command):
                msg = UNABLE_TO_HELP_FMT_STR.format(command=command)
                append(msg)

            def show_recommendation_header(command):
                msg = RECOMMENDATION_HEADER_FMT_STR.format(command=command)
                append(style_message(msg))

            if extension:
                reason = NoRecommendationReason.CommandFromExtension.value
                set_properties({
                    TelemetryProperty.NoRecommendationReason: reason,
                    TelemetryProperty.InferredExtension: extension
                })
                logger.debug('Detected extension. No action to perform.')
            if not command:
                reason = NoRecommendationReason.EmptyCommand.value
                set_property(
                    TelemetryProperty.NoRecommendationReason, reason
                )
                logger.debug('Command is empty. No action to perform.')

            # if an extension is in-use or the command is empty...
            if extension or not command:
                return result

            # perform some rudimentary parsing to extract the parameters and command in a standard form
            command, parameters = normalize_and_sort_parameters(cmd_tbl, command, parameters)
            response = call_aladdin_service(command, parameters, version)

            # only show recommendations when we can contact the service.
            if response and response.status_code == HTTPStatus.OK:
                recommendations = get_recommendations_from_http_response(response, cmd_tbl)

                if recommendations:
                    show_recommendation_header(command)

                    for recommendation in recommendations:
                        append(f"\t{recommendation}")
                # only prompt user to use "az find" for valid CLI commands
                # note: pylint has trouble resolving statically initialized variables, which is why
                # we need to disable the unsupported membership test rule
                elif any(cmd.startswith(command) for cmd in cmd_tbl.keys()):  # pylint: disable=unsupported-membership-test
                    set_property(TelemetryProperty.SuggestedAzFind, True)
                    unable_to_help(command)
            else:
                set_property(
                    TelemetryProperty.NoRecommendationReason,
                    NoRecommendationReason.ServiceRequestFailure.value
                )

        logger.debug(RECOMMENDATION_PROCESSING_TIME_FMT_STR, execution_time.elapsed_ms)
        set_property(TelemetryProperty.ExecutionTimeMs, execution_time.elapsed_ms)

    return result


def get_recommendations_from_http_response(response, command_table):
    suggestions = []
    _suggestions = response.json()
    suggestion_count = len(_suggestions)
    invalid_suggestion_count = 0

    for suggestion in _suggestions:
        suggestion = Suggestion(suggestion)
        if suggestion.command not in command_table:
            invalid_suggestion_count += 1
        else:
            suggestions.append(suggestion)

    valid_suggestion_count = len(suggestions)

    set_properties({
        TelemetryProperty.ValidSuggestionCount: valid_suggestion_count,
        TelemetryProperty.InvalidSuggestionCount: invalid_suggestion_count,
        TelemetryProperty.TotalSuggestionCount: suggestion_count
    })

    if invalid_suggestion_count > 0:
        set_property(TelemetryProperty.PrunedSuggestions, json.dumps(suggestions))

    return suggestions


def call_aladdin_service(command, parameters, version):
    logger.debug('call_aladdin_service: version: "%s", command: "%s", parameters: "%s"',
                 version, command, parameters)

    response = None

    time_to_get_user_info = Timer()

    with time_to_get_user_info:
        correlation_id = get_correlation_id()
        subscription_id = get_subscription_id()

    set_property(TelemetryProperty.TimeToRetrieveUserInfoMs, time_to_get_user_info.elapsed_ms)

    is_telemetry_enabled = telemetry.is_telemetry_enabled()

    telemetry_context = {
        'correlationId': correlation_id,
        'subscriptionId': subscription_id
    }

    telemetry_context = {k: v for k, v in telemetry_context.items() if v is not None and is_telemetry_enabled}

    if not is_telemetry_enabled:
        logger.debug(TELEMETRY_IS_DISABLED_STR)
    else:
        logger.debug(TELEMETRY_IS_ENABLED_STR)

        if subscription_id is None:
            set_property(TelemetryProperty.MissingSubscriptionId, True)
            logger.debug(TELEMETRY_MISSING_SUBSCRIPTION_ID_STR)
        if correlation_id is None:
            set_property(TelemetryProperty.MissingCorrelationId, True)
            logger.debug(TELEMETRY_MISSING_CORRELATION_ID_STR)

    context = {
        **telemetry_context,
        "versionNumber": version
    }

    query = {
        "command": command,
        "parameters": parameters
    }

    api_url = 'https://app.aladdindev.microsoft.com/api/v1.0/suggestions'
    headers = {'Content-Type': 'application/json'}

    try:
        round_trip_request_time = Timer()

        with round_trip_request_time:
            response = requests.get(
                api_url,
                params={
                    'query': json.dumps(query),
                    'clientType': 'AzureCli',
                    'context': json.dumps(context),
                    'extensionVersion': VERSION
                },
                headers=headers,
                timeout=(SERVICE_CONNECTION_TIMEOUT, None))

        set_property(TelemetryProperty.RoundTripRequestTimeMs, round_trip_request_time.elapsed_ms)
    except RequestException as ex:
        if isinstance(ex, requests.Timeout):
            set_property(TelemetryProperty.RequestTimedOut, True)

        logger.debug('requests.get() exception: %s', ex)
        set_exception(exception=ex,
                      fault_type=FaultType.RequestException.value,
                      summary='HTTP Get Request to Aladdin suggestions endpoint failed.')

    return response
