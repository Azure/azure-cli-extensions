# Azure CLI Module Creation Report

### machinelearningservices  list-sku

list-sku a machinelearningservices .

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices ||

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-sku|ListSkus|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### machinelearningservices machine-learning-compute aks create

aks create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|aks create|CreateOrUpdate#Create#AKS|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|ak_s_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|ak_s_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|ak_s_resource_id|resourceId|
|**--properties-properties**|object|AKS properties|ak_s_properties|properties|

### machinelearningservices machine-learning-compute aml-compute create

aml-compute create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|aml-compute create|CreateOrUpdate#Create#AmlCompute|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|aml_compute_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|aml_compute_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|aml_compute_resource_id|resourceId|
|**--properties-properties**|object|AML Compute properties|aml_compute_properties|properties|

### machinelearningservices machine-learning-compute compute-instance create

compute-instance create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|compute-instance create|CreateOrUpdate#Create#ComputeInstance|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|compute_instance_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|compute_instance_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|compute_instance_resource_id|resourceId|
|**--vm-size**|string|Virtual Machine Size|compute_instance_vm_size|vmSize|
|**--application-sharing-policy**|choice|Policy for sharing applications on this compute instance among users of parent workspace. If Personal, only the creator can access applications on this compute instance. When Shared, any workspace user can access applications on this instance depending on his/her assigned role.|compute_instance_application_sharing_policy|applicationSharingPolicy|
|**--ssh-settings**|object|Specifies policy and settings for SSH access.|compute_instance_ssh_settings|sshSettings|
|**--subnet-id**|string|The ID of the resource|compute_instance_id|id|

### machinelearningservices machine-learning-compute data-factory create

data-factory create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|data-factory create|CreateOrUpdate#Create#DataFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|data_factory_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|data_factory_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|data_factory_resource_id|resourceId|

### machinelearningservices machine-learning-compute data-lake-analytics create

data-lake-analytics create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|data-lake-analytics create|CreateOrUpdate#Create#DataLakeAnalytics|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|data_lake_analytics_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|data_lake_analytics_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|data_lake_analytics_resource_id|resourceId|
|**--data-lake-store-account-name**|string|DataLake Store Account Name|data_lake_analytics_data_lake_store_account_name|dataLakeStoreAccountName|

### machinelearningservices machine-learning-compute databricks create

databricks create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|databricks create|CreateOrUpdate#Create#Databricks|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|databricks_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|databricks_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|databricks_resource_id|resourceId|
|**--databricks-access-token**|string|Databricks access token|databricks_databricks_access_token|databricksAccessToken|

### machinelearningservices machine-learning-compute delete

delete a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--underlying-resource-action**|choice|Delete the underlying compute if 'Delete', or detach the underlying compute from workspace if 'Detach'.|underlying_resource_action|underlyingResourceAction|

### machinelearningservices machine-learning-compute hd-insight create

hd-insight create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|hd-insight create|CreateOrUpdate#Create#HDInsight|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|hd_insight_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|hd_insight_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|hd_insight_resource_id|resourceId|
|**--ssh-port**|integer|Port open for ssh connections on the master node of the cluster.|hd_insight_ssh_port|sshPort|
|**--address**|string|Public IP address of the master node of the cluster.|hd_insight_address|address|
|**--administrator-account**|object|Admin credentials for master node of the cluster|hd_insight_administrator_account|administratorAccount|

### machinelearningservices machine-learning-compute list

list a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByWorkspace|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--skiptoken**|string|Continuation token for pagination.|skiptoken|$skiptoken|

### machinelearningservices machine-learning-compute list-key

list-key a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-key|ListKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### machinelearningservices machine-learning-compute list-node

list-node a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-node|ListNodes|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### machinelearningservices machine-learning-compute restart

restart a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|restart|Restart|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### machinelearningservices machine-learning-compute show

show a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### machinelearningservices machine-learning-compute start

start a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start|Start|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### machinelearningservices machine-learning-compute stop

stop a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|stop|Stop|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|

### machinelearningservices machine-learning-compute update

update a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--scale-settings**|object|Desired scale settings for the amlCompute.|scale_settings|scaleSettings|

### machinelearningservices machine-learning-compute virtual-machine create

virtual-machine create a machinelearningservices machine-learning-compute.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices machine-learning-compute|MachineLearningCompute|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|virtual-machine create|CreateOrUpdate#Create#VirtualMachine|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|computeName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--compute-location**|string|Location for the underlying compute|virtual_machine_compute_location|computeLocation|
|**--description**|string|The description of the Machine Learning compute.|virtual_machine_description|description|
|**--resource-id**|string|ARM resource id of the underlying compute|virtual_machine_resource_id|resourceId|
|**--virtual-machine-size**|string|Virtual Machine size|virtual_machine_virtual_machine_size|virtualMachineSize|
|**--ssh-port**|integer|Port open for ssh connections.|virtual_machine_ssh_port|sshPort|
|**--address**|string|Public IP address of the virtual machine.|virtual_machine_address|address|
|**--administrator-account**|object|Admin credentials for virtual machine|virtual_machine_administrator_account|administratorAccount|

### machinelearningservices notebook prepare

prepare a machinelearningservices notebook.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices notebook|Notebooks|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|prepare|Prepare|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### machinelearningservices private-endpoint-connection delete

delete a machinelearningservices private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|privateEndpointConnectionName|

### machinelearningservices private-endpoint-connection put

put a machinelearningservices private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|put|Put|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|privateEndpointConnectionName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

### machinelearningservices private-endpoint-connection show

show a machinelearningservices private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|privateEndpointConnectionName|

### machinelearningservices private-link-resource list

list a machinelearningservices private-link-resource.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices private-link-resource|PrivateLinkResources|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByWorkspace|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### machinelearningservices quota list

list a machinelearningservices quota.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices quota|Quotas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location for which resource usage is queried.|location|location|

### machinelearningservices quota update

update a machinelearningservices quota.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices quota|Quotas|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location for update quota is queried.|location|location|
|**--value**|array|The list for update quota.|value|value|

### machinelearningservices usage list

list a machinelearningservices usage.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices usage|Usages|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location for which resource usage is queried.|location|location|

### machinelearningservices virtual-machine-size list

list a machinelearningservices virtual-machine-size.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices virtual-machine-size|VirtualMachineSizes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location upon which virtual-machine-sizes is queried.|location|location|

### machinelearningservices workspace create

create a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--location**|string|Specifies the location of the resource.|location|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--identity-type**|sealed-choice|The identity type.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|
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
|**--encryption-status**|choice|Indicates whether or not the encryption is enabled for the workspace.|status|status|
|**--encryption-key-vault-properties**|object|Customer Key vault properties.|key_vault_properties|keyVaultProperties|

### machinelearningservices workspace delete

delete a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### machinelearningservices workspace list

list a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--skiptoken**|string|Continuation token for pagination.|skiptoken|$skiptoken|

### machinelearningservices workspace list-key

list-key a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-key|ListKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### machinelearningservices workspace resync-key

resync-key a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|resync-key|ResyncKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### machinelearningservices workspace show

show a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|

### machinelearningservices workspace update

update a machinelearningservices workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--tags**|dictionary|The resource tags for the machine learning workspace.|tags|tags|
|**--sku**|object|The sku of the workspace.|sku|sku|
|**--description**|string|The description of this workspace.|description|description|
|**--friendly-name**|string|The friendly name for this workspace.|friendly_name|friendlyName|

### machinelearningservices workspace-connection create

create a machinelearningservices workspace-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace-connection|WorkspaceConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
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

### machinelearningservices workspace-connection delete

delete a machinelearningservices workspace-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace-connection|WorkspaceConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--connection-name**|string|Friendly name of the workspace connection|connection_name|connectionName|

### machinelearningservices workspace-connection list

list a machinelearningservices workspace-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace-connection|WorkspaceConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--target**|string|Target of the workspace connection.|target|target|
|**--category**|string|Category of the workspace connection.|category|category|

### machinelearningservices workspace-connection show

show a machinelearningservices workspace-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace-connection|WorkspaceConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
|**--connection-name**|string|Friendly name of the workspace connection|connection_name|connectionName|

### machinelearningservices workspace-feature list

list a machinelearningservices workspace-feature.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|machinelearningservices workspace-feature|WorkspaceFeatures|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|workspaceName|
