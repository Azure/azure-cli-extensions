# Azure CLI Module Creation Report

### operationsmanagement management-association create

create a operationsmanagement management-association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-association|ManagementAssociations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this association.|application_id|applicationId|

### operationsmanagement management-association delete

delete a operationsmanagement management-association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-association|ManagementAssociations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|

### operationsmanagement management-association list

list a operationsmanagement management-association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-association|ManagementAssociations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### operationsmanagement management-association show

show a operationsmanagement management-association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-association|ManagementAssociations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|

### operationsmanagement management-association update

update a operationsmanagement management-association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-association|ManagementAssociations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this association.|application_id|applicationId|

### operationsmanagement management-configuration create

create a operationsmanagement management-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-configuration|ManagementConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this Management.|application_id|applicationId|
|**--parent-resource-type**|string|The type of the parent resource.|parent_resource_type|parentResourceType|
|**--parameters**|array|Parameters to run the ARM template|parameters|parameters|
|**--template**|any|The Json object containing the ARM template to deploy|template|template|

### operationsmanagement management-configuration delete

delete a operationsmanagement management-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-configuration|ManagementConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|

### operationsmanagement management-configuration list

list a operationsmanagement management-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-configuration|ManagementConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### operationsmanagement management-configuration show

show a operationsmanagement management-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-configuration|ManagementConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|

### operationsmanagement management-configuration update

update a operationsmanagement management-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement management-configuration|ManagementConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this Management.|application_id|applicationId|
|**--parent-resource-type**|string|The type of the parent resource.|parent_resource_type|parentResourceType|
|**--parameters**|array|Parameters to run the ARM template|parameters|parameters|
|**--template**|any|The Json object containing the ARM template to deploy|template|template|

### operationsmanagement solution create

create a operationsmanagement solution.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement solution|Solutions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--plan**|object|Plan for solution object supported by the OperationsManagement resource provider.|plan|plan|
|**--properties**|object|Properties for solution object supported by the OperationsManagement resource provider.|properties|properties|

### operationsmanagement solution delete

delete a operationsmanagement solution.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement solution|Solutions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|

### operationsmanagement solution list

list a operationsmanagement solution.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement solution|Solutions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|

### operationsmanagement solution show

show a operationsmanagement solution.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement solution|Solutions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|

### operationsmanagement solution update

update a operationsmanagement solution.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|operationsmanagement solution|Solutions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|
|**--tags**|dictionary|Resource tags|tags|tags|
