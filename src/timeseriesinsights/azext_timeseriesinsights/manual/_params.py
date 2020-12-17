# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements


from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import (
    get_default_location_from_resource_group,
    validate_file_or_dict
)
from azext_timeseriesinsights.action import (
    AddSku,
    AddPartitionKeyProperties,
    AddTimeSeriesIdProperties,
    AddStorageConfiguration,
    AddWarmStoreConfiguration
)

def load_arguments(self, _):

    with self.argument_context('timeseriesinsights environment list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('timeseriesinsights environment show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the Time Series Insights environment associated with the specified resource group.', id_part=''
                   'name')
        c.argument('expand', type=str, help='Setting $expand=status will include the status of the internal services '
                   'of the environment in the Time Series Insights service.')
    
    with self.argument_context('timeseriesinsights environment delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the Time Series Insights environment associated with the specified resource group.', id_part=''
                   'name')

    with self.argument_context('timeseriesinsights environment wait') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='The name '
                   'of the Time Series Insights environment associated with the specified resource group.', id_part=''
                   'name')
        c.argument('expand', type=str, help='Setting $expand=status will include the status of the internal services '
                   'of the environment in the Time Series Insights service.')

    with self.argument_context('timeseriesinsights environment gen1') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='Name of '
                   'the environment')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku', action=AddSku, nargs='+', help='The sku determines the type of environment, either Gen1 (S1 '
                   'or S2) or Gen2 (L1). For Gen1 environments the sku determines the capacity of the environment, the '
                   'ingress rate, and the billing rate.')
        c.argument('data_retention_time', help='ISO8601 timespan specifying the minimum number of days the '
                   'environment\'s events will be available for query.')
        c.argument('storage_limit_exceeded_behavior', arg_type=get_enum_type(['PurgeOldData', 'PauseIngress']),
                   help='The behavior the Time Series Insights service should take when the environment\'s capacity '
                   'has been exceeded. If "PauseIngress" is specified, new events will not be read from the event '
                   'source. If "PurgeOldData" is specified, new events will continue to be read and old events will be '
                   'deleted from the environment. The default behavior is PurgeOldData.')
        c.argument('partition_key_properties', action=AddPartitionKeyProperties, nargs='+', help='The list of event '
                   'properties which will be used to partition data in the environment. Currently, only a single '
                   'partition key property is supported.')

    with self.argument_context('timeseriesinsights environment gen2') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='Name of '
                   'the environment')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku', action=AddSku, nargs='+', help='The sku determines the type of environment, either Gen1 (S1 '
                   'or S2) or Gen2 (L1). For Gen1 environments the sku determines the capacity of the environment, the '
                   'ingress rate, and the billing rate.')
        c.argument('time_series_id_properties', action=AddTimeSeriesIdProperties, nargs='+', help='The list of event '
                   'properties which will be used to define the environment\'s time series id.')
        c.argument('storage_configuration', action=AddStorageConfiguration, nargs='+', help='The storage configuration '
                   'provides the connection details that allows the Time Series Insights service to connect to the '
                   'customer storage account that is used to store the environment\'s data.')
        c.argument('warm_store_configuration', action=AddWarmStoreConfiguration, nargs='+', help='The warm store '
                   'configuration provides the details to create a warm store cache that will retain a copy of the '
                   'environment\'s data available for faster query.')
    
    with self.argument_context('timeseriesinsights event-source list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', type=str, help='The name of the Time Series Insights environment associated '
                   'with the specified resource group.')

    with self.argument_context('timeseriesinsights event-source show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', type=str, help='The name of the Time Series Insights environment associated '
                   'with the specified resource group.', id_part='name')
        c.argument('event_source_name', options_list=['--name', '-n', '--event-source-name'], type=str, help='The name '
                   'of the Time Series Insights event source associated with the specified environment.', id_part=''
                   'child_name_1')

    with self.argument_context('timeseriesinsights event-source delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', type=str, help='The name of the Time Series Insights environment associated '
                   'with the specified resource group.', id_part='name')
        c.argument('event_source_name', options_list=['--name', '-n', '--event-source-name'], type=str, help='The name '
                   'of the Time Series Insights event source associated with the specified environment.', id_part=''
                   'child_name_1')

    with self.argument_context('timeseriesinsights event-source event-hub') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', type=str, help='The name of the Time Series Insights environment associated '
                   'with the specified resource group.')
        c.argument('event_source_name', options_list=['--name', '-n', '--event-source-name'], type=str, help='Name of '
                   'the event source.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('local_timestamp', type=validate_file_or_dict, help='An object that represents the local timestamp '
                   'property. It contains the format of local timestamp that needs to be used and the corresponding '
                   'timezone offset information. If a value isn\'t specified for localTimestamp, or if null, then the '
                   'local timestamp will not be ingressed with the events. Expected value: json-string/@json-file.')
        c.argument('timestamp_property_name', type=str, help='The event property that will be used as the event '
                   'source\'s timestamp. If a value isn\'t specified for timestampPropertyName, or if null or '
                   'empty-string is specified, the event creation time will be used.')
        c.argument('event_source_resource_id', type=str, help='The resource id of the event source in Azure Resource '
                   'Manager.')
        c.argument('service_bus_namespace', type=str, help='The name of the service bus that contains the event hub.')
        c.argument('event_hub_name', type=str, help='The name of the event hub.')
        c.argument('consumer_group_name', type=str, help='The name of the event hub\'s consumer group that holds the '
                   'partitions from which events will be read.')
        c.argument('key_name', type=str, help='The name of the SAS key that grants the Time Series Insights service '
                   'access to the event hub. The shared access policies for this key must grant \'Listen\' permissions '
                   'to the event hub.')
        c.argument('shared_access_key', type=str, help='The value of the shared access key that grants the Time Series '
                   'Insights service read access to the event hub. This property is not shown in event source '
                   'responses.')

    with self.argument_context('timeseriesinsights event-source iot-hub') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', type=str, help='The name of the Time Series Insights environment associated '
                   'with the specified resource group.')
        c.argument('event_source_name', options_list=['--name', '-n', '--event-source-name'], type=str, help='Name of '
                   'the event source.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=False,
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('local_timestamp', type=validate_file_or_dict, help='An object that represents the local timestamp '
                   'property. It contains the format of local timestamp that needs to be used and the corresponding '
                   'timezone offset information. If a value isn\'t specified for localTimestamp, or if null, then the '
                   'local timestamp will not be ingressed with the events. Expected value: json-string/@json-file.')
        c.argument('timestamp_property_name', type=str, help='The event property that will be used as the event '
                   'source\'s timestamp. If a value isn\'t specified for timestampPropertyName, or if null or '
                   'empty-string is specified, the event creation time will be used.')
        c.argument('event_source_resource_id', type=str, help='The resource id of the event source in Azure Resource '
                   'Manager.')
        c.argument('iot_hub_name', type=str, help='The name of the iot hub.')
        c.argument('consumer_group_name', type=str, help='The name of the iot hub\'s consumer group that holds the '
                   'partitions from which events will be read.')
        c.argument('key_name', type=str, help='The name of the Shared Access Policy key that grants the Time Series '
                   'Insights service access to the iot hub. This shared access policy key must grant \'service '
                   'connect\' permissions to the iot hub.')
        c.argument('shared_access_key', type=str, help='The value of the Shared Access Policy key that grants the Time '
                   'Series Insights service read access to the iot hub. This property is not shown in event source '
                   'responses.')

