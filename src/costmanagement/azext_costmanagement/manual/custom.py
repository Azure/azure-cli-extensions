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
                                 definition_dataset_grouping=None,
                                 schedule_status=None,
                                 schedule_recurrence=None,
                                 schedule_recurrence_period=None):

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
                                   grouping=definition_dataset_grouping,
                                   destination=delivery_info_destination,
                                   status=schedule_status,
                                   recurrence=schedule_recurrence,
                                   recurrence_period=schedule_recurrence_period)


def costmanagement_export_update(cmd,
                                 client,
                                 scope,
                                 export_name,
                                 delivery_storage_container=None,
                                 delivery_storage_account_id=None,
                                 delivery_directory=None,
                                 definition_timeframe=None,
                                 definition_time_period=None,
                                 definition_dataset_configuration=None,
                                 definition_dataset_grouping=None,
                                 schedule_status=None,
                                 schedule_recurrence=None,
                                 schedule_recurrence_period=None):

    export_instance = client.get(scope=scope, export_name=export_name)

    delivery_info_destination = {
        'resource_id': delivery_storage_account_id or export_instance.destination.resource_id,
        'container': delivery_storage_container or export_instance.destination.container,
        'root_folder_path': delivery_directory or export_instance.destination.root_folder_path,
    }

    with cmd.update_context(export_instance) as c:
        # update export schedule configuration
        c.set_param('status', schedule_status)
        c.set_param('recurrence', schedule_recurrence)
        c.set_param('recurrence_period', schedule_recurrence_period)

        # update delivery info
        c.set_param('destination', delivery_info_destination)

        # update export definition
        c.set_param('timeframe', definition_timeframe)
        c.set_param('time_period', definition_time_period)
        c.set_param('configuration', definition_dataset_configuration)
        c.set_param('grouping', definition_dataset_grouping)

    return client.create_or_update(scope=scope,
                                   export_name=export_name,
                                   type=export_instance.type_properties_definition_type,
                                   timeframe=export_instance.timeframe,
                                   time_period=export_instance.time_period,
                                   configuration=export_instance.configuration,
                                   aggregation=export_instance.aggregation,
                                   grouping=export_instance.grouping,
                                   filter=export_instance.filter,
                                   destination=export_instance.destination,
                                   status=export_instance.status,
                                   recurrence=export_instance.recurrence,
                                   recurrence_period=export_instance.recurrence_period,
                                   e_tag=export_instance.e_tag)


def costmanagement_export_list(cmd, client, scope):
    return client.list(scope=scope).value   # value exist even the result is empty


def costmanagement_export_show(cmd, client,
                               scope,
                               export_name):
    return client.get(scope=scope, export_name=export_name)


def costmanagement_export_delete(cmd, client,
                                 scope,
                                 export_name):
    return client.delete(scope=scope,
                         export_name=export_name)
