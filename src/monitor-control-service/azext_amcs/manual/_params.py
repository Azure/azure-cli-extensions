# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type,
    get_enum_type
)
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group,
    validate_file_or_dict
)
from azext_amcs.action import (
    AddDataFlows,
    AddDestinationsLogAnalytics,
    AddDestinationsAzureMonitorMetrics,
    AddDataSourcesPerformanceCounters,
    AddDataSourcesWindowsEventLogs,
    AddDataSourcesSyslog
)


from azext_amcs.vendored_sdks.amcs.models import KnownDataFlowStreams, KnownPerfCounterDataSourceStreams, \
    KnownWindowsEventLogDataSourceStreams, KnownSyslogDataSourceStreams, \
    KnownSyslogDataSourceFacilityNames, KnownSyslogDataSourceLogLevels


def load_arguments(self, _):

    with self.argument_context('monitor data-collection endpoint') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('data_collection_endpoint_name', options_list=['--name', '-n'], type=str,
                   help='The name of the data collection endpoint. The name is case insensitive.', id_part='name')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('kind', arg_type=get_enum_type(['Linux', 'Windows']), help='The kind of the resource.')
        c.argument('description', type=str, help='Description of the data collection endpoint.')
        c.argument('public_network_access', arg_type=get_enum_type(['Enabled', 'Disabled']),
                   help='The configuration to set whether network access from public internet to the endpoints '
                        'are allowed.',
                   arg_group='Network Acls')

    with self.argument_context('monitor data-collection endpoint create') as c:
        c.argument('data_collection_endpoint_name', id_part=None)

    with self.argument_context('monitor data-collection rule association') as c:
        c.argument('resource_uri', options_list=['--resource'], help='The identifier of the resource.')
        c.argument('association_name', options_list=['--name', '-n'], help='The name of the association.')
        c.argument('description', help='Description of the association.')
        c.argument('rule_id', help='The resource ID of the data collection rule that is to be associated.')
        c.argument('data_collection_rule_name', options_list=['--rule-name'])

    with self.argument_context('monitor data-collection rule association list') as c:
        c.argument('data_collection_rule_name', options_list=['--rule-name'], id_part=None)

    with self.argument_context('monitor data-collection rule') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('data_collection_rule_name', options_list=['--name', '-n'], help='The name of the data '
                   'collection rule. The name is case insensitive.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('description', help='Description of the data collection rule.')

        c.argument('data_flows', action=AddDataFlows, options_list=['--data-flows'], arg_group="Data Flow",
                   nargs='+', help='The specification of data flows.')

        c.argument('destinations__log_analytics', options_list=['--log-analytics'], arg_group="Destinations",
                   action=AddDestinationsLogAnalytics, nargs='+', help='List of Log Analytics destinations.')
        c.argument('destinations__azure_monitor_metrics', options_list=['--monitor-metrics'], arg_group="Destinations",
                   action=AddDestinationsAzureMonitorMetrics, nargs='+', help='Azure Monitor Metrics destination.')

        c.argument('data_sources__performance_counters', options_list=['--performance-counters'],
                   arg_group="Data Sources", action=AddDataSourcesPerformanceCounters, nargs='+',
                   help='The list of performance counter data source configurations.')
        c.argument('data_sources__windows_event_logs', options_list=['--windows-event-logs'], arg_group="Data Sources",
                   action=AddDataSourcesWindowsEventLogs, nargs='+', help='The list of Windows Event Log data source '
                   'configurations.')
        c.argument('data_sources__syslog', options_list=['--syslog'], arg_group="Data Sources",
                   action=AddDataSourcesSyslog, nargs='+', help='The list of Syslog data source configurations.')
        c.argument('data_sources__extensions', options_list=['--extensions'], arg_group="Data Sources",
                   type=validate_file_or_dict, help='The list of Azure VM extension data source configurations. '
                   'Expected value: json-string/@json-file.')

    with self.argument_context('monitor data-collection rule list') as c:
        c.argument('data_collection_rule_name', id_part=None)

    with self.argument_context('monitor data-collection rule create') as c:
        c.argument('data_collection_rule_name', id_part=None)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)

    with self.argument_context('monitor data-collection rule data-flow') as c:
        c.argument('data_collection_rule_name', options_list=['--rule-name'])
        c.argument('streams', options_list=['--streams'], arg_type=get_enum_type(KnownDataFlowStreams),
                   nargs='+', help='List of streams for this data flow.')
        c.argument('destinations', options_list=['--destinations'], nargs='+',
                   help='List of destinations for this data flow.')

    with self.argument_context('monitor data-collection rule data-flow list') as c:
        c.argument('data_collection_rule_name', id_part=None)

    with self.argument_context('monitor data-collection rule log-analytics') as c:
        c.argument('data_collection_rule_name', options_list=['--rule-name'])
        c.argument('name', options_list=['--name', '-n'],
                   help='A friendly name for the destination. This name should be unique across all destinations '
                   '(regardless of type) within the data collection rule.')
        c.argument('workspace_resource_id', options_list=['--resource-id'],
                   help='The resource ID of the Log Analytics workspace.')

    with self.argument_context('monitor data-collection rule log-analytics list') as c:
        c.argument('data_collection_rule_name', id_part=None)

    with self.argument_context('monitor data-collection rule performance-counter') as c:
        c.argument('data_collection_rule_name', options_list=['--rule-name'])
        c.argument('name', options_list=['--name', '-n'],
                   help='A friendly name for the data source. This name should be unique across all data sources '
                   '(regardless of type) within the data collection rule.')
        c.argument('streams', options_list=['--streams'], arg_type=get_enum_type(KnownPerfCounterDataSourceStreams),
                   nargs='+', help='List of streams that this data source will be sent to. A stream '
                   'indicates what schema will be used for this data and usually what table in Log Analytics the data '
                   'will be sent to.')
        c.argument('sampling_frequency_in_seconds', options_list=['--sampling-frequency'], type=int,
                   help='The number of seconds between consecutive counter measurements (samples).')
        c.argument('counter_specifiers', options_list=['--counter-specifiers'], nargs='+',
                   help="A list of specifier names of the performance counters you want to collect."
                   "Use a wildcard (*) to collect a counter for all instances. "
                   "To get a list of performance counters on Windows, run the command 'typeperf'.")

    with self.argument_context('monitor data-collection rule performance-counter list') as c:
        c.argument('data_collection_rule_name', id_part=None)

    with self.argument_context('monitor data-collection rule windows-event-log') as c:
        c.argument('data_collection_rule_name', options_list=['--rule-name'])
        c.argument('name', options_list=['--name', '-n'],
                   help='A friendly name for the data source. This name should be unique across all data sources '
                   '(regardless of type) within the data collection rule.')
        c.argument('streams', options_list=['--streams'], arg_type=get_enum_type(KnownWindowsEventLogDataSourceStreams),
                   nargs='+', help='List of streams that this data source will be sent to. A stream '
                   'indicates what schema will be used for this data and usually what table in Log Analytics the data '
                   'will be sent to.')
        c.argument('x_path_queries', options_list=['--x-path-queries'], nargs='+',
                   help='A list of Windows Event Log queries in XPATH format.')

    with self.argument_context('monitor data-collection rule windows-event-log list') as c:
        c.argument('data_collection_rule_name', id_part=None)

    with self.argument_context('monitor data-collection rule syslog') as c:
        c.argument('data_collection_rule_name', options_list=['--rule-name'])
        c.argument('name', options_list=['--name', '-n'],
                   help='A friendly name for the data source. This name should be unique across all data sources '
                   '(regardless of type) within the data collection rule.')
        c.argument('streams', options_list=['--streams'], arg_type=get_enum_type(KnownSyslogDataSourceStreams),
                   nargs='+', help='List of streams that this data source will be sent to. A stream '
                   'indicates what schema will be used for this data and usually what table in Log Analytics the data '
                   'will be sent to.')
        c.argument('facility_names', options_list=['--facility-names'],
                   arg_type=get_enum_type(KnownSyslogDataSourceFacilityNames), nargs='+',
                   help='The list of facility names.')
        c.argument('log_levels', options_list=['--log-levels'], arg_type=get_enum_type(KnownSyslogDataSourceLogLevels),
                   nargs='+', help='The log levels to collect.')

    with self.argument_context('monitor data-collection rule syslog list') as c:
        c.argument('data_collection_rule_name', id_part=None)
