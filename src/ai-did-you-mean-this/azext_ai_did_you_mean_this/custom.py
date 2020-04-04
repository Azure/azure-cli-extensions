# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import sys
import colorama 

from knack.util import CLIError

RECOMMENDATION_FILE_PATH = 'src/ai-did-you-mean-this/azext_ai_did_you_mean_this/data/top_3_recommendations.json'
RECOMMENDATIONS = None

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
        # Style if tty stream is available
        if sys.stdout.isatty():
            return True
    except AttributeError:
        pass
    return False

# Commands
def show_extension_version():
    print(f'Current version: 0.1.0')

def parse_recommendation(recommendation):
    success_command = recommendation['SuccessCommand']
    success_command_parameters = recommendation['SuccessCommand_Parameters']
    succces_command_parameter_buffer = success_command_parameters.split(',')
    success_command_placeholder_arguments = []

    for parameter in succces_command_parameter_buffer:
        argument = parameter[2:]
        argument_buffer = [word.capitalize() for word in argument.split('-')]
        success_command_placeholder_arguments.append(''.join(argument_buffer))

    return success_command, succces_command_parameter_buffer, success_command_placeholder_arguments

def recommend_recovery_options(version, command, parameters, extension):
    if version in RECOMMENDATIONS:
        command_recommendations = RECOMMENDATIONS[version]

        if command in command_recommendations and len(command_recommendations[command]) > 0:
            print(f'\nHere are the most common ways users succeeded after [{command}] failed:')

            recommendations = command_recommendations[command]
            
            for recommendation in recommendations:
                command, parameters, placeholders = parse_recommendation(recommendation)
                parameter_and_argument_buffer = []

                for pair in zip(parameters, placeholders):
                    parameter_and_argument_buffer.append(' '.join(pair))

                print(f"\taz {command} {' '.join(parameter_and_argument_buffer)}")
        else:
            print(f'\nSorry I am not able to help with [{command}]'
                  f'\nTry running [az find "{command}"] to see examples of [{command}] from other users.')
    else:
        print(style_message("Better failure recovery recommendations are available from the latest version of the CLI. "
                             "Please update for the best experience.\n"))