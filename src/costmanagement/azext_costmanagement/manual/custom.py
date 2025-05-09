# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def costmanagement_export_create(client,
                                 scope,
                                 export_name,
                                 delivery_storage_container,
                                 delivery_storage_account_id,
                                 definition_timeframe,
                                 delivery_directory=None,
                                 definition_type=None,
                                 definition_time_period=None,
                                 definition_dataset_configuration=None,
                                 schedule_status=None,
                                 schedule_recurrence=None,
                                 schedule_recurrence_period=None):

    export_parameters = {}

    export_parameters['format'] = 'Csv'  # Currently only 'Csv' is supported.

    export_parameters['delivery_info'] = {}
    export_parameters['delivery_info']['destination'] = {}
    export_parameters['delivery_info']['destination']['resource_id'] = delivery_storage_account_id
    export_parameters['delivery_info']['destination']['container'] = delivery_storage_container
    export_parameters['delivery_info']['destination']['root_folder_path'] = delivery_directory

    export_parameters['definition'] = {}
    export_parameters['definition']['type'] = definition_type
    export_parameters['definition']['timeframe'] = definition_timeframe
    export_parameters['definition']['time_period'] = definition_time_period
    export_parameters['definition']['data_set'] = {}
    export_parameters['definition']['data_set']['granularity'] = 'Daily'  # Currently only 'Daily' is supported.
    export_parameters['definition']['data_set']['configuration'] = definition_dataset_configuration

    export_parameters['schedule'] = {}
    export_parameters['schedule']['status'] = schedule_status
    export_parameters['schedule']['recurrence'] = schedule_recurrence
    export_parameters['schedule']['recurrence_period'] = schedule_recurrence_period

    return client.create_or_update(scope=scope,
                                   export_name=export_name,
                                   parameters=export_parameters)


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
                                 schedule_status=None,
                                 schedule_recurrence=None,
                                 schedule_recurrence_period=None):

    export_instance = client.get(scope=scope, export_name=export_name)

    schedule = {
        'status': schedule_status or export_instance.schedule.status,
        'recurrence': schedule_recurrence or export_instance.schedule.recurrence,
        'recurrence_period': schedule_recurrence_period or export_instance.schedule.recurrence_period
    }

    delivery_info = {
        'destination': {
            'resource_id': delivery_storage_account_id or export_instance.delivery_info.destination.resource_id,
            'container': delivery_storage_container or export_instance.delivery_info.destination.container,
            'root_folder_path': delivery_directory or export_instance.delivery_info.destination.root_folder_path,
        }
    }

    definition = {
        'type': export_instance.definition.type,
        'timeframe': definition_timeframe or export_instance.definition.timeframe,
        'time_period': definition_time_period or export_instance.definition.time_period,
        'data_set': {
            'configuration': definition_dataset_configuration or export_instance.definition.data_set.configuration,
            'granularity': export_instance.definition.data_set.granularity
        }
    }

    with cmd.update_context(export_instance) as c:
        # update export schedule configuration
        c.set_param('schedule', schedule)

        # update delivery info
        c.set_param('delivery_info', delivery_info)

        # update export definition
        c.set_param('definition', definition)

    return client.create_or_update(scope=scope, export_name=export_name, parameters=export_instance)


def costmanagement_export_list(client, scope):
    return client.list(scope=scope).value   # value exist even the result is empty


def costmanagement_export_show(client, scope, export_name):
    return client.get(scope=scope, export_name=export_name)


def costmanagement_export_delete(client, scope, export_name):
    return client.delete(scope=scope, export_name=export_name)
