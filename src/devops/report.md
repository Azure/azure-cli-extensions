# Azure CLI Module Creation Report

### devops pipeline create

create a devops pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|devops pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--pipeline-name**|string|The name of the Azure Pipeline resource in ARM.|pipeline_name|pipelineName|
|**--bootstrap-configuration-template-id**|string|Unique identifier of the pipeline template.|id|id|
|**--project-name**|string|Name of the Azure DevOps Project.|name|name|
|**--organization-name**|string|Name of the Azure DevOps Organization.|organization_reference_name|name|
|**--tags**|dictionary|Resource Tags|tags|tags|
|**--location**|string|Resource Location|location|location|
|**--bootstrap-configuration-template-parameters**|dictionary|Dictionary of input parameters used in the pipeline template.|parameters|parameters|
|**--bootstrap-configuration-repository-repository-type**|choice|Type of code repository.|repository_type|repositoryType|
|**--bootstrap-configuration-repository-id**|string|Unique immutable identifier of the code repository.|code_repository_id|id|
|**--bootstrap-configuration-repository-default-branch**|string|Default branch used to configure Continuous Integration (CI) in the pipeline.|default_branch|defaultBranch|
|**--bootstrap-configuration-repository-properties**|dictionary|Repository-specific properties.|properties|properties|
|**--bootstrap-configuration-repository-authorization-parameters**|dictionary|Authorization parameters corresponding to the authorization type.|authorization_parameters|parameters|

### devops pipeline delete

delete a devops pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|devops pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--pipeline-name**|string|The name of the Azure Pipeline resource.|pipeline_name|pipelineName|

### devops pipeline list

list a devops pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|devops pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|

### devops pipeline show

show a devops pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|devops pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--pipeline-name**|string|The name of the Azure Pipeline resource in ARM.|pipeline_name|pipelineName|

### devops pipeline update

update a devops pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|devops pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|resourceGroupName|
|**--pipeline-name**|string|The name of the Azure Pipeline resource.|pipeline_name|pipelineName|
|**--tags**|dictionary|Dictionary of key-value pairs to be set as tags on the Azure Pipeline. This will overwrite any existing tags.|tags|tags|

### devops pipeline-template-definition list

list a devops pipeline-template-definition.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|devops pipeline-template-definition|PipelineTemplateDefinitions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
