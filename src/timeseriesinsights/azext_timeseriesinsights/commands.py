# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    from azext_timeseriesinsights._client_factory import cf_environment
    timeseriesinsights_environment = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._environments_operations#'
        'EnvironmentsOperations.{}',
        client_factory=cf_environment)
    with self.command_group('tsi environment', timeseriesinsights_environment, client_factory=cf_environment) as g:
        g.custom_command('list', 'timeseriesinsights_environment_list')
        g.custom_show_command('show', 'timeseriesinsights_environment_show')
        g.custom_command('delete', 'timeseriesinsights_environment_delete', confirmation=True)
        g.custom_wait_command('wait', 'timeseriesinsights_environment_show')

    with self.command_group('tsi environment gen1', timeseriesinsights_environment,
                            client_factory=cf_environment) as g:
        g.custom_command('create', 'timeseriesinsights_environment_gen1_create', supports_no_wait=True)
        g.custom_command('update', 'timeseriesinsights_environment_gen1_update', supports_no_wait=True)

    with self.command_group('tsi environment gen2', timeseriesinsights_environment,
                            client_factory=cf_environment) as g:
        g.custom_command('create', 'timeseriesinsights_environment_gen2_create', supports_no_wait=True)
        g.custom_command('update', 'timeseriesinsights_environment_gen2_update', supports_no_wait=True)

    from azext_timeseriesinsights._client_factory import cf_event_source
    timeseriesinsights_event_source = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._event_sources_operations'
        '#EventSourcesOperations.{}',
        client_factory=cf_event_source)
    with self.command_group('tsi event-source', timeseriesinsights_event_source, client_factory=cf_event_source) as g:
        g.custom_command('list', 'timeseriesinsights_event_source_list')
        g.custom_show_command('show', 'timeseriesinsights_event_source_show')
        g.custom_command('delete', 'timeseriesinsights_event_source_delete', confirmation=True)

    with self.command_group('tsi event-source eventhub', timeseriesinsights_event_source,
                            client_factory=cf_event_source) as g:
        g.custom_command('create', 'timeseriesinsights_event_source_event_hub_create')
        g.custom_command('update', 'timeseriesinsights_event_source_event_hub_update')

    with self.command_group('tsi event-source iothub', timeseriesinsights_event_source,
                            client_factory=cf_event_source) as g:
        g.custom_command('create', 'timeseriesinsights_event_source_iot_hub_create')
        g.custom_command('update', 'timeseriesinsights_event_source_iot_hub_update')

    from azext_timeseriesinsights._client_factory import cf_reference_data_set
    timeseriesinsights_reference_data_set = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._reference_data_sets_oper'
        'ations#ReferenceDataSetsOperations.{}',
        client_factory=cf_reference_data_set)
    with self.command_group('tsi reference-data-set', timeseriesinsights_reference_data_set,
                            client_factory=cf_reference_data_set) as g:
        g.custom_command('list', 'timeseriesinsights_reference_data_set_list')
        g.custom_show_command('show', 'timeseriesinsights_reference_data_set_show')
        g.custom_command('create', 'timeseriesinsights_reference_data_set_create')
        g.custom_command('update', 'timeseriesinsights_reference_data_set_update')
        g.custom_command('delete', 'timeseriesinsights_reference_data_set_delete', confirmation=True)

    from azext_timeseriesinsights._client_factory import cf_access_policy
    timeseriesinsights_access_policy = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._access_policies_operatio'
        'ns#AccessPoliciesOperations.{}',
        client_factory=cf_access_policy)
    with self.command_group('tsi access-policy', timeseriesinsights_access_policy,
                            client_factory=cf_access_policy) as g:
        g.custom_command('list', 'timeseriesinsights_access_policy_list')
        g.custom_show_command('show', 'timeseriesinsights_access_policy_show')
        g.custom_command('create', 'timeseriesinsights_access_policy_create')
        g.custom_command('update', 'timeseriesinsights_access_policy_update')
        g.custom_command('delete', 'timeseriesinsights_access_policy_delete', confirmation=True)
