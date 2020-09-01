# Azure CLI Module Creation Report

### devops pipeline create

create a devops pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|
|**--pipeline-name**|string|The name of the Azure Pipeline resource in ARM.|pipeline_name|
|**--bootstrap-configuration-template-id**|string|Unique identifier of the pipeline template.|id_properties_bootstrap_configuration_template_id|
|**--project-name**|string|Name of the Azure DevOps Project.|name_properties_project_name|
|**--organization-name**|string|Name of the Azure DevOps Organization.|name_properties_organization_name|
|**--tags**|dictionary|Resource Tags|tags|
|**--location**|string|Resource Location|location|
|**--bootstrap-configuration-template-parameters**|dictionary|Dictionary of input parameters used in the pipeline template.|parameters_properties_bootstrap_configuration_template_parameters|
|**--bootstrap-configuration-repository-repository-type**|choice|Type of code repository.|repository_type|
|**--bootstrap-configuration-repository-id**|string|Unique immutable identifier of the code repository.|id_properties_bootstrap_configuration_repository_id|
|**--bootstrap-configuration-repository-default-branch**|string|Default branch used to configure Continuous Integration (CI) in the pipeline.|default_branch|
|**--bootstrap-configuration-repository-properties**|dictionary|Repository-specific properties.|properties|
|**--bootstrap-configuration-repository-authorization-parameters**|dictionary|Authorization parameters corresponding to the authorization type.|parameters_properties_bootstrap_configuration_repository_authorization_parameters|
### devops pipeline delete

delete a devops pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|
|**--pipeline-name**|string|The name of the Azure Pipeline resource.|pipeline_name|
### devops pipeline list

list a devops pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|
### devops pipeline show

show a devops pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|
|**--pipeline-name**|string|The name of the Azure Pipeline resource in ARM.|pipeline_name|
### devops pipeline update

update a devops pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Name of the resource group within the Azure subscription.|resource_group_name|
|**--pipeline-name**|string|The name of the Azure Pipeline resource.|pipeline_name|
|**--tags**|dictionary|Dictionary of key-value pairs to be set as tags on the Azure Pipeline. This will overwrite any existing tags.|tags|
### devops pipeline-template-definition list

list a devops pipeline-template-definition.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|