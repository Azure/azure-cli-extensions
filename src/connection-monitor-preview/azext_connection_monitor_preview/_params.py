# pylint: disable=too-many-statements
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType, ignore_type
from azure.cli.core.commands.parameters import (tags_type,
                                                get_enum_type,
                                                get_location_type,
                                                get_three_state_flag)

from ._validators import (get_network_watcher_from_location,
                          NWConnectionMonitorEndpointFilterItemAction,
                          NWConnectionMonitorTestConfigurationHTTPRequestHeaderAction)


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    (ConnectionMonitorEndpointFilterType, ConnectionMonitorTestConfigurationProtocol,
     PreferredIPVersion, HTTPConfigurationMethod,
     OutputType) = self.get_models(
         'ConnectionMonitorEndpointFilterType', 'ConnectionMonitorTestConfigurationProtocol',
         'PreferredIPVersion', 'HTTPConfigurationMethod',
         'OutputType')

    with self.argument_context('network') as c:
        c.argument('tags', tags_type)

    with self.argument_context('network watcher') as c:
        c.argument('network_watcher_name', name_arg_type, help='Name of the Network Watcher.')
        c.argument('location', validator=None)
        c.ignore('watcher_rg')
        c.ignore('watcher_name')

    with self.argument_context('network watcher connection-monitor') as c:
        c.argument('network_watcher_name', arg_type=ignore_type, options_list=['--__NETWORK_WATCHER_NAME'])
        c.argument('connection_monitor_name', name_arg_type, help='Connection monitor name.')

    with self.argument_context('network watcher connection-monitor', arg_group='V1 Endpoint') as c:
        c.argument('source_resource', help='Name or ID of the resource from which to originate traffic. '
                                           'Currently only Virtual Machines are supported.')
        c.argument('source_port', help='Port number from which to originate traffic.')
        c.argument('dest_resource', help='Name of ID of the resource to receive traffic. '
                                         'Currently only Virtual Machines are supported.')
        c.argument('dest_port', help='Port number on which to receive traffic.')
        c.argument('dest_address', help='The IP address or URI at which to receive traffic.')
        c.argument('monitoring_interval', help='Monitoring interval in seconds.', type=int, default=60)
        c.argument('do_not_start', action='store_true',
                   help='Create the connection monitor but do not start it immediately.')

    nw_validator = get_network_watcher_from_location(remove=True, watcher_name='network_watcher_name',
                                                     rg_name='resource_group_name')
    for scope in ['list', 'show', 'start', 'stop', 'delete', 'query']:
        with self.argument_context('network watcher connection-monitor {}'.format(scope)) as c:
            c.extra('location', get_location_type(self.cli_ctx), required=True)
            c.argument('resource_group_name', arg_type=ignore_type, validator=nw_validator)

    # with self.argument_context('network watcher connection-monitor create', arg_group='V1') as c:
    #     c.argument('monitoring_interval', help='Monitoring interval in seconds.', type=int, default=60)
    #     c.argument('do_not_start', action='store_true',
    #                help='Create the connection monitor but do not start it immediately.')
        # c.ignore('location')

    with self.argument_context('network watcher connection-monitor', min_api='2019-11-01', arg_group='V2') as c:
        c.argument('notes', help='Optional notes to be associated with the connection monitor')

    # Argument Group for endpoint to create a V2 connection monitor
    with self.argument_context('network watcher connection-monitor',
                               arg_group='V2 Endpoint',
                               min_api='2019-11-01') as c:
        c.argument('endpoint_dest_name',
                   help='The name of the source of connection monitor endpoint. '
                        'If you are creating a V2 Connection Monitor, it\'s required')
        c.argument('endpoint_dest_resource_id',
                   help='Resource ID of the source of connection monitor endpoint')
        c.argument('endpoint_dest_address',
                   help='Address of the source of connection monitor endpoint (IP or domain name)')
        c.argument('endpoint_source_name',
                   help='The name of the destination of connection monitor endpoint. '
                        'If you are creating a V2 Connection Monitor, it\'s required')
        c.argument('endpoint_source_resource_id',
                   help='Resource ID of the destination of connection monitor endpoint. '
                        'If endpoint is intended to used as source, this option is required.')
        c.argument('endpoint_source_address',
                   help='Address of the destination of connection monitor endpoint (IP or domain name)')

    # Argument Group for test configuration to create a V2 connection monitor
    with self.argument_context('network watcher connection-monitor',
                               arg_group='V2 Test Configuration',
                               min_api='2019-11-01') as c:
        c.argument('test_config_name',
                   help='The name of the connection monitor test configuration. '
                        'If you are creating a V2 Connection Monitor, it\'s required')
        c.argument('test_config_frequency',
                   options_list='--frequency',
                   help='The frequency of test evaluation, in seconds',
                   type=int,
                   default=60)
        c.argument('test_config_protocol',
                   options_list='--protocol',
                   help='The protocol to use in test evaluation',
                   arg_type=get_enum_type(ConnectionMonitorTestConfigurationProtocol))
        c.argument('test_config_preferred_ip_version',
                   options_list='--preferred-ip-version',
                   help='The preferred IP version to use in test evaluation. '
                        'The connection monitor may choose to use a different version depending on other parameters',
                   arg_type=get_enum_type(PreferredIPVersion))
        c.argument('test_config_threshold_failed_percent',
                   options_list='--threshold-failed-percent',
                   help='The maximum percentage of failed checks permitted for a test to evaluate as successful',
                   type=int)
        c.argument('test_config_threshold_round_trip_time',
                   options_list='--threshold-round-trip-time',
                   help='The maximum round-trip time in milliseconds permitted for a test to evaluate as successful',
                   type=int)
        # TCP protocol configuration
        c.argument('test_config_tcp_port',
                   options_list='--tcp-port',
                   help='The port to connect to',
                   type=int)
        c.argument('test_config_tcp_disable_trace_route',
                   options_list='--tcp-disable-trace-route',
                   help='Value indicating whether path evaluation with trace route should be disabled. '
                        'false is default.',
                   arg_type=get_three_state_flag())
        # ICMP protocol configuration
        c.argument('test_config_icmp_disable_trace_route',
                   options_list='--icmp-disable-trace-route',
                   help='Value indicating whether path evaluation with trace route should be disabled. '
                        'false is default.',
                   arg_type=get_three_state_flag())
        # HTTP protocol configuration
        c.argument('test_config_http_port',
                   options_list='--http-port',
                   help='The port to connect to',
                   type=int)
        c.argument('test_config_http_method',
                   options_list='--http-method',
                   help='The HTTP method to use',
                   arg_type=get_enum_type(HTTPConfigurationMethod))
        c.argument('test_config_http_path',
                   options_list='--http-path',
                   help='The path component of the URI. For instance, "/dir1/dir2"')
        c.argument('test_config_http_valid_status_codes',
                   options_list='--http-valid-status-codes',
                   help='Space-separated list of HTTP status codes to consider successful. '
                        'For instance, "2xx 301-304 418"',
                   nargs='+')
        c.argument('test_config_http_prefer_https',
                   options_list='--https-prefer',
                   help='Value indicating whether HTTPS is preferred '
                        'over HTTP in cases where the choice is not explicit',
                   arg_type=get_three_state_flag())

    # Argument Group for test group to create a V2 connection monitor
    with self.argument_context('network watcher connection-monitor',
                               arg_group='V2 Test Group',
                               min_api='2019-11-01') as c:
        c.argument('test_group_name',
                   help='The name of the connection monitor test group',
                   default='DefaultTestGroup')
        c.argument('test_group_disable',
                   help='Value indicating whether test group is disabled. false is default.',
                   arg_type=get_three_state_flag())

    # Argument Group for output to create a V2 connection monitor
    with self.argument_context('network watcher connection-monitor',
                               arg_group='V2 Output',
                               min_api='2019-11-01') as c:
        c.argument('output_type',
                   help='Connection monitor output destination type. Currently, only "Workspace" is supported',
                   arg_type=get_enum_type(OutputType))
        c.argument('workspace_ids',
                   help='Space-separated list of ids of log analytics workspace',
                   nargs='+')

    # Argument Group for connection monitor V2 endpoint
    with self.argument_context('network watcher connection-monitor endpoint', min_api='2019-11-01') as c:
        c.argument('connection_monitor_name',
                   options_list=['--connection-monitor'],
                   help='Connection monitor name.')
        c.argument('name',
                   arg_type=name_arg_type,
                   help='The name of the connection monitor endpoint')
        c.argument('resource_id',
                   help='Resource ID of the connection monitor endpoint')
        c.argument('address',
                   help='Address of the connection monitor endpoint (IP or domain name)')
        c.argument('filter_type',
                   arg_type=get_enum_type(ConnectionMonitorEndpointFilterType),
                   help="The behavior of the endpoint filter. Currently only 'Include' is supported.")
        c.argument('filter_items',
                   options_list=['--filter-item'],
                   action=NWConnectionMonitorEndpointFilterItemAction,
                   nargs='+',
                   help="List of property=value pairs to define filter items. "
                        "Property currently include: type, address. "
                        "Property value of type supports 'AgentAddress' only now.")

    with self.argument_context('network watcher connection-monitor endpoint',
                               min_api='2019-11-01',
                               arg_group='V2 Test Group') as c:
        c.argument('test_groups',
                   nargs='+',
                   help='Space-separated list of names of test group which only need to be affected if specified')
        c.argument('source_test_groups',
                   nargs='+',
                   help='Space-separated list of names for test group to reference as source')
        c.argument('dest_test_groups',
                   nargs='+',
                   help='Space-separated list of names for test group to reference as destination')

    # Argument Group for connection monitor V2 test configuration
    with self.argument_context('network watcher connection-monitor test-configuration',
                               min_api='2019-11-01') as c:
        c.argument('connection_monitor_name',
                   options_list=['--connection-monitor'],
                   help='Connection monitor name')
        c.argument('name',
                   arg_type=name_arg_type,
                   help='The name of the connection monitor test configuration')
        c.argument('frequency',
                   help='The frequency of test evaluation, in seconds',
                   type=int,
                   default=60)
        c.argument('protocol',
                   help='The protocol to use in test evaluation',
                   arg_type=get_enum_type(ConnectionMonitorTestConfigurationProtocol))
        c.argument('preferred_ip_version',
                   help='The preferred IP version to use in test evaluation. '
                        'The connection monitor may choose to use a different version depending on other parameters',
                   arg_type=get_enum_type(PreferredIPVersion))
        c.argument('threshold_failed_percent',
                   help='The maximum percentage of failed checks permitted for a test to evaluate as successful',
                   type=int)
        c.argument('threshold_round_trip_time',
                   help='The maximum round-trip time in milliseconds permitted for a test to evaluate as successful',
                   type=int)
        c.argument('test_groups',
                   help='Space-separated list of names of test group which only need to be affected if specified',
                   nargs='+')
        # TCP protocol configuration
        with self.argument_context('network watcher connection-monitor test-configuration',
                                   min_api='2019-11-01',
                                   arg_group='TCP Protocol') as c:
            c.argument('tcp_port',
                       help='The port to connect to',
                       type=int)
            c.argument('tcp_disable_trace_route',
                       help='Value indicating whether path evaluation with trace route should be disabled. '
                            'false is default.',
                       arg_type=get_three_state_flag())
        # ICMP protocol configuration
        with self.argument_context('network watcher connection-monitor test-configuration',
                                   min_api='2019-11-01',
                                   arg_group='ICMP Protocol') as c:
            c.argument('icmp_disable_trace_route',
                       help='Value indicating whether path evaluation with trace route should be disabled. '
                            'false is default.',
                       arg_type=get_three_state_flag())
        # HTTP protocol configuration
        with self.argument_context('network watcher connection-monitor test-configuration',
                                   min_api='2019-11-01',
                                   arg_group='HTTP Protocol') as c:
            c.argument('http_port',
                       help='The port to connect to',
                       type=int)
            c.argument('http_method',
                       help='The HTTP method to use',
                       arg_type=get_enum_type(HTTPConfigurationMethod))
            c.argument('http_path',
                       help='The path component of the URI. For instance, "/dir1/dir2"')
            c.argument('http_valid_status_codes',
                       nargs='+',
                       help='Space-separated list of HTTP status codes to consider successful. '
                            'For instance, "2xx 301-304 418"')
            c.argument('http_prefer_https',
                       help='Value indicating whether HTTPS is preferred '
                            'over HTTP in cases where the choice is not explicit',
                       arg_type=get_three_state_flag())
            c.argument('http_request_headers',
                       options_list=['--http-request-header'],
                       help='The HTTP headers to transmit with the request. '
                            'List of property=value pairs to define HTTP headers.',
                       nargs='+',
                       action=NWConnectionMonitorTestConfigurationHTTPRequestHeaderAction)

    with self.argument_context('network watcher connection-monitor test-group', min_api='2019-11-01') as c:
        c.argument('connection_monitor_name',
                   options_list=['--connection-monitor'],
                   help='Connection monitor name.')
        c.argument('name',
                   arg_type=name_arg_type,
                   help='The name of the connection monitor test group')
        c.argument('disable',
                   help='Value indicating whether test group is disabled. false is default.',
                   arg_type=get_three_state_flag())

    with self.argument_context('network watcher connection-monitor output', min_api='2019-11-01') as c:
        c.argument('connection_monitor_name',
                   options_list=['--connection-monitor'],
                   help='Connection monitor name.')
        c.argument('out_type',
                   options_list=['--type'],
                   help='Connection monitor output destination type. Currently, only "Workspace" is supported',
                   arg_type=get_enum_type(OutputType))
        c.argument('workspace_id', help='The id of log analytics workspace')
