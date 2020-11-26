# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    from azext_amcs.generated._client_factory import cf_data_collection_rule_association
    data_collection_data_collection_rule_association = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rule_associations_operations#DataCol'
        'lectionRuleAssociationsOperations.{}',
        client_factory=cf_data_collection_rule_association)
    with self.command_group('monitor data-collection rule association',
                            data_collection_data_collection_rule_association,
                            client_factory=cf_data_collection_rule_association) as g:
        g.custom_command('list', 'monitor_data_collection_rule_association_list')
        g.custom_show_command('show', 'monitor_data_collection_rule_association_show')
        g.custom_command('delete', 'monitor_data_collection_rule_association_delete', confirmation=True)
        g.custom_command('create', 'monitor_data_collection_rule_association_create')
        g.generic_update_command('update', custom_func_name='monitor_data_collection_rule_association_update')

    from azext_amcs.generated._client_factory import cf_data_collection_rule
    data_collection_data_collection_rule = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rules_operations#DataCollectionRules'
        'Operations.{}',
        client_factory=cf_data_collection_rule)
    with self.command_group('monitor data-collection rule', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_command('list', 'monitor_data_collection_rule_list')
        g.custom_show_command('show', 'monitor_data_collection_rule_show')
        g.custom_command('delete', 'monitor_data_collection_rule_delete', confirmation=True)
        g.custom_command('create', 'monitor_data_collection_rule_create')
        g.generic_update_command('update', setter_name='create', custom_func_name='monitor_data_collection_rule_update')

    with self.command_group('monitor data-collection rule data-flow', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'monitor_data_collection_rule_data_flow_list')
        g.generic_update_command('add', 'monitor_data_collection_rule_data_flow_add')

    with self.command_group('monitor data-collection rule log-analytics', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'monitor_data_collection_rule_log_analytics_list')
        g.custom_show_command('show', 'monitor_data_collection_rule_log_analytics_show')
        g.generic_update_command('add', 'monitor_data_collection_rule_log_analytics_add')
        g.generic_update_command('delete', 'monitor_data_collection_rule_log_analytics_delete')
        g.generic_update_command('update', 'monitor_data_collection_rule_log_analytics_update')

    with self.command_group('monitor data-collection rule performance-counter', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'monitor_data_collection_rule_performance_counter_list')
        g.custom_show_command('show', 'monitor_data_collection_rule_performance_counter_show')
        g.generic_update_command('add', 'monitor_data_collection_rule_performance_counter_add')
        g.generic_update_command('delete', 'monitor_data_collection_rule_performance_counter_delete')
        g.generic_update_command('update', 'monitor_data_collection_rule_performance_counter_update')

    with self.command_group('monitor data-collection rule windows-event-log', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'monitor_data_collection_rule_windows_event_log_list')
        g.custom_show_command('show', 'monitor_data_collection_rule_windows_event_log_show')
        g.generic_update_command('add', 'monitor_data_collection_rule_windows_event_log_add')
        g.generic_update_command('delete', 'monitor_data_collection_rule_windows_event_log_delete')
        g.generic_update_command('update', 'monitor_data_collection_rule_windows_event_log_update')

    with self.command_group('monitor data-collection rule syslog', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'monitor_data_collection_rule_syslog_list')
        g.custom_show_command('show', 'monitor_data_collection_rule_syslog_show')
        g.generic_update_command('add', 'monitor_data_collection_rule_syslog_add')
        g.generic_update_command('delete', 'monitor_data_collection_rule_syslog_delete')
        g.generic_update_command('update', 'monitor_data_collection_rule_syslog_update')
