# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType, ignore_type
from azure.cli.core.commands.parameters import get_enum_type, get_location_type

from ._validators import get_network_watcher_from_location, NWConnectionMonitorEndpointFilterItemAction


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    ConnectionMonitorEndpointFilterType = self.get_models('ConnectionMonitorEndpointFilterType')

    with self.argument_context('network watcher') as c:
        c.argument('network_watcher_name', name_arg_type, help='Name of the Network Watcher.')
        c.argument('location', validator=None)
        c.ignore('watcher_rg')
        c.ignore('watcher_name')

    with self.argument_context('network watcher connection-monitor') as c:
        c.argument('network_watcher_name', arg_type=ignore_type, options_list=['--__NETWORK_WATCHER_NAME'])
        c.argument('connection_monitor_name', name_arg_type, help='Connection monitor name.')

    with self.argument_context('network watcher connection-monitor', arg_group='V1 Source') as c:
        c.argument('source_resource', help='Name or ID of the resource from which to originate traffic.')
        c.argument('source_port', help='Port number from which to originate traffic.')

    with self.argument_context('network watcher connection-monitor', arg_group='V1 Destination') as c:
        c.argument('dest_resource', help='Name of ID of the resource to receive traffic.')
        c.argument('dest_port', help='Port number on which to receive traffic.')
        c.argument('dest_address', help='The IP address or URI at which to receive traffic.')

    nw_validator = get_network_watcher_from_location(remove=True, watcher_name='network_watcher_name',
                                                     rg_name='resource_group_name')
    for scope in ['list', 'show', 'start', 'stop', 'delete', 'query']:
        with self.argument_context('network watcher connection-monitor {}'.format(scope)) as c:
            c.extra('location', get_location_type(self.cli_ctx), required=True)
            c.argument('resource_group_name', arg_type=ignore_type, validator=nw_validator)

    with self.argument_context('network watcher connection-monitor create', arg_group='V1') as c:
        c.argument('monitoring_interval', help='Monitoring interval in seconds.', type=int)
        c.argument('do_not_start', action='store_true',
                   help='Create the connection monitor but do not start it immediately.')
        # c.ignore('location')

    with self.argument_context('network watcher connection-monitor endpoint', arg_group='V2 Endpoint',
                               min_api='2019-11-01') as c:
        c.argument('connection_monitor_name',
                   options_list=['--connection-monitor'],
                   help='Connection monitor name.')
        c.argument('name',
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

    # with self.argument_context('network watcher connection-monitor create', arg_group='V2 Test Configuration',
    #                            min_api='2019-11-01') as c:
    #     pass
