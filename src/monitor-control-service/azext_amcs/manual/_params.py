# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    tags_type,
    resource_group_name_type,
    get_location_type
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


def load_arguments(self, _):

    with self.argument_context('monitor data-collection rule association create') as c:
        c.argument('resource_uri', options_list=['--resource'], type=str, help='The identifier of the resource.')
        c.argument('association_name', options_list=['--name', '-n'], type=str, help='The name of the association.')
        c.argument('description', type=str, help='Description of the association.')
        c.argument('rule_id', type=str, help='The resource ID of the data collection rule that is to be associated.')

    with self.argument_context('monitor data-collection rule') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('data_collection_rule_name', options_list=['--name', '-n'], type=str, help='The name of the data '
                   'collection rule. The name is case insensitive.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('description', type=str, help='Description of the data collection rule.')

        c.argument('data_flows', action=AddDataFlows, options_list=['--data-flow'], arg_group="Data Flow",
                   nargs='+', help='The specification of data flows.')

        c.argument('destinations_log_analytics', options_list=['--log-analytics'], arg_group="Destinations",
                   action=AddDestinationsLogAnalytics, nargs='+', help='List of Log Analytics destinations.')
        c.argument('destinations_azure_monitor_metrics', options_list=['--monitor-metrics'], arg_group="Destinations",
                   action=AddDestinationsAzureMonitorMetrics, nargs='+', help='Azure Monitor Metrics destination.')

        c.argument('data_sources_performance_counters', options_list=['--performance-counter'],
                   arg_group="Data Sources", action=AddDataSourcesPerformanceCounters, nargs='+',
                   help='The list of performance counter data source configurations.')
        c.argument('data_sources_windows_event_logs', options_list=['--windows-event-log'], arg_group="Data Sources",
                   action=AddDataSourcesWindowsEventLogs, nargs='+', help='The list of Windows Event Log data source '
                   'configurations.')
        c.argument('data_sources_syslog', options_list=['--syslog'], arg_group="Data Sources",
                   action=AddDataSourcesSyslog, nargs='+', help='The list of Syslog data source configurations.')
        c.argument('data_sources_extensions', options_list=['--extensions'], arg_group="Data Sources",
                   type=validate_file_or_dict, help='The list of Azure VM extension data source configurations. '
                   'Expected value: json-string/@json-file.')

    with self.argument_context('monitor data-collection rule create') as c:
        c.argument('data_collection_rule_name', id_part=None)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
