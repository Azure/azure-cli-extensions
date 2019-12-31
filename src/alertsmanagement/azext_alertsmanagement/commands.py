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

    from ._client_factory import cf_operations
    alertsmanagement_operations = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._operations_operations#OperationsOperations.{}',
        client_factory=cf_operations)
    with self.command_group('alertsmanagement', alertsmanagement_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_alertsmanagement')

    from ._client_factory import cf_alerts
    alertsmanagement_alerts = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._alerts_operations#AlertsOperations.{}',
        client_factory=cf_alerts)
    with self.command_group('alertsmanagement changestate', alertsmanagement_alerts, client_factory=cf_alerts) as g:
        g.custom_command('change_state', 'change_state_alertsmanagement_changestate')
        g.custom_command('meta_data', 'meta_data_alertsmanagement_changestate')
        g.custom_command('get_all', 'get_all_alertsmanagement_changestate')
        g.custom_command('get_by_id', 'get_by_id_alertsmanagement_changestate')
        g.custom_command('get_history', 'get_history_alertsmanagement_changestate')
        g.custom_command('get_summary', 'get_summary_alertsmanagement_changestate')

    from ._client_factory import cf_smart_groups
    alertsmanagement_smart_groups = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._smart_groups_operations#SmartGroupsOperations.{}',
        client_factory=cf_smart_groups)
    with self.command_group('alertsmanagement change-state', alertsmanagement_smart_groups, client_factory=cf_smart_groups) as g:
        g.custom_command('change_state', 'change_state_alertsmanagement_change_state')
        g.custom_command('get_all', 'get_all_alertsmanagement_change_state')
        g.custom_command('get_by_id', 'get_by_id_alertsmanagement_change_state')
        g.custom_command('get_history', 'get_history_alertsmanagement_change_state')

    from ._client_factory import cf_action_rules
    alertsmanagement_action_rules = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._action_rules_operations#ActionRulesOperations.{}',
        client_factory=cf_action_rules)
    with self.command_group('alertsmanagement', alertsmanagement_action_rules, client_factory=cf_action_rules) as g:
        g.custom_command('create', 'create_alertsmanagement')
        g.custom_command('update', 'update_alertsmanagement')
        g.custom_command('delete', 'delete_alertsmanagement')
        g.custom_command('show', 'get_alertsmanagement')
        g.custom_command('list', 'list_alertsmanagement')

    from ._client_factory import cf_smart_detector_alert_rules
    alertsmanagement_smart_detector_alert_rules = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._smart_detector_alert_rules_operations#SmartDetectorAlertRulesOperations.{}',
        client_factory=cf_smart_detector_alert_rules)
    with self.command_group('alertsmanagement', alertsmanagement_smart_detector_alert_rules, client_factory=cf_smart_detector_alert_rules) as g:
        g.custom_command('create', 'create_alertsmanagement')
        g.custom_command('update', 'update_alertsmanagement')
        g.custom_command('delete', 'delete_alertsmanagement')
        g.custom_command('show', 'get_alertsmanagement')
        g.custom_command('list', 'list_alertsmanagement')
