# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from typing_extensions import Required
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_three_state_flag
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType
from .vendored_sdks.alertsmanagement.models import ActionType, MonitorCondition, Severity, SignalType, Operator
from ._validators import validate_datetime_format, validate_severity, validate_monitor_condition, validate_signal_type, validate_time_format

def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    processing_rule_name = CLIArgumentType(overrides=name_arg_type, help='Name of the alert processing rule.',
                                       id_part='name')

    with self.argument_context('monitor alert-processing-rule create') as c:
        c.argument('processing_rule_name', processing_rule_name)
        c.argument('rule_type', arg_type=get_enum_type(ActionType), help='Indicate type of the alert processing rule')
        c.argument('action_groups',nargs='+', help='List of ARM IDs (space-delimited) of action groups to add. A use of this argument requires that rule-type is AddActionGroups')
        c.argument('description', nargs='+', help='Description of the alert processing rule')
        c.argument('scopes', nargs='+', required=True, help='List of ARM IDs (space-delimited) of the given scopes type which will be the target of the given processing rule.')
        c.argument('enabled', arg_type=get_three_state_flag(), help='Indicate if the given alert processing rule is enabled or disabled (values are True and False). Default True.')
        c.argument('tags', tags_type)
        c.argument('filter_severity', nargs='+', validator = validate_severity, help='Filter alerts by severity. All filters should follow format "operator value1 value2 ... valueN". Operator is one of Equals, NotEquals, Contains and DoesNotContain.')
        c.argument('filter_monitor_service', nargs='+', help='Filter alerts by monitor service')
        c.argument('filter_monitor_condition', nargs='+', validator = validate_monitor_condition, help='Filter alerts by monitor condition')
        c.argument('filter_alert_rule_name', nargs='+', help='Filter alerts by alert rule name')
        c.argument('filter_alert_rule_id', nargs='+', help='Filter alerts by alert ID')
        c.argument('filter_alert_rule_description', nargs='+', help='Filter alerts by alert rule description')
        c.argument('filter_alert_context', nargs='+', help='Filter alerts by alert context (payload)')
        c.argument('filter_signal_type', nargs='+', validator = validate_signal_type, help='Filter alerts by signal type')
        c.argument('filter_target_resource', nargs='+', help='Filter alerts by resource')
        c.argument('filter_resource_group', nargs='+', help='Filter alerts by resource group')
        c.argument('filter_resource_type', nargs='+', help='Filter alerts by resource type. All filters should follow format "operator value1 value2 ... valueN". Operator values: Equals, NotEquals, Contains and DoesNotContain.')
        c.argument('schedule_recurrence_type', arg_type=get_enum_type(['Daily', 'Weekly', 'Monthly']), help='Specifies when the processing rule should be applied. Default to Always')
        c.argument('schedule_start_datetime', help='Start date for the rule. Format: \'YYYY-MM-DD hh:mm:ss\'', validator = validate_datetime_format)
        c.argument('schedule_end_datetime', help='End date for the rule. Format: \'YYYY-MM-DD hh:mm:ss\'', validator = validate_datetime_format)
        c.argument('schedule_recurrence_start_time', help='Start time for the rule. Format: hh:mm:ss', validator = validate_time_format)
        c.argument('schedule_recurrence_end_time', help='End time for the rule. Format: hh:mm:ss', validator = validate_time_format)
        c.argument('schedule_time_zone', help='schedule time zone')
        c.argument('schedule_recurrence', nargs='+',
                           help='List of recurrence pattern values, delimited by space. If --schedule-recurrence-type is '
                                'Weekly, allowed values range from Sunday to Saturday. If --schedule-recurrence-type is Monthly, allowed values range from '
                                '1 to 31, stands for day of month')
        c.argument('schedule_recurrence_2_type', arg_type=get_enum_type(['Daily', 'Weekly', 'Monthly']), help='Specifies when the processing rule should be applied. Default to Always')
        c.argument('schedule_recurrence_2_start_time', help='Start time for enabling the rule. Format: hh:mm:ss', validator = validate_time_format)
        c.argument('schedule_recurrence_2_end_time', help='End time for disabling the rule. Format: hh:mm:ss', validator = validate_time_format)
        c.argument('schedule_recurrence_2', nargs='+',
                           help='List of recurrence pattern values, delimited by space. If --schedule-recurrence-type is '
                                'Weekly, allowed values range from Sunday to Saturday. If --schedule-recurrence-type is Monthly, allowed values range from '
                                '1 to 31, stands for day of month')

    with self.argument_context('monitor alert-processing-rule update') as c:
        c.argument('processing_rule_name', processing_rule_name)
        c.argument('tags', tags_type)
        c.argument('enabled', arg_type=get_three_state_flag(), help='Indicate if the given processing rule is enabled or disabled (values are True and False).')

    with self.argument_context('monitor alert-processing-rule delete') as c:
        c.argument('processing_rule_name', processing_rule_name)

    with self.argument_context('monitor alert-processing-rule show') as c:
        c.argument('processing_rule_name', processing_rule_name)
