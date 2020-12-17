# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import InvalidArgumentValueError


def timeseriesinsights_environment_list(client,
                                        resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def timeseriesinsights_environment_show(client,
                                        resource_group_name,
                                        environment_name,
                                        expand=None):
    return client.get(resource_group_name=resource_group_name,
                      environment_name=environment_name,
                      expand=expand)


def timeseriesinsights_environment_delete(client,
                                          resource_group_name,
                                          environment_name):
    return client.delete(resource_group_name=resource_group_name,
                         environment_name=environment_name)


def timeseriesinsights_environment_gen1_create(client,
                                               resource_group_name,
                                               environment_name,
                                               location,
                                               sku,
                                               data_retention_time,
                                               tags=None,
                                               storage_limit_exceeded_behavior=None,
                                               partition_key_properties=None,
                                               no_wait=False):
    parameters = {}
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['kind'] = 'Gen1'
    parameters['sku'] = sku
    parameters['data_retention_time'] = data_retention_time
    parameters['storage_limit_exceeded_behavior'] = storage_limit_exceeded_behavior
    parameters['partition_key_properties'] = partition_key_properties
    return sdk_no_wait(no_wait,
                       client.create_or_update,
                       resource_group_name=resource_group_name,
                       environment_name=environment_name,
                       parameters=parameters)


def timeseriesinsights_environment_gen1_update(client,
                                               resource_group_name,
                                               environment_name,
                                               sku=None,
                                               data_retention_time=None,
                                               tags=None,
                                               storage_limit_exceeded_behavior=None,
                                               partition_key_properties=None,
                                               no_wait=False):
    from ..custom import timeseriesinsights_environment_show
    instance = timeseriesinsights_environment_show(client, resource_group_name, environment_name)
    body = instance.as_dict(keep_readonly=False)
    if body['kind'] != 'Gen1':
        raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(body['kind'], 'Gen1'))

    put_parameters = {}
    if sku is not None:
        put_parameters['sku'] = sku
    if data_retention_time is not None:
        put_parameters['data_retention_time'] = data_retention_time
    if storage_limit_exceeded_behavior is not None:
        put_parameters['storage_limit_exceeded_behavior'] = storage_limit_exceeded_behavior
    if partition_key_properties is not None:
        put_parameters['partition_key_properties'] = partition_key_properties

    patch_parameters = {}
    if tags is not None:
        if put_parameters:
            put_parameters['tags'] = tags
        else:
            patch_parameters['tags'] = tags

    if put_parameters:
        body.update(put_parameters)
        return sdk_no_wait(no_wait,
                           client.begin_create_or_update,
                           resource_group_name=resource_group_name,
                           environment_name=environment_name,
                           parameters=body)
    else:
        return sdk_no_wait(no_wait,
                           client.begin_update,
                           resource_group_name=resource_group_name,
                           environment_name=environment_name,
                           environment_update_parameters=patch_parameters)


def timeseriesinsights_environment_gen2_create(client,
                                               resource_group_name,
                                               environment_name,
                                               location,
                                               sku,
                                               time_series_id_properties,
                                               storage_configuration,
                                               tags=None,
                                               warm_store_configuration=None,
                                               no_wait=False):
    parameters = {}
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['kind'] = 'Gen2'
    parameters['sku'] = sku
    parameters['time_series_id_properties'] = time_series_id_properties
    parameters['storage_configuration'] = storage_configuration
    parameters['warm_store_configuration'] = warm_store_configuration
    return sdk_no_wait(no_wait,
                       client.create_or_update,
                       resource_group_name=resource_group_name,
                       environment_name=environment_name,
                       parameters=parameters)


def timeseriesinsights_environment_gen2_update(client,
                                               resource_group_name,
                                               environment_name,
                                               sku=None,
                                               time_series_id_properties=None,
                                               storage_configuration=None,
                                               tags=None,
                                               warm_store_configuration=None,
                                               no_wait=False):
    from ..custom import timeseriesinsights_environment_show
    instance = timeseriesinsights_environment_show(client, resource_group_name, environment_name)
    body = instance.as_dict(keep_readonly=False)
    if body['kind'] != 'Gen2':
        raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(body['kind'], 'Gen2'))

    put_parameters = {}
    if sku is not None:
        put_parameters['sku'] = sku
    if time_series_id_properties is not None:
        put_parameters['time_series_id_properties'] = time_series_id_properties
    if storage_configuration is not None:
        put_parameters['storage_configuration'] = storage_configuration
    if warm_store_configuration is not None:
        put_parameters['warm_store_configuration'] = warm_store_configuration

    patch_parameters = {}
    if tags is not None:
        if put_parameters:
            put_parameters['tags'] = tags
        else:
            patch_parameters['tags'] = tags

    if put_parameters:
        return sdk_no_wait(no_wait,
                           client.begin_create_or_update,
                           resource_group_name=resource_group_name,
                           environment_name=environment_name,
                           parameters=body)
    else:
        return sdk_no_wait(no_wait,
                           client.begin_update,
                           resource_group_name=resource_group_name,
                           environment_name=environment_name,
                           environment_update_parameters=patch_parameters)


def timeseriesinsights_event_source_list(client,
                                         resource_group_name,
                                         environment_name):
    return client.list_by_environment(resource_group_name=resource_group_name,
                                      environment_name=environment_name)


def timeseriesinsights_event_source_show(client,
                                         resource_group_name,
                                         environment_name,
                                         event_source_name):
    return client.get(resource_group_name=resource_group_name,
                      environment_name=environment_name,
                      event_source_name=event_source_name)


def timeseriesinsights_event_source_delete(client,
                                           resource_group_name,
                                           environment_name,
                                           event_source_name):
    return client.delete(resource_group_name=resource_group_name,
                         environment_name=environment_name,
                         event_source_name=event_source_name)


def timeseriesinsights_event_source_event_hub_create(client,
                                                     resource_group_name,
                                                     environment_name,
                                                     event_source_name,
                                                     location,
                                                     event_source_resource_id,
                                                     service_bus_namespace,
                                                     event_hub_name,
                                                     consumer_group_name,
                                                     key_name,
                                                     shared_access_key,
                                                     tags=None,
                                                     local_timestamp=None,
                                                     timestamp_property_name=None):
    parameters = {}
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['kind'] = 'Microsoft.EventHub'
    parameters['local_timestamp'] = local_timestamp
    parameters['timestamp_property_name'] = timestamp_property_name
    parameters['event_source_resource_id'] = event_source_resource_id
    parameters['service_bus_namespace'] = service_bus_namespace
    parameters['event_hub_name'] = event_hub_name
    parameters['consumer_group_name'] = consumer_group_name
    parameters['key_name'] = key_name
    parameters['shared_access_key'] = shared_access_key
    return client.create_or_update(resource_group_name=resource_group_name,
                                   environment_name=environment_name,
                                   event_source_name=event_source_name,
                                   parameters=parameters)


def timeseriesinsights_event_source_event_hub_update(client,
                                                     resource_group_name,
                                                     environment_name,
                                                     event_source_name,
                                                     location,
                                                     event_source_resource_id,
                                                     service_bus_namespace,
                                                     event_hub_name,
                                                     consumer_group_name,
                                                     key_name,
                                                     shared_access_key,
                                                     tags=None,
                                                     local_timestamp=None,
                                                     timestamp_property_name=None):
    parameters = {}
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['kind'] = 'Microsoft.EventHub'
    parameters['local_timestamp'] = local_timestamp
    parameters['timestamp_property_name'] = timestamp_property_name
    parameters['event_source_resource_id'] = event_source_resource_id
    parameters['service_bus_namespace'] = service_bus_namespace
    parameters['event_hub_name'] = event_hub_name
    parameters['consumer_group_name'] = consumer_group_name
    parameters['key_name'] = key_name
    parameters['shared_access_key'] = shared_access_key
    return client.create_or_update(resource_group_name=resource_group_name,
                                   environment_name=environment_name,
                                   event_source_name=event_source_name,
                                   parameters=parameters)


def timeseriesinsights_event_source_iot_hub_create(client,
                                                   resource_group_name,
                                                   environment_name,
                                                   event_source_name,
                                                   location,
                                                   event_source_resource_id,
                                                   iot_hub_name,
                                                   consumer_group_name,
                                                   key_name,
                                                   shared_access_key,
                                                   tags=None,
                                                   local_timestamp=None,
                                                   timestamp_property_name=None):
    parameters = {}
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['kind'] = 'Microsoft.IoTHub'
    parameters['local_timestamp'] = local_timestamp
    parameters['timestamp_property_name'] = timestamp_property_name
    parameters['event_source_resource_id'] = event_source_resource_id
    parameters['iot_hub_name'] = iot_hub_name
    parameters['consumer_group_name'] = consumer_group_name
    parameters['key_name'] = key_name
    parameters['shared_access_key'] = shared_access_key
    return client.create_or_update(resource_group_name=resource_group_name,
                                   environment_name=environment_name,
                                   event_source_name=event_source_name,
                                   parameters=parameters)


def timeseriesinsights_event_source_iot_hub_update(client,
                                                   resource_group_name,
                                                   environment_name,
                                                   event_source_name,
                                                   location,
                                                   event_source_resource_id,
                                                   iot_hub_name,
                                                   consumer_group_name,
                                                   key_name,
                                                   shared_access_key,
                                                   tags=None,
                                                   local_timestamp=None,
                                                   timestamp_property_name=None):
    parameters = {}
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['kind'] = 'Microsoft.IoTHub'
    parameters['local_timestamp'] = local_timestamp
    parameters['timestamp_property_name'] = timestamp_property_name
    parameters['event_source_resource_id'] = event_source_resource_id
    parameters['iot_hub_name'] = iot_hub_name
    parameters['consumer_group_name'] = consumer_group_name
    parameters['key_name'] = key_name
    parameters['shared_access_key'] = shared_access_key
    return client.create_or_update(resource_group_name=resource_group_name,
                                   environment_name=environment_name,
                                   event_source_name=event_source_name,
                                   parameters=parameters)