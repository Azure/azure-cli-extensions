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
    AddWarmStoreConfiguration,
    AddKeyProperties
)


def load_arguments(self, _):
    with self.argument_context('tsi environment gen1') as c:
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='Name of the'
                   ' environment', id_part='name')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku', action=AddSku, nargs='+', help='The sku determines the type of environment, either Gen1 (S1 '
                   'or S2) or Gen2 (L1). For Gen1 environments the sku determines the capacity of the environment, the '
                   'ingress rate, and the billing rate.')
        c.argument('data_retention_time', help='ISO8601 timespan specifying the minimum number of days the '
                   'environment\'s events will be available for query.')
        c.argument('storage_limit_exceeded_behavior',
                   options_list=['--exceeded-behavior', '--storage-limit-exceeded-behavior'],
                   arg_type=get_enum_type(['PurgeOldData', 'PauseIngress']),
                   help='The behavior the Time Series Insights service should take when the environment\'s capacity '
                   'has been exceeded. If "PauseIngress" is specified, new events will not be read from the event '
                   'source. If "PurgeOldData" is specified, new events will continue to be read and old events will be '
                   'deleted from the environment. The default behavior is PurgeOldData.')
        c.argument('partition_key_properties',
                   options_list=['--key-properties', '--partition-key-properties'],
                   action=AddPartitionKeyProperties, nargs='+', help='The list of event '
                   'properties which will be used to partition data in the environment. Currently, only a single '
                   'partition key property is supported.')

    with self.argument_context('tsi environment gen1 create') as c:
        c.argument('environment_name', id_part=None)

    with self.argument_context('tsi environment gen2') as c:
        c.argument('environment_name', options_list=['--name', '-n', '--environment-name'], type=str, help='Name of the'
                   ' environment', id_part='name')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku', action=AddSku, nargs='+', help='The sku determines the type of environment, either Gen1 (S1 '
                   'or S2) or Gen2 (L1). For Gen1 environments the sku determines the capacity of the environment, the '
                   'ingress rate, and the billing rate.')
        c.argument('time_series_id_properties', options_list=['--id-properties', '--time-series-id-properties'],
                   action=AddTimeSeriesIdProperties, nargs='+', help='The list of event properties which will be used'
                   ' to define the environment\'s time series id.')
        c.argument('storage_configuration', options_list=['--storage-config', '--storage-configuration'],
                   action=AddStorageConfiguration, nargs='+', help='The storage configuration '
                   'provides the connection details that allows the Time Series Insights service to connect to the '
                   'customer storage account that is used to store the environment\'s data.')
        c.argument('warm_store_configuration', options_list=['--warm-store-config', '--warm-store-configuration'],
                   action=AddWarmStoreConfiguration, nargs='+', help='The warm store '
                   'configuration provides the details to create a warm store cache that will retain a copy of the '
                   'environment\'s data available for faster query.')

    with self.argument_context('tsi environment gen2 create') as c:
        c.argument('environment_name', id_part=None)

    with self.argument_context('tsi event-source') as c:
        c.argument('resource_group_name', resource_group_name_type,
                   help="Name of resource group of environment. "
                        "You can configure the default group using `az configure --defaults group=<name>`",)
        c.argument('environment_name', type=str, help='The name of the Time Series '
                   'Insights environment associated with the specified resource group.', id_part='name')
        c.argument('event_source_name', options_list=['--name', '-n', '--event-source-name'], type=str, help='The name '
                   'of the Time Series Insights event source associated with the specified environment.',
                   id_part='child_name_1')

    with self.argument_context('tsi event-source list') as c:
        c.argument('environment_name', id_part=None)

    with self.argument_context('tsi event-source eventhub') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('local_timestamp', type=validate_file_or_dict, help='An object that represents the local timestamp '
                   'property. It contains the format of local timestamp that needs to be used and the corresponding '
                   'timezone offset information. If a value isn\'t specified for localTimestamp, or if null, then the '
                   'local timestamp will not be ingressed with the events. Expected value: json-string/@json-file.')
        c.argument('timestamp_property_name', options_list=['--ts-property-name', '--timestamp-property-name'],
                   type=str, help='The event property that will be used as the event '
                   'source\'s timestamp. If a value isn\'t specified for timestampPropertyName, or if null or '
                   'empty-string is specified, the event creation time will be used.')
        c.argument('event_source_resource_id', options_list=['--resource-id', '--event-source-resource-id'], type=str,
                   help='The resource id of the event source in Azure Resource Manager.')
        c.argument('service_bus_namespace', options_list=['--namespace', '--service-bus-namespace'], type=str,
                   help='The name of the service bus that contains the event hub.')
        c.argument('event_hub_name', type=str, help='The name of the event hub.')
        c.argument('consumer_group_name', type=str, help='The name of the event hub\'s consumer group that holds the '
                   'partitions from which events will be read.')
        c.argument('key_name', options_list=['--key-name', '--shared-access-policy-name'], type=str,
                   help='The name of the SAS key that grants the Time Series Insights service '
                   'access to the event hub. The shared access policies for this key must grant \'Listen\' permissions '
                   'to the event hub.')
        c.argument('shared_access_key', type=str, help='The value of the shared access key that grants the Time Series '
                   'Insights service read access to the event hub. This property is not shown in event source '
                   'responses.')

    with self.argument_context('tsi event-source eventhub create') as c:
        c.argument('environment_name', id_part=None)
        c.argument('event_source_name', id_part=None)

    with self.argument_context('tsi event-source iothub') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('local_timestamp', type=validate_file_or_dict, help='An object that represents the local timestamp '
                   'property. It contains the format of local timestamp that needs to be used and the corresponding '
                   'timezone offset information. If a value isn\'t specified for localTimestamp, or if null, then the '
                   'local timestamp will not be ingressed with the events. Expected value: json-string/@json-file.')
        c.argument('timestamp_property_name', options_list=['--ts-property-name', '--timestamp-property-name'],
                   type=str, help='The event property that will be used as the event '
                   'source\'s timestamp. If a value isn\'t specified for timestampPropertyName, or if null or '
                   'empty-string is specified, the event creation time will be used.')
        c.argument('event_source_resource_id', options_list=['--resource-id', '--event-source-resource-id'],
                   type=str, help='The resource id of the event source in Azure Resource '
                   'Manager.')
        c.argument('iot_hub_name', type=str, help='The name of the iot hub.')
        c.argument('consumer_group_name', type=str, help='The name of the iot hub\'s consumer group that holds the '
                   'partitions from which events will be read.')
        c.argument('key_name', options_list=['--key-name', '--shared-access-policy-name'], type=str,
                   help='The name of the Shared Access Policy key that grants the Time Series '
                   'Insights service access to the iot hub. This shared access policy key must grant \'service '
                   'connect\' permissions to the iot hub.')
        c.argument('shared_access_key', type=str, help='The value of the Shared Access Policy key that grants the Time '
                   'Series Insights service read access to the iot hub. This property is not shown in event source '
                   'responses.')

    with self.argument_context('tsi event-source iothub create') as c:
        c.argument('environment_name', id_part=None)
        c.argument('event_source_name', id_part=None)

    with self.argument_context('tsi reference-data-set') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('environment_name', type=str, help='The name of the Time Series Insights environment associated '
                   'with the specified resource group.', id_part='name')
        c.argument('reference_data_set_name', options_list=['--name', '-n', '--reference-data-set-name'], type=str,
                   help='The name of the Time Series Insights reference data set associated with the specified '
                   'environment.', id_part='child_name_1')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('key_properties', action=AddKeyProperties, nargs='+', help='The list of key properties for the '
                   'reference data set.')
        c.argument('data_string_comparison_behavior',
                   options_list=['--comparison-behavior', '--data-string-comparison-behavior'],
                   arg_type=get_enum_type(['Ordinal', 'OrdinalIgnoreCase']), help='The reference data set key '
                   'comparison behavior can be set using this property. By default, the '
                   'value is \'Ordinal\' - which means case sensitive key comparison will be performed while joining '
                   'reference data with events or while adding new reference data. When \'OrdinalIgnoreCase\' is set, '
                   'case insensitive comparison will be used.')

    with self.argument_context('tsi reference-data-set list') as c:
        c.argument('environment_name', id_part=None)
