# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
from copy import deepcopy
from typing import Iterable, List, Pattern, Set, Tuple, Union

from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this._command import Command
from azext_ai_did_you_mean_this._parameter import (
    GLOBAL_PARAM_BLOCKLIST,
    GLOBAL_PARAM_LOOKUP_TBL
)
from azext_ai_did_you_mean_this._types import ArgumentsType
from azext_ai_did_you_mean_this._util import safe_repr
from azext_ai_did_you_mean_this.arguments import Arguments
from azext_ai_did_you_mean_this.tests.latest.data._command_normalization_scenario import \
    CommandNormalizationScenario

GLOBAL_PARAMS = list(set(parameter for parameter in GLOBAL_PARAM_LOOKUP_TBL if parameter.startswith('--')))

PARAMETER_PATTERN: Pattern[str] = re.compile(r'-{1,2}[\w-]+')
NORMALIZED_PARAMETER_PATTERN: Pattern[str] = re.compile(r'--[\w-]+')


def _rudimentary_parameter_normalizer(parameters: Iterable[str]) -> Iterable[str]:
    return sorted(set(parameters).difference(GLOBAL_PARAM_BLOCKLIST))


def _validate_parameters(parameters: Iterable[str], pattern: Pattern[str], error_msg_fmt_str: str):
    for parameter in parameters:
        if not parameter:
            continue
        if not pattern.match(parameter):
            raise ValueError(error_msg_fmt_str.format(parameter=parameter))


class CommandParameterNormalizationScenario():
    parameters = Arguments('parameters', delim=',')
    normalized_parameters = Arguments('normalized_parameters', delim=',')

    def __init__(self,
                 command: Union[str, CommandNormalizationScenario],
                 parameters: ArgumentsType = '',
                 normalized_parameters: ArgumentsType = '',
                 add_global_parameters: bool = False):

        self._command: Union[None, CommandNormalizationScenario] = None

        self.command = command
        self.parameters = parameters
        self.normalized_parameters = normalized_parameters
        self.global_parameters_were_added = add_global_parameters

        global_parameters: List[str] = GLOBAL_PARAMS

        if add_global_parameters:
            self.parameters = self.parameters + global_parameters
            self.normalized_parameters = self.normalized_parameters + global_parameters

        _validate_parameters(
            self.parameters, PARAMETER_PATTERN, 'Invalid parameter: "{parameter}"'
        )
        _validate_parameters(
            self.normalized_parameters, NORMALIZED_PARAMETER_PATTERN, 'Invalid normalized parameter: "{parameter}"'
        )

        # automate some of the more tedious to maintain normalization tasks.
        self.normalized_parameters = _rudimentary_parameter_normalizer(self.normalized_parameters)

    @property
    def command(self) -> str:
        return self._command.command

    @command.setter
    def command(self, value: Union[str, CommandNormalizationScenario]):
        self._command = value
        if not isinstance(value, CommandNormalizationScenario):
            self._command = CommandNormalizationScenario(value)
        return self._command

    @property
    def normalized_command(self) -> str:
        return self._command.normalized_command

    def normalize(self, command_table: dict = CommandTable.CMD_TBL) -> Tuple[str, List[str], List[str]]:
        command, parsed_command = Command.parse(command_table, self.command)
        parameters, unrecognized_parameters = Command.normalize(command, *self.parameters)

        normalized_parameters = list(parameters)
        unrecognized_parameters = list(unrecognized_parameters)

        return parsed_command, normalized_parameters, unrecognized_parameters

    @property
    def unrecognized_parameters(self) -> List[str]:
        parameter_set: Set[str] = set(sorted(parameter for parameter in self.parameters if parameter.startswith('--')))
        parameter_set.difference_update(GLOBAL_PARAM_BLOCKLIST)
        normalized_parameter_set = set(self.normalized_parameters)
        unrecognized_parameters = list(sorted(parameter_set - normalized_parameter_set))

        def is_prefix(token, parameters):
            number_of_matches = len([p for p in parameters if token != p and p.startswith(token)])
            return number_of_matches == 1

        return [
            parameter for parameter in unrecognized_parameters
            if not is_prefix(parameter, normalized_parameter_set)
        ]

    def __repr__(self) -> str:
        attrs = dict(
            command=self.command,
            parameters=self.parameters,
            normalized_parameters=self.normalized_parameters
        )
        return safe_repr(self, attrs)

    def __copy__(self):
        return type(self)(
            self.command,
            self.parameters,
            self.normalized_parameters,
            self.global_parameters_were_added
        )

    def __deepcopy__(self, memo):
        return type(self)(
            deepcopy(self.command, memo),
            deepcopy(self.parameters, memo),
            deepcopy(self.normalized_parameters, memo),
            deepcopy(self.global_parameters_were_added, memo)
        )
