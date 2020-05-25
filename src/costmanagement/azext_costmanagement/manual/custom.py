# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json


def costmanagement_query(cmd,
                         client,
                         scope,
                         type_,
                         timeframe,
                         time_period=None,
                         dataset_configuration=None,
                         dataset_aggregation=None,
                         dataset_grouping=None,
                         dataset_filter=None):
    from azext_costmanagement.generated.custom import costmanagement_query_usage

    # for now, query is for Azure cloud only, not for external cloud
    return costmanagement_query_usage(cmd,
                                      client,
                                      scope,
                                      type_,
                                      timeframe,
                                      time_period,
                                      dataset_configuration,
                                      dataset_aggregation,
                                      dataset_grouping,
                                      dataset_filter)


def costmanagement_export_create(cmd,
                                 client,
                                 scope,
                                 export_name,
                                 delivery_storage_container,
                                 delivery_storage_account_id,
                                 definition_timeframe,
                                 delivery_directory=None,
                                 definition_type=None,
                                 definition_time_period=None,
                                 definition_dataset_configuration=None,
                                 definition_dataset_aggregation=None,
                                 definition_dataset_grouping=None,
                                 definition_dataset_filter=None,
                                 schedule_status=None,
                                 schedule_recurrence=None,
                                 schedule_recurrence_period=None):
    if isinstance(definition_dataset_aggregation, str):
        definition_dataset_aggregation = json.loads(definition_dataset_aggregation)
    if isinstance(definition_dataset_filter, str):
        definition_dataset_filter = json.loads(definition_dataset_filter)

    delivery_info_destination = {
        'resource_id': delivery_storage_account_id,
        'container': delivery_storage_container,
        'root_folder_path': delivery_directory,
    }

    return client.create_or_update(scope=scope,
                                   export_name=export_name,
                                   type=definition_type,
                                   timeframe=definition_timeframe,
                                   time_period=definition_time_period,
                                   configuration=definition_dataset_configuration,
                                   aggregation=definition_dataset_aggregation,
                                   grouping=definition_dataset_grouping,
                                   filter=definition_dataset_filter,
                                   destination=delivery_info_destination,
                                   status=schedule_status,
                                   recurrence=schedule_recurrence,
                                   recurrence_period=schedule_recurrence_period)


def costmanagement_export_list(cmd, client, scope):
    return client.list(scope=scope).value   # value exist even the result is empty
