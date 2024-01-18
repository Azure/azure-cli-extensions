# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=raise-missing-from, consider-using-f-string

def _data_collection_rules_create(client,
                                  resource_group_name,
                                  data_collection_rule_name,
                                  body):
    return client.create(resource_group_name=resource_group_name,
                         data_collection_rule_name=data_collection_rule_name,
                         body=body)


def data_collection_rules_create_man(client, resource_group_name, data_collection_rule_name, rule_file,
                                     location=None, tags=None, description=None):
    from azure.cli.core.util import get_file_json
    from azure.cli.core.azclierror import FileOperationError, UnclassifiedUserFault
    body = {}
    body['location'] = location
    body['tags'] = tags
    body['description'] = description
    try:
        json_data = get_file_json(rule_file)
    except FileNotFoundError:
        raise FileOperationError("No such file: " + str(rule_file))
    except IsADirectoryError:
        raise FileOperationError("Is a directory: " + str(rule_file))
    except PermissionError:
        raise FileOperationError("Permission denied: " + str(rule_file))
    except OSError as e:
        raise UnclassifiedUserFault(e)
    for key_prop in json_data:
        if key_prop == 'properties':
            data = json_data['properties']
        else:
            data = json_data
    for key in data:
        if key == 'dataSources':
            body['data_sources'] = {}
            for key_ds in data['dataSources']:
                if key_ds == 'performanceCounters':
                    body['data_sources']['performance_counters'] = data['dataSources']['performanceCounters']
                if key_ds == 'windowsEventLogs':
                    body['data_sources']['windows_event_logs'] = data['dataSources']['windowsEventLogs']
                if key_ds == 'syslog':
                    body['data_sources']['syslog'] = data['dataSources']['syslog']
                if key_ds == 'extensions':
                    body['data_sources']['extensions'] = data['dataSources']['extensions']
        if key == 'destinations':
            body['destinations'] = {}
            for key_de in data['destinations']:
                if key_de == 'logAnalytics':
                    body['destinations']['log_analytics'] = data['destinations']['logAnalytics']
                if key_de == 'azureMonitorMetrics':
                    body['destinations']['azure_monitor_metrics'] = data['destinations']['azureMonitorMetrics']
        if key == 'dataFlows':
            body['data_flows'] = data['dataFlows']
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_data_flows_add(client,
                                         resource_group_name,
                                         data_collection_rule_name,
                                         streams,
                                         destinations):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_flows' not in body:
        body['data_flows'] = []
    item = {
        'streams': streams,
        'destinations': destinations,
    }
    body['data_flows'].append(item)
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_log_analytics_add(client,
                                            resource_group_name,
                                            data_collection_rule_name,
                                            name,
                                            workspace_resource_id):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'destinations' not in body:
        body['destinations'] = {}
    if 'log_analytics' not in body['destinations']:
        body['destinations']['log_analytics'] = []

    item_list = body['destinations']['log_analytics']
    for item in item_list:
        if item['name'] == name:
            from azure.cli.core.azclierror import InvalidArgumentValueError
            raise InvalidArgumentValueError("Name {} exists.".format(name))
    item = {
        'name': name,
        'workspace_resource_id': workspace_resource_id
    }
    item_list.append(item)
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_log_analytics_delete(client,
                                               resource_group_name,
                                               data_collection_rule_name,
                                               name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'destinations' not in body:
        body['destinations'] = {}
    if 'log_analytics' not in body['destinations']:
        body['destinations']['log_analytics'] = []

    item_list = body['destinations']['log_analytics']
    for idx, item in enumerate(item_list):
        if item['name'] == name:
            item_list.pop(idx)
            break

    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_log_analytics_update(client,
                                               resource_group_name,
                                               data_collection_rule_name,
                                               name,
                                               workspace_resource_id=None):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'destinations' not in body:
        body['destinations'] = {}
    if 'log_analytics' not in body['destinations']:
        body['destinations']['log_analytics'] = []

    item_list = body['destinations']['log_analytics']
    for item in item_list:
        if item['name'] == name:
            if workspace_resource_id is not None:
                item['workspace_resource_id'] = workspace_resource_id
            break
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_performance_counters_add(client,
                                                   resource_group_name,
                                                   data_collection_rule_name,
                                                   name,
                                                   streams,
                                                   sampling_frequency_in_seconds,
                                                   counter_specifiers):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'performance_counters' not in body['data_sources']:
        body['data_sources']['performance_counters'] = []

    item_list = body['data_sources']['performance_counters']
    for item in item_list:
        if item['name'] == name:
            from azure.cli.core.azclierror import InvalidArgumentValueError
            raise InvalidArgumentValueError("Name {} exists.".format(name))

    item = {
        'name': name,
        'streams': streams,
        'sampling_frequency_in_seconds': sampling_frequency_in_seconds,
        'counter_specifiers': counter_specifiers
    }

    item_list.append(item)
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_performance_counters_delete(client,
                                                      resource_group_name,
                                                      data_collection_rule_name,
                                                      name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'performance_counters' not in body['data_sources']:
        body['data_sources']['performance_counters'] = []

    item_list = body['data_sources']['performance_counters']
    for idx, item in enumerate(item_list):
        if item['name'] == name:
            item_list.pop(idx)
            break
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_performance_counters_update(client,
                                                      resource_group_name,
                                                      data_collection_rule_name,
                                                      name,
                                                      streams=None,
                                                      sampling_frequency_in_seconds=None,
                                                      counter_specifiers=None):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'performance_counters' not in body['data_sources']:
        body['data_sources']['performance_counters'] = []

    item_list = body['data_sources']['performance_counters']
    for item in item_list:
        if item['name'] == name:
            if streams is not None:
                item['streams'] = streams
            if sampling_frequency_in_seconds is not None:
                item['sampling_frequency_in_seconds'] = sampling_frequency_in_seconds
            if counter_specifiers is not None:
                item['counter_specifiers'] = counter_specifiers
            break
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_windows_event_logs_add(client,
                                                 resource_group_name,
                                                 data_collection_rule_name,
                                                 name,
                                                 streams,
                                                 x_path_queries):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'windows_event_logs' not in body['data_sources']:
        body['data_sources']['windows_event_logs'] = []

    item_list = body['data_sources']['windows_event_logs']
    for item in item_list:
        if item['name'] == name:
            from azure.cli.core.azclierror import InvalidArgumentValueError
            raise InvalidArgumentValueError("Name {} exists.".format(name))

    item = {
        'name': name,
        'streams': streams,
        'x_path_queries': x_path_queries
    }

    item_list.append(item)
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_windows_event_logs_delete(client,
                                                    resource_group_name,
                                                    data_collection_rule_name,
                                                    name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'windows_event_logs' not in body['data_sources']:
        body['data_sources']['windows_event_logs'] = []

    item_list = body['data_sources']['windows_event_logs']
    for idx, item in enumerate(item_list):
        if item['name'] == name:
            item_list.pop(idx)
            break
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_windows_event_logs_update(client,
                                                    resource_group_name,
                                                    data_collection_rule_name,
                                                    name,
                                                    streams=None,
                                                    x_path_queries=None):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'windows_event_logs' not in body['data_sources']:
        body['data_sources']['windows_event_logs'] = []

    item_list = body['data_sources']['windows_event_logs']
    for item in item_list:
        if item['name'] == name:
            if streams is not None:
                item['streams'] = streams
            if x_path_queries is not None:
                item['x_path_queries'] = x_path_queries
            break
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_syslog_add(client,
                                     resource_group_name,
                                     data_collection_rule_name,
                                     name,
                                     streams,
                                     facility_names,
                                     log_levels=None):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'syslog' not in body['data_sources']:
        body['data_sources']['syslog'] = []

    item_list = body['data_sources']['syslog']
    for item in item_list:
        if item['name'] == name:
            from azure.cli.core.azclierror import InvalidArgumentValueError
            raise InvalidArgumentValueError("Name {} exists.".format(name))

    item = {
        'name': name,
        'streams': streams,
        'facility_names': facility_names,
    }
    if log_levels is not None:
        item['log_levels'] = log_levels

    item_list.append(item)
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_syslog_delete(client,
                                        resource_group_name,
                                        data_collection_rule_name,
                                        name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'syslog' not in body['data_sources']:
        body['data_sources']['syslog'] = []

    item_list = body['data_sources']['syslog']
    for idx, item in enumerate(item_list):
        if item['name'] == name:
            item_list.pop(idx)
            break

    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_syslog_update(client,
                                        resource_group_name,
                                        data_collection_rule_name,
                                        name,
                                        streams=None,
                                        facility_names=None,
                                        log_levels=None):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if 'syslog' not in body['data_sources']:
        body['data_sources']['syslog'] = []

    item_list = body['data_sources']['syslog']
    for item in item_list:
        if item['name'] == name:
            if streams is not None:
                item['streams'] = streams
            if facility_names is not None:
                item['facility_names'] = facility_names
            if log_levels is not None:
                item['log_levels'] = log_levels

    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)
