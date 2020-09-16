# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List

from azext_ai_did_you_mean_this._cli_command import CliCommand
from azext_ai_did_you_mean_this._suggestion import Suggestion
from azext_ai_did_you_mean_this.tests.latest.data._command_parameter_normalization_scenario import \
    CommandParameterNormalizationScenario
from azext_ai_did_you_mean_this.tests.latest.data._command_normalization_scenario import \
    CommandNormalizationScenario
from azext_ai_did_you_mean_this.tests.latest.data._scenario import Scenario
from azext_ai_did_you_mean_this.tests.latest.data.user_fault_type import \
    UserFaultType

TEST_SCENARIOS: List[Scenario] = [
    Scenario(
        cli_command=CliCommand('account'),
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

NORMALIZATION_TEST_SCENARIOS: List[CommandParameterNormalizationScenario] = [
    # global + command shorthand parameters with 1 longhand duplicate
    CommandParameterNormalizationScenario(
        command='vm show',
        parameters=['-g', '--name', '-n', '--subscription', '-o'],
        normalized_parameters=['--name', '--resource-group', '--subscription', '--output'],
    ),
    # global + command shorthand parameters with 2 longhand duplicates
    # global parameter prefix
    CommandParameterNormalizationScenario(
        command='vm create',
        parameters=[
            '-z', '--vmss', '--location', '-l', '--nsg', '--subnet',
            '-g', '--name', '-n', '--subscription', '--out', '--ultra-ssd',
            '-h'
        ],
        normalized_parameters=[
            '--zone', '--vmss', '--location', '--nsg', '--subnet', '--name',
            '--resource-group', '--subscription', '--output', '--ultra-ssd-enabled',
            '--help'
        ]
    ),
    # command group + global parameter fallback
    CommandParameterNormalizationScenario(
        command='account',
        add_global_parameters=True
    ),
    # command shorthand parameter
    CommandParameterNormalizationScenario(
        command='account set',
        parameters='-s',
        normalized_parameters='--subscription'
    ),
    # no parameters
    CommandParameterNormalizationScenario(
        command='account set'
    ),
    # global parameter prefixes + duplicate parameters
    CommandParameterNormalizationScenario(
        command='account list',
        parameters=['--out', '--query', '--all', '--all'],
        normalized_parameters=['--output', '--query', '--all']
    ),
    # invalid parameters for command
    CommandParameterNormalizationScenario(
        command='extension list',
        parameters=['--foo', '--bar'],
        normalized_parameters=''
    ),
    # invalid parameter for command + global parameters
    CommandParameterNormalizationScenario(
        command='ai-did-you-mean-this version',
        parameters=['--baz'],
        add_global_parameters=True
    ),
    # global parameters
    CommandParameterNormalizationScenario(
        command='kusto cluster create',
        add_global_parameters=True
    ),
    # parameter shorthand + prefixes
    CommandParameterNormalizationScenario(
        command='group create',
        parameters=['-l', '-n', '--manag', '--tag', '--s'],
        normalized_parameters=['--location', '--resource-group', '--managed-by', '--tags', '--subscription']
    ),
    # invalid command and invalid parameters
    CommandParameterNormalizationScenario(
        CommandNormalizationScenario('Lorem ipsum.', 'Lorem'),
        parameters=['--foo', '--baz']
    ),
    # invalid (empty) command and no parameters
    CommandParameterNormalizationScenario(
        command=''
    )
]
