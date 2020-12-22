# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az operationsmanagement|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az operationsmanagement` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az operationsmanagement solution|Solutions|[commands](#CommandsInSolutions)|
|az operationsmanagement management-association|ManagementAssociations|[commands](#CommandsInManagementAssociations)|
|az operationsmanagement management-configuration|ManagementConfigurations|[commands](#CommandsInManagementConfigurations)|

## COMMANDS
### <a name="CommandsInManagementAssociations">Commands in `az operationsmanagement management-association` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az operationsmanagement management-association list](#ManagementAssociationsListBySubscription)|ListBySubscription|[Parameters](#ParametersManagementAssociationsListBySubscription)|[Example](#ExamplesManagementAssociationsListBySubscription)|
|[az operationsmanagement management-association show](#ManagementAssociationsGet)|Get|[Parameters](#ParametersManagementAssociationsGet)|[Example](#ExamplesManagementAssociationsGet)|
|[az operationsmanagement management-association create](#ManagementAssociationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersManagementAssociationsCreateOrUpdate#Create)|[Example](#ExamplesManagementAssociationsCreateOrUpdate#Create)|
|[az operationsmanagement management-association update](#ManagementAssociationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersManagementAssociationsCreateOrUpdate#Update)|Not Found|
|[az operationsmanagement management-association delete](#ManagementAssociationsDelete)|Delete|[Parameters](#ParametersManagementAssociationsDelete)|[Example](#ExamplesManagementAssociationsDelete)|

### <a name="CommandsInManagementConfigurations">Commands in `az operationsmanagement management-configuration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az operationsmanagement management-configuration list](#ManagementConfigurationsListBySubscription)|ListBySubscription|[Parameters](#ParametersManagementConfigurationsListBySubscription)|[Example](#ExamplesManagementConfigurationsListBySubscription)|
|[az operationsmanagement management-configuration show](#ManagementConfigurationsGet)|Get|[Parameters](#ParametersManagementConfigurationsGet)|[Example](#ExamplesManagementConfigurationsGet)|
|[az operationsmanagement management-configuration create](#ManagementConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersManagementConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesManagementConfigurationsCreateOrUpdate#Create)|
|[az operationsmanagement management-configuration update](#ManagementConfigurationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersManagementConfigurationsCreateOrUpdate#Update)|Not Found|
|[az operationsmanagement management-configuration delete](#ManagementConfigurationsDelete)|Delete|[Parameters](#ParametersManagementConfigurationsDelete)|[Example](#ExamplesManagementConfigurationsDelete)|

### <a name="CommandsInSolutions">Commands in `az operationsmanagement solution` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az operationsmanagement solution list](#SolutionsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersSolutionsListByResourceGroup)|[Example](#ExamplesSolutionsListByResourceGroup)|
|[az operationsmanagement solution list](#SolutionsListBySubscription)|ListBySubscription|[Parameters](#ParametersSolutionsListBySubscription)|[Example](#ExamplesSolutionsListBySubscription)|
|[az operationsmanagement solution show](#SolutionsGet)|Get|[Parameters](#ParametersSolutionsGet)|[Example](#ExamplesSolutionsGet)|
|[az operationsmanagement solution create](#SolutionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSolutionsCreateOrUpdate#Create)|[Example](#ExamplesSolutionsCreateOrUpdate#Create)|
|[az operationsmanagement solution update](#SolutionsUpdate)|Update|[Parameters](#ParametersSolutionsUpdate)|[Example](#ExamplesSolutionsUpdate)|
|[az operationsmanagement solution delete](#SolutionsDelete)|Delete|[Parameters](#ParametersSolutionsDelete)|[Example](#ExamplesSolutionsDelete)|


## COMMAND DETAILS

### group `az operationsmanagement management-association`
#### <a name="ManagementAssociationsListBySubscription">Command `az operationsmanagement management-association list`</a>

##### <a name="ExamplesManagementAssociationsListBySubscription">Example</a>
```
az operationsmanagement management-association list
```
##### <a name="ParametersManagementAssociationsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ManagementAssociationsGet">Command `az operationsmanagement management-association show`</a>

##### <a name="ExamplesManagementAssociationsGet">Example</a>
```
az operationsmanagement management-association show --name "managementAssociation1" --provider-name "providerName" \
--resource-group "rg1" --resource-name "resourceName" --resource-type "resourceType"
```
##### <a name="ParametersManagementAssociationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|

#### <a name="ManagementAssociationsCreateOrUpdate#Create">Command `az operationsmanagement management-association create`</a>

##### <a name="ExamplesManagementAssociationsCreateOrUpdate#Create">Example</a>
```
az operationsmanagement management-association create --name "managementAssociation1" --location "East US" \
--application-id "/subscriptions/sub1/resourcegroups/rg1/providers/Microsoft.Appliance/Appliances/appliance1" \
--provider-name "providerName" --resource-group "rg1" --resource-name "resourceName" --resource-type "resourceType"
```
##### <a name="ParametersManagementAssociationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this association.|application_id|applicationId|

#### <a name="ManagementAssociationsCreateOrUpdate#Update">Command `az operationsmanagement management-association update`</a>

##### <a name="ParametersManagementAssociationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this association.|application_id|applicationId|

#### <a name="ManagementAssociationsDelete">Command `az operationsmanagement management-association delete`</a>

##### <a name="ExamplesManagementAssociationsDelete">Example</a>
```
az operationsmanagement management-association delete --name "managementAssociationName" --provider-name \
"providerName" --resource-group "rg1" --resource-name "resourceName" --resource-type "resourceType"
```
##### <a name="ParametersManagementAssociationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--provider-name**|string|Provider name for the parent resource.|provider_name|providerName|
|**--resource-type**|string|Resource type for the parent resource|resource_type|resourceType|
|**--resource-name**|string|Parent resource name.|resource_name|resourceName|
|**--management-association-name**|string|User ManagementAssociation Name.|management_association_name|managementAssociationName|

### group `az operationsmanagement management-configuration`
#### <a name="ManagementConfigurationsListBySubscription">Command `az operationsmanagement management-configuration list`</a>

##### <a name="ExamplesManagementConfigurationsListBySubscription">Example</a>
```
az operationsmanagement management-configuration list
```
##### <a name="ParametersManagementConfigurationsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ManagementConfigurationsGet">Command `az operationsmanagement management-configuration show`</a>

##### <a name="ExamplesManagementConfigurationsGet">Example</a>
```
az operationsmanagement management-configuration show --name "managementConfigurationName" --resource-group "rg1"
```
##### <a name="ParametersManagementConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|

#### <a name="ManagementConfigurationsCreateOrUpdate#Create">Command `az operationsmanagement management-configuration create`</a>

##### <a name="ExamplesManagementConfigurationsCreateOrUpdate#Create">Example</a>
```
az operationsmanagement management-configuration create --name "managementConfiguration1" --properties-parameters \
location="East US" --resource-group "rg1"
```
##### <a name="ParametersManagementConfigurationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this Management.|application_id|applicationId|
|**--parent-resource-type**|string|The type of the parent resource.|parent_resource_type|parentResourceType|
|**--properties-parameters**|array|Parameters to run the ARM template|parameters|parameters|
|**--template**|any|The Json object containing the ARM template to deploy|template|template|

#### <a name="ManagementConfigurationsCreateOrUpdate#Update">Command `az operationsmanagement management-configuration update`</a>

##### <a name="ParametersManagementConfigurationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|
|**--location**|string|Resource location|location|location|
|**--application-id**|string|The applicationId of the appliance for this Management.|application_id|applicationId|
|**--parent-resource-type**|string|The type of the parent resource.|parent_resource_type|parentResourceType|
|**--properties-parameters**|array|Parameters to run the ARM template|parameters|parameters|
|**--template**|any|The Json object containing the ARM template to deploy|template|template|

#### <a name="ManagementConfigurationsDelete">Command `az operationsmanagement management-configuration delete`</a>

##### <a name="ExamplesManagementConfigurationsDelete">Example</a>
```
az operationsmanagement management-configuration delete --name "managementConfigurationName" --resource-group "rg1"
```
##### <a name="ParametersManagementConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--management-configuration-name**|string|User Management Configuration Name.|management_configuration_name|managementConfigurationName|

### group `az operationsmanagement solution`
#### <a name="SolutionsListByResourceGroup">Command `az operationsmanagement solution list`</a>

##### <a name="ExamplesSolutionsListByResourceGroup">Example</a>
```
az operationsmanagement solution list --resource-group "rg1"
```
##### <a name="ParametersSolutionsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="SolutionsListBySubscription">Command `az operationsmanagement solution list`</a>

##### <a name="ExamplesSolutionsListBySubscription">Example</a>
```
az operationsmanagement solution list
```
##### <a name="ParametersSolutionsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="SolutionsGet">Command `az operationsmanagement solution show`</a>

##### <a name="ExamplesSolutionsGet">Example</a>
```
az operationsmanagement solution show --resource-group "rg1" --name "solution1"
```
##### <a name="ParametersSolutionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|

#### <a name="SolutionsCreateOrUpdate#Create">Command `az operationsmanagement solution create`</a>

##### <a name="ExamplesSolutionsCreateOrUpdate#Create">Example</a>
```
az operationsmanagement solution create --location "East US" --plan name="name1" product="product1" \
promotion-code="promocode1" publisher="publisher1" --properties contained-resources="/subscriptions/sub2/resourceGroups\
/rg2/providers/provider1/resources/resource1" contained-resources="/subscriptions/sub2/resourceGroups/rg2/providers/pro\
vider2/resources/resource2" referenced-resources="/subscriptions/sub2/resourceGroups/rg2/providers/provider1/resources/\
resource2" referenced-resources="/subscriptions/sub2/resourceGroups/rg2/providers/provider2/resources/resource3" \
workspace-resource-id="/subscriptions/sub2/resourceGroups/rg2/providers/Microsoft.OperationalInsights/workspaces/ws1" \
--resource-group "rg1" --name "solution1"
```
##### <a name="ParametersSolutionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--plan**|object|Plan for solution object supported by the OperationsManagement resource provider.|plan|plan|
|**--properties**|object|Properties for solution object supported by the OperationsManagement resource provider.|properties|properties|

#### <a name="SolutionsUpdate">Command `az operationsmanagement solution update`</a>

##### <a name="ExamplesSolutionsUpdate">Example</a>
```
az operationsmanagement solution update --tags Dept="IT" Environment="Test" --resource-group "rg1" --name "solution1"
```
##### <a name="ParametersSolutionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|
|**--tags**|dictionary|Resource tags|tags|tags|

#### <a name="SolutionsDelete">Command `az operationsmanagement solution delete`</a>

##### <a name="ExamplesSolutionsDelete">Example</a>
```
az operationsmanagement solution delete --resource-group "rg1" --name "solution1"
```
##### <a name="ParametersSolutionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to get. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--solution-name**|string|User Solution Name.|solution_name|solutionName|
