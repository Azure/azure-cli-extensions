# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az healthcareapis|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az healthcareapis` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az healthcareapis service|Services|[commands](#CommandsInServices)|
|az healthcareapis operation-result|OperationResults|[commands](#CommandsInOperationResults)|
|az healthcareapis private-endpoint-connection|PrivateEndpointConnections|[commands](#CommandsInPrivateEndpointConnections)|
|az healthcareapis private-link-resource|PrivateLinkResources|[commands](#CommandsInPrivateLinkResources)|

## COMMANDS
### <a name="CommandsInOperationResults">Commands in `az healthcareapis operation-result` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis operation-result show](#OperationResultsGet)|Get|[Parameters](#ParametersOperationResultsGet)|[Example](#ExamplesOperationResultsGet)|

### <a name="CommandsInPrivateEndpointConnections">Commands in `az healthcareapis private-endpoint-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis private-endpoint-connection list](#PrivateEndpointConnectionsListByService)|ListByService|[Parameters](#ParametersPrivateEndpointConnectionsListByService)|[Example](#ExamplesPrivateEndpointConnectionsListByService)|
|[az healthcareapis private-endpoint-connection show](#PrivateEndpointConnectionsGet)|Get|[Parameters](#ParametersPrivateEndpointConnectionsGet)|[Example](#ExamplesPrivateEndpointConnectionsGet)|
|[az healthcareapis private-endpoint-connection create](#PrivateEndpointConnectionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersPrivateEndpointConnectionsCreateOrUpdate#Create)|[Example](#ExamplesPrivateEndpointConnectionsCreateOrUpdate#Create)|
|[az healthcareapis private-endpoint-connection update](#PrivateEndpointConnectionsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersPrivateEndpointConnectionsCreateOrUpdate#Update)|Not Found|
|[az healthcareapis private-endpoint-connection delete](#PrivateEndpointConnectionsDelete)|Delete|[Parameters](#ParametersPrivateEndpointConnectionsDelete)|[Example](#ExamplesPrivateEndpointConnectionsDelete)|

### <a name="CommandsInPrivateLinkResources">Commands in `az healthcareapis private-link-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis private-link-resource list](#PrivateLinkResourcesListByService)|ListByService|[Parameters](#ParametersPrivateLinkResourcesListByService)|[Example](#ExamplesPrivateLinkResourcesListByService)|
|[az healthcareapis private-link-resource show](#PrivateLinkResourcesGet)|Get|[Parameters](#ParametersPrivateLinkResourcesGet)|[Example](#ExamplesPrivateLinkResourcesGet)|

### <a name="CommandsInServices">Commands in `az healthcareapis service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis service list](#ServicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersServicesListByResourceGroup)|[Example](#ExamplesServicesListByResourceGroup)|
|[az healthcareapis service list](#ServicesList)|List|[Parameters](#ParametersServicesList)|[Example](#ExamplesServicesList)|
|[az healthcareapis service show](#ServicesGet)|Get|[Parameters](#ParametersServicesGet)|[Example](#ExamplesServicesGet)|
|[az healthcareapis service create](#ServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersServicesCreateOrUpdate#Create)|[Example](#ExamplesServicesCreateOrUpdate#Create)|
|[az healthcareapis service update](#ServicesUpdate)|Update|[Parameters](#ParametersServicesUpdate)|[Example](#ExamplesServicesUpdate)|
|[az healthcareapis service delete](#ServicesDelete)|Delete|[Parameters](#ParametersServicesDelete)|[Example](#ExamplesServicesDelete)|


## COMMAND DETAILS

### group `az healthcareapis operation-result`
#### <a name="OperationResultsGet">Command `az healthcareapis operation-result show`</a>

##### <a name="ExamplesOperationResultsGet">Example</a>
```
az healthcareapis operation-result show --location-name "westus" --operation-result-id "exampleid"
```
##### <a name="ParametersOperationResultsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location-name**|string|The location of the operation.|location_name|locationName|
|**--operation-result-id**|string|The ID of the operation result to get.|operation_result_id|operationResultId|

### group `az healthcareapis private-endpoint-connection`
#### <a name="PrivateEndpointConnectionsListByService">Command `az healthcareapis private-endpoint-connection list`</a>

##### <a name="ExamplesPrivateEndpointConnectionsListByService">Example</a>
```
az healthcareapis private-endpoint-connection list --resource-group "rgname" --resource-name "service1"
```
##### <a name="ParametersPrivateEndpointConnectionsListByService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|

#### <a name="PrivateEndpointConnectionsGet">Command `az healthcareapis private-endpoint-connection show`</a>

##### <a name="ExamplesPrivateEndpointConnectionsGet">Example</a>
```
az healthcareapis private-endpoint-connection show --name "myConnection" --resource-group "rgname" --resource-name \
"service1"
```
##### <a name="ParametersPrivateEndpointConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsCreateOrUpdate#Create">Command `az healthcareapis private-endpoint-connection create`</a>

##### <a name="ExamplesPrivateEndpointConnectionsCreateOrUpdate#Create">Example</a>
```
az healthcareapis private-endpoint-connection create --name "myConnection" --resource-group "rgname" --resource-name \
"service1"
```
##### <a name="ParametersPrivateEndpointConnectionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state-status**|choice|Indicates whether the connection has been Approved/Rejected/Removed by the owner of the service.|status|status|
|**--private-link-service-connection-state-description**|string|The reason for approval/rejection of the connection.|description|description|
|**--private-link-service-connection-state-actions-required**|string|A message indicating if changes on the service provider require any updates on the consumer.|actions_required|actionsRequired|

#### <a name="PrivateEndpointConnectionsCreateOrUpdate#Update">Command `az healthcareapis private-endpoint-connection update`</a>

##### <a name="ParametersPrivateEndpointConnectionsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state-status**|choice|Indicates whether the connection has been Approved/Rejected/Removed by the owner of the service.|status|status|
|**--private-link-service-connection-state-description**|string|The reason for approval/rejection of the connection.|description|description|
|**--private-link-service-connection-state-actions-required**|string|A message indicating if changes on the service provider require any updates on the consumer.|actions_required|actionsRequired|

#### <a name="PrivateEndpointConnectionsDelete">Command `az healthcareapis private-endpoint-connection delete`</a>

##### <a name="ExamplesPrivateEndpointConnectionsDelete">Example</a>
```
az healthcareapis private-endpoint-connection delete --name "myConnection" --resource-group "rgname" --resource-name \
"service1"
```
##### <a name="ParametersPrivateEndpointConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

### group `az healthcareapis private-link-resource`
#### <a name="PrivateLinkResourcesListByService">Command `az healthcareapis private-link-resource list`</a>

##### <a name="ExamplesPrivateLinkResourcesListByService">Example</a>
```
az healthcareapis private-link-resource list --resource-group "rgname" --resource-name "service1"
```
##### <a name="ParametersPrivateLinkResourcesListByService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|

#### <a name="PrivateLinkResourcesGet">Command `az healthcareapis private-link-resource show`</a>

##### <a name="ExamplesPrivateLinkResourcesGet">Example</a>
```
az healthcareapis private-link-resource show --group-name "fhir" --resource-group "rgname" --resource-name "service1"
```
##### <a name="ParametersPrivateLinkResourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--group-name**|string|The name of the private link resource group.|group_name|groupName|

### group `az healthcareapis service`
#### <a name="ServicesListByResourceGroup">Command `az healthcareapis service list`</a>

##### <a name="ExamplesServicesListByResourceGroup">Example</a>
```
az healthcareapis service list --resource-group "rgname"
```
##### <a name="ParametersServicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|

#### <a name="ServicesList">Command `az healthcareapis service list`</a>

##### <a name="ExamplesServicesList">Example</a>
```
az healthcareapis service list
```
##### <a name="ParametersServicesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ServicesGet">Command `az healthcareapis service show`</a>

##### <a name="ExamplesServicesGet">Example</a>
```
az healthcareapis service show --resource-group "rg1" --resource-name "service1"
```
##### <a name="ParametersServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|

#### <a name="ServicesCreateOrUpdate#Create">Command `az healthcareapis service create`</a>

##### <a name="ExamplesServicesCreateOrUpdate#Create">Example</a>
```
az healthcareapis service create --resource-group "rg1" --resource-name "service1" --identity-type "SystemAssigned" \
--kind "fhir-R4" --location "westus2" --access-policies object-id="c487e7d1-3210-41a3-8ccc-e9372b78da47" \
--access-policies object-id="5b307da8-43d4-492b-8b66-b0294ade872f" --authentication-configuration \
audience="https://azurehealthcareapis.com" authority="https://login.microsoftonline.com/abfde7b2-df0f-47e6-aabf-2462b07\
508dc" smart-proxy-enabled=true --cors-configuration allow-credentials=false headers="*" max-age=1440 methods="DELETE" \
methods="GET" methods="OPTIONS" methods="PATCH" methods="POST" methods="PUT" origins="*" --cosmos-db-configuration \
key-vault-key-uri="https://my-vault.vault.azure.net/keys/my-key" offer-throughput=1000 --export-configuration-storage-a\
ccount-name "existingStorageAccount" --public-network-access "Disabled"
```
##### <a name="ExamplesServicesCreateOrUpdate#Create">Example</a>
```
az healthcareapis service create --resource-group "rg1" --resource-name "service2" --kind "fhir-R4" --location \
"westus2" --access-policies object-id="c487e7d1-3210-41a3-8ccc-e9372b78da47"
```
##### <a name="ParametersServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--kind**|sealed-choice|The kind of the service.|kind|kind|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--access-policies**|array|The access policies of the service instance.|access_policies|accessPolicies|
|**--cosmos-db-configuration**|object|The settings for the Cosmos DB database backing the service.|cosmos_db_configuration|cosmosDbConfiguration|
|**--authentication-configuration**|object|The authentication configuration for the service instance.|authentication_configuration|authenticationConfiguration|
|**--cors-configuration**|object|The settings for the CORS configuration of the service instance.|cors_configuration|corsConfiguration|
|**--private-endpoint-connections**|array|The list of private endpoint connections that are set up for this resource.|private_endpoint_connections|privateEndpointConnections|
|**--public-network-access**|choice|Control permission for data plane traffic coming from public networks while private endpoint is enabled.|public_network_access|publicNetworkAccess|
|**--export-configuration-storage-account-name**|string|The name of the default export storage account.|storage_account_name|storageAccountName|

#### <a name="ServicesUpdate">Command `az healthcareapis service update`</a>

##### <a name="ExamplesServicesUpdate">Example</a>
```
az healthcareapis service update --resource-group "rg1" --resource-name "service1" --tags tag1="value1" tag2="value2"
```
##### <a name="ParametersServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--tags**|dictionary|Instance tags|tags|tags|
|**--public-network-access**|choice|Control permission for data plane traffic coming from public networks while private endpoint is enabled.|public_network_access|publicNetworkAccess|

#### <a name="ServicesDelete">Command `az healthcareapis service delete`</a>

##### <a name="ExamplesServicesDelete">Example</a>
```
az healthcareapis service delete --resource-group "rg1" --resource-name "service1"
```
##### <a name="ParametersServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
