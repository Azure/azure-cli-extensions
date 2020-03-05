# pylint: disable=unused-argument,too-many-locals
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def create_nw_connection_monitor(cmd,
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
                                 test_config_http_valid_status_codes=None,
                                 test_config_http_prefer_https=None,
                                 test_group_name=None,
                                 test_group_disable=None,
                                 output_type=None,
                                 workspace_ids=None,
                                 notes=None):
    v1_required_parameter_set = [
        source_resource, source_port,
        dest_resource, dest_address, dest_port
    ]

    v2_required_parameter_set = [
        endpoint_source_name, endpoint_source_resource_id,
        endpoint_dest_name, endpoint_dest_address,
        test_config_name, test_config_protocol,
        output_type, workspace_ids,
    ]

    if any(v1_required_parameter_set):  # V1 creation
        connection_monitor = _create_nw_connection_monitor_v1(cmd,
                                                              connection_monitor_name,
                                                              watcher_rg,
                                                              watcher_name,
                                                              source_resource,
                                                              resource_group_name,
                                                              source_port,
                                                              location,
                                                              dest_resource,
                                                              dest_port,
                                                              dest_address,
                                                              tags,
                                                              do_not_start,
                                                              monitoring_interval)
        from ._client_factory import cf_nw_connection_monitor_v1
        client = cf_nw_connection_monitor_v1(cmd.cli_ctx).connection_monitors   # overwrite to use 2019-06-01 API
    elif any(v2_required_parameter_set):  # V2 creation
        connection_monitor = _create_nw_connection_monitor_v2(cmd,
                                                              location,
                                                              tags,
                                                              endpoint_source_name,
                                                              endpoint_source_resource_id,
                                                              endpoint_source_address,
                                                              endpoint_dest_name,
                                                              endpoint_dest_resource_id,
                                                              endpoint_dest_address,
                                                              test_config_name,
                                                              test_config_frequency,
                                                              test_config_protocol,
                                                              test_config_preferred_ip_version,
                                                              test_config_threshold_failed_percent,
                                                              test_config_threshold_round_trip_time,
                                                              test_config_tcp_port,
                                                              test_config_tcp_disable_trace_route,
                                                              test_config_icmp_disable_trace_route,
                                                              test_config_http_port,
                                                              test_config_http_method,
                                                              test_config_http_path,
                                                              test_config_http_valid_status_codes,
                                                              test_config_http_prefer_https,
                                                              test_group_name,
                                                              test_group_disable,
                                                              output_type,
                                                              workspace_ids,
                                                              notes)
    else:
        raise CLIError('Unknown operation')

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def _create_nw_connection_monitor_v1(cmd,
                                     connection_monitor_name,
                                     watcher_rg,
                                     watcher_name,
                                     source_resource,
                                     resource_group_name=None,
                                     source_port=None,
                                     location=None,
                                     dest_resource=None,
                                     dest_port=None,
                                     dest_address=None,
                                     tags=None,
                                     do_not_start=None,
                                     monitoring_interval=60):
    ConnectionMonitor, ConnectionMonitorSource, ConnectionMonitorDestination = cmd.get_models(
        'ConnectionMonitor', 'ConnectionMonitorSource', 'ConnectionMonitorDestination')

    cmv1 = ConnectionMonitor(
        location=location,
        tags=tags,
        source=ConnectionMonitorSource(
            resource_id=source_resource,
            port=source_port
        ),
        destination=ConnectionMonitorDestination(
            resource_id=dest_resource,
            port=dest_port,
            address=dest_address
        ),
        auto_start=not do_not_start,
        monitoring_interval_in_seconds=monitoring_interval,
        endpoints=None,
        test_configurations=None,
        test_groups=None,
        outputs=None,
        nots=None
    )

    return cmv1


def _create_nw_connection_monitor_v2(cmd,
                                     location=None,
                                     tags=None,
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
                                     test_config_tcp_disable_trace_route=False,
                                     test_config_icmp_disable_trace_route=False,
                                     test_config_http_port=None,
                                     test_config_http_method=None,
                                     test_config_http_path=None,
                                     test_config_http_valid_status_codes=None,
                                     test_config_http_prefer_https=None,
                                     test_group_name=None,
                                     test_group_disable=False,
                                     output_type=None,
                                     workspace_ids=None,
                                     notes=None):
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
                                                                      test_config_http_valid_status_codes,
                                                                      test_config_http_prefer_https)
    test_group = _create_nw_connection_monitor_v2_test_group(cmd,
                                                             test_group_name,
                                                             test_group_disable,
                                                             [test_config],
                                                             [src_endpoint],
                                                             [dst_endpoint])
    if output_type:
        outputs = []
        if workspace_ids:
            for workspace_id in workspace_ids:
                output = _create_nw_connection_monitor_v2_output(cmd, output_type, workspace_id)
                outputs.append(output)
    else:
        outputs = []

    ConnectionMonitor = cmd.get_models('ConnectionMonitor')
    cmv2 = ConnectionMonitor(location=location,
                             tags=tags,
                             auto_start=None,
                             monitoring_interval_in_seconds=None,
                             endpoints=[src_endpoint, dst_endpoint],
                             test_configurations=[test_config],
                             test_groups=[test_group],
                             outputs=outputs,
                             notes=notes)
    return cmv2


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
    elif protocol == ConnectionMonitorTestConfigurationProtocol.icmp:
        ConnectionMonitorIcmpConfiguration = cmd.get_models('ConnectionMonitorIcmpConfiguration')
        icmp_config = ConnectionMonitorIcmpConfiguration(disable_trace_route=icmp_disable_trace_route)
        test_config.icmp_configuration = icmp_config
    elif protocol == ConnectionMonitorTestConfigurationProtocol.http:
        ConnectionMonitorHttpConfiguration = cmd.get_models('ConnectionMonitorHttpConfiguration')
        http_config = ConnectionMonitorHttpConfiguration(
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
                                            test_configurations=[tc.name for tc in test_configurations],
                                            sources=[e.name for e in source_endpoints],
                                            destinations=[e.name for e in destination_endpoints])
    return test_group


def _create_nw_connection_monitor_v2_output(cmd,
                                            output_type,
                                            workspace_id=None):
    ConnectionMonitorOutput, OutputType = cmd.get_models('ConnectionMonitorOutput', 'OutputType')
    output = ConnectionMonitorOutput(type=output_type)

    if output_type == OutputType.workspace:
        ConnectionMonitorWorkspaceSettings = cmd.get_models('ConnectionMonitorWorkspaceSettings')
        workspace = ConnectionMonitorWorkspaceSettings(workspace_resource_id=workspace_id)
        output.workspace_settings = workspace
    else:
        raise CLIError('Unsupported output type: "{}"'.format(output_type))

    return output


def add_nw_connection_monitor_v2_endpoint(cmd,
                                          client,
                                          watcher_rg,
                                          watcher_name,
                                          connection_monitor_name,
                                          location,
                                          name,
                                          source_test_groups=None,
                                          dest_test_groups=None,
                                          resource_id=None,
                                          address=None,
                                          filter_type=None,
                                          filter_items=None):
    ConnectionMonitorEndpoint, ConnectionMonitorEndpointFilter = cmd.get_models(
        'ConnectionMonitorEndpoint', 'ConnectionMonitorEndpointFilter')

    endpoint = ConnectionMonitorEndpoint(name=name, resource_id=resource_id, address=address)

    if filter_type and filter_items:
        endpoint_filter = ConnectionMonitorEndpointFilter(type=filter_type, items=filter_items)
        endpoint.filter = endpoint_filter

    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    connection_monitor.endpoints.append(endpoint)

    src_test_groups, dst_test_groups = set(source_test_groups or []), set(dest_test_groups or [])
    for test_group in connection_monitor.test_groups:
        if test_group.name in src_test_groups:
            test_group.sources.append(endpoint.name)
        if test_group.name in dst_test_groups:
            test_group.destinations.append(endpoint.name)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def remove_nw_connection_monitor_v2_endpoint(client,
                                             watcher_rg,
                                             watcher_name,
                                             connection_monitor_name,
                                             location,
                                             name,
                                             test_groups=None):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    # refresh endpoints
    new_endpoints = [endpoint for endpoint in connection_monitor.endpoints if endpoint.name != name]
    connection_monitor.endpoints = new_endpoints

    # refresh test groups
    if test_groups is not None:
        temp_test_groups = [t for t in connection_monitor.test_groups if t.name in test_groups]
    else:
        temp_test_groups = connection_monitor.test_groups

    for test_group in temp_test_groups:
        if name in test_group.sources:
            test_group.sources.remove(name)
        if name in test_group.destinations:
            test_group.destinations.remove(name)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def show_nw_connection_monitor_v2_endpoint(client,
                                           watcher_rg,
                                           watcher_name,
                                           connection_monitor_name,
                                           location,
                                           name):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    for endpoint in connection_monitor.endpoints:
        if endpoint.name == name:
            return endpoint

    raise CLIError('unknown endpoint: {}'.format(name))


def list_nw_connection_monitor_v2_endpoint(client,
                                           watcher_rg,
                                           watcher_name,
                                           connection_monitor_name,
                                           location):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    return connection_monitor.endpoints


def add_nw_connection_monitor_v2_test_configuration(cmd,
                                                    client,
                                                    watcher_rg,
                                                    watcher_name,
                                                    connection_monitor_name,
                                                    location,
                                                    name,
                                                    protocol,
                                                    test_groups,
                                                    frequency=None,
                                                    threshold_failed_percent=None,
                                                    threshold_round_trip_time=None,
                                                    preferred_ip_version=None,
                                                    tcp_port=None,
                                                    tcp_disable_trace_route=None,
                                                    icmp_disable_trace_route=None,
                                                    http_port=None,
                                                    http_method=None,
                                                    http_path=None,
                                                    http_valid_status_codes=None,
                                                    http_prefer_https=None,
                                                    http_request_headers=None):
    new_test_config = _create_nw_connection_monitor_v2_test_configuration(cmd,
                                                                          name,
                                                                          frequency,
                                                                          protocol,
                                                                          threshold_failed_percent,
                                                                          threshold_round_trip_time,
                                                                          preferred_ip_version,
                                                                          tcp_port,
                                                                          tcp_disable_trace_route,
                                                                          icmp_disable_trace_route,
                                                                          http_port,
                                                                          http_method,
                                                                          http_path,
                                                                          http_valid_status_codes,
                                                                          http_prefer_https,
                                                                          http_request_headers)

    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    connection_monitor.test_configurations.append(new_test_config)

    for test_group in connection_monitor.test_groups:
        if test_group.name in test_groups:
            test_group.test_configurations.append(new_test_config.name)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def remove_nw_connection_monitor_v2_test_configuration(client,
                                                       watcher_rg,
                                                       watcher_name,
                                                       connection_monitor_name,
                                                       location,
                                                       name,
                                                       test_groups=None):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    # refresh test configurations
    new_test_configurations = [t for t in connection_monitor.test_configurations if t.name != name]
    connection_monitor.test_configurations = new_test_configurations

    if test_groups is not None:
        temp_test_groups = [t for t in connection_monitor.test_groups if t.name in test_groups]
    else:
        temp_test_groups = connection_monitor.test_groups

    # refresh test groups
    for test_group in temp_test_groups:
        test_group.test_configurations.remove(name)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def show_nw_connection_monitor_v2_test_configuration(client,
                                                     watcher_rg,
                                                     watcher_name,
                                                     connection_monitor_name,
                                                     location,
                                                     name):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    for test_config in connection_monitor.test_configurations:
        if test_config.name == name:
            return test_config

    raise CLIError('unknown test configuration: {}'.format(name))


def list_nw_connection_monitor_v2_test_configuration(client,
                                                     watcher_rg,
                                                     watcher_name,
                                                     connection_monitor_name,
                                                     location):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    return connection_monitor.test_configurations


def add_nw_connection_monitor_v2_test_group(cmd,
                                            client,
                                            connection_monitor_name,
                                            watcher_rg,
                                            watcher_name,
                                            location,
                                            name,
                                            endpoint_source_name,
                                            endpoint_dest_name,
                                            test_config_name,
                                            disable=False,
                                            endpoint_source_resource_id=None,
                                            endpoint_source_address=None,
                                            endpoint_dest_resource_id=None,
                                            endpoint_dest_address=None,
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
                                            test_config_http_valid_status_codes=None,
                                            test_config_http_prefer_https=None):
    new_test_configuration_creation_requirements = [
        test_config_protocol, test_config_preferred_ip_version,
        test_config_threshold_failed_percent, test_config_threshold_round_trip_time,
        test_config_tcp_disable_trace_route, test_config_tcp_port,
        test_config_icmp_disable_trace_route,
        test_config_http_port, test_config_http_method,
        test_config_http_path, test_config_http_valid_status_codes, test_config_http_prefer_https
    ]

    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    new_test_group = _create_nw_connection_monitor_v2_test_group(cmd,
                                                                 name,
                                                                 disable,
                                                                 [], [], [])

    # deal with endpoint
    if any([endpoint_source_address, endpoint_source_resource_id]):
        src_endpoint = _create_nw_connection_monitor_v2_endpoint(cmd,
                                                                 endpoint_source_name,
                                                                 endpoint_source_resource_id,
                                                                 endpoint_source_address)
        connection_monitor.endpoints.append(src_endpoint)
    if any([endpoint_dest_address, endpoint_dest_resource_id]):
        dst_endpoint = _create_nw_connection_monitor_v2_endpoint(cmd,
                                                                 endpoint_dest_name,
                                                                 endpoint_dest_resource_id,
                                                                 endpoint_dest_address)
        connection_monitor.endpoints.append(dst_endpoint)

    new_test_group.sources.append(endpoint_source_name)
    new_test_group.destinations.append(endpoint_dest_name)

    # deal with test configuration
    if any(new_test_configuration_creation_requirements):
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
                                                                          test_config_http_valid_status_codes,
                                                                          test_config_http_prefer_https)
        connection_monitor.test_configurations.append(test_config)
    new_test_group.test_configurations.append(test_config_name)

    connection_monitor.test_groups.append(new_test_group)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def remove_nw_connection_monitor_v2_test_group(client,
                                               watcher_rg,
                                               watcher_name,
                                               connection_monitor_name,
                                               location,
                                               name):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    new_test_groups, removed_test_group = [], None
    for t in connection_monitor.test_groups:
        if t.name == name:
            removed_test_group = t
        else:
            new_test_groups.append(t)

    if removed_test_group is None:
        raise CLIError('test group: "{}" not exist'.format(name))
    connection_monitor.test_groups = new_test_groups

    # deal with endpoints which are only referenced by this removed test group
    removed_endpoints = []
    for e in removed_test_group.sources + removed_test_group.destinations:
        tmp = [t for t in connection_monitor.test_groups if (e in t.sources or e in t.destinations)]
        if not tmp:
            removed_endpoints.append(e)
    connection_monitor.endpoints = [e for e in connection_monitor.endpoints if e.name not in removed_endpoints]

    # deal with test configurations which are only referenced by this remove test group
    removed_test_configurations = []
    for c in removed_test_group.test_configurations:
        tmp = [t for t in connection_monitor.test_groups if c in t.test_configurations]
        if not tmp:
            removed_test_configurations.append(c)
    connection_monitor.test_configurations = [c for c in connection_monitor.test_configurations
                                              if c.name not in removed_test_configurations]

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def show_nw_connection_monitor_v2_test_group(client,
                                             watcher_rg,
                                             watcher_name,
                                             connection_monitor_name,
                                             location,
                                             name):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    for t in connection_monitor.test_groups:
        if t.name == name:
            return t

    raise CLIError('unknown test group: {}'.format(name))


def list_nw_connection_monitor_v2_test_group(client,
                                             watcher_rg,
                                             watcher_name,
                                             connection_monitor_name,
                                             location):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    return connection_monitor.test_groups


def add_nw_connection_monitor_v2_output(cmd,
                                        client,
                                        watcher_rg,
                                        watcher_name,
                                        connection_monitor_name,
                                        location,
                                        out_type,
                                        workspace_id=None):
    output = _create_nw_connection_monitor_v2_output(cmd, out_type, workspace_id)

    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)

    if connection_monitor.outputs is None:
        connection_monitor.outputs = []

    connection_monitor.outputs.append(output)

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def remove_nw_connection_monitor_v2_output(client,
                                           watcher_rg,
                                           watcher_name,
                                           connection_monitor_name,
                                           location):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    connection_monitor.outputs = []

    return client.create_or_update(watcher_rg, watcher_name, connection_monitor_name, connection_monitor)


def list_nw_connection_monitor_v2_output(client,
                                         watcher_rg,
                                         watcher_name,
                                         connection_monitor_name,
                                         location):
    connection_monitor = client.get(watcher_rg, watcher_name, connection_monitor_name)
    return connection_monitor.outputs
