
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, protected-access, too-few-public-methods

import argparse
from typing import Dict, List
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from knack.util import CLIError


class ScriptExecutionNamedOutputAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        namespace.named_outputs = script_execution_named_outputs(values)


def script_execution_named_outputs(values: List[str]) -> Dict[str, str]:
    try:
        return dict(map(lambda x: x.split('=', 1), values))
    except ValueError as error:
        raise CLIError('parsing named output parameter \'{}\''.format(values)) from error


class ScriptExecutionParameterAction(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parameter = script_execution_parameters(values)
        if namespace.parameters:
            namespace.parameters.append(parameter)
        else:
            namespace.parameters = [parameter]


def script_execution_parameters(values: List[str]):
    values = dict(map(lambda x: x.split('=', 1), values))
    tp = require(values, "type")
    type_lower = tp.lower()
    if type_lower == "Value".lower():
        try:
            return {
                "name": require(values, "name"),
                "value": {
                    "value": values.get("value")
                }
            }
        except CLIError as error:
            raise InvalidArgumentValueError('parsing {} script execution parameter'.format('Value')) from error

    elif type_lower == "SecureValue".lower():
        try:
            return {
                "name": require(values, "name"),
                "secure_value": {
                    "secure_value": values.get("secureValue")
                }
            }
        except CLIError as error:
            raise InvalidArgumentValueError('parsing {} script execution parameter'.format('SecureValue')) from error

    elif type_lower == "Credential".lower():
        try:
            return {
                "name": require(values, "name"),
                "credential": {
                    "username": values.get("username"),
                    "password": values.get("password"),
                }
            }
        except CLIError as error:
            raise InvalidArgumentValueError('parsing {} script execution parameter'.format('Credential')) from error
    else:
        raise InvalidArgumentValueError('script execution paramater type \'{}\' not matched'.format(tp))


def require(values: Dict[str, str], key: str) -> str:
    '''Gets the required script execution parameter or raises a CLIError.'''
    value = values.get(key)
    if value is None:
        raise RequiredArgumentMissingError('script execution parameter \'{}\' required'.format(key))
    return value
