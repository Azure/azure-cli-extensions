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
                                    endpoint_source_name=None,
                                    endpoint_source_resource_id=None,
                                    endpoint_source_address=None,
                                    endpoint_dest_name=None,
                                    endpoint_dest_resource_id=None,
                                    endpoint_dest_address=None,
                                    test_config_name=None,
                                    test_config_frequency=None,
                                    test_config_protocol=None,
                                    test_config_preferred_ip_version=None,
                                    test_config_threshold_failed_percent=None,
                                    test_config_threshold_round_trip_time=None,
                                    test_config_tcp_disable_trace_route=None,
                                    test_config_tcp_port=None,
                                    test_config_icmp_disable_trace_route=None,
                                    test_config_http_port=None,
                                    test_config_http_method=None,
                                    test_config_http_path=None,
                                    test_config_http_valid_code_ranges=None,
                                    test_config_http_prefer_https=None,
                                    test_group_name=None,
                                    test_group_disable=None):
    print(watcher_rg)
    print(watcher_name)

    v1_required_parameter_set = [
        source_resource, source_port,
        dest_resource, dest_address, dest_port
    ]

    v2_required_parameter_set = [
        endpoint_source_name, endpoint_source_resource_id,
        endpoint_dest_name, endpoint_dest_address
    ]

    if any(v1_required_parameter_set):  # V1 creation
        pass
    elif any(v2_required_parameter_set):  # V2 creation
        pass
    else:
        print('Oh!!!')

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


def _create_nw_connection_monitor_v2(cmd,
                                     client,
                                     connection_monitor_name,
                                     watcher_rg,
                                     watcher_name,
                                     resource_group_name=None,
                                     location=None,
                                     endpoint_source_name=None,
                                     endpoint_source_resource_id=None,
                                     endpoint_source_address=None,
                                     endpoint_dest_name=None,
                                     endpoint_dest_resource_id=None,
                                     endpoint_dest_address=None,
                                     test_config_name=None,
                                     test_config_frequency=None,
                                     test_config_protocol=None,
                                     test_config_preferred_ip_version=None,
                                     test_config_threshold_failed_percent=None,
                                     test_config_threshold_round_trip_time=None,
                                     test_config_tcp_port=None,
                                     test_config_tcp_disable_trace_route=None,
                                     test_config_icmp_disable_trace_route=None,
                                     test_config_http_port=None,
                                     test_config_http_method=None,
                                     test_config_http_path=None,
                                     test_config_http_valid_status_code=None,
                                     test_config_http_prefer_https=None,
                                     test_group_name=None,
                                     test_group_disable=None):
    src_endpoint = _create_nw_connection_monitor_v2_endpoint(cmd,
                                                             endpoint_source_name,
                                                             endpoint_source_resource_id,
                                                             endpoint_source_address)
    dst_endpoint = _create_nw_connection_monitor_v2_endpoint(cmd,
                                                             endpoint_dest_name,
                                                             endpoint_dest_resource_id,
                                                             endpoint_dest_address)
    test_config = _create_nw_connection_monitor_v2_test_configuration(cmd,
                                                                      test_config_name,
                                                                      test_config_frequency,
                                                                      test_config_protocol,
                                                                      test_config_threshold_failed_percent,
                                                                      test_config_threshold_round_trip_time,
                                                                      test_config_preferred_ip_version,
                                                                      test_config_tcp_port,
                                                                      test_config_tcp_disable_trace_route,
                                                                      test_config_icmp_disable_trace_route,
                                                                      test_config_http_port,
                                                                      test_config_http_method,
                                                                      test_config_http_path,
                                                                      test_config_http_valid_status_code,
                                                                      test_config_http_prefer_https)


def _create_nw_connection_monitor_v2_endpoint(cmd,
                                              name,
                                              resource_id=None,
                                              address=None,
                                              filter_type=None,
                                              filter_items=None):
    if (filter_type and not filter_items) or (not filter_type and filter_items):
        raise CLIError('usage error: '
                       '--filter-type and --filter-item for endpoint filter must be present at the same time.')

    ConnectionMonitorEndpoint, ConnectionMonitorEndpointFilter = cmd.get_models(
        'ConnectionMonitorEndpoint', 'ConnectionMonitorEndpointFilter')

    endpoint = ConnectionMonitorEndpoint(name=name, resource_id=resource_id, address=address)

    if filter_type and filter_items:
        endpoint_filter = ConnectionMonitorEndpointFilter(type=filter_type, items=filter_items)
        endpoint.filter = endpoint_filter

    return endpoint


def _create_nw_connection_monitor_v2_test_configuration(cmd,
                                                        name,
                                                        test_frequency,
                                                        protocol,
                                                        threshold_failed_percent,
                                                        threshold_round_trip_time,
                                                        preferred_ip_version,
                                                        tcp_port=None,
                                                        tcp_disable_trace_route=None,
                                                        icmp_disable_trace_route=None,
                                                        http_port=None,
                                                        http_method=None,
                                                        http_path=None,
                                                        http_valid_status_codes=None,
                                                        http_prefer_https=None,
                                                        http_request_headers=None):
    (ConnectionMonitorTestConfigurationProtocol,
     ConnectionMonitorTestConfiguration, ConnectionMonitorSuccessThreshold) = cmd.get_models(
        'ConnectionMonitorTestConfigurationProtocol',
        'ConnectionMonitorTestConfiguration', 'ConnectionMonitorSuccessThreshold')

    test_config = ConnectionMonitorTestConfiguration(name=name,
                                                     test_frequency_sec=test_frequency,
                                                     protocol=protocol,
                                                     preferred_ip_version=preferred_ip_version)

    if threshold_failed_percent or threshold_round_trip_time:
        threshold = ConnectionMonitorSuccessThreshold(checks_failed_percent=threshold_failed_percent,
                                                      round_trip_time_ms=threshold_round_trip_time)
        test_config.success_threshold = threshold

    if protocol == ConnectionMonitorTestConfigurationProtocol.tcp:
        ConnectionMonitorTcpConfiguration = cmd.get_models('ConnectionMonitorTcpConfiguration')
        tcp_config = ConnectionMonitorTcpConfiguration(
            port=tcp_port,
            tcp_disable_trace_route=tcp_disable_trace_route
        )
        test_config.tcp_configuration = tcp_config
    elif protocol == ConnectionMonitorTestConfiguration.icmp:
        ConnectionMonitorIcmpConfiguration = cmd.get_models('ConnectionMonitorIcmpConfiguration')
        icmp_config = ConnectionMonitorIcmpConfiguration(disable_trace_route=icmp_disable_trace_route)
        test_config.icmp_configuration = icmp_config
    elif protocol == ConnectionMonitorTestConfigurationProtocol.http:
        ConnectionMonitorTestConfigurationProtocol = cmd.get_models('ConnectionMonitorTestConfigurationProtocol')
        http_config = ConnectionMonitorTestConfigurationProtocol(
            port=http_port,
            method=http_method,
            path=http_path,
            request_headers=http_request_headers,
            valid_status_code_ranges=http_valid_status_codes,
            prefer_https=http_prefer_https)
        test_config.http_configuration = http_config
    else:
        raise CLIError('Unsupported protocol: "{}" for test configuration'.format(protocol))

    return test_config


def _create_nw_connection_monitor_v2_test_group(cmd,
                                                name,
                                                disable,
                                                test_configurations,
                                                source_endpoints,
                                                destination_endpoints):
    ConnectionMonitorTestGroup = cmd.get_models('ConnectionMonitorTestGroup')

    test_group = ConnectionMonitorTestGroup(name=name,
                                            disable=disable,
                                            test_configurations=test_configurations,
                                            sources=source_endpoints,
                                            destinations=destination_endpoints)
    return test_group


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
