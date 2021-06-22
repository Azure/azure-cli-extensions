# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def data_collection_endpoint_create(client,
                                    resource_group_name,
                                    data_collection_endpoint_name,
                                    location,
                                    public_network_access,
                                    tags=None,
                                    kind=None,
                                    description=None):
    body = {}
    body['location'] = location
    body['tags'] = tags
    body['kind'] = kind
    body['description'] = description
    body['network_acls'] = {}
    body['network_acls']['public_network_access'] = public_network_access
    return client.create(resource_group_name=resource_group_name,
                         data_collection_endpoint_name=data_collection_endpoint_name,
                         body=body)


def data_collection_endpoint_update(client,
                                    resource_group_name,
                                    data_collection_endpoint_name,
                                    tags=None,
                                    kind=None,
                                    description=None,
                                    public_network_access=None):
    from ..custom import monitor_data_collection_endpoint_show
    instance = monitor_data_collection_endpoint_show(client, resource_group_name=resource_group_name,
                                                     data_collection_endpoint_name=data_collection_endpoint_name)
    body = instance.as_dict(keep_readonly=False)

    if description is not None:
        body['description'] = description
    if tags is not None:
        body['tags'] = tags
    if kind is not None:
        body['kind'] = kind
    if public_network_access is not None:
        body['network_acls'] = {}
        body['network_acls']['public_network_access'] = public_network_access
    return client.create(resource_group_name=resource_group_name,
                         data_collection_endpoint_name=data_collection_endpoint_name,
                         body=body)


def data_collection_rule_associations_create(client,
                                             resource_uri,
                                             association_name,
                                             description=None,
                                             rule_id=None):
    body = {}
    body['description'] = description
    body['data_collection_rule_id'] = rule_id
    return client.create(resource_uri=resource_uri,
                         association_name=association_name,
                         body=body)


def data_collection_rule_associations_update(client,
                                             resource_uri,
                                             association_name,
                                             description=None,
                                             rule_id=None):
    from ..custom import monitor_data_collection_rule_association_show
    instance = monitor_data_collection_rule_association_show(client, resource_uri, association_name)
    body = instance.as_dict(keep_readonly=False)

    if description is not None:
        body['description'] = description
    if rule_id is not None:
        body['data_collection_rule_id'] = rule_id
    return client.create(resource_uri=resource_uri,
                         association_name=association_name,
                         body=body)


def _data_collection_rules_create(client,
                                  resource_group_name,
                                  data_collection_rule_name,
                                  body):
    return client.create(resource_group_name=resource_group_name,
                         data_collection_rule_name=data_collection_rule_name,
                         body=body)


def data_collection_rules_create(client,
                                 resource_group_name,
                                 data_collection_rule_name,
                                 location=None,
                                 tags=None,
                                 description=None,
                                 data_flows=None,
                                 destinations__log_analytics=None,
                                 destinations__azure_monitor_metrics=None,
                                 data_sources__performance_counters=None,
                                 data_sources__windows_event_logs=None,
                                 data_sources__syslog=None,
                                 data_sources__extensions=None):
    body = {}
    body['location'] = location
    body['tags'] = tags
    body['description'] = description
    body['data_flows'] = data_flows
    body['destinations'] = {}
    body['destinations']['log_analytics'] = destinations__log_analytics
    body['destinations']['azure_monitor_metrics'] = destinations__azure_monitor_metrics
    body['data_sources'] = {}
    body['data_sources']['performance_counters'] = data_sources__performance_counters
    body['data_sources']['windows_event_logs'] = data_sources__windows_event_logs
    body['data_sources']['syslog'] = data_sources__syslog
    body['data_sources']['extensions'] = data_sources__extensions
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_update(client,
                                 resource_group_name,
                                 data_collection_rule_name,
                                 tags=None,
                                 description=None,
                                 data_flows=None,
                                 destinations__log_analytics=None,
                                 destinations__azure_monitor_metrics=None,
                                 data_sources__performance_counters=None,
                                 data_sources__windows_event_logs=None,
                                 data_sources__syslog=None,
                                 data_sources__extensions=None):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    body = instance.as_dict(keep_readonly=False)
    if tags is not None:
        body['tags'] = tags
    if description is not None:
        body['description'] = description
    if data_flows is not None:
        body['data_flows'] = data_flows
    if 'destinations' not in body:
        body['destinations'] = {}
    if destinations__log_analytics is not None:
        body['destinations']['log_analytics'] = destinations__log_analytics
    if destinations__azure_monitor_metrics is not None:
        body['destinations']['azure_monitor_metrics'] = destinations__azure_monitor_metrics
    if 'data_sources' not in body:
        body['data_sources'] = {}
    if data_sources__performance_counters is not None:
        body['data_sources']['performance_counters'] = data_sources__performance_counters
    if data_sources__windows_event_logs is not None:
        body['data_sources']['windows_event_logs'] = data_sources__windows_event_logs
    if data_sources__syslog is not None:
        body['data_sources']['syslog'] = data_sources__syslog
    if data_sources__extensions is not None:
        body['data_sources']['extensions'] = data_sources__extensions
    return _data_collection_rules_create(client,
                                         resource_group_name=resource_group_name,
                                         data_collection_rule_name=data_collection_rule_name,
                                         body=body)


def data_collection_rules_data_flows_list(client,
                                          resource_group_name,
                                          data_collection_rule_name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    if instance:
        return instance.data_flows
    return []


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


def data_collection_rules_log_analytics_list(client,
                                             resource_group_name,
                                             data_collection_rule_name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    if instance:
        return instance.destinations.log_analytics
    return []


def data_collection_rules_log_analytics_show(client,
                                             resource_group_name,
                                             data_collection_rule_name,
                                             name):
    item_list = data_collection_rules_log_analytics_list(
        client, resource_group_name, data_collection_rule_name)
    for item in item_list:
        if item.name == name:
            return item
    return {}


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


def data_collection_rules_list_by_subscription(client):
    return client.list_by_subscription()


def data_collection_rules_list_by_resource_group(client, resource_group_name):
    return client.list_by_resource_group(resource_group_name=resource_group_name)


def data_collection_rules_list(client,
                               resource_group_name=None):
    if resource_group_name:
        return data_collection_rules_list_by_resource_group(
            client=client,
            resource_group_name=resource_group_name
        )
    return data_collection_rules_list_by_subscription(client)


def data_collection_rules_performance_counters_list(client,
                                                    resource_group_name,
                                                    data_collection_rule_name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    if instance:
        return instance.data_sources.performance_counters
    return []


def data_collection_rules_performance_counters_show(client,
                                                    resource_group_name,
                                                    data_collection_rule_name,
                                                    name):
    item_list = data_collection_rules_performance_counters_list(
        client, resource_group_name, data_collection_rule_name)
    for item in item_list:
        if item.name == name:
            return item
    return {}


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


def data_collection_rules_windows_event_logs_list(client,
                                                  resource_group_name,
                                                  data_collection_rule_name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    if instance:
        return instance.data_sources.windows_event_logs
    return []


def data_collection_rules_windows_event_logs_show(client,
                                                  resource_group_name,
                                                  data_collection_rule_name,
                                                  name):
    item_list = data_collection_rules_windows_event_logs_list(
        client, resource_group_name, data_collection_rule_name)
    for item in item_list:
        if item.name == name:
            return item
    return {}


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


def data_collection_rules_syslog_list(client,
                                      resource_group_name,
                                      data_collection_rule_name):
    from ..custom import monitor_data_collection_rule_show
    instance = monitor_data_collection_rule_show(client, resource_group_name, data_collection_rule_name)
    if instance:
        return instance.data_sources.syslog
    return []


def data_collection_rules_syslog_show(client,
                                      resource_group_name,
                                      data_collection_rule_name,
                                      name):
    item_list = data_collection_rules_syslog_list(client, resource_group_name,
                                                  data_collection_rule_name)
    for item in item_list:
        if item.name == name:
            return item
    return {}


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
