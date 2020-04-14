# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import sys

from enum import Enum, auto

import colorama

import azure.cli.core.telemetry as telemetry

from knack.log import get_logger
from knack.util import CLIError  # pylint: disable=unused-import

logger = get_logger(__name__)

EXTENSION_DIR = os.path.dirname(os.path.realpath(__file__))
RECOMMENDATION_FILE_PATH = os.path.join(
    EXTENSION_DIR,
    'data/top_3_recommendations.json'
)

RECOMMENDATIONS = None

UPDATE_RECOMMENDATION_STR = (
    "Better failure recovery recommendations are available from the latest version of the CLI. "
    "Please update for the best experience.\n"
)

with open(RECOMMENDATION_FILE_PATH) as recommendation_file:
    RECOMMENDATIONS = json.load(recommendation_file)


def style_message(msg):
    if should_enable_styling():
        try:
            msg = colorama.Style.BRIGHT + msg + colorama.Style.RESET_ALL
        except KeyError:
            pass
    return msg


def should_enable_styling():
    try:
        if sys.stdout.isatty():
            return True
    except AttributeError:
        pass
    return False


# Commands
def show_extension_version():
    print(f'Current version: 0.1.0')


def get_values(comma_separated_values):
    if not comma_separated_values:
        return []
    return comma_separated_values.split(',')


def parse_recommendation(recommendation):
    success_command = recommendation['SuccessCommand']
    success_command_parameters = recommendation['SuccessCommand_Parameters']
    success_command_argument_placeholders = recommendation['SuccessCommand_ArgumentPlaceholders']

    if not success_command_parameters:
        success_command_argument_placeholders = ''

    parameter_buffer = get_values(success_command_parameters)
    placeholder_buffer = get_values(success_command_argument_placeholders)

    return success_command, parameter_buffer, placeholder_buffer


def log_debug(msg):
    # TODO: see if there's a way to change the log formatter locally without printing to stdout
    prefix = '[Thoth]'
    logger.debug('%s: %s', prefix, msg)


class RecommendationStatus(Enum):
    RECOMMENDATIONS_AVAILABLE = auto()
    NO_RECOMMENDATIONS_AVAILABLE = auto()
    UNKNOWN_VERSION = auto()


def try_get_recommendations(version, command, parameters):
    recommendations = RECOMMENDATIONS
    status = RecommendationStatus.NO_RECOMMENDATIONS_AVAILABLE

    # if the specified CLI version doesn't have recommendations...
    if version not in RECOMMENDATIONS:
        # CLI version may be invalid or too old.
        return RecommendationStatus.UNKNOWN_VERSION, None, None

    recommendations = recommendations[version]

    # if there are no recommendations for the specified command...
    if command not in recommendations or not recommendations[command]:
        return RecommendationStatus.NO_RECOMMENDATIONS_AVAILABLE, None, None

    recommendations = recommendations[command]

    # try getting a comma-separated parameter list
    try:
        parameters = ','.join(parameters)
    # assume the parameters are already in the correct format.
    except TypeError:
        pass

    # use recommendations for a specific parameter set where applicable.
    parameters = parameters if parameters in recommendations else ''

    # if there are no recommendations for the specified parameters...
    if parameters in recommendations and recommendations[parameters]:
        status = RecommendationStatus.RECOMMENDATIONS_AVAILABLE
        recommendations = recommendations[parameters]

    # return status and processed list of parameters
    return status, parameters, recommendations


def recommend_recovery_options(version, command, parameters, extension):
    result = []

    # if the command is empty...
    if not command:
        # try to get the raw command field from telemetry.
        session = telemetry._session  # pylint: disable=protected-access
        # get the raw command parsed by the CommandInvoker object.
        command = session.raw_command
        if command:
            log_debug(f'Setting command to [{command}] from telemtry.')

    def append(line):
        result.append(line)

    def unable_to_help(command):
        append(f'\nSorry I am not able to help with [{command}]'
               f'\nTry running [az find "{command}"] to see examples of [{command}] from other users.')

    if extension:
        log_debug('Detected extension. No action to perform.')
    if not command:
        log_debug('Command is empty. No action to perform.')

    # if an extension is in-use or the command is empty...
    if extension or not command:
        return result

    status, parameters, recommendations = try_get_recommendations(version, command, parameters)

    if status == RecommendationStatus.RECOMMENDATIONS_AVAILABLE:
        append(f'\nHere are the most common ways users succeeded after [{command}] failed:')

        for recommendation in recommendations:
            command, parameters, placeholders = parse_recommendation(recommendation)
            parameter_and_argument_buffer = []

            for pair in zip(parameters, placeholders):
                parameter_and_argument_buffer.append(' '.join(pair))

            append(f"\taz {command} {' '.join(parameter_and_argument_buffer)}")
    elif status == RecommendationStatus.NO_RECOMMENDATIONS_AVAILABLE:
        unable_to_help(command)
    elif status == RecommendationStatus.UNKNOWN_VERSION:
        append(style_message(UPDATE_RECOMMENDATION_STR))

    return result
