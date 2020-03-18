# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ._client_factory import cf_action_rules
    alertsmanagement_action_rules = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._action_rules_operations'
                        '#ActionRulesOperations.{}',
        client_factory=cf_action_rules)
    with self.command_group('monitor action-rule', alertsmanagement_action_rules, client_factory=cf_action_rules,
                            is_preview=True) as g:
        g.custom_command('create', 'create_alertsmanagement_action_rule')
        g.generic_update_command('update', custom_func_name='update_alertsmanagement_action_rule',
                                 setter_arg_name='action_rule', getter_name='get_by_name',
                                 setter_name='create_update')
        g.custom_command('delete', 'delete_alertsmanagement_action_rule')
        g.custom_show_command('show', 'get_alertsmanagement_action_rule')
        g.custom_command('list', 'list_alertsmanagement_action_rule')
