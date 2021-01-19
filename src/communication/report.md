# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az communication|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az communication` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az communication|CommunicationService|[commands](#CommandsInCommunicationService)|
|az communication|OperationStatuses|[commands](#CommandsInOperationStatuses)|

## COMMANDS
### <a name="CommandsInCommunicationService">Commands in `az communication` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az communication list](#CommunicationServiceListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCommunicationServiceListByResourceGroup)|[Example](#ExamplesCommunicationServiceListByResourceGroup)|
|[az communication list](#CommunicationServiceListBySubscription)|ListBySubscription|[Parameters](#ParametersCommunicationServiceListBySubscription)|[Example](#ExamplesCommunicationServiceListBySubscription)|
|[az communication show](#CommunicationServiceGet)|Get|[Parameters](#ParametersCommunicationServiceGet)|[Example](#ExamplesCommunicationServiceGet)|
|[az communication create](#CommunicationServiceCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCommunicationServiceCreateOrUpdate#Create)|[Example](#ExamplesCommunicationServiceCreateOrUpdate#Create)|
|[az communication update](#CommunicationServiceUpdate)|Update|[Parameters](#ParametersCommunicationServiceUpdate)|[Example](#ExamplesCommunicationServiceUpdate)|
|[az communication delete](#CommunicationServiceDelete)|Delete|[Parameters](#ParametersCommunicationServiceDelete)|[Example](#ExamplesCommunicationServiceDelete)|
|[az communication link-notification-hub](#CommunicationServiceLinkNotificationHub)|LinkNotificationHub|[Parameters](#ParametersCommunicationServiceLinkNotificationHub)|[Example](#ExamplesCommunicationServiceLinkNotificationHub)|
|[az communication list-key](#CommunicationServiceListKeys)|ListKeys|[Parameters](#ParametersCommunicationServiceListKeys)|[Example](#ExamplesCommunicationServiceListKeys)|
|[az communication regenerate-key](#CommunicationServiceRegenerateKey)|RegenerateKey|[Parameters](#ParametersCommunicationServiceRegenerateKey)|[Example](#ExamplesCommunicationServiceRegenerateKey)|

### <a name="CommandsInOperationStatuses">Commands in `az communication` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az communication show-status](#OperationStatusesGet)|Get|[Parameters](#ParametersOperationStatusesGet)|[Example](#ExamplesOperationStatusesGet)|


## COMMAND DETAILS

### group `az communication`
#### <a name="CommunicationServiceListByResourceGroup">Command `az communication list`</a>

##### <a name="ExamplesCommunicationServiceListByResourceGroup">Example</a>
```
az communication list --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="CommunicationServiceListBySubscription">Command `az communication list`</a>

##### <a name="ExamplesCommunicationServiceListBySubscription">Example</a>
```
az communication list
```
##### <a name="ParametersCommunicationServiceListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CommunicationServiceGet">Command `az communication show`</a>

##### <a name="ExamplesCommunicationServiceGet">Example</a>
```
az communication show --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|

#### <a name="CommunicationServiceCreateOrUpdate#Create">Command `az communication create`</a>

##### <a name="ExamplesCommunicationServiceCreateOrUpdate#Create">Example</a>
```
az communication create --name "MyCommunicationResource" --location "Global" --data-location "United States" \
--resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|
|**--location**|string|The Azure location where the CommunicationService is running.|location|location|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describe the resource.|tags|tags|
|**--data-location**|string|The location where the communication service stores its data at rest.|data_location|dataLocation|

#### <a name="CommunicationServiceUpdate">Command `az communication update`</a>

##### <a name="ExamplesCommunicationServiceUpdate">Example</a>
```
az communication update --name "MyCommunicationResource" --tags newTag="newVal" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describe the resource.|tags|tags|

#### <a name="CommunicationServiceDelete">Command `az communication delete`</a>

##### <a name="ExamplesCommunicationServiceDelete">Example</a>
```
az communication delete --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|

#### <a name="CommunicationServiceLinkNotificationHub">Command `az communication link-notification-hub`</a>

##### <a name="ExamplesCommunicationServiceLinkNotificationHub">Example</a>
```
az communication link-notification-hub --name "MyCommunicationResource" --connection-string \
"Endpoint=sb://MyNamespace.servicebus.windows.net/;SharedAccessKey=abcd1234" --resource-id \
"/subscriptions/12345/resourceGroups/MyOtherResourceGroup/providers/Microsoft.NotificationHubs/namespaces/MyNamespace/n\
otificationHubs/MyHub" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceLinkNotificationHub">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|
|**--resource-id**|string|The resource ID of the notification hub|resource_id|resourceId|
|**--connection-string**|string|Connection string for the notification hub|connection_string|connectionString|

#### <a name="CommunicationServiceListKeys">Command `az communication list-key`</a>

##### <a name="ExamplesCommunicationServiceListKeys">Example</a>
```
az communication list-key --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|

#### <a name="CommunicationServiceRegenerateKey">Command `az communication regenerate-key`</a>

##### <a name="ExamplesCommunicationServiceRegenerateKey">Example</a>
```
az communication regenerate-key --name "MyCommunicationResource" --key-type "Primary" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceRegenerateKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|
|**--key-type**|sealed-choice|The keyType to regenerate. Must be either 'primary' or 'secondary'(case-insensitive).|key_type|keyType|

### group `az communication`
#### <a name="OperationStatusesGet">Command `az communication show-status`</a>

##### <a name="ExamplesOperationStatusesGet">Example</a>
```
az communication show-status --operation-id "db5f291f-284d-46e9-9152-d5c83f7c14b8" --location "westus2"
```
##### <a name="ParametersOperationStatusesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure region|location|location|
|**--operation-id**|string|The ID of an ongoing async operation|operation_id|operationId|
