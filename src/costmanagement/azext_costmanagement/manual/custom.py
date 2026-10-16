# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from urllib.parse import quote

from azure.cli.core.util import send_raw_request


COSTMANAGEMENT_EXPORT_API_VERSION = '2023-11-01'
STORAGE_ACCOUNT_API_VERSION = '2023-05-01'


def _normalize_arm_id(resource_id):
    return '/{}'.format(resource_id.strip('/'))


def _get_attribute_value(value, name):
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None)


def _serialize_dataset_configuration(configuration):
    columns = _get_attribute_value(configuration, 'columns')
    if columns is None:
        return None
    return {'columns': columns}


def _serialize_time_period(time_period):
    from_value = _get_attribute_value(time_period, 'from_property')
    to_value = _get_attribute_value(time_period, 'to')
    if from_value is None and to_value is None:
        return None

    serialized_period = {}
    if from_value is not None:
        serialized_period['from'] = from_value
    if to_value is not None:
        serialized_period['to'] = to_value
    return serialized_period


def _build_export_body(format_type,
                       delivery_storage_container,
                       delivery_storage_account_id,
                       delivery_directory,
                       definition_type,
                       definition_timeframe,
                       definition_time_period,
                       definition_dataset_configuration,
                       schedule_status,
                       schedule_recurrence,
                       schedule_recurrence_period,
                       e_tag=None,
                       location=None):
    export_body = {
        'properties': {
            'format': format_type,
            'deliveryInfo': {
                'destination': {
                    'resourceId': delivery_storage_account_id,
                    'container': delivery_storage_container,
                    'rootFolderPath': delivery_directory
                }
            },
            'definition': {
                'type': definition_type,
                'timeframe': definition_timeframe,
                'timePeriod': _serialize_time_period(definition_time_period),
                'dataSet': {
                    'granularity': 'Daily',
                    'configuration': _serialize_dataset_configuration(definition_dataset_configuration)
                }
            },
            'schedule': {
                'status': schedule_status,
                'recurrence': schedule_recurrence,
                'recurrencePeriod': _serialize_time_period(schedule_recurrence_period)
            }
        }
    }

    if e_tag is not None:
        export_body['eTag'] = e_tag

    if delivery_storage_account_id:
        export_body['identity'] = {'type': 'SystemAssigned'}
        export_body['location'] = location

    return export_body


def _get_storage_account_location(cmd, storage_account_id):
    management_endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip('/')
    request_url = '{}{}?api-version={}'.format(
        management_endpoint,
        _normalize_arm_id(storage_account_id),
        STORAGE_ACCOUNT_API_VERSION)
    return send_raw_request(cmd.cli_ctx, 'GET', request_url).json()['location']


def _put_export(cmd, scope, export_name, export_body):
    management_endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip('/')
    request_url = '{}{}/providers/Microsoft.CostManagement/exports/{}?api-version={}'.format(
        management_endpoint,
        _normalize_arm_id(scope),
        quote(export_name, safe=''),
        COSTMANAGEMENT_EXPORT_API_VERSION)
    return send_raw_request(cmd.cli_ctx, 'PUT', request_url, body=export_body).json()


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
                                 schedule_status=None,
                                 schedule_recurrence=None,
                                 schedule_recurrence_period=None):
    del client

    location = _get_storage_account_location(cmd, delivery_storage_account_id)
    export_body = _build_export_body(format_type='Csv',
                                     delivery_storage_container=delivery_storage_container,
                                     delivery_storage_account_id=delivery_storage_account_id,
                                     delivery_directory=delivery_directory,
                                     definition_type=definition_type,
                                     definition_timeframe=definition_timeframe,
                                     definition_time_period=definition_time_period,
                                     definition_dataset_configuration=definition_dataset_configuration,
                                     schedule_status=schedule_status,
                                     schedule_recurrence=schedule_recurrence,
                                     schedule_recurrence_period=schedule_recurrence_period,
                                     location=location)
    return _put_export(cmd, scope, export_name, export_body)


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

    del client

    resource_id = delivery_storage_account_id or export_instance.delivery_info.destination.resource_id
    location = _get_storage_account_location(cmd, resource_id)
    export_body = _build_export_body(
        format_type=export_instance.format,
        delivery_storage_container=delivery_storage_container or export_instance.delivery_info.destination.container,
        delivery_storage_account_id=resource_id,
        delivery_directory=delivery_directory or export_instance.delivery_info.destination.root_folder_path,
        definition_type=export_instance.definition.type,
        definition_timeframe=definition_timeframe or export_instance.definition.timeframe,
        definition_time_period=definition_time_period or export_instance.definition.time_period,
        definition_dataset_configuration=definition_dataset_configuration or export_instance.definition.data_set.configuration,
        schedule_status=schedule_status or export_instance.schedule.status,
        schedule_recurrence=schedule_recurrence or export_instance.schedule.recurrence,
        schedule_recurrence_period=schedule_recurrence_period or export_instance.schedule.recurrence_period,
        e_tag=export_instance.e_tag,
        location=location)
    return _put_export(cmd, scope, export_name, export_body)


def costmanagement_export_list(client, scope):
    return client.list(scope=scope).value   # value exist even the result is empty


def costmanagement_export_show(client, scope, export_name):
    return client.get(scope=scope, export_name=export_name)


def costmanagement_export_delete(client, scope, export_name):
    return client.delete(scope=scope, export_name=export_name)
