# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
    return client.create(resource_group_name=resource_group_name,
                         data_collection_rule_name=name,
                         location=location,
                         tags=tags,
                         description=description,
                         data_flows=data_flows,
                         log_analytics=destinations_log_analytics,
                         azure_monitor_metrics=destinations_azure_monitor_metrics,
                         performance_counters=data_sources_performance_counters,
                         windows_event_logs=data_sources_windows_event_logs,
                         syslog=data_sources_syslog,
                         extensions=data_sources_extensions)

def monitor_data_collection_rule_update(client,
                                        resource_group_name,
                                        name,
                                        tags=None):
    return client.update(resource_group_name=resource_group_name,
                         data_collection_rule_name=name,
                         tags=tags)
