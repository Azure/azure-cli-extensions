# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType
#from .vendored_sdks.alertsmanagement.models import ActionRuleStatus, SuppressionType
from .vendored_sdks.alertsmanagement.models import ActionType, MonitorCondition, Severity, SignalType

def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    processing_rule_name = CLIArgumentType(overrides=name_arg_type, help='Name of action rule.',
                                       id_part='name')

    with self.argument_context('monitor action-rule create') as c:
        c.argument('processing_rule_name', processing_rule_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('description', help='Description of action rule')
        c.argument('rule_type', arg_type=get_enum_type(ActionType), help='Indicate type of action rule')
        c.argument('scopes', nargs='+', help='List of ARM IDs (space-delimited) of the given scopes type which will be the target of the given action rule.')
        c.argument('enabled', nargs='+', arg_type=get_enum_type(['True', 'False']), help='Indicate if the given processing rule is enabled or disabled (values are True and False). Default True.')
        c.argument('severity', nargs='+', arg_type=get_enum_type(Severity), help='Filter alerts by severity. All filters should follow format "operator value1 value2 ... valueN". Operator is one of Equals, NotEquals, Contains and DoesNotContain.')
        c.argument('monitor_service', nargs='+', help='Filter alerts by monitor service')
        c.argument('monitor_condition', nargs='+', arg_type=get_enum_type(MonitorCondition), help='Filter alerts by monitor condition')
        c.argument('alert_rule', nargs='+', help='Filter alerts by alert rule name or ID')
        c.argument('alert_description', nargs='+', help='Filter alerts by alert rule description')
        c.argument('alert_context', nargs='+', help='Filter alerts by alert context (payload)')
        c.argument('signal_type', nargs='+', arg_type=get_enum_type(SignalType), help='Filter alerts by signal type')
        c.argument('resource_filter', nargs='+', help='Filter alerts by resource')
        c.argument('resource_group_filter', nargs='+', help='Filter alerts by resource group')
        c.argument('resource_type', nargs='+', help='Filter alerts by resource type. All filters should follow format "operator value1 value2 ... valueN". Operator is one of Equals, NotEquals, Contains and DoesNotContain.')
        c.argument('schedule_recurrence_type', arg_type=get_enum_type(['Always', 'Once', 'Daily', 'Weekly', 'Monthly']), help='Specifies when the suppression should be applied')
        c.argument('schedule_start_date', nargs='+', help='Start date for enabling the rule. Format: MM/DD/YYYY')
        c.argument('schedule_end_date', nargs='+', help='End date for disabling the rule. Format: MM/DD/YYYY')
        c.argument('schedule_start_time', nargs='+', help='Start time for enabling the rule. Format: hh:mm:ss')
        c.argument('schedule_end_time', nargs='+', help='End time for disabling the rule. Format: hh:mm:ss')
        c.argument('schedule_recurrence', nargs='+',
                           help='List of recurrence pattern values, delimited by space. If --schedule-recurrence-type is '
                                'Weekly, allowed values range from 0 to 6. 0 stands for Sunday, 1 stands for Monday, ..., 6 '
                                'stands for Saturday. If --schedule-recurrence-type is Monthly, allowed values range from '
                                '1 to 31, stands for day of month')

    with self.argument_context('monitor action-rule update') as c:
        c.argument('processing_rule_name', processing_rule_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='Indicates if the given action rule is enabled or disabled')

    with self.argument_context('monitor action-rule delete') as c:
        c.argument('processing_rule_name', processing_rule_name)

    with self.argument_context('monitor action-rule show') as c:
        c.argument('processing_rule_name', processing_rule_name)
