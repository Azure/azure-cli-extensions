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
    get_three_state_flag
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType
from .vendored_sdks.alertsmanagement.models import ActionType
from ._validators import validate_datetime_format, validate_severity, \
    validate_monitor_condition, validate_signal_type, validate_time_format, \
    validate_monitor_service, validate_alert_rule_name, validate_alert_rule_id, \
    validate_alert_rule_description, validate_alert_context, validate_target_resource, \
    validate_resource_group, validate_resource_type


def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    processing_rule_name = CLIArgumentType(overrides=name_arg_type, help='Name of the alert processing rule.',
                                           id_part='name')

    with self.argument_context('monitor alert-processing-rule create') as c:
        c.argument('processing_rule_name', processing_rule_name)
        c.argument('rule_type', arg_type=get_enum_type(ActionType), help='Indicate type of the alert processing rule')
        c.argument('action_groups', nargs='+', help='List of resource ids (space-delimited) of action groups to add. A use of this argument requires that rule-type is AddActionGroups')
        c.argument('description', nargs='+', help='Description of the alert processing rule')
        c.argument('scopes', nargs='+', required=True, help='List of resource IDs (space-delimited) for scope. The rule will apply to alerts that fired on resources within that scope.')
        c.argument('enabled', arg_type=get_three_state_flag(), help='Indicate if the given alert processing rule is enabled or disabled (default is enabled).')
        c.argument('tags', tags_type)
        c.argument('filter_severity', nargs='+', arg_group='Filter', validator=validate_severity, help='Filter alerts by severity <Sev0, Sev1, Sev2, Sev3, Sev4>')
        c.argument('filter_monitor_service', nargs='+', arg_group='Filter', validator=validate_monitor_service, help='Filter alerts by monitor service')
        c.argument('filter_monitor_condition', nargs='+', arg_group='Filter', validator=validate_monitor_condition, help='Filter alerts by monitor condition')
        c.argument('filter_alert_rule_name', nargs='+', arg_group='Filter', validator=validate_alert_rule_name, help='Filter alerts by alert rule name')
        c.argument('filter_alert_rule_id', nargs='+', arg_group='Filter', validator=validate_alert_rule_id, help='Filter alerts by alert ID')
        c.argument('filter_alert_rule_description', nargs='+', validator=validate_alert_rule_description, arg_group='Filter', help='Filter alerts by alert rule description')
        c.argument('filter_alert_context', nargs='+', arg_group='Filter', validator=validate_alert_context, help='Filter alerts by alert context (payload)')
        c.argument('filter_signal_type', nargs='+', arg_group='Filter', validator=validate_signal_type, help='Filter alerts by signal type')
        c.argument('filter_target_resource', nargs='+', arg_group='Filter', validator=validate_target_resource, help='Filter alerts by resource')
        c.argument('filter_resource_group', nargs='+', arg_group='Filter', validator=validate_resource_group, help='Filter alerts by resource group')
        c.argument('filter_resource_type', nargs='+', arg_group='Filter', validator=validate_resource_type, help='Filter alerts by resource type.')
        c.argument('schedule_start_datetime', arg_group='Schedule', help='Start date for the rule. Format: \'YYYY-MM-DD hh:mm:ss\'', validator=validate_datetime_format)
        c.argument('schedule_end_datetime', arg_group='Schedule', help='End date for the rule. Format: \'YYYY-MM-DD hh:mm:ss\'', validator=validate_datetime_format)
        c.argument('schedule_recurrence_type', arg_group='Schedule First Recurrence', arg_type=get_enum_type(['Daily', 'Weekly', 'Monthly']), help='Specifies when the processing rule should be applied')
        c.argument('schedule_recurrence_start_time', arg_group='Schedule First Recurrence', help='Start time for each recurrence. Format: \'hh:mm:ss\'', validator=validate_time_format)
        c.argument('schedule_recurrence_end_time', arg_group='Schedule First Recurrence', help='End time for each recurrence. Format: \'hh:mm:ss\'', validator=validate_time_format)
        c.argument('schedule_time_zone', arg_group='Schedule', help='schedule time zone')
        c.argument('schedule_recurrence', nargs='+', arg_group='Schedule First Recurrence')
        c.argument('schedule_recurrence_2_type', arg_group='Schedule Second Recurrence', arg_type=get_enum_type(['Daily', 'Weekly', 'Monthly']), help='Specifies when the processing rule should be applied. Default to Always')
        c.argument('schedule_recurrence_2_start_time', arg_group='Schedule Second Recurrence', help='Start time for each recurrence. Format: hh:mm:ss', validator=validate_time_format)
        c.argument('schedule_recurrence_2_end_time', arg_group='Schedule Second Recurrence', help='End time for each recurrence. Format: hh:mm:ss', validator=validate_time_format)
        c.argument('schedule_recurrence_2', nargs='+', arg_group='Schedule Second Recurrence')

    with self.argument_context('monitor alert-processing-rule update') as c:
        c.argument('processing_rule_name', processing_rule_name)
        c.argument('tags', tags_type)
        c.argument('enabled', arg_type=get_three_state_flag(), help='Indicate if the given processing rule is enabled or disabled (values are True and False).')

    with self.argument_context('monitor alert-processing-rule delete') as c:
        c.argument('processing_rule_name', processing_rule_name)

    with self.argument_context('monitor alert-processing-rule show') as c:
        c.argument('processing_rule_name', processing_rule_name)
