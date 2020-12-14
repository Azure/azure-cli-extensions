# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az timeseriesinsights|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az timeseriesinsights` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az timeseriesinsights environment|Environments|[commands](#CommandsInEnvironments)|
|az timeseriesinsights event-source|EventSources|[commands](#CommandsInEventSources)|
|az timeseriesinsights reference-data-set|ReferenceDataSets|[commands](#CommandsInReferenceDataSets)|
|az timeseriesinsights access-policy|AccessPolicies|[commands](#CommandsInAccessPolicies)|

## COMMANDS
### <a name="CommandsInAccessPolicies">Commands in `az timeseriesinsights access-policy` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az timeseriesinsights access-policy list](#AccessPoliciesListByEnvironment)|ListByEnvironment|[Parameters](#ParametersAccessPoliciesListByEnvironment)|[Example](#ExamplesAccessPoliciesListByEnvironment)|
|[az timeseriesinsights access-policy show](#AccessPoliciesGet)|Get|[Parameters](#ParametersAccessPoliciesGet)|[Example](#ExamplesAccessPoliciesGet)|
|[az timeseriesinsights access-policy create](#AccessPoliciesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAccessPoliciesCreateOrUpdate#Create)|[Example](#ExamplesAccessPoliciesCreateOrUpdate#Create)|
|[az timeseriesinsights access-policy update](#AccessPoliciesUpdate)|Update|[Parameters](#ParametersAccessPoliciesUpdate)|[Example](#ExamplesAccessPoliciesUpdate)|
|[az timeseriesinsights access-policy delete](#AccessPoliciesDelete)|Delete|[Parameters](#ParametersAccessPoliciesDelete)|[Example](#ExamplesAccessPoliciesDelete)|

### <a name="CommandsInEnvironments">Commands in `az timeseriesinsights environment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az timeseriesinsights environment list](#EnvironmentsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersEnvironmentsListByResourceGroup)|[Example](#ExamplesEnvironmentsListByResourceGroup)|
|[az timeseriesinsights environment list](#EnvironmentsListBySubscription)|ListBySubscription|[Parameters](#ParametersEnvironmentsListBySubscription)|[Example](#ExamplesEnvironmentsListBySubscription)|
|[az timeseriesinsights environment show](#EnvironmentsGet)|Get|[Parameters](#ParametersEnvironmentsGet)|[Example](#ExamplesEnvironmentsGet)|
|[az timeseriesinsights environment gen1 create](#EnvironmentsCreateOrUpdate#Create#Gen1)|CreateOrUpdate#Create#Gen1|[Parameters](#ParametersEnvironmentsCreateOrUpdate#Create#Gen1)|[Example](#ExamplesEnvironmentsCreateOrUpdate#Create#Gen1)|
|[az timeseriesinsights environment gen2 create](#EnvironmentsCreateOrUpdate#Create#Gen2)|CreateOrUpdate#Create#Gen2|[Parameters](#ParametersEnvironmentsCreateOrUpdate#Create#Gen2)|Not Found|
|[az timeseriesinsights environment update](#EnvironmentsUpdate)|Update|[Parameters](#ParametersEnvironmentsUpdate)|[Example](#ExamplesEnvironmentsUpdate)|
|[az timeseriesinsights environment delete](#EnvironmentsDelete)|Delete|[Parameters](#ParametersEnvironmentsDelete)|[Example](#ExamplesEnvironmentsDelete)|

### <a name="CommandsInEventSources">Commands in `az timeseriesinsights event-source` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az timeseriesinsights event-source list](#EventSourcesListByEnvironment)|ListByEnvironment|[Parameters](#ParametersEventSourcesListByEnvironment)|[Example](#ExamplesEventSourcesListByEnvironment)|
|[az timeseriesinsights event-source show](#EventSourcesGet)|Get|[Parameters](#ParametersEventSourcesGet)|[Example](#ExamplesEventSourcesGet)|
|[az timeseriesinsights event-source microsoft.-event-hub create](#EventSourcesCreateOrUpdate#Create#Microsoft.EventHub)|CreateOrUpdate#Create#Microsoft.EventHub|[Parameters](#ParametersEventSourcesCreateOrUpdate#Create#Microsoft.EventHub)|[Example](#ExamplesEventSourcesCreateOrUpdate#Create#Microsoft.EventHub)|
|[az timeseriesinsights event-source microsoft.-io-t-hub create](#EventSourcesCreateOrUpdate#Create#Microsoft.IoTHub)|CreateOrUpdate#Create#Microsoft.IoTHub|[Parameters](#ParametersEventSourcesCreateOrUpdate#Create#Microsoft.IoTHub)|Not Found|
|[az timeseriesinsights event-source update](#EventSourcesUpdate)|Update|[Parameters](#ParametersEventSourcesUpdate)|[Example](#ExamplesEventSourcesUpdate)|
|[az timeseriesinsights event-source delete](#EventSourcesDelete)|Delete|[Parameters](#ParametersEventSourcesDelete)|[Example](#ExamplesEventSourcesDelete)|

### <a name="CommandsInReferenceDataSets">Commands in `az timeseriesinsights reference-data-set` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az timeseriesinsights reference-data-set list](#ReferenceDataSetsListByEnvironment)|ListByEnvironment|[Parameters](#ParametersReferenceDataSetsListByEnvironment)|[Example](#ExamplesReferenceDataSetsListByEnvironment)|
|[az timeseriesinsights reference-data-set show](#ReferenceDataSetsGet)|Get|[Parameters](#ParametersReferenceDataSetsGet)|[Example](#ExamplesReferenceDataSetsGet)|
|[az timeseriesinsights reference-data-set create](#ReferenceDataSetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersReferenceDataSetsCreateOrUpdate#Create)|[Example](#ExamplesReferenceDataSetsCreateOrUpdate#Create)|
|[az timeseriesinsights reference-data-set update](#ReferenceDataSetsUpdate)|Update|[Parameters](#ParametersReferenceDataSetsUpdate)|[Example](#ExamplesReferenceDataSetsUpdate)|
|[az timeseriesinsights reference-data-set delete](#ReferenceDataSetsDelete)|Delete|[Parameters](#ParametersReferenceDataSetsDelete)|[Example](#ExamplesReferenceDataSetsDelete)|


## COMMAND DETAILS

### group `az timeseriesinsights access-policy`
#### <a name="AccessPoliciesListByEnvironment">Command `az timeseriesinsights access-policy list`</a>

##### <a name="ExamplesAccessPoliciesListByEnvironment">Example</a>
```
az timeseriesinsights access-policy list --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|

#### <a name="AccessPoliciesGet">Command `az timeseriesinsights access-policy show`</a>

##### <a name="ExamplesAccessPoliciesGet">Example</a>
```
az timeseriesinsights access-policy show --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|The name of the Time Series Insights access policy associated with the specified environment.|access_policy_name|accessPolicyName|

#### <a name="AccessPoliciesCreateOrUpdate#Create">Command `az timeseriesinsights access-policy create`</a>

##### <a name="ExamplesAccessPoliciesCreateOrUpdate#Create">Example</a>
```
az timeseriesinsights access-policy create --name "ap1" --environment-name "env1" --description "some description" \
--principal-object-id "aGuid" --roles "Reader" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|Name of the access policy.|access_policy_name|accessPolicyName|
|**--principal-object-id**|string|The objectId of the principal in Azure Active Directory.|principal_object_id|principalObjectId|
|**--description**|string|An description of the access policy.|description|description|
|**--roles**|array|The list of roles the principal is assigned on the environment.|roles|roles|

#### <a name="AccessPoliciesUpdate">Command `az timeseriesinsights access-policy update`</a>

##### <a name="ExamplesAccessPoliciesUpdate">Example</a>
```
az timeseriesinsights access-policy update --name "ap1" --roles "Reader" --roles "Contributor" --environment-name \
"env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|The name of the Time Series Insights access policy associated with the specified environment.|access_policy_name|accessPolicyName|
|**--description**|string|An description of the access policy.|description|description|
|**--roles**|array|The list of roles the principal is assigned on the environment.|roles|roles|

#### <a name="AccessPoliciesDelete">Command `az timeseriesinsights access-policy delete`</a>

##### <a name="ExamplesAccessPoliciesDelete">Example</a>
```
az timeseriesinsights access-policy delete --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|The name of the Time Series Insights access policy associated with the specified environment.|access_policy_name|accessPolicyName|

### group `az timeseriesinsights environment`
#### <a name="EnvironmentsListByResourceGroup">Command `az timeseriesinsights environment list`</a>

##### <a name="ExamplesEnvironmentsListByResourceGroup">Example</a>
```
az timeseriesinsights environment list --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|

#### <a name="EnvironmentsListBySubscription">Command `az timeseriesinsights environment list`</a>

##### <a name="ExamplesEnvironmentsListBySubscription">Example</a>
```
az timeseriesinsights environment list
```
##### <a name="ParametersEnvironmentsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="EnvironmentsGet">Command `az timeseriesinsights environment show`</a>

##### <a name="ExamplesEnvironmentsGet">Example</a>
```
az timeseriesinsights environment show --name "env1" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--expand**|string|Setting $expand=status will include the status of the internal services of the environment in the Time Series Insights service.|expand|$expand|

#### <a name="EnvironmentsCreateOrUpdate#Create#Gen1">Command `az timeseriesinsights environment gen1 create`</a>

##### <a name="ExamplesEnvironmentsCreateOrUpdate#Create#Gen1">Example</a>
```
az timeseriesinsights environment gen1 create --name "env1" --location "West US" --data-retention-time "P31D" \
--partition-key-properties name="DeviceId1" type="String" --sku name="S1" capacity=1 --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsCreateOrUpdate#Create#Gen1">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|Name of the environment|environment_name|environmentName|
|**--location**|string|The location of the resource.|gen1_location|location|
|**--sku**|object|The sku determines the type of environment, either Gen1 (S1 or S2) or Gen2 (L1). For Gen1 environments the sku determines the capacity of the environment, the ingress rate, and the billing rate.|gen1_sku|sku|
|**--data-retention-time**|duration|ISO8601 timespan specifying the minimum number of days the environment's events will be available for query.|gen1_data_retention_time|dataRetentionTime|
|**--tags**|dictionary|Key-value pairs of additional properties for the resource.|gen1_tags|tags|
|**--storage-limit-exceeded-behavior**|choice|The behavior the Time Series Insights service should take when the environment's capacity has been exceeded. If "PauseIngress" is specified, new events will not be read from the event source. If "PurgeOldData" is specified, new events will continue to be read and old events will be deleted from the environment. The default behavior is PurgeOldData.|gen1_storage_limit_exceeded_behavior|storageLimitExceededBehavior|
|**--partition-key-properties**|array|The list of event properties which will be used to partition data in the environment. Currently, only a single partition key property is supported.|gen1_partition_key_properties|partitionKeyProperties|

#### <a name="EnvironmentsCreateOrUpdate#Create#Gen2">Command `az timeseriesinsights environment gen2 create`</a>

##### <a name="ParametersEnvironmentsCreateOrUpdate#Create#Gen2">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|Name of the environment|environment_name|environmentName|
|**--location**|string|The location of the resource.|gen2_location|location|
|**--sku**|object|The sku determines the type of environment, either Gen1 (S1 or S2) or Gen2 (L1). For Gen1 environments the sku determines the capacity of the environment, the ingress rate, and the billing rate.|gen2_sku|sku|
|**--time-series-id-properties**|array|The list of event properties which will be used to define the environment's time series id.|gen2_time_series_id_properties|timeSeriesIdProperties|
|**--storage-configuration**|object|The storage configuration provides the connection details that allows the Time Series Insights service to connect to the customer storage account that is used to store the environment's data.|gen2_storage_configuration|storageConfiguration|
|**--tags**|dictionary|Key-value pairs of additional properties for the resource.|gen2_tags|tags|
|**--warm-store-configuration**|object|The warm store configuration provides the details to create a warm store cache that will retain a copy of the environment's data available for faster query.|gen2_warm_store_configuration|warmStoreConfiguration|

#### <a name="EnvironmentsUpdate">Command `az timeseriesinsights environment update`</a>

##### <a name="ExamplesEnvironmentsUpdate">Example</a>
```
az timeseriesinsights environment update --name "env1" --tags someTag="someTagValue" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--tags**|dictionary|Key-value pairs of additional properties for the environment.|tags|tags|

#### <a name="EnvironmentsDelete">Command `az timeseriesinsights environment delete`</a>

##### <a name="ExamplesEnvironmentsDelete">Example</a>
```
az timeseriesinsights environment delete --name "env1" --resource-group "rg1"
```
##### <a name="ParametersEnvironmentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|

### group `az timeseriesinsights event-source`
#### <a name="EventSourcesListByEnvironment">Command `az timeseriesinsights event-source list`</a>

##### <a name="ExamplesEventSourcesListByEnvironment">Example</a>
```
az timeseriesinsights event-source list --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersEventSourcesListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|

#### <a name="EventSourcesGet">Command `az timeseriesinsights event-source show`</a>

##### <a name="ExamplesEventSourcesGet">Example</a>
```
az timeseriesinsights event-source show --environment-name "env1" --name "es1" --resource-group "rg1"
```
##### <a name="ParametersEventSourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--event-source-name**|string|The name of the Time Series Insights event source associated with the specified environment.|event_source_name|eventSourceName|

#### <a name="EventSourcesCreateOrUpdate#Create#Microsoft.EventHub">Command `az timeseriesinsights event-source microsoft.-event-hub create`</a>

##### <a name="ExamplesEventSourcesCreateOrUpdate#Create#Microsoft.EventHub">Example</a>
```
az timeseriesinsights event-source microsoft.-event-hub create --environment-name "env1" --name "es1" --location "West \
US" --consumer-group-name "cgn" --event-hub-name "ehn" --event-source-resource-id "somePathInArm" --key-name \
"managementKey" --service-bus-namespace "sbn" --shared-access-key "someSecretvalue" --timestamp-property-name \
"someTimestampProperty" --resource-group "rg1"
```
##### <a name="ParametersEventSourcesCreateOrUpdate#Create#Microsoft.EventHub">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--event-source-name**|string|Name of the event source.|event_source_name|eventSourceName|
|**--location**|string|The location of the resource.|microsoft._event_hub_location|location|
|**--event-source-resource-id**|string|The resource id of the event source in Azure Resource Manager.|microsoft._event_hub_event_source_resource_id|eventSourceResourceId|
|**--service-bus-namespace**|string|The name of the service bus that contains the event hub.|microsoft._event_hub_service_bus_namespace|serviceBusNamespace|
|**--event-hub-name**|string|The name of the event hub.|microsoft._event_hub_event_hub_name|eventHubName|
|**--consumer-group-name**|string|The name of the event hub's consumer group that holds the partitions from which events will be read.|microsoft._event_hub_consumer_group_name|consumerGroupName|
|**--key-name**|string|The name of the SAS key that grants the Time Series Insights service access to the event hub. The shared access policies for this key must grant 'Listen' permissions to the event hub.|microsoft._event_hub_key_name|keyName|
|**--shared-access-key**|string|The value of the shared access key that grants the Time Series Insights service read access to the event hub. This property is not shown in event source responses.|microsoft._event_hub_shared_access_key|sharedAccessKey|
|**--tags**|dictionary|Key-value pairs of additional properties for the resource.|microsoft._event_hub_tags|tags|
|**--local-timestamp**|object|An object that represents the local timestamp property. It contains the format of local timestamp that needs to be used and the corresponding timezone offset information. If a value isn't specified for localTimestamp, or if null, then the local timestamp will not be ingressed with the events.|microsoft._event_hub_local_timestamp|localTimestamp|
|**--timestamp-property-name**|string|The event property that will be used as the event source's timestamp. If a value isn't specified for timestampPropertyName, or if null or empty-string is specified, the event creation time will be used.|microsoft._event_hub_timestamp_property_name|timestampPropertyName|

#### <a name="EventSourcesCreateOrUpdate#Create#Microsoft.IoTHub">Command `az timeseriesinsights event-source microsoft.-io-t-hub create`</a>

##### <a name="ParametersEventSourcesCreateOrUpdate#Create#Microsoft.IoTHub">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--event-source-name**|string|Name of the event source.|event_source_name|eventSourceName|
|**--location**|string|The location of the resource.|microsoft._io_t_hub_location|location|
|**--event-source-resource-id**|string|The resource id of the event source in Azure Resource Manager.|microsoft._io_t_hub_event_source_resource_id|eventSourceResourceId|
|**--iot-hub-name**|string|The name of the iot hub.|microsoft._io_t_hub_iot_hub_name|iotHubName|
|**--consumer-group-name**|string|The name of the iot hub's consumer group that holds the partitions from which events will be read.|microsoft._io_t_hub_consumer_group_name|consumerGroupName|
|**--key-name**|string|The name of the Shared Access Policy key that grants the Time Series Insights service access to the iot hub. This shared access policy key must grant 'service connect' permissions to the iot hub.|microsoft._io_t_hub_key_name|keyName|
|**--shared-access-key**|string|The value of the Shared Access Policy key that grants the Time Series Insights service read access to the iot hub. This property is not shown in event source responses.|microsoft._io_t_hub_shared_access_key|sharedAccessKey|
|**--tags**|dictionary|Key-value pairs of additional properties for the resource.|microsoft._io_t_hub_tags|tags|
|**--local-timestamp**|object|An object that represents the local timestamp property. It contains the format of local timestamp that needs to be used and the corresponding timezone offset information. If a value isn't specified for localTimestamp, or if null, then the local timestamp will not be ingressed with the events.|microsoft._io_t_hub_local_timestamp|localTimestamp|
|**--timestamp-property-name**|string|The event property that will be used as the event source's timestamp. If a value isn't specified for timestampPropertyName, or if null or empty-string is specified, the event creation time will be used.|microsoft._io_t_hub_timestamp_property_name|timestampPropertyName|

#### <a name="EventSourcesUpdate">Command `az timeseriesinsights event-source update`</a>

##### <a name="ExamplesEventSourcesUpdate">Example</a>
```
az timeseriesinsights event-source update --environment-name "env1" --name "es1" --tags someKey="someValue" \
--resource-group "rg1"
```
##### <a name="ParametersEventSourcesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--event-source-name**|string|The name of the Time Series Insights event source associated with the specified environment.|event_source_name|eventSourceName|
|**--tags**|dictionary|Key-value pairs of additional properties for the event source.|tags|tags|

#### <a name="EventSourcesDelete">Command `az timeseriesinsights event-source delete`</a>

##### <a name="ExamplesEventSourcesDelete">Example</a>
```
az timeseriesinsights event-source delete --environment-name "env1" --name "es1" --resource-group "rg1"
```
##### <a name="ParametersEventSourcesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--event-source-name**|string|The name of the Time Series Insights event source associated with the specified environment.|event_source_name|eventSourceName|

### group `az timeseriesinsights reference-data-set`
#### <a name="ReferenceDataSetsListByEnvironment">Command `az timeseriesinsights reference-data-set list`</a>

##### <a name="ExamplesReferenceDataSetsListByEnvironment">Example</a>
```
az timeseriesinsights reference-data-set list --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|

#### <a name="ReferenceDataSetsGet">Command `az timeseriesinsights reference-data-set show`</a>

##### <a name="ExamplesReferenceDataSetsGet">Example</a>
```
az timeseriesinsights reference-data-set show --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|The name of the Time Series Insights reference data set associated with the specified environment.|reference_data_set_name|referenceDataSetName|

#### <a name="ReferenceDataSetsCreateOrUpdate#Create">Command `az timeseriesinsights reference-data-set create`</a>

##### <a name="ExamplesReferenceDataSetsCreateOrUpdate#Create">Example</a>
```
az timeseriesinsights reference-data-set create --environment-name "env1" --location "West US" --key-properties \
name="DeviceId1" type="String" --key-properties name="DeviceFloor" type="Double" --name "rds1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|Name of the reference data set.|reference_data_set_name|referenceDataSetName|
|**--location**|string|The location of the resource.|location|location|
|**--key-properties**|array|The list of key properties for the reference data set.|key_properties|keyProperties|
|**--tags**|dictionary|Key-value pairs of additional properties for the resource.|tags|tags|
|**--data-string-comparison-behavior**|choice|The reference data set key comparison behavior can be set using this property. By default, the value is 'Ordinal' - which means case sensitive key comparison will be performed while joining reference data with events or while adding new reference data. When 'OrdinalIgnoreCase' is set, case insensitive comparison will be used.|data_string_comparison_behavior|dataStringComparisonBehavior|

#### <a name="ReferenceDataSetsUpdate">Command `az timeseriesinsights reference-data-set update`</a>

##### <a name="ExamplesReferenceDataSetsUpdate">Example</a>
```
az timeseriesinsights reference-data-set update --environment-name "env1" --name "rds1" --tags someKey="someValue" \
--resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|The name of the Time Series Insights reference data set associated with the specified environment.|reference_data_set_name|referenceDataSetName|
|**--tags**|dictionary|Key-value pairs of additional properties for the reference data set.|tags|tags|

#### <a name="ReferenceDataSetsDelete">Command `az timeseriesinsights reference-data-set delete`</a>

##### <a name="ExamplesReferenceDataSetsDelete">Example</a>
```
az timeseriesinsights reference-data-set delete --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|The name of the Time Series Insights reference data set associated with the specified environment.|reference_data_set_name|referenceDataSetName|
