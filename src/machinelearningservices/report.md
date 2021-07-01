# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az machinelearningservices|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az machinelearningservices` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az machinelearningservices workspace|Workspaces|[commands](#CommandsInWorkspaces)|
|az machinelearningservices workspace-feature|WorkspaceFeatures|[commands](#CommandsInWorkspaceFeatures)|
|az machinelearningservices usage|Usages|[commands](#CommandsInUsages)|
|az machinelearningservices virtual-machine-size|VirtualMachineSizes|[commands](#CommandsInVirtualMachineSizes)|
|az machinelearningservices quota|Quotas|[commands](#CommandsInQuotas)|
|az machinelearningservices machine-learning-compute|MachineLearningCompute|[commands](#CommandsInMachineLearningCompute)|
|az machinelearningservices workspace|Workspace|[commands](#CommandsInWorkspace)|
|az machinelearningservices private-endpoint-connection|PrivateEndpointConnections|[commands](#CommandsInPrivateEndpointConnections)|
|az machinelearningservices private-link-resource|PrivateLinkResources|[commands](#CommandsInPrivateLinkResources)|
|az machinelearningservices machine-learning-service|MachineLearningService|[commands](#CommandsInMachineLearningService)|
|az machinelearningservices notebook|Notebooks|[commands](#CommandsInNotebooks)|
|az machinelearningservices storage-account|StorageAccount|[commands](#CommandsInStorageAccount)|
|az machinelearningservices workspace-connection|WorkspaceConnections|[commands](#CommandsInWorkspaceConnections)|

## COMMANDS
### <a name="CommandsInMachineLearningCompute">Commands in `az machinelearningservices machine-learning-compute` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices machine-learning-compute list](#MachineLearningComputeListByWorkspace)|ListByWorkspace|[Parameters](#ParametersMachineLearningComputeListByWorkspace)|[Example](#ExamplesMachineLearningComputeListByWorkspace)|
|[az machinelearningservices machine-learning-compute show](#MachineLearningComputeGet)|Get|[Parameters](#ParametersMachineLearningComputeGet)|[Example](#ExamplesMachineLearningComputeGet)|
|[az machinelearningservices machine-learning-compute aks create](#MachineLearningComputeCreateOrUpdate#Create#AKS)|CreateOrUpdate#Create#AKS|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#AKS)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#AKS)|
|[az machinelearningservices machine-learning-compute aml-compute create](#MachineLearningComputeCreateOrUpdate#Create#AmlCompute)|CreateOrUpdate#Create#AmlCompute|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#AmlCompute)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#AmlCompute)|
|[az machinelearningservices machine-learning-compute compute-instance create](#MachineLearningComputeCreateOrUpdate#Create#ComputeInstance)|CreateOrUpdate#Create#ComputeInstance|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#ComputeInstance)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#ComputeInstance)|
|[az machinelearningservices machine-learning-compute data-factory create](#MachineLearningComputeCreateOrUpdate#Create#DataFactory)|CreateOrUpdate#Create#DataFactory|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#DataFactory)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#DataFactory)|
|[az machinelearningservices machine-learning-compute data-lake-analytics create](#MachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics)|CreateOrUpdate#Create#DataLakeAnalytics|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics)|
|[az machinelearningservices machine-learning-compute databricks create](#MachineLearningComputeCreateOrUpdate#Create#Databricks)|CreateOrUpdate#Create#Databricks|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#Databricks)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#Databricks)|
|[az machinelearningservices machine-learning-compute hd-insight create](#MachineLearningComputeCreateOrUpdate#Create#HDInsight)|CreateOrUpdate#Create#HDInsight|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#HDInsight)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#HDInsight)|
|[az machinelearningservices machine-learning-compute synapse-spark create](#MachineLearningComputeCreateOrUpdate#Create#SynapseSpark)|CreateOrUpdate#Create#SynapseSpark|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#SynapseSpark)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#SynapseSpark)|
|[az machinelearningservices machine-learning-compute virtual-machine create](#MachineLearningComputeCreateOrUpdate#Create#VirtualMachine)|CreateOrUpdate#Create#VirtualMachine|[Parameters](#ParametersMachineLearningComputeCreateOrUpdate#Create#VirtualMachine)|[Example](#ExamplesMachineLearningComputeCreateOrUpdate#Create#VirtualMachine)|
|[az machinelearningservices machine-learning-compute update](#MachineLearningComputeUpdate)|Update|[Parameters](#ParametersMachineLearningComputeUpdate)|[Example](#ExamplesMachineLearningComputeUpdate)|
|[az machinelearningservices machine-learning-compute delete](#MachineLearningComputeDelete)|Delete|[Parameters](#ParametersMachineLearningComputeDelete)|[Example](#ExamplesMachineLearningComputeDelete)|
|[az machinelearningservices machine-learning-compute list-key](#MachineLearningComputeListKeys)|ListKeys|[Parameters](#ParametersMachineLearningComputeListKeys)|[Example](#ExamplesMachineLearningComputeListKeys)|
|[az machinelearningservices machine-learning-compute list-node](#MachineLearningComputeListNodes)|ListNodes|[Parameters](#ParametersMachineLearningComputeListNodes)|[Example](#ExamplesMachineLearningComputeListNodes)|
|[az machinelearningservices machine-learning-compute restart](#MachineLearningComputeRestart)|Restart|[Parameters](#ParametersMachineLearningComputeRestart)|[Example](#ExamplesMachineLearningComputeRestart)|
|[az machinelearningservices machine-learning-compute start](#MachineLearningComputeStart)|Start|[Parameters](#ParametersMachineLearningComputeStart)|[Example](#ExamplesMachineLearningComputeStart)|
|[az machinelearningservices machine-learning-compute stop](#MachineLearningComputeStop)|Stop|[Parameters](#ParametersMachineLearningComputeStop)|[Example](#ExamplesMachineLearningComputeStop)|

### <a name="CommandsInMachineLearningService">Commands in `az machinelearningservices machine-learning-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices machine-learning-service list](#MachineLearningServiceListByWorkspace)|ListByWorkspace|[Parameters](#ParametersMachineLearningServiceListByWorkspace)|[Example](#ExamplesMachineLearningServiceListByWorkspace)|
|[az machinelearningservices machine-learning-service show](#MachineLearningServiceGet)|Get|[Parameters](#ParametersMachineLearningServiceGet)|[Example](#ExamplesMachineLearningServiceGet)|
|[az machinelearningservices machine-learning-service create](#MachineLearningServiceCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMachineLearningServiceCreateOrUpdate#Create)|[Example](#ExamplesMachineLearningServiceCreateOrUpdate#Create)|
|[az machinelearningservices machine-learning-service update](#MachineLearningServiceCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersMachineLearningServiceCreateOrUpdate#Update)|Not Found|
|[az machinelearningservices machine-learning-service delete](#MachineLearningServiceDelete)|Delete|[Parameters](#ParametersMachineLearningServiceDelete)|[Example](#ExamplesMachineLearningServiceDelete)|

### <a name="CommandsInNotebooks">Commands in `az machinelearningservices notebook` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices notebook list-key](#NotebooksListKeys)|ListKeys|[Parameters](#ParametersNotebooksListKeys)|[Example](#ExamplesNotebooksListKeys)|
|[az machinelearningservices notebook prepare](#NotebooksPrepare)|Prepare|[Parameters](#ParametersNotebooksPrepare)|[Example](#ExamplesNotebooksPrepare)|

### <a name="CommandsInPrivateEndpointConnections">Commands in `az machinelearningservices private-endpoint-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices private-endpoint-connection show](#PrivateEndpointConnectionsGet)|Get|[Parameters](#ParametersPrivateEndpointConnectionsGet)|[Example](#ExamplesPrivateEndpointConnectionsGet)|
|[az machinelearningservices private-endpoint-connection delete](#PrivateEndpointConnectionsDelete)|Delete|[Parameters](#ParametersPrivateEndpointConnectionsDelete)|[Example](#ExamplesPrivateEndpointConnectionsDelete)|
|[az machinelearningservices private-endpoint-connection put](#PrivateEndpointConnectionsPut)|Put|[Parameters](#ParametersPrivateEndpointConnectionsPut)|[Example](#ExamplesPrivateEndpointConnectionsPut)|

### <a name="CommandsInPrivateLinkResources">Commands in `az machinelearningservices private-link-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices private-link-resource list](#PrivateLinkResourcesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersPrivateLinkResourcesListByWorkspace)|[Example](#ExamplesPrivateLinkResourcesListByWorkspace)|

### <a name="CommandsInQuotas">Commands in `az machinelearningservices quota` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices quota list](#QuotasList)|List|[Parameters](#ParametersQuotasList)|[Example](#ExamplesQuotasList)|
|[az machinelearningservices quota update](#QuotasUpdate)|Update|[Parameters](#ParametersQuotasUpdate)|[Example](#ExamplesQuotasUpdate)|

### <a name="CommandsInStorageAccount">Commands in `az machinelearningservices storage-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices storage-account list-key](#StorageAccountListKeys)|ListKeys|[Parameters](#ParametersStorageAccountListKeys)|[Example](#ExamplesStorageAccountListKeys)|

### <a name="CommandsInUsages">Commands in `az machinelearningservices usage` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices usage list](#UsagesList)|List|[Parameters](#ParametersUsagesList)|[Example](#ExamplesUsagesList)|

### <a name="CommandsInVirtualMachineSizes">Commands in `az machinelearningservices virtual-machine-size` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices virtual-machine-size list](#VirtualMachineSizesList)|List|[Parameters](#ParametersVirtualMachineSizesList)|[Example](#ExamplesVirtualMachineSizesList)|

### <a name="CommandsInWorkspaces">Commands in `az machinelearningservices workspace` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices workspace list](#WorkspacesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersWorkspacesListByResourceGroup)|[Example](#ExamplesWorkspacesListByResourceGroup)|
|[az machinelearningservices workspace list](#WorkspacesListBySubscription)|ListBySubscription|[Parameters](#ParametersWorkspacesListBySubscription)|[Example](#ExamplesWorkspacesListBySubscription)|
|[az machinelearningservices workspace show](#WorkspacesGet)|Get|[Parameters](#ParametersWorkspacesGet)|[Example](#ExamplesWorkspacesGet)|
|[az machinelearningservices workspace create](#WorkspacesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersWorkspacesCreateOrUpdate#Create)|[Example](#ExamplesWorkspacesCreateOrUpdate#Create)|
|[az machinelearningservices workspace update](#WorkspacesUpdate)|Update|[Parameters](#ParametersWorkspacesUpdate)|[Example](#ExamplesWorkspacesUpdate)|
|[az machinelearningservices workspace delete](#WorkspacesDelete)|Delete|[Parameters](#ParametersWorkspacesDelete)|[Example](#ExamplesWorkspacesDelete)|
|[az machinelearningservices workspace list-key](#WorkspacesListKeys)|ListKeys|[Parameters](#ParametersWorkspacesListKeys)|[Example](#ExamplesWorkspacesListKeys)|
|[az machinelearningservices workspace list-notebook-access-token](#WorkspacesListNotebookAccessToken)|ListNotebookAccessToken|[Parameters](#ParametersWorkspacesListNotebookAccessToken)|[Example](#ExamplesWorkspacesListNotebookAccessToken)|
|[az machinelearningservices workspace resync-key](#WorkspacesResyncKeys)|ResyncKeys|[Parameters](#ParametersWorkspacesResyncKeys)|[Example](#ExamplesWorkspacesResyncKeys)|

### <a name="CommandsInWorkspace">Commands in `az machinelearningservices workspace` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices workspace list-sku](#WorkspaceListSkus)|ListSkus|[Parameters](#ParametersWorkspaceListSkus)|[Example](#ExamplesWorkspaceListSkus)|

### <a name="CommandsInWorkspaceConnections">Commands in `az machinelearningservices workspace-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices workspace-connection list](#WorkspaceConnectionsList)|List|[Parameters](#ParametersWorkspaceConnectionsList)|[Example](#ExamplesWorkspaceConnectionsList)|
|[az machinelearningservices workspace-connection show](#WorkspaceConnectionsGet)|Get|[Parameters](#ParametersWorkspaceConnectionsGet)|[Example](#ExamplesWorkspaceConnectionsGet)|
|[az machinelearningservices workspace-connection create](#WorkspaceConnectionsCreate)|Create|[Parameters](#ParametersWorkspaceConnectionsCreate)|[Example](#ExamplesWorkspaceConnectionsCreate)|
|[az machinelearningservices workspace-connection delete](#WorkspaceConnectionsDelete)|Delete|[Parameters](#ParametersWorkspaceConnectionsDelete)|[Example](#ExamplesWorkspaceConnectionsDelete)|

### <a name="CommandsInWorkspaceFeatures">Commands in `az machinelearningservices workspace-feature` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az machinelearningservices workspace-feature list](#WorkspaceFeaturesList)|List|[Parameters](#ParametersWorkspaceFeaturesList)|[Example](#ExamplesWorkspaceFeaturesList)|


## COMMAND DETAILS

### group `az machinelearningservices machine-learning-compute`
#### <a name="MachineLearningComputeListByWorkspace">Command `az machinelearningservices machine-learning-compute list`</a>

##### <a name="ExamplesMachineLearningComputeListByWorkspace">Example</a>
```
az machinelearningservices machine-learning-compute list --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--skip**|string|Continuation token for pagination.|skip|$skip|

#### <a name="MachineLearningComputeGet">Command `az machinelearningservices machine-learning-compute show`</a>

##### <a name="ExamplesMachineLearningComputeGet">Example</a>
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeGet">Example</a>
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeGet">Example</a>
```
az machinelearningservices machine-learning-compute show --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#AKS">Command `az machinelearningservices machine-learning-compute aks create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AKS">Example</a>
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AKS">Example</a>
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
--ak-s-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remoteLogin\
PortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdleTimeBe\
foreScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-000000000000\
/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/versions/\
0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AKS">Example</a>
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AKS">Example</a>
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
--ak-s-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"personal\\"\
,\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-000000000000\\",\
\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\\"},\\\
"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AKS">Example</a>
```
az machinelearningservices machine-learning-compute aks create --compute-name "compute123" --location "eastus" \
--ak-s-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#AKS">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--ak-s-compute-location**|string|Location for the underlying compute|ak_s_compute_location|computeLocation|
|**--ak-s-description**|string|The description of the Machine Learning compute.|ak_s_description|description|
|**--ak-s-resource-id**|string|ARM resource id of the underlying compute|ak_s_resource_id|resourceId|
|**--ak-s-disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|ak_s_disable_local_auth|disableLocalAuth|
|**--ak-s-properties**|object|AKS properties|ak_s_properties|properties|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#AmlCompute">Command `az machinelearningservices machine-learning-compute aml-compute create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AmlCompute">Example</a>
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AmlCompute">Example</a>
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
--aml-compute-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\\",\\"remo\
teLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0,\\"nodeIdl\
eTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000-0000-00000\
0000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDefinition/ve\
rsions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AmlCompute">Example</a>
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AmlCompute">Example</a>
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
--aml-compute-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\\":\\"pers\
onal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000-0000000000\
00\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\\"Disabled\
\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#AmlCompute">Example</a>
```
az machinelearningservices machine-learning-compute aml-compute create --compute-name "compute123" --location "eastus" \
--aml-compute-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" --workspace-name \
"workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#AmlCompute">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|aml_compute_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|aml_compute_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|aml_compute_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|aml_compute_disable_local_auth|disableLocalAuth|
|**--aml-compute-properties**|object|AML Compute properties|aml_compute_properties|properties|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Command `az machinelearningservices machine-learning-compute compute-instance create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Example</a>
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Example</a>
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" --location \
"eastus" --compute-instance-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Wind\
ows\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\\
":0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0\
000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImag\
eDefinition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group \
"testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Example</a>
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Example</a>
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" --location \
"eastus" --compute-instance-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationT\
ype\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0\
000-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\\
":\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group \
"testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Example</a>
```
az machinelearningservices machine-learning-compute compute-instance create --compute-name "compute123" --location \
"eastus" --compute-instance-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#ComputeInstance">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|compute_instance_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|compute_instance_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|compute_instance_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|compute_instance_disable_local_auth|disableLocalAuth|
|**--compute-instance-properties**|object|Compute Instance properties|compute_instance_properties|properties|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#DataFactory">Command `az machinelearningservices machine-learning-compute data-factory create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataFactory">Example</a>
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataFactory">Example</a>
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataFactory">Example</a>
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataFactory">Example</a>
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataFactory">Example</a>
```
az machinelearningservices machine-learning-compute data-factory create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#DataFactory">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|data_factory_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|data_factory_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|data_factory_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|data_factory_disable_local_auth|disableLocalAuth|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Command `az machinelearningservices machine-learning-compute data-lake-analytics create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Example</a>
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Example</a>
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Example</a>
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Example</a>
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Example</a>
```
az machinelearningservices machine-learning-compute data-lake-analytics create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#DataLakeAnalytics">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|data_lake_analytics_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|data_lake_analytics_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|data_lake_analytics_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|data_lake_analytics_disable_local_auth|disableLocalAuth|
|**--data-lake-store-account-name**|string|DataLake Store Account Name|data_lake_analytics_data_lake_store_account_name|dataLakeStoreAccountName|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#Databricks">Command `az machinelearningservices machine-learning-compute databricks create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#Databricks">Example</a>
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#Databricks">Example</a>
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#Databricks">Example</a>
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#Databricks">Example</a>
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#Databricks">Example</a>
```
az machinelearningservices machine-learning-compute databricks create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#Databricks">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|databricks_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|databricks_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|databricks_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|databricks_disable_local_auth|disableLocalAuth|
|**--databricks-access-token**|string|Databricks access token|databricks_databricks_access_token|databricksAccessToken|
|**--workspace-url**|string|Workspace Url|databricks_workspace_url|workspaceUrl|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#HDInsight">Command `az machinelearningservices machine-learning-compute hd-insight create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#HDInsight">Example</a>
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#HDInsight">Example</a>
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#HDInsight">Example</a>
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#HDInsight">Example</a>
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#HDInsight">Example</a>
```
az machinelearningservices machine-learning-compute hd-insight create --compute-name "compute123" --location "eastus" \
--resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#HDInsight">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|hd_insight_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|hd_insight_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|hd_insight_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|hd_insight_disable_local_auth|disableLocalAuth|
|**--ssh-port**|integer|Port open for ssh connections on the master node of the cluster.|hd_insight_ssh_port|sshPort|
|**--address**|string|Public IP address of the master node of the cluster.|hd_insight_address|address|
|**--administrator-account**|object|Admin credentials for master node of the cluster|hd_insight_administrator_account|administratorAccount|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Command `az machinelearningservices machine-learning-compute synapse-spark create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Example</a>
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Example</a>
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" --location \
"eastus" --synapse-spark-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windows\
\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\":0\
,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-0000\
-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImageDe\
finition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group \
"testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Example</a>
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Example</a>
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" --location \
"eastus" --synapse-spark-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationType\
\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-0000\
-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\":\
\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group \
"testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Example</a>
```
az machinelearningservices machine-learning-compute synapse-spark create --compute-name "compute123" --location \
"eastus" --synapse-spark-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" --workspace-name \
"workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#SynapseSpark">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|synapse_spark_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|synapse_spark_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|synapse_spark_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|synapse_spark_disable_local_auth|disableLocalAuth|
|**--synapse-spark-properties**|object|AKS properties|synapse_spark_properties|properties|

#### <a name="MachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Command `az machinelearningservices machine-learning-compute virtual-machine create`</a>

##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Example</a>
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Example</a>
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" --location \
"eastus" --virtual-machine-properties "{\\"enableNodePublicIp\\":true,\\"isolatedNetwork\\":false,\\"osType\\":\\"Windo\
ws\\",\\"remoteLoginPortPublicAccess\\":\\"NotSpecified\\",\\"scaleSettings\\":{\\"maxNodeCount\\":1,\\"minNodeCount\\"\
:0,\\"nodeIdleTimeBeforeScaleDown\\":\\"PT5M\\"},\\"virtualMachineImage\\":{\\"id\\":\\"/subscriptions/00000000-0000-00\
00-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/galleries/myImageGallery/images/myImage\
Definition/versions/0.0.1\\"},\\"vmPriority\\":\\"Dedicated\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group \
"testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Example</a>
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" --location \
"eastus" --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Example</a>
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" --location \
"eastus" --virtual-machine-properties "{\\"applicationSharingPolicy\\":\\"Personal\\",\\"computeInstanceAuthorizationTy\
pe\\":\\"personal\\",\\"personalComputeInstanceSettings\\":{\\"assignedUser\\":{\\"objectId\\":\\"00000000-0000-0000-00\
00-000000000000\\",\\"tenantId\\":\\"00000000-0000-0000-0000-000000000000\\"}},\\"sshSettings\\":{\\"sshPublicAccess\\"\
:\\"Disabled\\"},\\"subnet\\":\\"test-subnet-resource-id\\",\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group \
"testrg123" --workspace-name "workspaces123"
```
##### <a name="ExamplesMachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Example</a>
```
az machinelearningservices machine-learning-compute virtual-machine create --compute-name "compute123" --location \
"eastus" --virtual-machine-properties "{\\"vmSize\\":\\"STANDARD_NC6\\"}" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeCreateOrUpdate#Create#VirtualMachine">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|virtual_machine_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|virtual_machine_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|virtual_machine_resource_id|resourceId|
|**--disable-local-auth**|boolean|Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication.|virtual_machine_disable_local_auth|disableLocalAuth|
|**--virtual-machine-properties**|object||virtual_machine_properties|properties|

#### <a name="MachineLearningComputeUpdate">Command `az machinelearningservices machine-learning-compute update`</a>

##### <a name="ExamplesMachineLearningComputeUpdate">Example</a>
```
az machinelearningservices machine-learning-compute update --compute-name "compute123" --scale-settings \
max-node-count=4 min-node-count=4 node-idle-time-before-scale-down="PT5M" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--scale-settings**|object|Desired scale settings for the amlCompute.|scale_settings|scaleSettings|

#### <a name="MachineLearningComputeDelete">Command `az machinelearningservices machine-learning-compute delete`</a>

##### <a name="ExamplesMachineLearningComputeDelete">Example</a>
```
az machinelearningservices machine-learning-compute delete --compute-name "compute123" --resource-group "testrg123" \
--underlying-resource-action "Delete" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--underlying-resource-action**|choice|Delete the underlying compute if 'Delete', or detach the underlying compute from workspace if 'Detach'.|underlying_resource_action|underlyingResourceAction|

#### <a name="MachineLearningComputeListKeys">Command `az machinelearningservices machine-learning-compute list-key`</a>

##### <a name="ExamplesMachineLearningComputeListKeys">Example</a>
```
az machinelearningservices machine-learning-compute list-key --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

#### <a name="MachineLearningComputeListNodes">Command `az machinelearningservices machine-learning-compute list-node`</a>

##### <a name="ExamplesMachineLearningComputeListNodes">Example</a>
```
az machinelearningservices machine-learning-compute list-node --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeListNodes">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

#### <a name="MachineLearningComputeRestart">Command `az machinelearningservices machine-learning-compute restart`</a>

##### <a name="ExamplesMachineLearningComputeRestart">Example</a>
```
az machinelearningservices machine-learning-compute restart --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

#### <a name="MachineLearningComputeStart">Command `az machinelearningservices machine-learning-compute start`</a>

##### <a name="ExamplesMachineLearningComputeStart">Example</a>
```
az machinelearningservices machine-learning-compute start --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

#### <a name="MachineLearningComputeStop">Command `az machinelearningservices machine-learning-compute stop`</a>

##### <a name="ExamplesMachineLearningComputeStop">Example</a>
```
az machinelearningservices machine-learning-compute stop --compute-name "compute123" --resource-group "testrg123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningComputeStop">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### group `az machinelearningservices machine-learning-service`
#### <a name="MachineLearningServiceListByWorkspace">Command `az machinelearningservices machine-learning-service list`</a>

##### <a name="ExamplesMachineLearningServiceListByWorkspace">Example</a>
```
az machinelearningservices machine-learning-service list --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningServiceListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--skip**|string|Continuation token for pagination.|skip|$skip|
|**--model-id**|string|The Model Id.|model_id|modelId|
|**--model-name**|string|The Model name.|model_name|modelName|
|**--tag**|string|The object tag.|tag|tag|
|**--tags**|string|A set of tags with which to filter the returned services. It is a comma separated string of tags key or tags key=value Example: tagKey1,tagKey2,tagKey3=value3 .|tags|tags|
|**--properties**|string|A set of properties with which to filter the returned services. It is a comma separated string of properties key and/or properties key=value Example: propKey1,propKey2,propKey3=value3 .|properties|properties|
|**--run-id**|string|runId for model associated with service.|run_id|runId|
|**--expand**|boolean|Set to True to include Model details.|expand|expand|
|**--orderby**|choice|The option to order the response.|orderby|orderby|

#### <a name="MachineLearningServiceGet">Command `az machinelearningservices machine-learning-service show`</a>

##### <a name="ExamplesMachineLearningServiceGet">Example</a>
```
az machinelearningservices machine-learning-service show --resource-group "testrg123" --service-name "service123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningServiceGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--service-name**|string|Name of the Azure Machine Learning service.|service_name|serviceName|
|**--expand**|boolean|Set to True to include Model details.|expand|expand|

#### <a name="MachineLearningServiceCreateOrUpdate#Create">Command `az machinelearningservices machine-learning-service create`</a>

##### <a name="ExamplesMachineLearningServiceCreateOrUpdate#Create">Example</a>
```
az machinelearningservices machine-learning-service create --properties "{\\"appInsightsEnabled\\":true,\\"authEnabled\
\\":true,\\"computeType\\":\\"ACI\\",\\"containerResourceRequirements\\":{\\"cpu\\":1,\\"memoryInGB\\":1},\\"environmen\
tImageRequest\\":{\\"assets\\":[{\\"id\\":null,\\"mimeType\\":\\"application/x-python\\",\\"unpack\\":false,\\"url\\":\
\\"aml://storage/azureml/score.py\\"}],\\"driverProgram\\":\\"score.py\\",\\"environment\\":{\\"name\\":\\"AzureML-Scik\
it-learn-0.20.3\\",\\"docker\\":{\\"baseDockerfile\\":null,\\"baseImage\\":\\"mcr.microsoft.com/azureml/base:openmpi3.1\
.2-ubuntu16.04\\",\\"baseImageRegistry\\":{\\"address\\":null,\\"password\\":null,\\"username\\":null}},\\"environmentV\
ariables\\":{\\"EXAMPLE_ENV_VAR\\":\\"EXAMPLE_VALUE\\"},\\"inferencingStackVersion\\":null,\\"python\\":{\\"baseCondaEn\
vironment\\":null,\\"condaDependencies\\":{\\"name\\":\\"azureml_ae1acbe6e1e6aabbad900b53c491a17c\\",\\"channels\\":[\\\
"conda-forge\\"],\\"dependencies\\":[\\"python=3.6.2\\",{\\"pip\\":[\\"azureml-core==1.0.69\\",\\"azureml-defaults==1.0\
.69\\",\\"azureml-telemetry==1.0.69\\",\\"azureml-train-restclients-hyperdrive==1.0.69\\",\\"azureml-train-core==1.0.69\
\\",\\"scikit-learn==0.20.3\\",\\"scipy==1.2.1\\",\\"numpy==1.16.2\\",\\"joblib==0.13.2\\"]}]},\\"interpreterPath\\":\\\
"python\\",\\"userManagedDependencies\\":false},\\"spark\\":{\\"packages\\":[],\\"precachePackages\\":true,\\"repositor\
ies\\":[]},\\"version\\":\\"3\\"},\\"models\\":[{\\"name\\":\\"sklearn_regression_model.pkl\\",\\"mimeType\\":\\"applic\
ation/x-python\\",\\"url\\":\\"aml://storage/azureml/sklearn_regression_model.pkl\\"}]},\\"location\\":\\"eastus2\\"}" \
--resource-group "testrg123" --service-name "service456" --workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningServiceCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--service-name**|string|Name of the Azure Machine Learning service.|service_name|serviceName|
|**--properties**|object|The payload that is used to create or update the Service.|properties|properties|

#### <a name="MachineLearningServiceCreateOrUpdate#Update">Command `az machinelearningservices machine-learning-service update`</a>

##### <a name="ParametersMachineLearningServiceCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--service-name**|string|Name of the Azure Machine Learning service.|service_name|serviceName|
|**--properties**|object|The payload that is used to create or update the Service.|properties|properties|

#### <a name="MachineLearningServiceDelete">Command `az machinelearningservices machine-learning-service delete`</a>

##### <a name="ExamplesMachineLearningServiceDelete">Example</a>
```
az machinelearningservices machine-learning-service delete --resource-group "testrg123" --service-name "service123" \
--workspace-name "workspaces123"
```
##### <a name="ParametersMachineLearningServiceDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--service-name**|string|Name of the Azure Machine Learning service.|service_name|serviceName|

### group `az machinelearningservices notebook`
#### <a name="NotebooksListKeys">Command `az machinelearningservices notebook list-key`</a>

##### <a name="ExamplesNotebooksListKeys">Example</a>
```
az machinelearningservices notebook list-key --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersNotebooksListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

#### <a name="NotebooksPrepare">Command `az machinelearningservices notebook prepare`</a>

##### <a name="ExamplesNotebooksPrepare">Example</a>
```
az machinelearningservices notebook prepare --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersNotebooksPrepare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### group `az machinelearningservices private-endpoint-connection`
#### <a name="PrivateEndpointConnectionsGet">Command `az machinelearningservices private-endpoint-connection show`</a>

##### <a name="ExamplesPrivateEndpointConnectionsGet">Example</a>
```
az machinelearningservices private-endpoint-connection show --name "{privateEndpointConnectionName}" --resource-group \
"rg-1234" --workspace-name "testworkspace"
```
##### <a name="ParametersPrivateEndpointConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsDelete">Command `az machinelearningservices private-endpoint-connection delete`</a>

##### <a name="ExamplesPrivateEndpointConnectionsDelete">Example</a>
```
az machinelearningservices private-endpoint-connection delete --name "{privateEndpointConnectionName}" \
--resource-group "rg-1234" --workspace-name "testworkspace"
```
##### <a name="ParametersPrivateEndpointConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsPut">Command `az machinelearningservices private-endpoint-connection put`</a>

##### <a name="ExamplesPrivateEndpointConnectionsPut">Example</a>
```
az machinelearningservices private-endpoint-connection put --name "{privateEndpointConnectionName}" \
--private-link-service-connection-state description="Auto-Approved" status="Approved" --resource-group "rg-1234" \
--workspace-name "testworkspace"
```
##### <a name="ParametersPrivateEndpointConnectionsPut">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|privateEndpointConnectionName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

### group `az machinelearningservices private-link-resource`
#### <a name="PrivateLinkResourcesListByWorkspace">Command `az machinelearningservices private-link-resource list`</a>

##### <a name="ExamplesPrivateLinkResourcesListByWorkspace">Example</a>
```
az machinelearningservices private-link-resource list --resource-group "rg-1234" --workspace-name "testworkspace"
```
##### <a name="ParametersPrivateLinkResourcesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### group `az machinelearningservices quota`
#### <a name="QuotasList">Command `az machinelearningservices quota list`</a>

##### <a name="ExamplesQuotasList">Example</a>
```
az machinelearningservices quota list --location "eastus"
```
##### <a name="ParametersQuotasList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location for which resource usage is queried.|location|location|

#### <a name="QuotasUpdate">Command `az machinelearningservices quota update`</a>

##### <a name="ExamplesQuotasUpdate">Example</a>
```
az machinelearningservices quota update --location "eastus" --value type="Microsoft.MachineLearningServices/workspaces/\
quotas" id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.MachineLearningSe\
rvices/workspaces/demo_workspace1/quotas/Standard_DSv2_Family_Cluster_Dedicated_vCPUs" limit=100 unit="Count" --value \
type="Microsoft.MachineLearningServices/workspaces/quotas" id="/subscriptions/00000000-0000-0000-0000-000000000000/reso\
urceGroups/rg/providers/Microsoft.MachineLearningServices/workspaces/demo_workspace2/quotas/Standard_DSv2_Family_Cluste\
r_Dedicated_vCPUs" limit=200 unit="Count"
```
##### <a name="ParametersQuotasUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location for update quota is queried.|location|location|
|**--value**|array|The list for update quota.|value|value|
|**--quota-update-parameters-location**|string|Region of workspace quota to be updated.|quota_update_parameters_location|location|

### group `az machinelearningservices storage-account`
#### <a name="StorageAccountListKeys">Command `az machinelearningservices storage-account list-key`</a>

##### <a name="ExamplesStorageAccountListKeys">Example</a>
```
az machinelearningservices storage-account list-key --resource-group "testrg123" --workspace-name "workspaces123"
```
##### <a name="ParametersStorageAccountListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### group `az machinelearningservices usage`
#### <a name="UsagesList">Command `az machinelearningservices usage list`</a>

##### <a name="ExamplesUsagesList">Example</a>
```
az machinelearningservices usage list --location "eastus"
```
##### <a name="ParametersUsagesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location for which resource usage is queried.|location|location|

### group `az machinelearningservices virtual-machine-size`
#### <a name="VirtualMachineSizesList">Command `az machinelearningservices virtual-machine-size list`</a>

##### <a name="ExamplesVirtualMachineSizesList">Example</a>
```
az machinelearningservices virtual-machine-size list --location "eastus"
```
##### <a name="ParametersVirtualMachineSizesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location upon which virtual-machine-sizes is queried.|location|location|

### group `az machinelearningservices workspace`
#### <a name="WorkspacesListByResourceGroup">Command `az machinelearningservices workspace list`</a>

##### <a name="ExamplesWorkspacesListByResourceGroup">Example</a>
```
az machinelearningservices workspace list --resource-group "workspace-1234"
```
##### <a name="ParametersWorkspacesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--skip**|string|Continuation token for pagination.|skip|$skip|

#### <a name="WorkspacesListBySubscription">Command `az machinelearningservices workspace list`</a>

##### <a name="ExamplesWorkspacesListBySubscription">Example</a>
```
az machinelearningservices workspace list
```
##### <a name="ParametersWorkspacesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="WorkspacesGet">Command `az machinelearningservices workspace show`</a>

##### <a name="ExamplesWorkspacesGet">Example</a>
```
az machinelearningservices workspace show --resource-group "workspace-1234" --name "testworkspace"
```
##### <a name="ParametersWorkspacesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

#### <a name="WorkspacesCreateOrUpdate#Create">Command `az machinelearningservices workspace create`</a>

##### <a name="ExamplesWorkspacesCreateOrUpdate#Create">Example</a>
```
az machinelearningservices workspace create --identity type="SystemAssigned,UserAssigned" \
userAssignedIdentities={"/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Mi\
crosoft.ManagedIdentity/userAssignedIdentities/testuai":{}} --location "eastus2euap" --description "test description" \
--application-insights "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/mic\
rosoft.insights/components/testinsights" --container-registry "/subscriptions/00000000-1111-2222-3333-444444444444/reso\
urceGroups/workspace-1234/providers/Microsoft.ContainerRegistry/registries/testRegistry" --identity \
user-assigned-identity="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Mic\
rosoft.ManagedIdentity/userAssignedIdentities/testuai" --key-vault-properties identity-client-id="" \
key-identifier="https://testkv.vault.azure.net/keys/testkey/aabbccddee112233445566778899aabb" \
key-vault-arm-id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft\
.KeyVault/vaults/testkv" --status "Enabled" --friendly-name "HelloName" --hbi-workspace false --key-vault \
"/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.KeyVault/vaults/\
testkv" --shared-private-link-resources name="testdbresource" private-link-resource-id="/subscriptions/00000000-1111-22\
22-3333-444444444444/resourceGroups/workspace-1234/providers/Microsoft.DocumentDB/databaseAccounts/testdbresource/priva\
teLinkResources/Sql" group-id="Sql" request-message="Please approve" status="Approved" --storage-account \
"/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/accountcrud-1234/providers/Microsoft.Storage/storag\
eAccounts/testStorageAccount" --resource-group "workspace-1234" --name "testworkspace"
```
##### <a name="ParametersWorkspacesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|
|**--description**|string|The description of this workspace.|description|description|
|**--friendly-name**|string|The friendly name for this workspace. This name in mutable|friendly_name|friendlyName|
|**--key-vault**|string|ARM id of the key vault associated with this workspace. This cannot be changed once the workspace has been created|key_vault|keyVault|
|**--application-insights**|string|ARM id of the application insights associated with this workspace. This cannot be changed once the workspace has been created|application_insights|applicationInsights|
|**--container-registry**|string|ARM id of the container registry associated with this workspace. This cannot be changed once the workspace has been created|container_registry|containerRegistry|
|**--storage-account**|string|ARM id of the storage account associated with this workspace. This cannot be changed once the workspace has been created|storage_account|storageAccount|
|**--discovery-url**|string|Url for the discovery service to identify regional endpoints for machine learning experimentation services|discovery_url|discoveryUrl|
|**--hbi-workspace**|boolean|The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service|hbi_workspace|hbiWorkspace|
|**--image-build-compute**|string|The compute name for image build|image_build_compute|imageBuildCompute|
|**--allow-public-access-when-behind-vnet**|boolean|The flag to indicate whether to allow public access when behind VNet.|allow_public_access_when_behind_vnet|allowPublicAccessWhenBehindVnet|
|**--shared-private-link-resources**|array|The list of shared private link resources in this workspace.|shared_private_link_resources|sharedPrivateLinkResources|
|**--primary-user-assigned-identity**|string|The user assigned identity resource id that represents the workspace identity.|primary_user_assigned_identity|primaryUserAssignedIdentity|
|**--collections-throughput**|integer|The throughput of the collections in cosmosdb database|collections_throughput|collectionsThroughput|
|**--status**|choice|Indicates whether or not the encryption is enabled for the workspace.|status|status|
|**--identity**|object|The identity that will be used to access the key vault for encryption at rest.|identity|identity|
|**--key-vault-properties**|object|Customer Key vault properties.|key_vault_properties|keyVaultProperties|

#### <a name="WorkspacesUpdate">Command `az machinelearningservices workspace update`</a>

##### <a name="ExamplesWorkspacesUpdate">Example</a>
```
az machinelearningservices workspace update --description "new description" --friendly-name "New friendly name" \
--resource-group "workspace-1234" --name "testworkspace"
```
##### <a name="ParametersWorkspacesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--tags**|dictionary|The resource tags for the machine learning workspace.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--description**|string|The description of this workspace.|description|description|
|**--friendly-name**|string|The friendly name for this workspace.|friendly_name|friendlyName|
|**--image-build-compute**|string|The compute name for image build|image_build_compute|imageBuildCompute|
|**--primary-user-assigned-identity**|string|The user assigned identity resource id that represents the workspace identity.|primary_user_assigned_identity|primaryUserAssignedIdentity|
|**--collections-throughput**|integer|The throughput of the collections in cosmosdb database|collections_throughput|collectionsThroughput|
|**--type**|sealed-choice|The identity type.|type|type|
|**--user-assigned-identities**|dictionary|The user assigned identities associated with the resource.|user_assigned_identities|userAssignedIdentities|

#### <a name="WorkspacesDelete">Command `az machinelearningservices workspace delete`</a>

##### <a name="ExamplesWorkspacesDelete">Example</a>
```
az machinelearningservices workspace delete --resource-group "workspace-1234" --name "testworkspace"
```
##### <a name="ParametersWorkspacesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

#### <a name="WorkspacesListKeys">Command `az machinelearningservices workspace list-key`</a>

##### <a name="ExamplesWorkspacesListKeys">Example</a>
```
az machinelearningservices workspace list-key --resource-group "testrg123" --name "workspaces123"
```
##### <a name="ParametersWorkspacesListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

#### <a name="WorkspacesListNotebookAccessToken">Command `az machinelearningservices workspace list-notebook-access-token`</a>

##### <a name="ExamplesWorkspacesListNotebookAccessToken">Example</a>
```
az machinelearningservices workspace list-notebook-access-token --resource-group "workspace-1234" --name \
"testworkspace"
```
##### <a name="ParametersWorkspacesListNotebookAccessToken">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

#### <a name="WorkspacesResyncKeys">Command `az machinelearningservices workspace resync-key`</a>

##### <a name="ExamplesWorkspacesResyncKeys">Example</a>
```
az machinelearningservices workspace resync-key --resource-group "testrg123" --name "workspaces123"
```
##### <a name="ParametersWorkspacesResyncKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### group `az machinelearningservices workspace`
#### <a name="WorkspaceListSkus">Command `az machinelearningservices workspace list-sku`</a>

##### <a name="ExamplesWorkspaceListSkus">Example</a>
```
az machinelearningservices workspace list-sku
```
##### <a name="ParametersWorkspaceListSkus">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az machinelearningservices workspace-connection`
#### <a name="WorkspaceConnectionsList">Command `az machinelearningservices workspace-connection list`</a>

##### <a name="ExamplesWorkspaceConnectionsList">Example</a>
```
az machinelearningservices workspace-connection list --category "ACR" --resource-group "resourceGroup-1" --target \
"www.facebook.com" --workspace-name "workspace-1"
```
##### <a name="ParametersWorkspaceConnectionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--target**|string|Target of the workspace connection.|target|target|
|**--category**|string|Category of the workspace connection.|category|category|

#### <a name="WorkspaceConnectionsGet">Command `az machinelearningservices workspace-connection show`</a>

##### <a name="ExamplesWorkspaceConnectionsGet">Example</a>
```
az machinelearningservices workspace-connection show --connection-name "connection-1" --resource-group \
"resourceGroup-1" --workspace-name "workspace-1"
```
##### <a name="ParametersWorkspaceConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--connection-name**|string|Friendly name of the workspace connection|connection_name|connectionName|

#### <a name="WorkspaceConnectionsCreate">Command `az machinelearningservices workspace-connection create`</a>

##### <a name="ExamplesWorkspaceConnectionsCreate">Example</a>
```
az machinelearningservices workspace-connection create --connection-name "connection-1" --name "connection-1" \
--auth-type "PAT" --category "ACR" --target "www.facebook.com" --value "secrets" --resource-group "resourceGroup-1" \
--workspace-name "workspace-1"
```
##### <a name="ParametersWorkspaceConnectionsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--connection-name**|string|Friendly name of the workspace connection|connection_name|connectionName|
|**--name**|string|Friendly name of the workspace connection|name|name|
|**--category**|string|Category of the workspace connection.|category|category|
|**--target**|string|Target of the workspace connection.|target|target|
|**--auth-type**|string|Authorization type of the workspace connection.|auth_type|authType|
|**--value**|string|Value details of the workspace connection.|value|value|

#### <a name="WorkspaceConnectionsDelete">Command `az machinelearningservices workspace-connection delete`</a>

##### <a name="ExamplesWorkspaceConnectionsDelete">Example</a>
```
az machinelearningservices workspace-connection delete --connection-name "connection-1" --resource-group \
"resourceGroup-1" --workspace-name "workspace-1"
```
##### <a name="ParametersWorkspaceConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--connection-name**|string|Friendly name of the workspace connection|connection_name|connectionName|

### group `az machinelearningservices workspace-feature`
#### <a name="WorkspaceFeaturesList">Command `az machinelearningservices workspace-feature list`</a>

##### <a name="ExamplesWorkspaceFeaturesList">Example</a>
```
az machinelearningservices workspace-feature list --resource-group "myResourceGroup" --workspace-name "testworkspace"
```
##### <a name="ParametersWorkspaceFeaturesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
