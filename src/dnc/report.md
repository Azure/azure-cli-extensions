# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az dnc|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az dnc` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az dnc controller|Controller|[commands](#CommandsInController)|
|az dnc delegated-network|DelegatedNetwork|[commands](#CommandsInDelegatedNetwork)|
|az dnc orchestrator-instance-service|OrchestratorInstanceService|[commands](#CommandsInOrchestratorInstanceService)|
|az dnc delegated-subnet-service|DelegatedSubnetService|[commands](#CommandsInDelegatedSubnetService)|

## COMMANDS
### <a name="CommandsInController">Commands in `az dnc controller` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dnc controller show](#ControllerGetDetails)|GetDetails|[Parameters](#ParametersControllerGetDetails)|[Example](#ExamplesControllerGetDetails)|
|[az dnc controller create](#ControllerCreate)|Create|[Parameters](#ParametersControllerCreate)|[Example](#ExamplesControllerCreate)|
|[az dnc controller delete](#ControllerDelete)|Delete|[Parameters](#ParametersControllerDelete)|[Example](#ExamplesControllerDelete)|

### <a name="CommandsInDelegatedNetwork">Commands in `az dnc delegated-network` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dnc delegated-network list](#DelegatedNetworkListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDelegatedNetworkListByResourceGroup)|[Example](#ExamplesDelegatedNetworkListByResourceGroup)|
|[az dnc delegated-network list](#DelegatedNetworkListBySubscription)|ListBySubscription|[Parameters](#ParametersDelegatedNetworkListBySubscription)|[Example](#ExamplesDelegatedNetworkListBySubscription)|

### <a name="CommandsInDelegatedSubnetService">Commands in `az dnc delegated-subnet-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dnc delegated-subnet-service list](#DelegatedSubnetServiceListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDelegatedSubnetServiceListByResourceGroup)|[Example](#ExamplesDelegatedSubnetServiceListByResourceGroup)|
|[az dnc delegated-subnet-service list](#DelegatedSubnetServiceListBySubscription)|ListBySubscription|[Parameters](#ParametersDelegatedSubnetServiceListBySubscription)|[Example](#ExamplesDelegatedSubnetServiceListBySubscription)|
|[az dnc delegated-subnet-service show](#DelegatedSubnetServiceGetDetails)|GetDetails|[Parameters](#ParametersDelegatedSubnetServiceGetDetails)|[Example](#ExamplesDelegatedSubnetServiceGetDetails)|
|[az dnc delegated-subnet-service create](#DelegatedSubnetServicePutDetails)|PutDetails|[Parameters](#ParametersDelegatedSubnetServicePutDetails)|[Example](#ExamplesDelegatedSubnetServicePutDetails)|
|[az dnc delegated-subnet-service delete](#DelegatedSubnetServiceDeleteDetails)|DeleteDetails|[Parameters](#ParametersDelegatedSubnetServiceDeleteDetails)|[Example](#ExamplesDelegatedSubnetServiceDeleteDetails)|

### <a name="CommandsInOrchestratorInstanceService">Commands in `az dnc orchestrator-instance-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dnc orchestrator-instance-service list](#OrchestratorInstanceServiceListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersOrchestratorInstanceServiceListByResourceGroup)|[Example](#ExamplesOrchestratorInstanceServiceListByResourceGroup)|
|[az dnc orchestrator-instance-service list](#OrchestratorInstanceServiceListBySubscription)|ListBySubscription|[Parameters](#ParametersOrchestratorInstanceServiceListBySubscription)|[Example](#ExamplesOrchestratorInstanceServiceListBySubscription)|
|[az dnc orchestrator-instance-service show](#OrchestratorInstanceServiceGetDetails)|GetDetails|[Parameters](#ParametersOrchestratorInstanceServiceGetDetails)|[Example](#ExamplesOrchestratorInstanceServiceGetDetails)|
|[az dnc orchestrator-instance-service create](#OrchestratorInstanceServiceCreate)|Create|[Parameters](#ParametersOrchestratorInstanceServiceCreate)|[Example](#ExamplesOrchestratorInstanceServiceCreate)|
|[az dnc orchestrator-instance-service delete](#OrchestratorInstanceServiceDelete)|Delete|[Parameters](#ParametersOrchestratorInstanceServiceDelete)|[Example](#ExamplesOrchestratorInstanceServiceDelete)|


## COMMAND DETAILS

### group `az dnc controller`
#### <a name="ControllerGetDetails">Command `az dnc controller show`</a>

##### <a name="ExamplesControllerGetDetails">Example</a>
```
az dnc controller show --resource-group "TestRG" --resource-name "testcontroller"
```
##### <a name="ParametersControllerGetDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|

#### <a name="ControllerCreate">Command `az dnc controller create`</a>

##### <a name="ExamplesControllerCreate">Example</a>
```
az dnc controller create --location "West US" --resource-group "TestRG" --resource-name "testcontroller"
```
##### <a name="ParametersControllerCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|
|**--location**|string|Location of the resource.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|

#### <a name="ControllerDelete">Command `az dnc controller delete`</a>

##### <a name="ExamplesControllerDelete">Example</a>
```
az dnc controller delete --resource-group "TestRG" --resource-name "testcontroller"
```
##### <a name="ParametersControllerDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|

### group `az dnc delegated-network`
#### <a name="DelegatedNetworkListByResourceGroup">Command `az dnc delegated-network list`</a>

##### <a name="ExamplesDelegatedNetworkListByResourceGroup">Example</a>
```
az dnc delegated-network list --resource-group "testRG"
```
##### <a name="ParametersDelegatedNetworkListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DelegatedNetworkListBySubscription">Command `az dnc delegated-network list`</a>

##### <a name="ExamplesDelegatedNetworkListBySubscription">Example</a>
```
az dnc delegated-network list
```
##### <a name="ParametersDelegatedNetworkListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az dnc delegated-subnet-service`
#### <a name="DelegatedSubnetServiceListByResourceGroup">Command `az dnc delegated-subnet-service list`</a>

##### <a name="ExamplesDelegatedSubnetServiceListByResourceGroup">Example</a>
```
az dnc delegated-subnet-service list --resource-group "testRG"
```
##### <a name="ParametersDelegatedSubnetServiceListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DelegatedSubnetServiceListBySubscription">Command `az dnc delegated-subnet-service list`</a>

##### <a name="ExamplesDelegatedSubnetServiceListBySubscription">Example</a>
```
az dnc delegated-subnet-service list
```
##### <a name="ParametersDelegatedSubnetServiceListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DelegatedSubnetServiceGetDetails">Command `az dnc delegated-subnet-service show`</a>

##### <a name="ExamplesDelegatedSubnetServiceGetDetails">Example</a>
```
az dnc delegated-subnet-service show --resource-group "TestRG" --resource-name "delegated1"
```
##### <a name="ParametersDelegatedSubnetServiceGetDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|

#### <a name="DelegatedSubnetServicePutDetails">Command `az dnc delegated-subnet-service create`</a>

##### <a name="ExamplesDelegatedSubnetServicePutDetails">Example</a>
```
az dnc delegated-subnet-service create --location "West US" --id "/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/r\
esourceGroups/TestRG/providers/Microsoft.DelegatedNetwork/controller/dnctestcontroller" --subnet-details-id \
"/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/resourceGroups/TestRG/providers/Microsoft.Network/virtualNetworks/\
testvnet/subnets/testsubnet" --resource-group "TestRG" --resource-name "delegated1"
```
##### <a name="ParametersDelegatedSubnetServicePutDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|
|**--location**|string|Location of the resource.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--id**|string|controller arm resource id|id|id|
|**--subnet-details-id**|string|subnet arm resource id|subnet_details_id|id|

#### <a name="DelegatedSubnetServiceDeleteDetails">Command `az dnc delegated-subnet-service delete`</a>

##### <a name="ExamplesDelegatedSubnetServiceDeleteDetails">Example</a>
```
az dnc delegated-subnet-service delete --resource-group "TestRG" --resource-name "delegated1"
```
##### <a name="ParametersDelegatedSubnetServiceDeleteDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|
|**--force-delete**|boolean|Force delete resource|force_delete|forceDelete|

### group `az dnc orchestrator-instance-service`
#### <a name="OrchestratorInstanceServiceListByResourceGroup">Command `az dnc orchestrator-instance-service list`</a>

##### <a name="ExamplesOrchestratorInstanceServiceListByResourceGroup">Example</a>
```
az dnc orchestrator-instance-service list --resource-group "testRG"
```
##### <a name="ParametersOrchestratorInstanceServiceListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="OrchestratorInstanceServiceListBySubscription">Command `az dnc orchestrator-instance-service list`</a>

##### <a name="ExamplesOrchestratorInstanceServiceListBySubscription">Example</a>
```
az dnc orchestrator-instance-service list
```
##### <a name="ParametersOrchestratorInstanceServiceListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="OrchestratorInstanceServiceGetDetails">Command `az dnc orchestrator-instance-service show`</a>

##### <a name="ExamplesOrchestratorInstanceServiceGetDetails">Example</a>
```
az dnc orchestrator-instance-service show --resource-group "TestRG" --resource-name "testk8s1"
```
##### <a name="ParametersOrchestratorInstanceServiceGetDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|

#### <a name="OrchestratorInstanceServiceCreate">Command `az dnc orchestrator-instance-service create`</a>

##### <a name="ExamplesOrchestratorInstanceServiceCreate">Example</a>
```
az dnc orchestrator-instance-service create --type "SystemAssigned" --location "West US" --api-server-endpoint \
"https://testk8s.cloudapp.net" --cluster-root-ca "ddsadsad344mfdsfdl" --id "/subscriptions/613192d7-503f-477a-9cfe-4efc\
3ee2bd60/resourceGroups/TestRG/providers/Microsoft.DelegatedNetwork/controller/testcontroller" --orchestrator-app-id \
"546192d7-503f-477a-9cfe-4efc3ee2b6e1" --orchestrator-tenant-id "da6192d7-503f-477a-9cfe-4efc3ee2b6c3" \
--priv-link-resource-id "/subscriptions/613192d7-503f-477a-9cfe-4efc3ee2bd60/resourceGroups/TestRG/providers/Microsoft.\
Network/privateLinkServices/plresource1" --resource-group "TestRG" --resource-name "testk8s1"
```
##### <a name="ParametersOrchestratorInstanceServiceCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|
|**--location**|string|Location of the resource.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--type**|sealed-choice|The type of identity used for orchestrator cluster. Type 'SystemAssigned' will use an implicitly created identity orchestrator clusters|type|type|
|**--orchestrator-app-id**|string|AAD ID used with apiserver|orchestrator_app_id|orchestratorAppId|
|**--orchestrator-tenant-id**|string|TenantID of server App ID|orchestrator_tenant_id|orchestratorTenantId|
|**--cluster-root-ca**|string|RootCA certificate of kubernetes cluster base64 encoded|cluster_root_ca|clusterRootCA|
|**--api-server-endpoint**|string|K8s APIServer url. Either one of apiServerEndpoint or privateLinkResourceId can be specified|api_server_endpoint|apiServerEndpoint|
|**--private-link-resource-id**|string|private link arm resource id. Either one of apiServerEndpoint or privateLinkResourceId can be specified|private_link_resource_id|privateLinkResourceId|
|**--id**|string|controller arm resource id|id|id|

#### <a name="OrchestratorInstanceServiceDelete">Command `az dnc orchestrator-instance-service delete`</a>

##### <a name="ExamplesOrchestratorInstanceServiceDelete">Example</a>
```
az dnc orchestrator-instance-service delete --resource-group "TestRG" --resource-name "k8stest1"
```
##### <a name="ParametersOrchestratorInstanceServiceDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource-name**|string|The name of the resource. It must be a minimum of 3 characters, and a maximum of 63.|resource_name|resourceName|
|**--force-delete**|boolean|Force delete resource|force_delete|forceDelete|
