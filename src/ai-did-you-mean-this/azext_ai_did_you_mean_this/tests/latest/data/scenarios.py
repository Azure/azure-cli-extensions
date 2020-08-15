# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List
from azext_ai_did_you_mean_this._cli_command import CliCommand
from azext_ai_did_you_mean_this._suggestion import Suggestion
from azext_ai_did_you_mean_this.tests.latest.data._scenario import Scenario
from azext_ai_did_you_mean_this.tests.latest.data.user_fault_type import UserFaultType

TEST_SCENARIOS: List[Scenario] = [
    Scenario(
        cli_command=CliCommand('account', '', ''),
        expected_user_fault_type=UserFaultType.MISSING_REQUIRED_SUBCOMMAND,
        suggestions=[
            Suggestion('account list'),
            Suggestion('account show'),
            Suggestion('account set', '--subscription', 'Subscription')
        ]
    ),
    Scenario(
        cli_command=CliCommand('account get-access-token', ['--test', '--debug'], 'a'),
        expected_user_fault_type=UserFaultType.UNRECOGNIZED_ARGUMENTS
    ),
    Scenario(
        cli_command=CliCommand('ai-did-you-mean-this ve'),
        expected_user_fault_type=UserFaultType.NOT_IN_A_COMMAND_GROUP,
        extension='ai-did-you-mean-this'
    ),
    Scenario(
        cli_command=CliCommand('ai-did-you-mean-this version', '--name', '"Christopher"'),
        expected_user_fault_type=UserFaultType.UNRECOGNIZED_ARGUMENTS,
        extension='ai-did-you-mean-this'
    ),
    Scenario(
        cli_command=CliCommand('boi'),
        expected_user_fault_type=UserFaultType.NOT_IN_A_COMMAND_GROUP
    ),
    Scenario(
        cli_command=CliCommand('extension'),
        expected_user_fault_type=UserFaultType.MISSING_REQUIRED_SUBCOMMAND,
        suggestions=[
            Suggestion('extension list')
        ]
    ),
    Scenario(
        cli_command=CliCommand('vm', '--debug'),
        expected_user_fault_type=UserFaultType.MISSING_REQUIRED_SUBCOMMAND
    ),
    Scenario(
        cli_command=CliCommand('vm list', '--query', '".id"'),
        expected_user_fault_type=UserFaultType.INVALID_JMESPATH_QUERY,
        suggestions=[
            Suggestion('vm list', ['--output', '--query'], ['json', '"[].id"'])
        ]
    ),
    Scenario(
        cli_command=CliCommand('vm show', ['--name', '--ids'], '"BigJay"'),
        expected_user_fault_type=UserFaultType.EXPECTED_AT_LEAST_ONE_ARGUMENT
    ),
]
