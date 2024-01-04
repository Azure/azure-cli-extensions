# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from azure.cli.core.azclierror import InvalidArgumentValueError
from .aaz.latest.tsi.environment import List as _EnvironmentList
from .aaz.latest.tsi.reference_data_set import List as _ReferenceDataSetList


def timeseriesinsights_environment_gen1_create(cmd, resource_group_name,
                                               environment_name,
                                               location,
                                               sku,
                                               data_retention_time,
                                               tags=None,
                                               storage_limit_exceeded_behavior=None,
                                               partition_key_properties=None,
                                               no_wait=False):
    from .aaz.latest.tsi.environment import Create as _EnvironmentCreate
    Create = _EnvironmentCreate(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['sku'] = sku
    parameters['gen1'] = {}
    parameters['gen1']['data_retention_time'] = data_retention_time
    parameters['gen1']['storage_limit_exceeded_behavior'] = storage_limit_exceeded_behavior
    parameters['gen1']['partition_key_properties'] = partition_key_properties
    parameters['no_wait'] = no_wait

    return Create(parameters)


def timeseriesinsights_environment_gen1_update(cmd,
                                               resource_group_name,
                                               environment_name,
                                               sku=None,
                                               data_retention_time=None,
                                               tags=None,
                                               storage_limit_exceeded_behavior=None,
                                               no_wait=False):
    from .aaz.latest.tsi.environment import Update as _EnvironmentUpdate
    Update = _EnvironmentUpdate(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    parameters['gen1'] = {}
    if sku is not None:
        parameters['sku'] = sku
    if data_retention_time is not None:
        parameters['gen1']['data_retention_time'] = data_retention_time
    if storage_limit_exceeded_behavior is not None:
        parameters['gen1']['storage_limit_exceeded_behavior'] = storage_limit_exceeded_behavior
    if tags is not None:
        parameters['tags'] = tags
    parameters['no_wait'] = no_wait

    return Update(parameters)


def timeseriesinsights_environment_gen2_create(cmd,
                                               resource_group_name,
                                               environment_name,
                                               location,
                                               sku,
                                               time_series_id_properties,
                                               storage_configuration,
                                               tags=None,
                                               warm_store_configuration=None,
                                               no_wait=False):
    from .aaz.latest.tsi.environment import Create as _EnvironmentCreate
    Create = _EnvironmentCreate(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['sku'] = sku
    parameters['gen2'] = {}
    parameters['gen2']['time_series_id_properties'] = time_series_id_properties
    parameters['gen2']['storage_configuration'] = storage_configuration
    if warm_store_configuration is not None:
        parameters['gen2']['warm_store_configuration'] = warm_store_configuration
    parameters['no_wait'] = no_wait

    return Create(parameters)


def timeseriesinsights_environment_gen2_update(cmd,
                                               resource_group_name,
                                               environment_name,
                                               storage_configuration=None,
                                               tags=None,
                                               warm_store_configuration=None,
                                               no_wait=False):
    from .aaz.latest.tsi.environment import Update as _EnvironmentUpdate
    Update = _EnvironmentUpdate(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    parameters['gen2'] = {}
    if storage_configuration is not None:
        parameters['gen2']['storage_configuration'] = storage_configuration
    if warm_store_configuration is not None:
        parameters['gen2']['warm_store_configuration'] = warm_store_configuration
    if tags is not None:
        parameters['tags'] = tags
    parameters['no_wait'] = no_wait

    return Update(parameters)


def timeseriesinsights_event_source_list(client,
                                         resource_group_name,
                                         environment_name):
    return client.list_by_environment(resource_group_name=resource_group_name,
                                      environment_name=environment_name).value


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
                                                     shared_access_key=None,
                                                     local_timestamp=None,
                                                     timestamp_property_name=None,
                                                     tags=None):
    instance = timeseriesinsights_event_source_show(client, resource_group_name, environment_name, event_source_name)
    body = instance.as_dict(keep_readonly=False)
    if body['kind'] != 'Microsoft.EventHub':
        raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(
            body['kind'], 'Microsoft.EventHub'))

    patch_parameters = {
        'kind': 'Microsoft.EventHub'
    }
    if tags is not None:
        patch_parameters['tags'] = tags
    if shared_access_key is not None:
        patch_parameters['shared_access_key'] = shared_access_key
    if local_timestamp is not None:
        patch_parameters['local_timestamp'] = local_timestamp
    if timestamp_property_name is not None:
        patch_parameters['timestamp_property_name'] = timestamp_property_name

    if len(patch_parameters) > 2:  # Only a single event source property can be updated per PATCH request
        body.update(patch_parameters)
        if 'shared_access_key' not in patch_parameters:
            raise InvalidArgumentValueError('--shared-access-key is required for multi properties update')
        return client.create_or_update(resource_group_name=resource_group_name,
                                       environment_name=environment_name,
                                       event_source_name=event_source_name,
                                       parameters=body)
    return client.update(resource_group_name=resource_group_name,
                         environment_name=environment_name,
                         event_source_name=event_source_name,
                         event_source_update_parameters=patch_parameters)


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
                                                   shared_access_key=None,
                                                   local_timestamp=None,
                                                   timestamp_property_name=None,
                                                   tags=None):
    instance = timeseriesinsights_event_source_show(client, resource_group_name, environment_name, event_source_name)
    body = instance.as_dict(keep_readonly=False)
    if body['kind'] != 'Microsoft.IoTHub':
        raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(
            body['kind'], 'Microsoft.IoTHub'))

    patch_parameters = {
        'kind': 'Microsoft.IoTHub'
    }
    if tags is not None:
        patch_parameters['tags'] = tags
    if shared_access_key is not None:
        patch_parameters['shared_access_key'] = shared_access_key
    if local_timestamp is not None:
        patch_parameters['local_timestamp'] = local_timestamp
    if timestamp_property_name is not None:
        patch_parameters['timestamp_property_name'] = timestamp_property_name

    if len(patch_parameters) > 2:  # Only a single event source property can be updated per PATCH request
        body.update(patch_parameters)
        if 'shared_access_key' not in patch_parameters:
            raise InvalidArgumentValueError('--shared-access-key is required for multi properties update')
        return client.create_or_update(resource_group_name=resource_group_name,
                                       environment_name=environment_name,
                                       event_source_name=event_source_name,
                                       parameters=body)
    return client.update(resource_group_name=resource_group_name,
                         environment_name=environment_name,
                         event_source_name=event_source_name,
                         event_source_update_parameters=patch_parameters)


def timeseriesinsights_reference_data_set_create(cmd,
                                                 resource_group_name,
                                                 environment_name,
                                                 reference_data_set_name,
                                                 location,
                                                 key_properties,
                                                 tags=None,
                                                 data_string_comparison_behavior=None):
    from .aaz.latest.tsi.reference_data_set import Create as _ReferenceDataSetCreate
    Create = _ReferenceDataSetCreate(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    parameters['reference_data_set_name'] = reference_data_set_name
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['key_properties'] = key_properties
    parameters['data_string_comparison_behavior'] = data_string_comparison_behavior
    return Create(parameters)


class EnvironmentList(_EnvironmentList):
    def _output(self):
        result = super()._output(self)
        return result["value"]


class ReferenceDataSetList(_ReferenceDataSetList):
    def _output(self):
        result = super()._output(self)
        return result["value"]
