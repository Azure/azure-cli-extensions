# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def monitor_data_collection_rule_association_create(client,
                                                    resource,
                                                    name,
                                                    description=None,
                                                    rule_id=None):
    body = {}
    body['description'] = description
    body['data_collection_rule_id'] = rule_id
    return client.create(resource_uri=resource,
                         association_name=name,
                         body=body)

# def monitor_data_collection_rule_association_update(client,
#                                                     resource,
#                                                     name,
#                                                     description=None,
#                                                     rule_id=None):
#     body = {}
#     body['description'] = description
#     body['data_collection_rule_id'] = rule_id
#     return client.create(resource_uri=resource,
#                          association_name=name,
#                          body=body)

def monitor_data_collection_rule_create(client,
                                        resource_group_name,
                                        name,
                                        location=None,
                                        tags=None,
                                        description=None,
                                        data_flows=None,
                                        destinations_log_analytics=None,
                                        destinations_azure_monitor_metrics=None,
                                        data_sources_performance_counters=None,
                                        data_sources_windows_event_logs=None,
                                        data_sources_syslog=None,
                                        data_sources_extensions=None):
    body = {}
    body['location'] = location
    body['tags'] = tags
    body['description'] = description
    body['data_flows'] = data_flows
    body['destinations'] = {}
    body['destinations']['log_analytics'] = destinations_log_analytics
    body['destinations']['azure_monitor_metrics'] = destinations_azure_monitor_metrics
    body['data_sources'] = {}
    body['data_sources']['performance_counters'] = data_sources_performance_counters
    body['data_sources']['windows_event_logs'] = data_sources_windows_event_logs
    body['data_sources']['syslog'] = data_sources_syslog
    body['data_sources']['extensions'] = data_sources_extensions
    return client.create(resource_group_name=resource_group_name,
                         data_collection_rule_name=name,
                         body=body)

# def monitor_data_collection_rule_update(client,
#                                         resource_group_name,
#                                         name,
#                                         location=None,
#                                         tags=None,
#                                         description=None,
#                                         data_flows=None,
#                                         destinations_log_analytics=None,
#                                         destinations_azure_monitor_metrics=None,
#                                         data_sources_performance_counters=None,
#                                         data_sources_windows_event_logs=None,
#                                         data_sources_syslog=None,
#                                         data_sources_extensions=None):
#     body = {}
#     body['location'] = location
#     body['tags'] = tags
#     body['description'] = description
#     body['data_flows'] = data_flows
#     body['destinations'] = {}
#     body['destinations']['log_analytics'] = destinations_log_analytics
#     body['destinations']['azure_monitor_metrics'] = destinations_azure_monitor_metrics
#     body['data_sources'] = {}
#     body['data_sources']['performance_counters'] = data_sources_performance_counters
#     body['data_sources']['windows_event_logs'] = data_sources_windows_event_logs
#     body['data_sources']['syslog'] = data_sources_syslog
#     body['data_sources']['extensions'] = data_sources_extensions
#     return client.create(resource_group_name=resource_group_name,
#                          data_collection_rule_name=name,
#                          body=body)
