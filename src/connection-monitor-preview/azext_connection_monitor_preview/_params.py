# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import get_enum_type

from ._validators import NWConnectionMonitorEndpointFilterItemAction


def load_arguments(self, _):
    name_arg_type = CLIArgumentType(options_list=['--name', '-n'], metavar='NAME')

    ConnectionMonitorEndpointFilterType = self.get_models('ConnectionMonitorEndpointFilterType')

    with self.argument_context('network watcher') as c:
        c.argument('network_watcher_name', name_arg_type, help='Name of the Network Watcher.')
        c.argument('location', validator=None)
        c.ignore('watcher_rg')
        c.ignore('watcher_name')

    with self.argument_context('network watcher connection-monitor') as c:
        c.argument('connection_monitor_name', options_list=['--connection-monitor'], help='Connection monitor name.')

    with self.argument_context('network watcher connection-monitor endpoint', min_api='2019-11-01') as c:
        c.argument('endpoint_name',
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
                        "Property type supports 'AgentAddress' only now.")
