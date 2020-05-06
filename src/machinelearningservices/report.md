# Azure CLI Module Creation Report

### machinelearningservices  list-sku

list-sku a machinelearningservices .

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### machinelearningservices machine-learning-compute aks create

aks create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|aks_compute_location|
|**--description**|string|The description of the Machine Learning compute.|aks_description|
|**--resource-id**|string|ARM resource id of the underlying compute|aks_resource_id|
|**--aks-properties**|object|AKS properties|aks_properties|
### machinelearningservices machine-learning-compute aml-compute create

aml-compute create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|aml_compute_compute_location|
|**--description**|string|The description of the Machine Learning compute.|aml_compute_description|
|**--resource-id**|string|ARM resource id of the underlying compute|aml_compute_resource_id|
|**--aml-compute-properties**|object|AML Compute properties|aml_compute_properties|
### machinelearningservices machine-learning-compute data-factory create

data-factory create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|data_factory_compute_location|
|**--description**|string|The description of the Machine Learning compute.|data_factory_description|
|**--resource-id**|string|ARM resource id of the underlying compute|data_factory_resource_id|
### machinelearningservices machine-learning-compute data-lake-analytics create

data-lake-analytics create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|data_lake_analytics_compute_location|
|**--description**|string|The description of the Machine Learning compute.|data_lake_analytics_description|
|**--resource-id**|string|ARM resource id of the underlying compute|data_lake_analytics_resource_id|
|**--data-lake-analytics-properties**|object||data_lake_analytics_properties|
### machinelearningservices machine-learning-compute databricks create

databricks create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|databricks_compute_location|
|**--description**|string|The description of the Machine Learning compute.|databricks_description|
|**--resource-id**|string|ARM resource id of the underlying compute|databricks_resource_id|
|**--databricks-properties**|object||databricks_properties|
### machinelearningservices machine-learning-compute delete

delete a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--underlying-resource-action**|choice|Delete the underlying compute if 'Delete', or detach the underlying compute from workspace if 'Detach'.|underlying_resource_action|
### machinelearningservices machine-learning-compute hd-insight create

hd-insight create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|hd_insight_compute_location|
|**--description**|string|The description of the Machine Learning compute.|hd_insight_description|
|**--resource-id**|string|ARM resource id of the underlying compute|hd_insight_resource_id|
|**--ssh-port**|integer|Port open for ssh connections on the master node of the cluster.|hd_insight_ssh_port|
|**--address**|string|Public IP address of the master node of the cluster.|hd_insight_address|
|**--administrator-account**|object|Admin credentials for master node of the cluster|hd_insight_administrator_account|
### machinelearningservices machine-learning-compute list

list a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--skiptoken**|string|Continuation token for pagination.|skiptoken|
### machinelearningservices machine-learning-compute list-key

list-key a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
### machinelearningservices machine-learning-compute list-node

list-node a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
### machinelearningservices machine-learning-compute show

show a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
### machinelearningservices machine-learning-compute update

update a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--scale-settings**|object|Desired scale settings for the amlCompute.|scale_settings|
### machinelearningservices machine-learning-compute virtual-machine create

virtual-machine create a machinelearningservices machine-learning-compute.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--compute-name**|string|Name of the Azure Machine Learning compute.|compute_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--compute-location**|string|Location for the underlying compute|virtual_machine_compute_location|
|**--description**|string|The description of the Machine Learning compute.|virtual_machine_description|
|**--resource-id**|string|ARM resource id of the underlying compute|virtual_machine_resource_id|
|**--virtual-machine-size**|string|Virtual Machine size|virtual_machine_virtual_machine_size|
|**--ssh-port**|integer|Port open for ssh connections.|virtual_machine_ssh_port|
|**--address**|string|Public IP address of the virtual machine.|virtual_machine_address|
|**--administrator-account**|object|Admin credentials for virtual machine|virtual_machine_administrator_account|
### machinelearningservices private-endpoint-connection delete

delete a machinelearningservices private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|
### machinelearningservices private-endpoint-connection put

put a machinelearningservices private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--private-endpoint**|object|The resource of private end point.|private_endpoint|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|
### machinelearningservices private-endpoint-connection show

show a machinelearningservices private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the workspace|private_endpoint_connection_name|
### machinelearningservices private-link-resource list

list a machinelearningservices private-link-resource.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
### machinelearningservices quota list

list a machinelearningservices quota.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location for which resource usage is queried.|location|
### machinelearningservices quota update

update a machinelearningservices quota.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location for update quota is queried.|location|
|**--value**|array|The list for update quota.|value|
### machinelearningservices usage list

list a machinelearningservices usage.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location for which resource usage is queried.|location|
### machinelearningservices virtual-machine-size list

list a machinelearningservices virtual-machine-size.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location upon which virtual-machine-sizes is queried.|location|
### machinelearningservices workspace create

create a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--location**|string|Specifies the location of the resource.|location|
|**--tags**|dictionary|Contains resource tags defined as key/value pairs.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
|**--description**|string|The description of this workspace.|description|
|**--friendly-name**|string|The friendly name for this workspace. This name in mutable|friendly_name|
|**--key-vault**|string|ARM id of the key vault associated with this workspace. This cannot be changed once the workspace has been created|key_vault|
|**--application-insights**|string|ARM id of the application insights associated with this workspace. This cannot be changed once the workspace has been created|application_insights|
|**--container-registry**|string|ARM id of the container registry associated with this workspace. This cannot be changed once the workspace has been created|container_registry|
|**--storage-account**|string|ARM id of the storage account associated with this workspace. This cannot be changed once the workspace has been created|storage_account|
|**--discovery-url**|string|Url for the discovery service to identify regional endpoints for machine learning experimentation services|discovery_url|
|**--hbi-workspace**|boolean|The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service|hbi_workspace|
|**--image-build-compute**|string|The compute name for image build|image_build_compute|
|**--allow-public-access-when-behind-vnet**|boolean|The flag to indicate whether to allow public access when behind VNet.|allow_public_access_when_behind_vnet|
|**--shared-private-link-resources**|array|The list of shared private link resources in this workspace.|shared_private_link_resources|
|**--encryption-status**|choice|Indicates whether or not the encryption is enabled for the workspace.|status|
|**--encryption-key-vault-properties**|object|Customer Key vault properties.|key_vault_properties|
### machinelearningservices workspace delete

delete a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
### machinelearningservices workspace list

list a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--skiptoken**|string|Continuation token for pagination.|skiptoken|
### machinelearningservices workspace list-key

list-key a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
### machinelearningservices workspace resync-key

resync-key a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
### machinelearningservices workspace show

show a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
### machinelearningservices workspace update

update a machinelearningservices workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|
|**--tags**|dictionary|The resource tags for the machine learning workspace.|tags|
|**--sku**|object|The sku of the workspace.|sku|
|**--description**|string|The description of this workspace.|description|
|**--friendly-name**|string|The friendly name for this workspace.|friendly_name|
### machinelearningservices workspace-feature list

list a machinelearningservices workspace-feature.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group in which workspace is located.|resource_group_name|
|**--workspace-name**|string|Name of Azure Machine Learning workspace.|workspace_name|