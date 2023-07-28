# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import InvalidArgumentValueError
from .aaz.latest.tsi.environment import Create as _EnvironmentCreate
from .aaz.latest.tsi.environment import Update as _EnvironmentUpdate
from .aaz.latest.tsi.environment import List as _EnvironmentList
from .aaz.latest.tsi.reference_data_set import Create as _ReferenceDataSetCreate
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

def timeseriesinsights_environment_list(cmd,
                                        resource_group_name=None):
    List = _EnvironmentList(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name

    return List(parameters)["value"]
#
#
# def timeseriesinsights_environment_show(client,
#                                         resource_group_name,
#                                         environment_name,
#                                         expand=None):
#     return client.get(resource_group_name=resource_group_name,
#                       environment_name=environment_name,
#                       expand=expand)
#
#
# def timeseriesinsights_environment_delete(client,
#                                           resource_group_name,
#                                           environment_name):
#     return client.delete(resource_group_name=resource_group_name,
#                          environment_name=environment_name)
#
#
def timeseriesinsights_environment_gen1_update(cmd,
                                               resource_group_name,
                                               environment_name,
                                               sku=None,
                                               data_retention_time=None,
                                               tags=None,
                                               storage_limit_exceeded_behavior=None,
                                               no_wait=False):
    Patch = _EnvironmentUpdate(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    parameters['gen1'] = {}
    parameters['sku'] = sku
    parameters['gen1']['data_retention_time'] = data_retention_time
    parameters['gen1']['storage_limit_exceeded_behavior'] = storage_limit_exceeded_behavior
    parameters['tags'] = tags
    parameters['no_wait'] = no_wait

    return Patch(parameters)
#
# def timeseriesinsights_environment_gen2_create(client,
#                                                resource_group_name,
#                                                environment_name,
#                                                location,
#                                                sku,
#                                                time_series_id_properties,
#                                                storage_configuration,
#                                                tags=None,
#                                                warm_store_configuration=None,
#                                                no_wait=False):
#     parameters = {}
#     parameters['location'] = location
#     parameters['tags'] = tags
#     parameters['kind'] = 'Gen2'
#     parameters['sku'] = sku
#     parameters['time_series_id_properties'] = time_series_id_properties
#     parameters['storage_configuration'] = storage_configuration
#     parameters['warm_store_configuration'] = warm_store_configuration
#     return sdk_no_wait(no_wait,
#                        client.begin_create_or_update,
#                        resource_group_name=resource_group_name,
#                        environment_name=environment_name,
#                        parameters=parameters)
#
#
# def timeseriesinsights_environment_gen2_update(client,
#                                                resource_group_name,
#                                                environment_name,
#                                                storage_configuration=None,
#                                                tags=None,
#                                                warm_store_configuration=None,
#                                                no_wait=False):
#     instance = timeseriesinsights_environment_show(client, resource_group_name, environment_name)
#     body = instance.as_dict(keep_readonly=False)
#     if body['kind'] != 'Gen2':
#         raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(body['kind'], 'Gen2'))
#
#     patch_parameters = {
#         'kind': 'Gen2'
#     }
#     if storage_configuration is not None:
#         patch_parameters['storage_configuration'] = storage_configuration
#     if warm_store_configuration is not None:
#         patch_parameters['warm_store_configuration'] = warm_store_configuration
#
#     if tags is not None:
#         patch_parameters['tags'] = tags
#
#     if len(patch_parameters) > 2:  # Only a single event source property can be updated per PATCH request
#         if 'storage_configuration' not in patch_parameters:
#             raise InvalidArgumentValueError('--storage-configuration is required for multi properties update')
#         body.update(patch_parameters)
#         return sdk_no_wait(no_wait,
#                            client.begin_create_or_update,
#                            resource_group_name=resource_group_name,
#                            environment_name=environment_name,
#                            parameters=body)
#     return sdk_no_wait(no_wait,
#                        client.begin_update,
#                        resource_group_name=resource_group_name,
#                        environment_name=environment_name,
#                        environment_update_parameters=patch_parameters)
#
#
# def timeseriesinsights_event_source_list(client,
#                                          resource_group_name,
#                                          environment_name):
#     return client.list_by_environment(resource_group_name=resource_group_name,
#                                       environment_name=environment_name).value
#
#
# def timeseriesinsights_event_source_show(client,
#                                          resource_group_name,
#                                          environment_name,
#                                          event_source_name):
#     return client.get(resource_group_name=resource_group_name,
#                       environment_name=environment_name,
#                       event_source_name=event_source_name)
#
#
# def timeseriesinsights_event_source_delete(client,
#                                            resource_group_name,
#                                            environment_name,
#                                            event_source_name):
#     return client.delete(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          event_source_name=event_source_name)
#
#
# def timeseriesinsights_event_source_event_hub_create(client,
#                                                      resource_group_name,
#                                                      environment_name,
#                                                      event_source_name,
#                                                      location,
#                                                      event_source_resource_id,
#                                                      service_bus_namespace,
#                                                      event_hub_name,
#                                                      consumer_group_name,
#                                                      key_name,
#                                                      shared_access_key,
#                                                      tags=None,
#                                                      local_timestamp=None,
#                                                      timestamp_property_name=None):
#     parameters = {}
#     parameters['location'] = location
#     parameters['tags'] = tags
#     parameters['kind'] = 'Microsoft.EventHub'
#     parameters['local_timestamp'] = local_timestamp
#     parameters['timestamp_property_name'] = timestamp_property_name
#     parameters['event_source_resource_id'] = event_source_resource_id
#     parameters['service_bus_namespace'] = service_bus_namespace
#     parameters['event_hub_name'] = event_hub_name
#     parameters['consumer_group_name'] = consumer_group_name
#     parameters['key_name'] = key_name
#     parameters['shared_access_key'] = shared_access_key
#     return client.create_or_update(resource_group_name=resource_group_name,
#                                    environment_name=environment_name,
#                                    event_source_name=event_source_name,
#                                    parameters=parameters)
#
#
# def timeseriesinsights_event_source_event_hub_update(client,
#                                                      resource_group_name,
#                                                      environment_name,
#                                                      event_source_name,
#                                                      shared_access_key=None,
#                                                      local_timestamp=None,
#                                                      timestamp_property_name=None,
#                                                      tags=None):
#     instance = timeseriesinsights_event_source_show(client, resource_group_name, environment_name, event_source_name)
#     body = instance.as_dict(keep_readonly=False)
#     if body['kind'] != 'Microsoft.EventHub':
#         raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(
#             body['kind'], 'Microsoft.EventHub'))
#
#     patch_parameters = {
#         'kind': 'Microsoft.EventHub'
#     }
#     if tags is not None:
#         patch_parameters['tags'] = tags
#     if shared_access_key is not None:
#         patch_parameters['shared_access_key'] = shared_access_key
#     if local_timestamp is not None:
#         patch_parameters['local_timestamp'] = local_timestamp
#     if timestamp_property_name is not None:
#         patch_parameters['timestamp_property_name'] = timestamp_property_name
#
#     if len(patch_parameters) > 2:  # Only a single event source property can be updated per PATCH request
#         body.update(patch_parameters)
#         if 'shared_access_key' not in patch_parameters:
#             raise InvalidArgumentValueError('--shared-access-key is required for multi properties update')
#         return client.create_or_update(resource_group_name=resource_group_name,
#                                        environment_name=environment_name,
#                                        event_source_name=event_source_name,
#                                        parameters=body)
#     return client.update(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          event_source_name=event_source_name,
#                          event_source_update_parameters=patch_parameters)
#
#
# def timeseriesinsights_event_source_iot_hub_create(client,
#                                                    resource_group_name,
#                                                    environment_name,
#                                                    event_source_name,
#                                                    location,
#                                                    event_source_resource_id,
#                                                    iot_hub_name,
#                                                    consumer_group_name,
#                                                    key_name,
#                                                    shared_access_key,
#                                                    tags=None,
#                                                    local_timestamp=None,
#                                                    timestamp_property_name=None):
#     parameters = {}
#     parameters['location'] = location
#     parameters['tags'] = tags
#     parameters['kind'] = 'Microsoft.IoTHub'
#     parameters['local_timestamp'] = local_timestamp
#     parameters['timestamp_property_name'] = timestamp_property_name
#     parameters['event_source_resource_id'] = event_source_resource_id
#     parameters['iot_hub_name'] = iot_hub_name
#     parameters['consumer_group_name'] = consumer_group_name
#     parameters['key_name'] = key_name
#     parameters['shared_access_key'] = shared_access_key
#     return client.create_or_update(resource_group_name=resource_group_name,
#                                    environment_name=environment_name,
#                                    event_source_name=event_source_name,
#                                    parameters=parameters)
#
#
# def timeseriesinsights_event_source_iot_hub_update(client,
#                                                    resource_group_name,
#                                                    environment_name,
#                                                    event_source_name,
#                                                    shared_access_key=None,
#                                                    local_timestamp=None,
#                                                    timestamp_property_name=None,
#                                                    tags=None):
#     instance = timeseriesinsights_event_source_show(client, resource_group_name, environment_name, event_source_name)
#     body = instance.as_dict(keep_readonly=False)
#     if body['kind'] != 'Microsoft.IoTHub':
#         raise InvalidArgumentValueError('Instance kind value is "{}", not match "{}"'.format(
#             body['kind'], 'Microsoft.IoTHub'))
#
#     patch_parameters = {
#         'kind': 'Microsoft.IoTHub'
#     }
#     if tags is not None:
#         patch_parameters['tags'] = tags
#     if shared_access_key is not None:
#         patch_parameters['shared_access_key'] = shared_access_key
#     if local_timestamp is not None:
#         patch_parameters['local_timestamp'] = local_timestamp
#     if timestamp_property_name is not None:
#         patch_parameters['timestamp_property_name'] = timestamp_property_name
#
#     if len(patch_parameters) > 2:  # Only a single event source property can be updated per PATCH request
#         body.update(patch_parameters)
#         if 'shared_access_key' not in patch_parameters:
#             raise InvalidArgumentValueError('--shared-access-key is required for multi properties update')
#         return client.create_or_update(resource_group_name=resource_group_name,
#                                        environment_name=environment_name,
#                                        event_source_name=event_source_name,
#                                        parameters=body)
#     return client.update(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          event_source_name=event_source_name,
#                          event_source_update_parameters=patch_parameters)
#
#
def timeseriesinsights_reference_data_set_list(cmd,
                                               resource_group_name,
                                               environment_name):
    List = _ReferenceDataSetList(cmd.loader)
    parameters = {}
    parameters['resource_group'] = resource_group_name
    parameters['environment_name'] = environment_name
    return List(parameters)["value"]
#
#
# def timeseriesinsights_reference_data_set_show(client,
#                                                resource_group_name,
#                                                environment_name,
#                                                reference_data_set_name):
#     return client.get(resource_group_name=resource_group_name,
#                       environment_name=environment_name,
#                       reference_data_set_name=reference_data_set_name)
#
#
def timeseriesinsights_reference_data_set_create(cmd,
                                                 resource_group_name,
                                                 environment_name,
                                                 reference_data_set_name,
                                                 location,
                                                 key_properties,
                                                 tags=None,
                                                 data_string_comparison_behavior=None):
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
#
#
# def timeseriesinsights_reference_data_set_update(client,
#                                                  resource_group_name,
#                                                  environment_name,
#                                                  reference_data_set_name,
#                                                  tags=None):
#     patch_parameters = {}
#     if tags is not None:
#         patch_parameters['tags'] = tags
#
#     return client.update(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          reference_data_set_name=reference_data_set_name,
#                          reference_data_set_update_parameters=patch_parameters)
#
#
# def timeseriesinsights_reference_data_set_delete(client,
#                                                  resource_group_name,
#                                                  environment_name,
#                                                  reference_data_set_name):
#     return client.delete(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          reference_data_set_name=reference_data_set_name)
#
#
# def timeseriesinsights_access_policy_list(client,
#                                           resource_group_name,
#                                           environment_name):
#     return client.list_by_environment(resource_group_name=resource_group_name,
#                                       environment_name=environment_name).value
#
#
# def timeseriesinsights_access_policy_show(client,
#                                           resource_group_name,
#                                           environment_name,
#                                           access_policy_name):
#     return client.get(resource_group_name=resource_group_name,
#                       environment_name=environment_name,
#                       access_policy_name=access_policy_name)
#
#
# def timeseriesinsights_access_policy_create(client,
#                                             resource_group_name,
#                                             environment_name,
#                                             access_policy_name,
#                                             principal_object_id=None,
#                                             description=None,
#                                             roles=None):
#     parameters = {}
#     parameters['principal_object_id'] = principal_object_id
#     parameters['description'] = description
#     parameters['roles'] = roles
#     return client.create_or_update(resource_group_name=resource_group_name,
#                                    environment_name=environment_name,
#                                    access_policy_name=access_policy_name,
#                                    parameters=parameters)
#
#
# def timeseriesinsights_access_policy_update(client,
#                                             resource_group_name,
#                                             environment_name,
#                                             access_policy_name,
#                                             description=None,
#                                             roles=None):
#     patch_parameters = {}
#     if description is not None:
#         patch_parameters['description'] = description
#
#     if roles is not None:
#         patch_parameters['roles'] = roles
#
#     return client.update(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          access_policy_name=access_policy_name,
#                          access_policy_update_parameters=patch_parameters)
#
#
# def timeseriesinsights_access_policy_delete(client,
#                                             resource_group_name,
#                                             environment_name,
#                                             access_policy_name):
#     return client.delete(resource_group_name=resource_group_name,
#                          environment_name=environment_name,
#                          access_policy_name=access_policy_name)
