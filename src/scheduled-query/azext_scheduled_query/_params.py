# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import tags_type, get_three_state_flag
from azure.cli.command_modules.monitor.actions import get_period_type
from azure.cli.command_modules.monitor.validators import get_action_group_validator
from knack.arguments import CLIArgumentType
from ._actions import ScheduleQueryConditionAction, ScheduleQueryAddAction


def load_arguments(self, _):

    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')
    with self.argument_context('monitor scheduled-query') as c:
        c.argument('rule_name', name_arg_type, id_part='name', help='Name of the scheduled query rule.')
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('severity', type=int, help='Severity of the alert from 0 (critical) to 4 (verbose).')
        c.argument('window_size', type=get_period_type(), help='Time over which to aggregate metrics in "##h##m##s" format.')
        c.argument('evaluation_frequency', type=get_period_type(), help='Frequency with which to evaluate the rule in "##h##m##s" format.')
        c.argument('condition', options_list=['--condition'], action=ScheduleQueryConditionAction, nargs='+')
        c.argument('description', help='Free-text description of the rule.')
        c.argument('scopes', nargs='+', help='Space-separated list of scopes the rule applies to. '
                                             'The resources specified in this parameter must be of the same type and exist in the same location.')
        c.argument('disabled', arg_type=get_three_state_flag(), help='Disable the scheduled query.')
        c.argument('target_resource_type', options_list=['--target-resource-type', '--type'],
                   help='The resource type of the target resource(s) in scopes. '
                        'This must be provided when scopes is resource group or subscription.')
        c.argument('mute_actions_duration', type=get_period_type(as_timedelta=True),
                   options_list=['--mute-actions-duration', '--mad'],
                   help='Mute actions for the chosen period of time (in ISO 8601 duration format) after the alert is fired.')
        c.argument('actions', options_list=['--action', '-a'], action=ScheduleQueryAddAction, nargs='+', validator=get_action_group_validator('actions'))
