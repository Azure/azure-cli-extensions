# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.transform import gen_dict_to_list_transform


def load_command_table(self, _):

    with self.command_group('timeseriesinsights', is_experimental=True) as g:
        pass

    # region environment
    from ._client_factory import cf_environments
    timeseriesinsights_environments = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._environments_operations#EnvironmentsOperations.{}',
        client_factory=cf_environments)

    with self.command_group('timeseriesinsights environment standard', timeseriesinsights_environments, client_factory=cf_environments) as g:
        g.custom_command('create', 'create_timeseriesinsights_environment_standard',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#StandardEnvironmentCreateOrUpdateParameters",
                         supports_no_wait=True)
        g.custom_command('update', 'update_timeseriesinsights_environment_standard',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#StandardEnvironmentCreateOrUpdateParameters",
                         supports_no_wait=True)

    with self.command_group('timeseriesinsights environment longterm', timeseriesinsights_environments, client_factory=cf_environments) as g:
        g.custom_command('create', 'create_timeseriesinsights_environment_longterm',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#LongTermEnvironmentCreateOrUpdateParameters",
                         supports_no_wait=True)
        g.custom_command('update', 'update_timeseriesinsights_environment_longterm',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#LongTermEnvironmentUpdateParameters",
                         supports_no_wait=True)

    with self.command_group('timeseriesinsights environment', timeseriesinsights_environments, client_factory=cf_environments) as g:
        g.command('delete', 'delete', confirmation=True)
        g.show_command('show', 'get')
        g.custom_command('list', 'list_timeseriesinsights_environment', transform=gen_dict_to_list_transform(key='value'))
    # endregion

    # region event-source
    from ._client_factory import cf_event_sources
    timeseriesinsights_event_sources = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._event_sources_operations#EventSourcesOperations.{}',
        client_factory=cf_event_sources)

    with self.command_group('timeseriesinsights event-source eventhub', timeseriesinsights_event_sources, client_factory=cf_event_sources) as g:
        g.custom_command('create', 'create_timeseriesinsights_event_source_eventhub',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#EventHubEventSourceCreateOrUpdateParameters")
        g.custom_command('update', 'update_timeseriesinsights_event_source_eventhub',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#EventHubEventSourceUpdateParameters")

    with self.command_group('timeseriesinsights event-source iothub', timeseriesinsights_event_sources, client_factory=cf_event_sources) as g:
        g.custom_command('create', 'create_timeseriesinsights_event_source_iothub',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#IoTHubEventSourceCreateOrUpdateParameters")
        g.custom_command('update', 'update_timeseriesinsights_event_source_iothub',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#IoTHubEventSourceUpdateParameters")

    with self.command_group('timeseriesinsights event-source', timeseriesinsights_event_sources, client_factory=cf_event_sources) as g:
        g.command('delete', 'delete', confirmation=True)
        g.show_command('show', 'get')
        g.command('list', 'list_by_environment')
    # endregion

    # region reference-data-set
    from ._client_factory import cf_reference_data_sets
    timeseriesinsights_reference_data_sets = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._reference_data_sets_operations#ReferenceDataSetsOperations.{}',
        client_factory=cf_reference_data_sets)

    with self.command_group('timeseriesinsights reference-data-set', timeseriesinsights_reference_data_sets, client_factory=cf_reference_data_sets) as g:
        g.custom_command('create', 'create_timeseriesinsights_reference_data_set',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#ReferenceDataSetCreateOrUpdateParameters")
        g.custom_command('update', 'update_timeseriesinsights_reference_data_set')
        g.command('delete', 'delete', confirmation=True)
        g.show_command('show', 'get')
        g.command('list', 'list_by_environment')
    # endregion

    # region access-policy
    from ._client_factory import cf_access_policies
    timeseriesinsights_access_policies = CliCommandType(
        operations_tmpl='azext_timeseriesinsights.vendored_sdks.timeseriesinsights.operations._access_policies_operations#AccessPoliciesOperations.{}',
        client_factory=cf_access_policies)
    with self.command_group('timeseriesinsights access-policy', timeseriesinsights_access_policies, client_factory=cf_access_policies) as g:
        g.custom_command('create', 'create_timeseriesinsights_access_policy',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#AccessPolicyCreateOrUpdateParameters")
        g.custom_command('update', 'update_timeseriesinsights_access_policy',
                         doc_string_source="azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models#AccessPolicyUpdateParameters")
        g.command('delete', 'delete', confirmation=True)
        g.show_command('show', 'get')
        g.command('list', 'list_by_environment')
    # endregion
