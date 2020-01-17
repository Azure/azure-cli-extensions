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
    with self.command_group('alertsmanagement operation', alertsmanagement_operations, client_factory=cf_operations) as g:
        g.custom_command('list', 'list_alertsmanagement_operation')

    from ._client_factory import cf_alerts
    alertsmanagement_alerts = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._alerts_operations#AlertsOperations.{}',
        client_factory=cf_alerts)
    with self.command_group('alertsmanagement alert', alertsmanagement_alerts, client_factory=cf_alerts) as g:
        g.custom_command('change-state', 'change_state_alertsmanagement_alert')
        g.custom_command('meta-data', 'meta_data_alertsmanagement_alert')
        g.custom_command('get-all', 'get_all_alertsmanagement_alert')
        g.custom_command('get-by-id', 'get_by_id_alertsmanagement_alert')
        g.custom_command('get-history', 'get_history_alertsmanagement_alert')
        g.custom_command('get-summary', 'get_summary_alertsmanagement_alert')

    from ._client_factory import cf_smart_groups
    alertsmanagement_smart_groups = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._smart_groups_operations#SmartGroupsOperations.{}',
        client_factory=cf_smart_groups)
    with self.command_group('alertsmanagement smart-group', alertsmanagement_smart_groups, client_factory=cf_smart_groups) as g:
        g.custom_command('change-state', 'change_state_alertsmanagement_smart_group')
        g.custom_command('get-all', 'get_all_alertsmanagement_smart_group')
        g.custom_command('get-by-id', 'get_by_id_alertsmanagement_smart_group')
        g.custom_command('get-history', 'get_history_alertsmanagement_smart_group')

    from ._client_factory import cf_action_rules
    alertsmanagement_action_rules = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._action_rules_operations#ActionRulesOperations.{}',
        client_factory=cf_action_rules)
    with self.command_group('alertsmanagement action-rule', alertsmanagement_action_rules, client_factory=cf_action_rules) as g:
        g.custom_command('create', 'create_alertsmanagement_action_rule')
        g.custom_command('update', 'update_alertsmanagement_action_rule')
        g.custom_command('delete', 'delete_alertsmanagement_action_rule')
        g.custom_show_command('show', 'get_alertsmanagement_action_rule')
        g.custom_command('list', 'list_alertsmanagement_action_rule')

    from ._client_factory import cf_smart_detector_alert_rules
    alertsmanagement_smart_detector_alert_rules = CliCommandType(
        operations_tmpl='azext_alertsmanagement.vendored_sdks.alertsmanagement.operations._smart_detector_alert_rules_operations#SmartDetectorAlertRulesOperations.{}',
        client_factory=cf_smart_detector_alert_rules)
    with self.command_group('alertsmanagement smart-detector-alert-rule', alertsmanagement_smart_detector_alert_rules, client_factory=cf_smart_detector_alert_rules) as g:
        g.custom_command('create', 'create_alertsmanagement_smart_detector_alert_rule')
        g.custom_command('update', 'update_alertsmanagement_smart_detector_alert_rule')
        g.custom_command('delete', 'delete_alertsmanagement_smart_detector_alert_rule')
        g.custom_show_command('show', 'get_alertsmanagement_smart_detector_alert_rule')
        g.custom_command('list', 'list_alertsmanagement_smart_detector_alert_rule')
