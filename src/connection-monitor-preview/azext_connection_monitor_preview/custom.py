# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from ._client_factory import network_client_factory


def create_nw_connection_monitor_v2(cmd,
                                    client,
                                    connection_monitor_name,
                                    watcher_rg,
                                    watcher_name,
                                    resource_group_name=None,
                                    location=None,
                                    source_resource=None,
                                    source_port=None,
                                    dest_resource=None,
                                    dest_port=None,
                                    dest_address=None,
                                    tags=None,
                                    do_not_start=None,
                                    monitoring_interval=None,
                                    endpoint_name=None,
                                    endpoint_resource_id=None,
                                    endpoint_address=None,
                                    endpoint_filter_type=None,
                                    endpoint_filter_items=None):
    print(watcher_rg)
    print(watcher_name)

    ConnectionMonitor, ConnectionMonitorSource, ConnectionMonitorDestination = cmd.get_models(
        'ConnectionMonitor', 'ConnectionMonitorSource', 'ConnectionMonitorDestination')

    ConnectionMonitorTestConfiguration, ConnectionMonitorTcpConfiguration = cmd.get_models(
        'ConnectionMonitorTestConfiguration', 'ConnectionMonitorTcpConfiguration'
    )
    # connection_monitor = ConnectionMonitor(
    #     location=location,
    #     tags=tags,
    #     source=ConnectionMonitorSource(
    #         resource_id=source_resource,
    #         port=source_port
    #     ),
    #     destination=ConnectionMonitorDestination(
    #         resource_id=dest_resource,
    #         port=dest_port,
    #         address=dest_address
    #     ),
    #     auto_start=not do_not_start,
    #     monitoring_interval_in_seconds=monitoring_interval)

    ConnectionMonitorEndpoint, ConnectionMonitorEndpointFilter, ConnectionMonitorEndpointFilterItem = cmd.get_models(
        'ConnectionMonitorEndpoint', 'ConnectionMonitorEndpointFilter', 'ConnectionMonitorEndpointFilterItem')

    endpoint_filter = ConnectionMonitorEndpointFilter(type='Include',
                                                      items=[
                                                          ConnectionMonitorEndpointFilterItem(type='AgentAddress', address='npmuser')
                                                      ])
    endpoint1 = ConnectionMonitorEndpoint(name='MyEndpoint01',
                                          resource_id='/subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/harold-test/providers/Microsoft.Compute/virtualMachines/harold-monitor-vm-01')
    endpoint2 = ConnectionMonitorEndpoint(name='MyEndpoint02',
                                          resource_id=None,
                                          address='google.com')

    test_tcp_config = ConnectionMonitorTcpConfiguration(port=80, disable_trace_route=False)
    test_config01 = ConnectionMonitorTestConfiguration(name="MyTestConfig01",
                                                       test_frequency_sec=300,
                                                       protocol='Tcp',
                                                       tcp_configuration=test_tcp_config)

    ConnectionMonitorTestGroup = cmd.get_models('ConnectionMonitorTestGroup')
    test_group = ConnectionMonitorTestGroup(
        name="MyTestGroup01",
        disable=False,
        test_configurations=[test_config01.name],
        sources=[endpoint1.name],
        destinations=[endpoint2.name]
    )

    connection_monitor = ConnectionMonitor(
        location=location,
        tags=tags,
        # auto_start=not do_not_start,
        auto_start=None,
        # source=None,
        # destination=None,
        monitoring_interval_in_seconds=None,
        endpoints=[endpoint1, endpoint2],
        test_configurations=[test_config01],
        test_groups=[test_group]
    )
    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def add_nw_connection_monitor_v2_endpoint(cmd,
                                          client,
                                          watcher_rg,
                                          watcher_name,
                                          connection_monitor_name,
                                          location,
                                          name,
                                          resource_id=None,
                                          address=None,
                                          filter_type=None,
                                          filter_items=None):
    if filter_items:
        from pprint import pprint
        for item in filter_items:
            pprint(vars(item))

    ConnectionMonitorEndpoint, ConnectionMonitorEndpointFilter = cmd.get_models(
        'ConnectionMonitorEndpoint', 'ConnectionMonitorEndpointFilter')

    if (filter_type and not filter_items) or (not filter_type and filter_items):
        raise CLIError('usage error: --filter-type and --filter-item must be present at the same time.')

    endpoint = ConnectionMonitorEndpoint(name=name, resource_id=resource_id, address=address)

    if filter_type and filter_items:
        endpoint_filter = ConnectionMonitorEndpointFilter(type=filter_type, items=filter_items)
        endpoint.filter = endpoint_filter

    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    connection_monitor.endpoints.append(endpoint)
    connection_monitor.test_groups[0].destinations.append(endpoint.name)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def add_nw_connection_monitor_v2_test_group(cmd,
                                            client,
                                            connection_monitor_name,
                                            watcher_rg,
                                            watcher_name,
                                            resource_group_name=None,
                                            location=None,
                                            endpoint_name=None,
                                            endpoint_resource_id=None,
                                            endpoint_address=None,
                                            endpoint_filter_type=None,
                                            endpoint_filter_items=None):
    pass