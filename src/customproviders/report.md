# Azure CLI Module Creation Report

### customproviders association create

create a customproviders association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders association|Associations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association. The scope can be any valid REST resource instance. For example, use '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.Compute/virtualMachines/{vm-name}' for a virtual machine resource.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|
|**--target-resource-id**|string|The REST resource instance of the target resource for this association.|target_resource_id|targetResourceId|

### customproviders association delete

delete a customproviders association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders association|Associations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|

### customproviders association list-all

list-all a customproviders association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders association|Associations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-all|ListAll|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association.|scope|scope|

### customproviders association show

show a customproviders association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders association|Associations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|

### customproviders association update

update a customproviders association.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders association|Associations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association. The scope can be any valid REST resource instance. For example, use '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.Compute/virtualMachines/{vm-name}' for a virtual machine resource.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|
|**--target-resource-id**|string|The REST resource instance of the target resource for this association.|target_resource_id|targetResourceId|

### customproviders custom-resource-provider create

create a customproviders custom-resource-provider.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders custom-resource-provider|CustomResourceProvider|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--actions**|array|A list of actions that the custom resource provider implements.|actions|actions|
|**--resource-types**|array|A list of resource types that the custom resource provider implements.|resource_types|resourceTypes|
|**--validations**|array|A list of validations to run on the custom resource provider's requests.|validations|validations|

### customproviders custom-resource-provider delete

delete a customproviders custom-resource-provider.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders custom-resource-provider|CustomResourceProvider|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|

### customproviders custom-resource-provider list

list a customproviders custom-resource-provider.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders custom-resource-provider|CustomResourceProvider|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

### customproviders custom-resource-provider show

show a customproviders custom-resource-provider.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders custom-resource-provider|CustomResourceProvider|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|

### customproviders custom-resource-provider update

update a customproviders custom-resource-provider.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|customproviders custom-resource-provider|CustomResourceProvider|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|
|**--tags**|dictionary|Resource tags|tags|tags|
