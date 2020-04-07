# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
from azext_alertsmanagement.vendored_sdks.alertsmanagement.models import ActionRuleStatus, SuppressionType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    action_rule_name = CLIArgumentType(overrides=name_arg_type, help='Name of action rule.',
                                       id_part='name')

    with self.argument_context('monitor action-rule create') as c:
        c.argument('action_rule_name', action_rule_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(ActionRuleStatus), id_part=None, help='Indicate if the given action rule is enabled or disabled. Default to enabled.')
        c.argument('rule_type', arg_type=get_enum_type(['Suppression', 'ActionGroup', 'Diagnostics']), help='Indicate type of action rule')
        c.argument('description', help='Description of action rule')
        c.argument('scope_type', help='Type of target scope', arg_type=get_enum_type(['ResourceGroup', 'Resource']))
        c.argument('scope', nargs='+', help='List of ARM IDs (space-delimited) of the given scope type which will be the target of the given action rule.')
        c.argument('severity', nargs='+', help='Filter alerts by severity. All filters should follow format "operator value1 value2 ... valueN". Operator is one of Equals, NotEquals, Contains and DoesNotContain.')
        c.argument('monitor_service', nargs='+', help='Filter alerts by monitor service')
        c.argument('monitor_condition', nargs='+', help='Filter alerts by monitor condition')
        c.argument('target_resource_type', nargs='+', help='Filter alerts by target resource type')
        c.argument('alert_rule', nargs='+', help='Filter alerts by alert rule name or ID')
        c.argument('alert_description', nargs='+', help='Filter alerts by alert rule description')
        c.argument('alert_context', nargs='+', help='Filter alerts by alert context (payload)')
        c.argument('suppression_recurrence_type', arg_type=get_enum_type(SuppressionType), help='Specifies when the suppression should be applied')
        c.argument('suppression_start_date', help='Start date for suppression. Format: MM/DD/YYYY')
        c.argument('suppression_end_date', help='End date for suppression. Format: MM/DD/YYYY')
        c.argument('suppression_start_time', help='Start time for suppression. Format: hh:mm:ss')
        c.argument('suppression_end_time', help='End time for suppression. Format: hh:mm:ss')
        c.argument('suppression_recurrence', nargs='+',
                   help='List of recurrence pattern values, delimited by space. If --suppression-recurrence-type is '
                        'Weekly, allowed values range from 0 to 6. 0 stands for Sunday, 1 stands for Monday, ..., 6 '
                        'stands for Saturday. If --suppression-recurrence-type is Monthly, allowed values range from '
                        '1 to 31, stands for day of month')

    with self.argument_context('monitor action-rule update') as c:
        c.argument('action_rule_name', action_rule_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='Indicates if the given action rule is enabled or disabled')

    with self.argument_context('monitor action-rule delete') as c:
        c.argument('action_rule_name', action_rule_name)

    with self.argument_context('monitor action-rule show') as c:
        c.argument('action_rule_name', action_rule_name)

    with self.argument_context('monitor action-rule list') as c:
        c.argument('target_resource_group', id_part=None, help='Filter by target resource group name. Default value is select all.')
        c.argument('target_resource_type', id_part=None, help='Filter by target resource type. Default value is select all.')
        c.argument('target_resource', id_part=None, help='Filter by target resource (which is full ARM ID). Default value is select all.')
        c.argument('severity', id_part=None, help='Filter by severity. Default value is select all.')
        c.argument('monitor_service', id_part=None, help='Filter by monitor service which generates the alert instance. Default value is select all.')
        c.argument('impacted_scope', id_part=None, help='Filter by impacted/target scope (provide comma separated list for multiple scopes). The value should be an well constructed ARM id of the scope.')
        c.argument('description', id_part=None, help='Filter by alert rule description')
        c.argument('alert_rule_id', id_part=None, help='Filter by alert rule ID')
        c.argument('action_group', id_part=None, help='Filter by action group configured as part of action rule')
        c.argument('name', id_part=None, help='Filter by action rule name')
