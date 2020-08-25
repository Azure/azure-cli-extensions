# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List, Tuple, Union

from azure.cli.core.commands import AzCliCommand

from azext_ai_did_you_mean_this._logging import get_logger
from azext_ai_did_you_mean_this._parameter import (GLOBAL_PARAM_BLOCKLIST,
                                                   GLOBAL_PARAM_LOOKUP_TBL,
                                                   Parameter, parameter_gen)
from azext_ai_did_you_mean_this._types import ParameterTableType

logger = get_logger(__name__)


class Command():

    def __init__(self, command: str, parameters: List[Parameter]):
        self.command: str = command
        self.parameters = parameters
        self.parameter_lookup_table = {}
        self.parameter_lookup_table.update(GLOBAL_PARAM_LOOKUP_TBL)

        for parameter in self.parameters:
            self.parameter_lookup_table[parameter.standard_form] = None

            for alias in parameter.aliases:
                self.parameter_lookup_table[alias] = parameter.standard_form

    @classmethod
    def normalize(cls, command: Union[None, 'Command'], *parameters: Tuple[str]):
        normalized_parameters = []
        unrecognized_parameters = []
        parameter_lookup_table = command.parameter_lookup_table if command else GLOBAL_PARAM_LOOKUP_TBL.copy()
        terms = parameter_lookup_table.keys()

        def is_recognized(parameter: str) -> bool:
            return parameter in parameter_lookup_table

        def match_prefix(parameter: str) -> str:
            matches: List[str] = [term for term in terms if term.startswith(parameter)]
            if len(matches) == 1:
                return matches[0]

            return parameter

        def get_normalized_form(parameter) -> str:
            normalized_form = None

            if not is_recognized(parameter):
                parameter = match_prefix(parameter)

            normalized_form = parameter_lookup_table.get(parameter, None) or parameter
            return normalized_form

        for parameter in parameters:
            normalized_form = get_normalized_form(parameter)

            if normalized_form in GLOBAL_PARAM_BLOCKLIST:
                continue
            if is_recognized(normalized_form):
                normalized_parameters.append(normalized_form)
            else:
                unrecognized_parameters.append(normalized_form)

        return sorted(set(normalized_parameters)), sorted(set(unrecognized_parameters))

    @classmethod
    def get_parameter_table(cls, command_table: dict, command: str,
                            recurse: bool = True) -> Tuple[ParameterTableType, str]:
        az_cli_command: Union[AzCliCommand, None] = command_table.get(command, None)
        parameter_table: ParameterTableType = az_cli_command.arguments if az_cli_command else {}
        partial_match = True

        if not az_cli_command:
            partial_match = any(cmd for cmd in command_table if cmd.startswith(command))

        # if the specified command was not found and no similar command exists and recursive search is enabled...
        if not az_cli_command and not partial_match and recurse:
            # if there are at least two tokens separated by whitespace, remove the last token
            last_delim_idx = command.rfind(' ')
            if last_delim_idx != -1:
                logger.debug('Removing unknown token "%s" from command.', command[last_delim_idx + 1:])
                # try to find the truncated command.
                parameter_table, command = cls.get_parameter_table(
                    command_table,
                    command[:last_delim_idx],
                    recurse=False
                )

        return parameter_table, command

    @staticmethod
    def parse(command_table: dict, command: str, recurse: bool = True) -> Tuple['Command', str]:
        instance: 'Command' = None
        (parameter_table, command) = Command.get_parameter_table(
            command_table,
            command,
            recurse
        )

        if parameter_table:
            parameters = [parameter for parameter in parameter_gen(parameter_table)]
            instance = Command(command, parameters)

        return instance, command
