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
|az healthcareapis workspace|Workspaces|[commands](#CommandsInWorkspaces)|
|az healthcareapis workspace dicom-service|DicomServices|[commands](#CommandsInDicomServices)|
|az healthcareapis workspace fhir-service|FhirServices|[commands](#CommandsInFhirServices)|
|az healthcareapis workspace iot-connector|IotConnectors|[commands](#CommandsInIotConnectors)|
|az healthcareapis workspace iot-connector fhir-destination|FhirDestinations|[commands](#CommandsInFhirDestinations)|
|az healthcareapis workspace iot-connector fhir-destination|IotConnectorFhirDestination|[commands](#CommandsInIotConnectorFhirDestination)|
|az healthcareapis workspace private-endpoint-connection|WorkspacePrivateEndpointConnections|[commands](#CommandsInWorkspacePrivateEndpointConnections)|
|az healthcareapis workspace private-link-resource|WorkspacePrivateLinkResources|[commands](#CommandsInWorkspacePrivateLinkResources)|

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

### <a name="CommandsInWorkspaces">Commands in `az healthcareapis workspace` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace list](#WorkspacesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersWorkspacesListByResourceGroup)|[Example](#ExamplesWorkspacesListByResourceGroup)|
|[az healthcareapis workspace list](#WorkspacesListBySubscription)|ListBySubscription|[Parameters](#ParametersWorkspacesListBySubscription)|[Example](#ExamplesWorkspacesListBySubscription)|
|[az healthcareapis workspace show](#WorkspacesGet)|Get|[Parameters](#ParametersWorkspacesGet)|[Example](#ExamplesWorkspacesGet)|
|[az healthcareapis workspace create](#WorkspacesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersWorkspacesCreateOrUpdate#Create)|[Example](#ExamplesWorkspacesCreateOrUpdate#Create)|
|[az healthcareapis workspace update](#WorkspacesUpdate)|Update|[Parameters](#ParametersWorkspacesUpdate)|[Example](#ExamplesWorkspacesUpdate)|
|[az healthcareapis workspace delete](#WorkspacesDelete)|Delete|[Parameters](#ParametersWorkspacesDelete)|[Example](#ExamplesWorkspacesDelete)|

### <a name="CommandsInDicomServices">Commands in `az healthcareapis workspace dicom-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace dicom-service list](#DicomServicesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersDicomServicesListByWorkspace)|[Example](#ExamplesDicomServicesListByWorkspace)|
|[az healthcareapis workspace dicom-service show](#DicomServicesGet)|Get|[Parameters](#ParametersDicomServicesGet)|[Example](#ExamplesDicomServicesGet)|
|[az healthcareapis workspace dicom-service create](#DicomServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDicomServicesCreateOrUpdate#Create)|[Example](#ExamplesDicomServicesCreateOrUpdate#Create)|
|[az healthcareapis workspace dicom-service update](#DicomServicesUpdate)|Update|[Parameters](#ParametersDicomServicesUpdate)|[Example](#ExamplesDicomServicesUpdate)|
|[az healthcareapis workspace dicom-service delete](#DicomServicesDelete)|Delete|[Parameters](#ParametersDicomServicesDelete)|[Example](#ExamplesDicomServicesDelete)|

### <a name="CommandsInFhirServices">Commands in `az healthcareapis workspace fhir-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace fhir-service list](#FhirServicesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersFhirServicesListByWorkspace)|[Example](#ExamplesFhirServicesListByWorkspace)|
|[az healthcareapis workspace fhir-service show](#FhirServicesGet)|Get|[Parameters](#ParametersFhirServicesGet)|[Example](#ExamplesFhirServicesGet)|
|[az healthcareapis workspace fhir-service create](#FhirServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersFhirServicesCreateOrUpdate#Create)|[Example](#ExamplesFhirServicesCreateOrUpdate#Create)|
|[az healthcareapis workspace fhir-service update](#FhirServicesUpdate)|Update|[Parameters](#ParametersFhirServicesUpdate)|[Example](#ExamplesFhirServicesUpdate)|
|[az healthcareapis workspace fhir-service delete](#FhirServicesDelete)|Delete|[Parameters](#ParametersFhirServicesDelete)|[Example](#ExamplesFhirServicesDelete)|

### <a name="CommandsInIotConnectors">Commands in `az healthcareapis workspace iot-connector` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace iot-connector list](#IotConnectorsListByWorkspace)|ListByWorkspace|[Parameters](#ParametersIotConnectorsListByWorkspace)|[Example](#ExamplesIotConnectorsListByWorkspace)|
|[az healthcareapis workspace iot-connector show](#IotConnectorsGet)|Get|[Parameters](#ParametersIotConnectorsGet)|[Example](#ExamplesIotConnectorsGet)|
|[az healthcareapis workspace iot-connector create](#IotConnectorsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIotConnectorsCreateOrUpdate#Create)|[Example](#ExamplesIotConnectorsCreateOrUpdate#Create)|
|[az healthcareapis workspace iot-connector update](#IotConnectorsUpdate)|Update|[Parameters](#ParametersIotConnectorsUpdate)|[Example](#ExamplesIotConnectorsUpdate)|
|[az healthcareapis workspace iot-connector delete](#IotConnectorsDelete)|Delete|[Parameters](#ParametersIotConnectorsDelete)|[Example](#ExamplesIotConnectorsDelete)|

### <a name="CommandsInFhirDestinations">Commands in `az healthcareapis workspace iot-connector fhir-destination` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace iot-connector fhir-destination list](#FhirDestinationsListByIotConnector)|ListByIotConnector|[Parameters](#ParametersFhirDestinationsListByIotConnector)|[Example](#ExamplesFhirDestinationsListByIotConnector)|

### <a name="CommandsInIotConnectorFhirDestination">Commands in `az healthcareapis workspace iot-connector fhir-destination` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace iot-connector fhir-destination show](#IotConnectorFhirDestinationGet)|Get|[Parameters](#ParametersIotConnectorFhirDestinationGet)|[Example](#ExamplesIotConnectorFhirDestinationGet)|
|[az healthcareapis workspace iot-connector fhir-destination create](#IotConnectorFhirDestinationCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIotConnectorFhirDestinationCreateOrUpdate#Create)|[Example](#ExamplesIotConnectorFhirDestinationCreateOrUpdate#Create)|
|[az healthcareapis workspace iot-connector fhir-destination update](#IotConnectorFhirDestinationCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIotConnectorFhirDestinationCreateOrUpdate#Update)|Not Found|
|[az healthcareapis workspace iot-connector fhir-destination delete](#IotConnectorFhirDestinationDelete)|Delete|[Parameters](#ParametersIotConnectorFhirDestinationDelete)|[Example](#ExamplesIotConnectorFhirDestinationDelete)|

### <a name="CommandsInWorkspacePrivateEndpointConnections">Commands in `az healthcareapis workspace private-endpoint-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace private-endpoint-connection list](#WorkspacePrivateEndpointConnectionsListByWorkspace)|ListByWorkspace|[Parameters](#ParametersWorkspacePrivateEndpointConnectionsListByWorkspace)|[Example](#ExamplesWorkspacePrivateEndpointConnectionsListByWorkspace)|
|[az healthcareapis workspace private-endpoint-connection show](#WorkspacePrivateEndpointConnectionsGet)|Get|[Parameters](#ParametersWorkspacePrivateEndpointConnectionsGet)|[Example](#ExamplesWorkspacePrivateEndpointConnectionsGet)|
|[az healthcareapis workspace private-endpoint-connection create](#WorkspacePrivateEndpointConnectionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersWorkspacePrivateEndpointConnectionsCreateOrUpdate#Create)|[Example](#ExamplesWorkspacePrivateEndpointConnectionsCreateOrUpdate#Create)|
|[az healthcareapis workspace private-endpoint-connection update](#WorkspacePrivateEndpointConnectionsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersWorkspacePrivateEndpointConnectionsCreateOrUpdate#Update)|Not Found|
|[az healthcareapis workspace private-endpoint-connection delete](#WorkspacePrivateEndpointConnectionsDelete)|Delete|[Parameters](#ParametersWorkspacePrivateEndpointConnectionsDelete)|[Example](#ExamplesWorkspacePrivateEndpointConnectionsDelete)|

### <a name="CommandsInWorkspacePrivateLinkResources">Commands in `az healthcareapis workspace private-link-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthcareapis workspace private-link-resource list](#WorkspacePrivateLinkResourcesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersWorkspacePrivateLinkResourcesListByWorkspace)|[Example](#ExamplesWorkspacePrivateLinkResourcesListByWorkspace)|
|[az healthcareapis workspace private-link-resource show](#WorkspacePrivateLinkResourcesGet)|Get|[Parameters](#ParametersWorkspacePrivateLinkResourcesGet)|[Example](#ExamplesWorkspacePrivateLinkResourcesGet)|


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
az healthcareapis private-endpoint-connection create --name "myConnection" --private-link-service-connection-state \
description="Auto-Approved" status="Approved" --resource-group "rgname" --resource-name "service1"
```
##### <a name="ParametersPrivateEndpointConnectionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the service instance.|resource_name|resourceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|
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
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|
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
|**--login-servers**|array|The list of the ACR login servers.|login_servers|loginServers|
|**--oci-artifacts**|array|The list of Open Container Initiative (OCI) artifacts.|oci_artifacts|ociArtifacts|
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

### group `az healthcareapis workspace`
#### <a name="WorkspacesListByResourceGroup">Command `az healthcareapis workspace list`</a>

##### <a name="ExamplesWorkspacesListByResourceGroup">Example</a>
```
az healthcareapis workspace list --resource-group "testRG"
```
##### <a name="ParametersWorkspacesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|

#### <a name="WorkspacesListBySubscription">Command `az healthcareapis workspace list`</a>

##### <a name="ExamplesWorkspacesListBySubscription">Example</a>
```
az healthcareapis workspace list
```
##### <a name="ParametersWorkspacesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="WorkspacesGet">Command `az healthcareapis workspace show`</a>

##### <a name="ExamplesWorkspacesGet">Example</a>
```
az healthcareapis workspace show --resource-group "testRG" --name "workspace1"
```
##### <a name="ParametersWorkspacesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

#### <a name="WorkspacesCreateOrUpdate#Create">Command `az healthcareapis workspace create`</a>

##### <a name="ExamplesWorkspacesCreateOrUpdate#Create">Example</a>
```
az healthcareapis workspace create --resource-group "testRG" --location "westus" --name "workspace1"
```
##### <a name="ParametersWorkspacesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--location**|string|The resource location.|location|location|
|**--public-network-access**|choice|Control permission for data plane traffic coming from public networks while private endpoint is enabled.|public_network_access|publicNetworkAccess|

#### <a name="WorkspacesUpdate">Command `az healthcareapis workspace update`</a>

##### <a name="ExamplesWorkspacesUpdate">Example</a>
```
az healthcareapis workspace update --resource-group "testRG" --name "workspace1" --tags tagKey="tagValue"
```
##### <a name="ParametersWorkspacesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="WorkspacesDelete">Command `az healthcareapis workspace delete`</a>

##### <a name="ExamplesWorkspacesDelete">Example</a>
```
az healthcareapis workspace delete --resource-group "testRG" --name "workspace1"
```
##### <a name="ParametersWorkspacesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

### group `az healthcareapis workspace dicom-service`
#### <a name="DicomServicesListByWorkspace">Command `az healthcareapis workspace dicom-service list`</a>

##### <a name="ExamplesDicomServicesListByWorkspace">Example</a>
```
az healthcareapis workspace dicom-service list --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersDicomServicesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

#### <a name="DicomServicesGet">Command `az healthcareapis workspace dicom-service show`</a>

##### <a name="ExamplesDicomServicesGet">Example</a>
```
az healthcareapis workspace dicom-service show --name "blue" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersDicomServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--dicom-service-name**|string|The name of DICOM Service resource.|dicom_service_name|dicomServiceName|

#### <a name="DicomServicesCreateOrUpdate#Create">Command `az healthcareapis workspace dicom-service create`</a>

##### <a name="ExamplesDicomServicesCreateOrUpdate#Create">Example</a>
```
az healthcareapis workspace dicom-service create --name "blue" --location "westus" --resource-group "testRG" \
--workspace-name "workspace1"
```
##### <a name="ParametersDicomServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--dicom-service-name**|string|The name of DICOM Service resource.|dicom_service_name|dicomServiceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--location**|string|The resource location.|location|location|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|
|**--public-network-access**|choice|Control permission for data plane traffic coming from public networks while private endpoint is enabled.|public_network_access|publicNetworkAccess|

#### <a name="DicomServicesUpdate">Command `az healthcareapis workspace dicom-service update`</a>

##### <a name="ExamplesDicomServicesUpdate">Example</a>
```
az healthcareapis workspace dicom-service update --name "blue" --tags tagKey="tagValue" --resource-group "testRG" \
--workspace-name "workspace1"
```
##### <a name="ParametersDicomServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--dicom-service-name**|string|The name of DICOM Service resource.|dicom_service_name|dicomServiceName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="DicomServicesDelete">Command `az healthcareapis workspace dicom-service delete`</a>

##### <a name="ExamplesDicomServicesDelete">Example</a>
```
az healthcareapis workspace dicom-service delete --name "blue" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersDicomServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--dicom-service-name**|string|The name of DICOM Service resource.|dicom_service_name|dicomServiceName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

### group `az healthcareapis workspace fhir-service`
#### <a name="FhirServicesListByWorkspace">Command `az healthcareapis workspace fhir-service list`</a>

##### <a name="ExamplesFhirServicesListByWorkspace">Example</a>
```
az healthcareapis workspace fhir-service list --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersFhirServicesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

#### <a name="FhirServicesGet">Command `az healthcareapis workspace fhir-service show`</a>

##### <a name="ExamplesFhirServicesGet">Example</a>
```
az healthcareapis workspace fhir-service show --name "fhirservices1" --resource-group "testRG" --workspace-name \
"workspace1"
```
##### <a name="ParametersFhirServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--fhir-service-name**|string|The name of FHIR Service resource.|fhir_service_name|fhirServiceName|

#### <a name="FhirServicesCreateOrUpdate#Create">Command `az healthcareapis workspace fhir-service create`</a>

##### <a name="ExamplesFhirServicesCreateOrUpdate#Create">Example</a>
```
az healthcareapis workspace fhir-service create --name "fhirservice1" --identity-type "SystemAssigned" --kind "fhir-R4" \
--location "westus" --access-policies object-id="c487e7d1-3210-41a3-8ccc-e9372b78da47" --access-policies \
object-id="5b307da8-43d4-492b-8b66-b0294ade872f" --login-servers "test1.azurecr.io" --authentication-configuration \
audience="https://azurehealthcareapis.com" authority="https://login.microsoftonline.com/abfde7b2-df0f-47e6-aabf-2462b07\
508dc" smart-proxy-enabled=true --cors-configuration allow-credentials=false headers="*" max-age=1440 methods="DELETE" \
methods="GET" methods="OPTIONS" methods="PATCH" methods="POST" methods="PUT" origins="*" --export-configuration-storage-account-name \
"existingStorageAccount" --tags additionalProp1="string" additionalProp2="string" additionalProp3="string" \
--resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersFhirServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--fhir-service-name**|string|The name of FHIR Service resource.|fhir_service_name|fhirServiceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--location**|string|The resource location.|location|location|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|
|**--kind**|choice|The kind of the service.|kind|kind|
|**--access-policies**|array|Fhir Service access policies.|access_policies|accessPolicies|
|**--authentication-configuration**|object|Fhir Service authentication configuration.|authentication_configuration|authenticationConfiguration|
|**--cors-configuration**|object|Fhir Service Cors configuration.|cors_configuration|corsConfiguration|
|**--public-network-access**|choice|Control permission for data plane traffic coming from public networks while private endpoint is enabled.|public_network_access|publicNetworkAccess|
|**--default**|choice|The default value for tracking history across all resources.|default|default|
|**--resource-type-overrides**|dictionary|A list of FHIR Resources and their version policy overrides.|resource_type_overrides|resourceTypeOverrides|
|**--export-configuration-storage-account-name**|string|The name of the default export storage account.|storage_account_name|storageAccountName|
|**--login-servers**|array|The list of the Azure container registry login servers.|login_servers|loginServers|
|**--oci-artifacts**|array|The list of Open Container Initiative (OCI) artifacts.|oci_artifacts|ociArtifacts|

#### <a name="FhirServicesUpdate">Command `az healthcareapis workspace fhir-service update`</a>

##### <a name="ExamplesFhirServicesUpdate">Example</a>
```
az healthcareapis workspace fhir-service update --name "fhirservice1" --tags tagKey="tagValue" --resource-group \
"testRG" --workspace-name "workspace1"
```
##### <a name="ParametersFhirServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--fhir-service-name**|string|The name of FHIR Service resource.|fhir_service_name|fhirServiceName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="FhirServicesDelete">Command `az healthcareapis workspace fhir-service delete`</a>

##### <a name="ExamplesFhirServicesDelete">Example</a>
```
az healthcareapis workspace fhir-service delete --name "fhirservice1" --resource-group "testRG" --workspace-name \
"workspace1"
```
##### <a name="ParametersFhirServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--fhir-service-name**|string|The name of FHIR Service resource.|fhir_service_name|fhirServiceName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

### group `az healthcareapis workspace iot-connector`
#### <a name="IotConnectorsListByWorkspace">Command `az healthcareapis workspace iot-connector list`</a>

##### <a name="ExamplesIotConnectorsListByWorkspace">Example</a>
```
az healthcareapis workspace iot-connector list --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorsListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

#### <a name="IotConnectorsGet">Command `az healthcareapis workspace iot-connector show`</a>

##### <a name="ExamplesIotConnectorsGet">Example</a>
```
az healthcareapis workspace iot-connector show --name "blue" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|

#### <a name="IotConnectorsCreateOrUpdate#Create">Command `az healthcareapis workspace iot-connector create`</a>

##### <a name="ExamplesIotConnectorsCreateOrUpdate#Create">Example</a>
```
az healthcareapis workspace iot-connector create --identity-type "SystemAssigned" --location "westus" --content \
"{\\"template\\":[{\\"template\\":{\\"deviceIdExpression\\":\\"$.deviceid\\",\\"timestampExpression\\":\\"$.measurement\
datetime\\",\\"typeMatchExpression\\":\\"$..[?(@heartrate)]\\",\\"typeName\\":\\"heartrate\\",\\"values\\":[{\\"require\
d\\":\\"true\\",\\"valueExpression\\":\\"$.heartrate\\",\\"valueName\\":\\"hr\\"}]},\\"templateType\\":\\"JsonPathConte\
nt\\"}],\\"templateType\\":\\"CollectionContent\\"}" --ingestion-endpoint-configuration consumer-group="ConsumerGroupA"\
 event-hub-name="MyEventHubName" fully-qualified-event-hub-namespace="myeventhub.servicesbus.windows.net" --tags \
additionalProp1="string" additionalProp2="string" additionalProp3="string" --name "blue" --resource-group "testRG" \
--workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--location**|string|The resource location.|location|location|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|
|**--ingestion-endpoint-configuration**|object|Source configuration.|ingestion_endpoint_configuration|ingestionEndpointConfiguration|
|**--content**|any|The mapping.|content|content|

#### <a name="IotConnectorsUpdate">Command `az healthcareapis workspace iot-connector update`</a>

##### <a name="ExamplesIotConnectorsUpdate">Example</a>
```
az healthcareapis workspace iot-connector update --name "blue" --identity-type "SystemAssigned" --tags additionalProp1="string" \
additionalProp2="string" additionalProp3="string" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--identity-type**|choice|Type of identity being specified, currently SystemAssigned and None are allowed.|type|type|
|**--user-assigned-identities**|dictionary|The set of user assigned identities associated with the resource. The userAssignedIdentities dictionary keys will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}. The dictionary values can be empty objects ({}) in requests.|user_assigned_identities|userAssignedIdentities|

#### <a name="IotConnectorsDelete">Command `az healthcareapis workspace iot-connector delete`</a>

##### <a name="ExamplesIotConnectorsDelete">Example</a>
```
az healthcareapis workspace iot-connector delete --name "blue" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

### group `az healthcareapis workspace iot-connector fhir-destination`
#### <a name="FhirDestinationsListByIotConnector">Command `az healthcareapis workspace iot-connector fhir-destination list`</a>

##### <a name="ExamplesFhirDestinationsListByIotConnector">Example</a>
```
az healthcareapis workspace iot-connector fhir-destination list --iot-connector-name "blue" --resource-group "testRG" \
--workspace-name "workspace1"
```
##### <a name="ParametersFhirDestinationsListByIotConnector">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|

### group `az healthcareapis workspace iot-connector fhir-destination`
#### <a name="IotConnectorFhirDestinationGet">Command `az healthcareapis workspace iot-connector fhir-destination show`</a>

##### <a name="ExamplesIotConnectorFhirDestinationGet">Example</a>
```
az healthcareapis workspace iot-connector fhir-destination show --fhir-destination-name "dest1" --iot-connector-name \
"blue" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorFhirDestinationGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--fhir-destination-name**|string|The name of IoT Connector FHIR destination resource.|fhir_destination_name|fhirDestinationName|

#### <a name="IotConnectorFhirDestinationCreateOrUpdate#Create">Command `az healthcareapis workspace iot-connector fhir-destination create`</a>

##### <a name="ExamplesIotConnectorFhirDestinationCreateOrUpdate#Create">Example</a>
```
az healthcareapis workspace iot-connector fhir-destination create --fhir-destination-name "dest1" --iot-connector-name \
"blue" --location "westus" --content "{\\"template\\":[{\\"template\\":{\\"codes\\":[{\\"code\\":\\"8867-4\\",\\"displa\
y\\":\\"Heart rate\\",\\"system\\":\\"http://loinc.org\\"}],\\"periodInterval\\":60,\\"typeName\\":\\"heartrate\\",\\"v\
alue\\":{\\"defaultPeriod\\":5000,\\"unit\\":\\"count/min\\",\\"valueName\\":\\"hr\\",\\"valueType\\":\\"SampledData\\"\
}},\\"templateType\\":\\"CodeValueFhir\\"}],\\"templateType\\":\\"CollectionFhirTemplate\\"}" \
--fhir-service-resource-id "subscriptions/11111111-2222-3333-4444-555566667777/resourceGroups/myrg/providers/Microsoft.\
HealthcareApis/workspaces/myworkspace/fhirservices/myfhirservice" --resource-identity-resolution-type "Create" \
--resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorFhirDestinationCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--fhir-destination-name**|string|The name of IoT Connector FHIR destination resource.|fhir_destination_name|fhirDestinationName|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--location**|string|The resource location.|location|location|
|**--resource-identity-resolution-type**|choice|Determines how resource identity is resolved on the destination.|resource_identity_resolution_type|resourceIdentityResolutionType|
|**--fhir-service-resource-id**|string|Fully qualified resource id of the FHIR service to connect to.|fhir_service_resource_id|fhirServiceResourceId|
|**--content**|any|The mapping.|content|content|

#### <a name="IotConnectorFhirDestinationCreateOrUpdate#Update">Command `az healthcareapis workspace iot-connector fhir-destination update`</a>


##### <a name="ParametersIotConnectorFhirDestinationCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--fhir-destination-name**|string|The name of IoT Connector FHIR destination resource.|fhir_destination_name|fhirDestinationName|
|**--etag**|string|An etag associated with the resource, used for optimistic concurrency when editing it.|etag|etag|
|**--location**|string|The resource location.|location|location|
|**--resource-identity-resolution-type**|choice|Determines how resource identity is resolved on the destination.|resource_identity_resolution_type|resourceIdentityResolutionType|
|**--fhir-service-resource-id**|string|Fully qualified resource id of the FHIR service to connect to.|fhir_service_resource_id|fhirServiceResourceId|
|**--content**|any|The mapping.|content|content|

#### <a name="IotConnectorFhirDestinationDelete">Command `az healthcareapis workspace iot-connector fhir-destination delete`</a>

##### <a name="ExamplesIotConnectorFhirDestinationDelete">Example</a>
```
az healthcareapis workspace iot-connector fhir-destination delete --fhir-destination-name "dest1" --iot-connector-name \
"blue" --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersIotConnectorFhirDestinationDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--iot-connector-name**|string|The name of IoT Connector resource.|iot_connector_name|iotConnectorName|
|**--fhir-destination-name**|string|The name of IoT Connector FHIR destination resource.|fhir_destination_name|fhirDestinationName|

### group `az healthcareapis workspace private-endpoint-connection`
#### <a name="WorkspacePrivateEndpointConnectionsListByWorkspace">Command `az healthcareapis workspace private-endpoint-connection list`</a>

##### <a name="ExamplesWorkspacePrivateEndpointConnectionsListByWorkspace">Example</a>
```
az healthcareapis workspace private-endpoint-connection list --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersWorkspacePrivateEndpointConnectionsListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

#### <a name="WorkspacePrivateEndpointConnectionsGet">Command `az healthcareapis workspace private-endpoint-connection show`</a>

##### <a name="ExamplesWorkspacePrivateEndpointConnectionsGet">Example</a>
```
az healthcareapis workspace private-endpoint-connection show --private-endpoint-connection-name "myConnection" \
--resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersWorkspacePrivateEndpointConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="WorkspacePrivateEndpointConnectionsCreateOrUpdate#Create">Command `az healthcareapis workspace private-endpoint-connection create`</a>

##### <a name="ExamplesWorkspacePrivateEndpointConnectionsCreateOrUpdate#Create">Example</a>
```
az healthcareapis workspace private-endpoint-connection create --private-endpoint-connection-name "myConnection" \
--private-link-service-connection-state description="Auto-Approved" status="Approved" --resource-group "testRG" \
--workspace-name "workspace1"
```
##### <a name="ParametersWorkspacePrivateEndpointConnectionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

#### <a name="WorkspacePrivateEndpointConnectionsCreateOrUpdate#Update">Command `az healthcareapis workspace private-endpoint-connection update`</a>


##### <a name="ParametersWorkspacePrivateEndpointConnectionsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

#### <a name="WorkspacePrivateEndpointConnectionsDelete">Command `az healthcareapis workspace private-endpoint-connection delete`</a>

##### <a name="ExamplesWorkspacePrivateEndpointConnectionsDelete">Example</a>
```
az healthcareapis workspace private-endpoint-connection delete --private-endpoint-connection-name "myConnection" \
--resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersWorkspacePrivateEndpointConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

### group `az healthcareapis workspace private-link-resource`
#### <a name="WorkspacePrivateLinkResourcesListByWorkspace">Command `az healthcareapis workspace private-link-resource list`</a>

##### <a name="ExamplesWorkspacePrivateLinkResourcesListByWorkspace">Example</a>
```
az healthcareapis workspace private-link-resource list --resource-group "testRG" --workspace-name "workspace1"
```
##### <a name="ParametersWorkspacePrivateLinkResourcesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|

#### <a name="WorkspacePrivateLinkResourcesGet">Command `az healthcareapis workspace private-link-resource show`</a>

##### <a name="ExamplesWorkspacePrivateLinkResourcesGet">Example</a>
```
az healthcareapis workspace private-link-resource show --group-name "healthcareworkspace" --resource-group "testRG" \
--workspace-name "workspace1"
```
##### <a name="ParametersWorkspacePrivateLinkResourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the service instance.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of workspace resource.|workspace_name|workspaceName|
|**--group-name**|string|The name of the private link resource group.|group_name|groupName|
