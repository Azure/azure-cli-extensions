# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    with self.command_group('monitor data-collection', is_preview=True):
        pass

    from azext_amcs.generated._client_factory import cf_data_collection_rule_association
    monitor_control_service_data_collection_rule_association = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rule_associations_operations#DataCol'
                        'lectionRuleAssociationsOperations.{}',
        client_factory=cf_data_collection_rule_association)
    with self.command_group('monitor data-collection rule association',
                            monitor_control_service_data_collection_rule_association,
                            client_factory=cf_data_collection_rule_association) as g:
        g.custom_command('create', 'data_collection_rule_associations_create')
        g.generic_update_command('update', custom_func_name='data_collection_rule_associations_update')

    from azext_amcs.generated._client_factory import cf_data_collection_rule
    monitor_control_service_data_collection_rule = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rules_operations#DataCollectionRules'
                        'Operations.{}',
        client_factory=cf_data_collection_rule)
    with self.command_group('monitor data-collection rule', monitor_control_service_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_command(
            'list', 'data_collection_rules_list')
        g.custom_command(
            'create', 'data_collection_rules_create')
        g.generic_update_command(
            'update', setter_name='create', custom_func_name='data_collection_rules_update')

    with self.command_group('monitor data-collection rule data-flow', monitor_control_service_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command(
            'list', 'data_collection_rules_data_flows_list')
        g.generic_update_command(
            'add', 'data_collection_rules_data_flows_add')

    with self.command_group('monitor data-collection rule log-analytics', monitor_control_service_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command(
            'list', 'data_collection_rules_log_analytics_list')
        g.custom_show_command(
            'show', 'data_collection_rules_log_analytics_show')
        g.generic_update_command(
            'add', 'data_collection_rules_log_analytics_add')
        g.generic_update_command(
            'delete', 'data_collection_rules_log_analytics_delete')
        g.generic_update_command(
            'update', 'data_collection_rules_log_analytics_update')

    with self.command_group('monitor data-collection rule performance-counter', monitor_control_service_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command(
            'list', 'data_collection_rules_performance_counters_list')
        g.custom_show_command(
            'show', 'data_collection_rules_performance_counters_show')
        g.generic_update_command(
            'add', 'data_collection_rules_performance_counters_add')
        g.generic_update_command(
            'delete', 'data_collection_rules_performance_counters_delete')
        g.generic_update_command(
            'update', 'data_collection_rules_performance_counters_update')

    with self.command_group('monitor data-collection rule windows-event-log', monitor_control_service_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command(
            'list', 'data_collection_rules_windows_event_logs_list')
        g.custom_show_command(
            'show', 'data_collection_rules_windows_event_logs_show')
        g.generic_update_command(
            'add', 'data_collection_rules_windows_event_logs_add')
        g.generic_update_command(
            'delete', 'data_collection_rules_windows_event_logs_delete')
        g.generic_update_command(
            'update', 'data_collection_rules_windows_event_logs_update')

    with self.command_group('monitor data-collection rule syslog', monitor_control_service_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command(
            'list', 'data_collection_rules_syslog_list')
        g.custom_show_command(
            'show', 'data_collection_rules_syslog_show')
        g.generic_update_command(
            'add', 'data_collection_rules_syslog_add')
        g.generic_update_command(
            'delete', 'data_collection_rules_syslog_delete')
        g.generic_update_command(
            'update', 'data_collection_rules_syslog_update')
