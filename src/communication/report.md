# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az communication|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az communication` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az communication service|CommunicationService|[commands](#CommandsInCommunicationService)|
|az communication status|OperationStatuses|[commands](#CommandsInOperationStatuses)|

## COMMANDS
### <a name="CommandsInCommunicationService">Commands in `az communication service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az communication service list](#CommunicationServiceListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCommunicationServiceListByResourceGroup)|[Example](#ExamplesCommunicationServiceListByResourceGroup)|
|[az communication service list](#CommunicationServiceListBySubscription)|ListBySubscription|[Parameters](#ParametersCommunicationServiceListBySubscription)|[Example](#ExamplesCommunicationServiceListBySubscription)|
|[az communication service show](#CommunicationServiceGet)|Get|[Parameters](#ParametersCommunicationServiceGet)|[Example](#ExamplesCommunicationServiceGet)|
|[az communication service create](#CommunicationServiceCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCommunicationServiceCreateOrUpdate#Create)|[Example](#ExamplesCommunicationServiceCreateOrUpdate#Create)|
|[az communication service update](#CommunicationServiceUpdate)|Update|[Parameters](#ParametersCommunicationServiceUpdate)|[Example](#ExamplesCommunicationServiceUpdate)|
|[az communication service delete](#CommunicationServiceDelete)|Delete|[Parameters](#ParametersCommunicationServiceDelete)|[Example](#ExamplesCommunicationServiceDelete)|
|[az communication service link-notification-hub](#CommunicationServiceLinkNotificationHub)|LinkNotificationHub|[Parameters](#ParametersCommunicationServiceLinkNotificationHub)|[Example](#ExamplesCommunicationServiceLinkNotificationHub)|
|[az communication service list-key](#CommunicationServiceListKeys)|ListKeys|[Parameters](#ParametersCommunicationServiceListKeys)|[Example](#ExamplesCommunicationServiceListKeys)|
|[az communication service regenerate-key](#CommunicationServiceRegenerateKey)|RegenerateKey|[Parameters](#ParametersCommunicationServiceRegenerateKey)|[Example](#ExamplesCommunicationServiceRegenerateKey)|

### <a name="CommandsInOperationStatuses">Commands in `az communication status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az communication status show](#OperationStatusesGet)|Get|[Parameters](#ParametersOperationStatusesGet)|[Example](#ExamplesOperationStatusesGet)|


## COMMAND DETAILS

### group `az communication service`
#### <a name="CommunicationServiceListByResourceGroup">Command `az communication service list`</a>

##### <a name="ExamplesCommunicationServiceListByResourceGroup">Example</a>
```
az communication service list --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="CommunicationServiceListBySubscription">Command `az communication service list`</a>

##### <a name="ExamplesCommunicationServiceListBySubscription">Example</a>
```
az communication service list
```
##### <a name="ParametersCommunicationServiceListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CommunicationServiceGet">Command `az communication service show`</a>

##### <a name="ExamplesCommunicationServiceGet">Example</a>
```
az communication service show --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|

#### <a name="CommunicationServiceCreateOrUpdate#Create">Command `az communication service create`</a>

##### <a name="ExamplesCommunicationServiceCreateOrUpdate#Create">Example</a>
```
az communication service create --name "MyCommunicationResource" --location "Global" --data-location "United States" \
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

#### <a name="CommunicationServiceUpdate">Command `az communication service update`</a>

##### <a name="ExamplesCommunicationServiceUpdate">Example</a>
```
az communication service update --name "MyCommunicationResource" --tags newTag="newVal" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|
|**--tags**|dictionary|Tags of the service which is a list of key value pairs that describe the resource.|tags|tags|

#### <a name="CommunicationServiceDelete">Command `az communication service delete`</a>

##### <a name="ExamplesCommunicationServiceDelete">Example</a>
```
az communication service delete --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|

#### <a name="CommunicationServiceLinkNotificationHub">Command `az communication service link-notification-hub`</a>

##### <a name="ExamplesCommunicationServiceLinkNotificationHub">Example</a>
```
az communication service link-notification-hub --name "MyCommunicationResource" --connection-string \
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

#### <a name="CommunicationServiceListKeys">Command `az communication service list-key`</a>

##### <a name="ExamplesCommunicationServiceListKeys">Example</a>
```
az communication service list-key --name "MyCommunicationResource" --resource-group "MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|

#### <a name="CommunicationServiceRegenerateKey">Command `az communication service regenerate-key`</a>

##### <a name="ExamplesCommunicationServiceRegenerateKey">Example</a>
```
az communication service regenerate-key --name "MyCommunicationResource" --key-type "Primary" --resource-group \
"MyResourceGroup"
```
##### <a name="ParametersCommunicationServiceRegenerateKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the CommunicationService resource.|name|communicationServiceName|
|**--key-type**|sealed-choice|The keyType to regenerate. Must be either 'primary' or 'secondary'(case-insensitive).|key_type|keyType|

### group `az communication status`
#### <a name="OperationStatusesGet">Command `az communication status show`</a>

##### <a name="ExamplesOperationStatusesGet">Example</a>
```
az communication status show --operation-id "db5f291f-284d-46e9-9152-d5c83f7c14b8" --location "westus2"
```
##### <a name="ParametersOperationStatusesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The Azure region|location|location|
|**--operation-id**|string|The ID of an ongoing async operation|operation_id|operationId|
