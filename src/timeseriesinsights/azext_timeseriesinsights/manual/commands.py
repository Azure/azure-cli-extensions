# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    from azext_timeseriesinsights.generated._client_factory import cf_environment
    timeseriesinsights_environment = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._environments_operations#'
        'EnvironmentsOperations.{}',
        client_factory=cf_environment)
    with self.command_group('timeseriesinsights environment gen1', timeseriesinsights_environment,
                            client_factory=cf_environment) as g:
        g.custom_command('create', 'timeseriesinsights_environment_gen1_create', supports_no_wait=True)
        g.custom_command('update', 'timeseriesinsights_environment_gen1_update', supports_no_wait=True)
    
    with self.command_group('timeseriesinsights environment gen2', timeseriesinsights_environment,
                            client_factory=cf_environment) as g:
        g.custom_command('create', 'timeseriesinsights_environment_gen2_create', supports_no_wait=True)
        g.custom_command('update', 'timeseriesinsights_environment_gen2_update', supports_no_wait=True)

    from azext_timeseriesinsights.generated._client_factory import cf_event_source
    timeseriesinsights_event_source = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._event_sources_operations'
        '#EventSourcesOperations.{}',
        client_factory=cf_event_source)
    with self.command_group('timeseriesinsights event-source event-hub', timeseriesinsights_event_source,
                            client_factory=cf_event_source) as g:
        g.custom_command('create', 'timeseriesinsights_event_source_event_hub_create')
        g.custom_command('update', 'timeseriesinsights_event_source_event_hub_update')
    
    with self.command_group('timeseriesinsights event-source iot-hub', timeseriesinsights_event_source,
                            client_factory=cf_event_source) as g:
        g.custom_command('create', 'timeseriesinsights_event_source_iot_hub_create')
        g.custom_command('update', 'timeseriesinsights_event_source_iot_hub_update')
