# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import network_client_factory


def add_nw_connection_monitor_v2_endpoint(cmd,
                                          client,
                                          watcher_rg,
                                          watcher_name,
                                          connection_monitor_name,
                                          location,
                                          endpoint_name,
                                          resource_id=None,
                                          address=None,
                                          filter_type=None,
                                          filter_items=None):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    ConnectionMonitorEndpoint, ConnectionMonitorEndpointFilter, ConnectionMonitorEndpointFilterItem = cmd.get_models(
        'ConnectionMonitorEndpoint', 'ConnectionMonitorEndpointFilter', 'ConnectionMonitorEndpointFilterItem')

    endpoint_filter = ConnectionMonitorEndpointFilter(type=filter_type)

    endpoint = ConnectionMonitorEndpoint(name=endpoint_name,
                                         resource_id=resource_id,
                                         address=address)
