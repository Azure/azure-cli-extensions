# Azure CLI Module Creation Report

### footprint experiment create

create a footprint experiment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint experiment|experiments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--experiment-name**|string|Name of the Footprint experiment resource.|experiment_name|experimentName|
|**--description**|string|The description of a Footprint experiment.|description|description|

### footprint experiment delete

delete a footprint experiment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint experiment|experiments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--experiment-name**|string|Name of the Footprint experiment resource.|experiment_name|experimentName|

### footprint experiment list

list a footprint experiment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint experiment|experiments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByProfile|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|

### footprint experiment show

show a footprint experiment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint experiment|experiments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--experiment-name**|string|Name of the Footprint experiment resource.|experiment_name|experimentName|

### footprint experiment update

update a footprint experiment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint experiment|experiments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--experiment-name**|string|Name of the Footprint experiment resource.|experiment_name|experimentName|
|**--description**|string|The description of a Footprint experiment.|description|description|

### footprint measurement-endpoint create

create a footprint measurement-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint|measurementEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|
|**--endpoint**|string|The value of a measurement endpoint.|endpoint|endpoint|
|**--measurement-type**|integer|The type of a measurement endpoint.|measurement_type|measurementType|
|**--weight**|integer|The weight of a measurement endpoint, higher weight means higher priority.|weight|weight|
|**--description**|string|The description of a measurement endpoint.|description|description|
|**--experiment-id**|string|The id of an experiment that a measurement endpoint is part of.|experiment_id|experimentId|
|**--object-path**|string|The path of the object that a measurement endpoint points to.|object_path|objectPath|
|**--start-time-utc**|date-time|The start time that a measurement endpoint should be served.|start_time_utc|startTimeUTC|
|**--end-time-utc**|date-time|The end time that a measurement endpoint should be served.|end_time_utc|endTimeUTC|
|**--hot-path-sampling-percentage-rate**|number|The percentual sampling rate for the hot path logging of a measurement endpoint.|hot_path_sampling_percentage_rate|hotPathSamplingPercentageRate|
|**--warm-path-sampling-percentage-rate**|number|The percentual sampling rate for the warm path logging of a measurement endpoint.|warm_path_sampling_percentage_rate|warmPathSamplingPercentageRate|
|**--cold-path-sampling-percentage-rate-override**|number|The percentual sampling rate for the cold path logging of a measurement endpoint.|cold_path_sampling_percentage_rate_override|coldPathSamplingPercentageRateOverride|
|**--metadata**|string|The metadata of a measurement endpoint.|metadata|metadata|

### footprint measurement-endpoint delete

delete a footprint measurement-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint|measurementEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|

### footprint measurement-endpoint list

list a footprint measurement-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint|measurementEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByProfile|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|

### footprint measurement-endpoint show

show a footprint measurement-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint|measurementEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|

### footprint measurement-endpoint update

update a footprint measurement-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint|measurementEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|
|**--endpoint**|string|The value of a measurement endpoint.|endpoint|endpoint|
|**--measurement-type**|integer|The type of a measurement endpoint.|measurement_type|measurementType|
|**--weight**|integer|The weight of a measurement endpoint, higher weight means higher priority.|weight|weight|
|**--description**|string|The description of a measurement endpoint.|description|description|
|**--experiment-id**|string|The id of an experiment that a measurement endpoint is part of.|experiment_id|experimentId|
|**--object-path**|string|The path of the object that a measurement endpoint points to.|object_path|objectPath|
|**--start-time-utc**|date-time|The start time that a measurement endpoint should be served.|start_time_utc|startTimeUTC|
|**--end-time-utc**|date-time|The end time that a measurement endpoint should be served.|end_time_utc|endTimeUTC|
|**--hot-path-sampling-percentage-rate**|number|The percentual sampling rate for the hot path logging of a measurement endpoint.|hot_path_sampling_percentage_rate|hotPathSamplingPercentageRate|
|**--warm-path-sampling-percentage-rate**|number|The percentual sampling rate for the warm path logging of a measurement endpoint.|warm_path_sampling_percentage_rate|warmPathSamplingPercentageRate|
|**--cold-path-sampling-percentage-rate-override**|number|The percentual sampling rate for the cold path logging of a measurement endpoint.|cold_path_sampling_percentage_rate_override|coldPathSamplingPercentageRateOverride|
|**--metadata**|string|The metadata of a measurement endpoint.|metadata|metadata|

### footprint measurement-endpoint-condition create

create a footprint measurement-endpoint-condition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint-condition|measurementEndpointConditions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|
|**--condition-name**|string|Name of the Footprint measurement endpoint condition resource.|condition_name|conditionName|
|**--variable**|string|The variable of a Footprint measurement endpoint condition.|variable|variable|
|**--operator**|choice|The operator of a Footprint measurement endpoint condition.|operator|operator|
|**--constant**|string|The constant of a Footprint measurement endpoint condition.|constant|constant|

### footprint measurement-endpoint-condition delete

delete a footprint measurement-endpoint-condition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint-condition|measurementEndpointConditions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|
|**--condition-name**|string|Name of the Footprint measurement endpoint condition resource.|condition_name|conditionName|

### footprint measurement-endpoint-condition list

list a footprint measurement-endpoint-condition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint-condition|measurementEndpointConditions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByMeasurementEndpoint|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|

### footprint measurement-endpoint-condition show

show a footprint measurement-endpoint-condition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint-condition|measurementEndpointConditions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|
|**--condition-name**|string|Name of the Footprint measurement endpoint condition resource.|condition_name|conditionName|

### footprint measurement-endpoint-condition update

update a footprint measurement-endpoint-condition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint measurement-endpoint-condition|measurementEndpointConditions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--measurement-endpoint-name**|string|Name of the Footprint measurement endpoint resource.|measurement_endpoint_name|measurementEndpointName|
|**--condition-name**|string|Name of the Footprint measurement endpoint condition resource.|condition_name|conditionName|
|**--variable**|string|The variable of a Footprint measurement endpoint condition.|variable|variable|
|**--operator**|choice|The operator of a Footprint measurement endpoint condition.|operator|operator|
|**--constant**|string|The constant of a Footprint measurement endpoint condition.|constant|constant|

### footprint profile create

create a footprint profile.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint profile|profiles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--start-delay-milliseconds**|integer|The delay in milliseconds that the clients should wait for until they start performing measurements.|start_delay_milliseconds|startDelayMilliseconds|
|**--measurement-count**|integer|The number of measurements to perform.|measurement_count|measurementCount|
|**--tags**|dictionary|Tags for the resource.|tags|tags|
|**--location**|string|Region where the Azure resource is located.|location|location|
|**--description**|string|The description of the Footprint profile.|description|description|
|**--cold-path-sampling-percentage-rate**|number|The default sampling percentage for cold path measurement storage.|cold_path_sampling_percentage_rate|coldPathSamplingPercentageRate|
|**--reporting-endpoints**|array|The endpoints which to upload measurements to.|reporting_endpoints|reportingEndpoints|

### footprint profile delete

delete a footprint profile.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint profile|profiles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|

### footprint profile list

list a footprint profile.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint profile|profiles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

### footprint profile show

show a footprint profile.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint profile|profiles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|

### footprint profile update

update a footprint profile.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|footprint profile|profiles|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--profile-name**|string|Name of the Footprint profile resource.|profile_name|profileName|
|**--tags**|dictionary|The tags for this resource.|tags|tags|
