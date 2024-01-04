# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    with self.command_group('tsi environment') as g:
        from .custom import EnvironmentList
        self.command_table['tsi environment list'] = EnvironmentList(loader=self)

    with self.command_group('tsi environment gen1') as g:
        g.custom_command('create', 'timeseriesinsights_environment_gen1_create', supports_no_wait=True)
        g.custom_command('update', 'timeseriesinsights_environment_gen1_update', supports_no_wait=True)

    with self.command_group('tsi environment gen2') as g:
        g.custom_command('create', 'timeseriesinsights_environment_gen2_create', supports_no_wait=True)
        g.custom_command('update', 'timeseriesinsights_environment_gen2_update', supports_no_wait=True)

    with self.command_group('tsi reference-data-set') as g:
        g.custom_command('create', 'timeseriesinsights_reference_data_set_create')
        from .custom import ReferenceDataSetList
        self.command_table['tsi reference-data-set list'] = ReferenceDataSetList(loader=self)

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
