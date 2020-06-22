# Azure CLI Module Creation Report

### healthcareapis operation-result show

show a healthcareapis operation-result.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location-name**|string|The location of the operation.|location_name|
|**--operation-result-id**|string|The ID of the operation result to get.|operation_result_id|
### healthcareapis service create

create a healthcareapis service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|
|**--resource-name**|string|The name of the service instance.|resource_name|
|**--kind**|sealed-choice|The kind of the service.|kind|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|
|**--identity**|object|Setting indicating whether the service has a managed identity associated with it.|identity|
|**--properties**|object|The common properties of a service.|properties|
### healthcareapis service delete

delete a healthcareapis service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|
|**--resource-name**|string|The name of the service instance.|resource_name|
### healthcareapis service list

list a healthcareapis service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|
### healthcareapis service show

show a healthcareapis service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|
|**--resource-name**|string|The name of the service instance.|resource_name|
### healthcareapis service update

update a healthcareapis service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|
|**--resource-name**|string|The name of the service instance.|resource_name|
|**--tags**|dictionary|Instance tags|tags|