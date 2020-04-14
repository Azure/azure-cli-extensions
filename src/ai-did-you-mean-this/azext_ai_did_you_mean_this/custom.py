# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import sys

import colorama

import azure.cli.core.telemetry as telemetry

from knack.log import get_logger
from knack.util import CLIError # pylint: disable=unused-import

logger = get_logger(__name__)

EXTENSION_DIR = os.path.dirname(os.path.realpath(__file__))
RECOMMENDATION_FILE_PATH = os.path.join(EXTENSION_DIR, 'data/top_3_recommendations.json')
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

def recommend_recovery_options(version, command, parameters, extension):
    recommendations = []

    # if the command is empty...
    if not command:
        # try to get the raw command field from telemetry.
        session = telemetry._session # pylint: disable=protected-access
        # get the raw command parsed by the CommandInvoker object.
        command = session.raw_command
        if command:
            log_debug(f'Setting command to [{command}] from telemtry.')

    def append(line):
        recommendations.append(line)

    def unable_to_help(command):
        append(f'\nSorry I am not able to help with [{command}]'
               f'\nTry running [az find "{command}"] to see examples of [{command}] from other users.')

    if extension:
        log_debug('Detected extension. No action to perform.')
    if not command:
        log_debug('Command is empty. No action to perform.')

    if extension is None and command:
        if version in RECOMMENDATIONS:
            command_recommendations = RECOMMENDATIONS[version]

            if command in command_recommendations and command_recommendations[command]:
                parameters = ','.join(parameters)
                parameters = parameters if parameters in command_recommendations[command] else ''

                if parameters in command_recommendations[command]:
                    append(f'\nHere are the most common ways users succeeded after [{command}] failed:')

                    top_recommendations = command_recommendations[command][parameters]

                    for top_recommendation in top_recommendations:
                        command, parameters, placeholders = parse_recommendation(top_recommendation)
                        parameter_and_argument_buffer = []

                        for pair in zip(parameters, placeholders):
                            parameter_and_argument_buffer.append(' '.join(pair))

                        append(f"\taz {command} {' '.join(parameter_and_argument_buffer)}")
                else:
                    unable_to_help(command)
            else:
                unable_to_help(command)
        else:
            append(style_message(UPDATE_RECOMMENDATION_STR))

    return recommendations
