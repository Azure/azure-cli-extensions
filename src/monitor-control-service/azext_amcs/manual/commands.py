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
        g.custom_command('delete', 'insights__data_collection_rule_associations__delete', confirmation=True)
        g.generic_update_command('update', custom_func_name='insights__data_collection_rule_associations__update')

    from azext_amcs.generated._client_factory import cf_data_collection_rule
    data_collection_data_collection_rule = CliCommandType(
        operations_tmpl='azext_amcs.vendored_sdks.amcs.operations._data_collection_rules_operations#DataCollectionRules'
        'Operations.{}',
        client_factory=cf_data_collection_rule)
    with self.command_group('monitor data-collection rule', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_command('create', 'insights__data_collection_rules__create')
        g.generic_update_command('update', setter_name='create',
                                 custom_func_name='insights__data_collection_rules__update')

    with self.command_group('monitor data-collection rule data-flow', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'insights__data_collection_rules__2__data_flows__list')
        g.generic_update_command('add', 'insights__data_collection_rules__2__data_flows__add')

    with self.command_group('monitor data-collection rule log-analytics', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'insights__data_collection_rules__2__destinations__log_analytics__list')
        g.custom_show_command('show', 'insights__data_collection_rules__2__destinations__log_analytics__show')
        g.generic_update_command('add', 'insights__data_collection_rules__2__destinations__log_analytics__add')
        g.generic_update_command('delete', 'insights__data_collection_rules__2__destinations__log_analytics__delete')
        g.generic_update_command('update', 'insights__data_collection_rules__2__destinations__log_analytics__update')

    with self.command_group('monitor data-collection rule performance-counter', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'insights__data_collection_rules__2__data_sources__performance_counters__list')
        g.custom_show_command('show', 'insights__data_collection_rules__2__data_sources__performance_counters__show')
        g.generic_update_command('add', 'insights__data_collection_rules__2__data_sources__performance_counters__add')
        g.generic_update_command(
            'delete', 'insights__data_collection_rules__2__data_sources__performance_counters__delete')
        g.generic_update_command(
            'update', 'insights__data_collection_rules__2__data_sources__performance_counters__update')

    with self.command_group('monitor data-collection rule windows-event-log', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'insights__data_collection_rules__2__data_sources__windows_event_logs__list')
        g.custom_show_command('show', 'insights__data_collection_rules__2__data_sources__windows_event_logs__show')
        g.generic_update_command('add', 'insights__data_collection_rules__2__data_sources__windows_event_logs__add')
        g.generic_update_command(
            'delete', 'insights__data_collection_rules__2__data_sources__windows_event_logs__delete')
        g.generic_update_command(
            'update', 'insights__data_collection_rules__2__data_sources__windows_event_logs__update')

    with self.command_group('monitor data-collection rule syslog', data_collection_data_collection_rule,
                            client_factory=cf_data_collection_rule) as g:
        g.custom_show_command('list', 'insights__data_collection_rules__2__data_sources__syslog__list')
        g.custom_show_command('show', 'insights__data_collection_rules__2__data_sources__syslog__show')
        g.generic_update_command('add', 'insights__data_collection_rules__2__data_sources__syslog__add')
        g.generic_update_command('delete', 'insights__data_collection_rules__2__data_sources__syslog__delete')
        g.generic_update_command('update', 'insights__data_collection_rules__2__data_sources__syslog__update')
