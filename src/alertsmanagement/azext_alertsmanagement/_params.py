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
    resource_group_name_type,
    get_location_type
)
from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    action_rule_name = CLIArgumentType(overrides=name_arg_type, help='Name of action rule.',
                                       id_part='name')

    with self.argument_context('alertsmanagement action-rule create') as c:
        c.argument('action_rule_name', action_rule_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='Indicates if the given action rule is enabled or disabled')
        c.argument('rule_type', arg_type=get_enum_type(['Suppression', 'ActionGroup', 'Diagnostics']), help='Indicates type of action rule')
        c.argument('description', help='Description of action rule')
        c.argument('scope_type', help='Type of target scope', arg_type=get_enum_type(['ResourceGroup', 'Resource']))
        c.argument('scope', nargs='+', help='List of ARM IDs (space-delimited) of the given scope type which will be the target of the given action rule.')
        c.argument('severity', nargs='+', help='Filter alerts by severity. All filters should follow format "operator value1 value2 ... valueN". Operator is one of Equals, NotEquals, Contains and DoesNotContain.')
        c.argument('monitor_service', nargs='+', help='Filter alerts by monitor service')
        c.argument('monitor_condition', nargs='+', help='Filter alerts by monitor condition')
        c.argument('target_resource_type', nargs='+', help='Filter alerts by target resource type')
        c.argument('alert_rule_id', nargs='+', help='Filter alerts by alert rule ID')
        c.argument('alert_description', nargs='+', help='Filter alerts by alert rule description')
        c.argument('alert_context', nargs='+', help='Filter alerts by alert context (payload)')
        c.argument('recurrence_type', arg_type=get_enum_type(['Always', 'Once', 'Daily', 'Weekly', 'Monthly']), help='Specifies when the suppression should be applied')
        c.argument('start_date', help='Start date for suppression')
        c.argument('end_date', help='End date for suppression')
        c.argument('start_time', help='Start time for suppression')
        c.argument('end_time', help='End date for suppression')

    with self.argument_context('alertsmanagement action-rule update') as c:
        c.argument('action_rule_name', action_rule_name)
        c.argument('location', arg_type=get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)
        c.argument('status', arg_type=get_enum_type(['Enabled', 'Disabled']), id_part=None, help='Indicates if the given action rule is enabled or disabled')

    with self.argument_context('alertsmanagement action-rule delete') as c:
        c.argument('action_rule_name', action_rule_name)

    with self.argument_context('alertsmanagement action-rule show') as c:
        c.argument('action_rule_name', action_rule_name)

    with self.argument_context('alertsmanagement action-rule list') as c:
        c.argument('target_resource_group', id_part=None, help='Filter by target resource group name. Default value is select all.')
        c.argument('target_resource_type', id_part=None, help='Filter by target resource type. Default value is select all.')
        c.argument('target_resource', id_part=None, help='Filter by target resource( which is full ARM ID) Default value is select all.')
        c.argument('severity', id_part=None, help='Filter by severity.  Default value is select all.')
        c.argument('monitor_service', id_part=None, help='Filter by monitor service which generates the alert instance. Default value is select all.')
        c.argument('impacted_scope', id_part=None, help='Filter by impacted/target scope (provide comma separated list for multiple scopes). The value should be an well constructed ARM id of the scope.')
        c.argument('description', id_part=None, help='Filter by alert rule description')
        c.argument('alert_rule_id', id_part=None, help='Filter by alert rule id')
        c.argument('action_group', id_part=None, help='Filter by action group configured as part of action rule')
        c.argument('name', id_part=None, help='Filter by action rule name')
