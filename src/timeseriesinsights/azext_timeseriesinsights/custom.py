# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from azure.cli.core.util import sdk_no_wait


def create_timeseriesinsights_environment_standard(cmd, client,
                                                   resource_group_name, environment_name,
                                                   sku_name, sku_capacity,
                                                   data_retention_time,
                                                   storage_limit_exceeded_behavior=None,
                                                   partition_key_properties=None,
                                                   location=None, tags=None, no_wait=False):
    from .vendored_sdks.timeseriesinsights.models import StandardEnvironmentCreateOrUpdateParameters, Sku, \
        TimeSeriesIdProperty

    parameters = StandardEnvironmentCreateOrUpdateParameters(
        location=location,
        tags=tags,
        sku=Sku(name=sku_name, capacity=sku_capacity),
        data_retention_time=data_retention_time,
        storage_limit_exceeded_behavior=storage_limit_exceeded_behavior,
        # Need to confirm whether multiple key properties are supported
        partition_key_properties=[TimeSeriesIdProperty(name=id_property, type="String") for id_property in partition_key_properties]
    )
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name=resource_group_name, environment_name=environment_name, parameters=parameters)


def update_timeseriesinsights_environment_standard(cmd, client,
                                                   resource_group_name, environment_name,
                                                   sku_name=None, sku_capacity=None,
                                                   data_retention_time=None, storage_limit_exceeded_behavior=None,
                                                   partition_key_properties=None, tags=None, no_wait=False):
    from .vendored_sdks.timeseriesinsights.models import StandardEnvironmentUpdateParameters, Sku, TimeSeriesIdProperty

    parameters = StandardEnvironmentUpdateParameters(
        tags=tags,
        sku=Sku(name=sku_name, capacity=sku_capacity) if sku_name and sku_capacity else None,
        data_retention_time=data_retention_time,
        storage_limit_exceeded_behavior=storage_limit_exceeded_behavior,
        partition_key_properties=[TimeSeriesIdProperty(name=id_property, type="String") for id_property in partition_key_properties] if partition_key_properties else None
    )
    return sdk_no_wait(no_wait, client.update, resource_group_name=resource_group_name, environment_name=environment_name, parameters=parameters)


def create_timeseriesinsights_environment_longterm(cmd, client,
                                                   resource_group_name, environment_name,
                                                   sku_name, sku_capacity,
                                                   time_series_id_properties,
                                                   storage_account_name,
                                                   storage_management_key,
                                                   data_retention,
                                                   location=None, tags=None, no_wait=False):
    from .vendored_sdks.timeseriesinsights.models import LongTermEnvironmentCreateOrUpdateParameters, Sku, \
        TimeSeriesIdProperty, LongTermStorageConfigurationInput
    parameters = LongTermEnvironmentCreateOrUpdateParameters(
        location=location,
        tags=tags,
        sku=Sku(name=sku_name, capacity=sku_capacity),
        time_series_id_properties=[TimeSeriesIdProperty(name=time_series_id_properties, type="String")],
        storage_configuration=LongTermStorageConfigurationInput(account_name=storage_account_name, management_key=storage_management_key),
        data_retention=data_retention)
    return sdk_no_wait(no_wait, client.create_or_update, resource_group_name=resource_group_name, environment_name=environment_name, parameters=parameters)


def update_timeseriesinsights_environment_longterm(cmd, client,
                                                   resource_group_name, environment_name,
                                                   storage_management_key=None,
                                                   data_retention=None,
                                                   tags=None, no_wait=False):
    from .vendored_sdks.timeseriesinsights.models import LongTermEnvironmentUpdateParameters, \
        LongTermStorageConfigurationMutableProperties
    parameters = LongTermEnvironmentUpdateParameters(
        tags=tags,
        storage_configuration=LongTermStorageConfigurationMutableProperties(management_key=storage_management_key) if storage_management_key else None,
        data_retention=data_retention)
    return sdk_no_wait(no_wait, client.update, resource_group_name=resource_group_name, environment_name=environment_name, parameters=parameters)


def list_timeseriesinsights_environment(cmd, client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def create_timeseriesinsights_event_source_eventhub(cmd, client,
                                                    resource_group_name, environment_name, event_source_name,
                                                    timestamp_property_name, event_source_resource_id,
                                                    consumer_group_name, key_name, shared_access_key,
                                                    location=None, tags=None):
    from azext_timeseriesinsights.vendored_sdks.timeseriesinsights.models import EventHubEventSourceCreateOrUpdateParameters
    from msrestazure.tools import parse_resource_id
    parsed_id = parse_resource_id(event_source_resource_id)
    parameters = EventHubEventSourceCreateOrUpdateParameters(
        location=location,
        timestamp_property_name=timestamp_property_name,
        event_source_resource_id=event_source_resource_id,
        service_bus_namespace=parsed_id['name'],
        event_hub_name=parsed_id['child_name_1'],
        consumer_group_name=consumer_group_name,
        key_name=key_name,
        shared_access_key=shared_access_key,
        tags=tags
    )
    return client.create_or_update(resource_group_name=resource_group_name, environment_name=environment_name, event_source_name=event_source_name, parameters=parameters)


def update_timeseriesinsights_event_source_eventhub(cmd, client, resource_group_name, environment_name, event_source_name,
                                                    timestamp_property_name=None,
                                                    local_timestamp_format=None, time_zone_offset_property_name=None,
                                                    shared_access_key=None, tags=None):
    from .vendored_sdks.timeseriesinsights.models import EventHubEventSourceUpdateParameters, LocalTimestamp, \
        LocalTimestampTimeZoneOffset, LocalTimestampFormat
    local_timestamp = None
    if local_timestamp_format == LocalTimestampFormat.embedded:
        local_timestamp = LocalTimestamp(format=local_timestamp_format)
    elif local_timestamp_format and time_zone_offset_property_name:
        local_timestamp = LocalTimestamp(format=local_timestamp_format,
                                         time_zone_offset=LocalTimestampTimeZoneOffset(property_name=time_zone_offset_property_name))
    parameters = EventHubEventSourceUpdateParameters(tags=tags,
                                                     timestamp_property_name=timestamp_property_name,
                                                     local_timestamp=local_timestamp,
                                                     shared_access_key=shared_access_key)

    return client.update(resource_group_name=resource_group_name, environment_name=environment_name, event_source_name=event_source_name,
                         parameters=parameters)


def create_timeseriesinsights_event_source_iothub(cmd, client,
                                                  resource_group_name, environment_name, event_source_name,
                                                  timestamp_property_name, event_source_resource_id,
                                                  consumer_group_name, key_name, shared_access_key,
                                                  location=None, tags=None):
    from .vendored_sdks.timeseriesinsights.models import IoTHubEventSourceCreateOrUpdateParameters
    from msrestazure.tools import parse_resource_id
    parsed_id = parse_resource_id(event_source_resource_id)
    parameters = IoTHubEventSourceCreateOrUpdateParameters(
        location=location,
        tags=tags,
        timestamp_property_name=timestamp_property_name,
        event_source_resource_id=event_source_resource_id,
        iot_hub_name=parsed_id['name'],
        consumer_group_name=consumer_group_name,
        key_name=key_name,
        shared_access_key=shared_access_key)
    return client.create_or_update(
        resource_group_name=resource_group_name, environment_name=environment_name, event_source_name=event_source_name,
        parameters=parameters)


def update_timeseriesinsights_event_source_iothub(cmd, client,
                                                  resource_group_name, environment_name, event_source_name,
                                                  timestamp_property_name=None,
                                                  local_timestamp_format=None, time_zone_offset_property_name=None,
                                                  shared_access_key=None,
                                                  tags=None):
    from .vendored_sdks.timeseriesinsights.models import IoTHubEventSourceUpdateParameters, LocalTimestamp, \
        LocalTimestampTimeZoneOffset, LocalTimestampFormat
    local_timestamp = None
    if local_timestamp_format == LocalTimestampFormat.embedded:
        local_timestamp = LocalTimestamp(format=local_timestamp_format)
    elif local_timestamp_format and time_zone_offset_property_name:
        local_timestamp = LocalTimestamp(format=local_timestamp_format,
                                         time_zone_offset=LocalTimestampTimeZoneOffset(property_name=time_zone_offset_property_name))
    parameters = IoTHubEventSourceUpdateParameters(
        tags=tags,
        timestamp_property_name=timestamp_property_name,
        local_timestamp=local_timestamp,
        shared_access_key=shared_access_key
    )
    return client.update(resource_group_name=resource_group_name, environment_name=environment_name, event_source_name=event_source_name, parameters=parameters)


def create_timeseriesinsights_reference_data_set(cmd, client,
                                                 resource_group_name, environment_name, reference_data_set_name,
                                                 key_properties, data_string_comparison_behavior,
                                                 location=None, tags=None):
    from .vendored_sdks.timeseriesinsights.models import ReferenceDataSetCreateOrUpdateParameters, \
        ReferenceDataSetKeyProperty

    key_properties_list = []
    key_property_count, remaining = divmod(len(key_properties), 2)
    if remaining:
        from knack.util import CLIError
        raise CLIError("Usage error: --key-properties NAME TYPE ...")

    for _ in range(0, key_property_count):
        # eg. --key-properties DeviceId1 String DeviceFloor Double
        key_properties_list.append(ReferenceDataSetKeyProperty(name=key_properties.pop(0), type=key_properties.pop(0)))

    parameters = ReferenceDataSetCreateOrUpdateParameters(
        location=location,
        tags=tags,
        key_properties=key_properties_list,
        data_string_comparison_behavior=data_string_comparison_behavior
    )

    return client.create_or_update(resource_group_name=resource_group_name, environment_name=environment_name, reference_data_set_name=reference_data_set_name, parameters=parameters)


def update_timeseriesinsights_reference_data_set(cmd, client,
                                                 resource_group_name, environment_name, reference_data_set_name,
                                                 tags=None):
    return client.update(resource_group_name=resource_group_name, environment_name=environment_name, reference_data_set_name=reference_data_set_name, tags=tags)


def create_timeseriesinsights_access_policy(cmd, client,
                                            resource_group_name, environment_name, access_policy_name,
                                            principal_object_id=None, description=None, roles=None):
    from .vendored_sdks.timeseriesinsights.models import AccessPolicyCreateOrUpdateParameters
    parameters = AccessPolicyCreateOrUpdateParameters(
        principal_object_id=principal_object_id,
        description=description,
        roles=roles)
    return client.create_or_update(resource_group_name=resource_group_name, environment_name=environment_name, access_policy_name=access_policy_name, parameters=parameters)


def update_timeseriesinsights_access_policy(cmd, client, resource_group_name, environment_name, access_policy_name,
                                            description=None, roles=None):
    return client.update(resource_group_name=resource_group_name, environment_name=environment_name, access_policy_name=access_policy_name, description=description, roles=roles)
