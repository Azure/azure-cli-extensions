# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az customproviders|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az customproviders` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az customproviders custom-resource-provider|CustomResourceProvider|[commands](#CommandsInCustomResourceProvider)|
|az customproviders association|Associations|[commands](#CommandsInAssociations)|

## COMMANDS
### <a name="CommandsInAssociations">Commands in `az customproviders association` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az customproviders association show](#AssociationsGet)|Get|[Parameters](#ParametersAssociationsGet)|[Example](#ExamplesAssociationsGet)|
|[az customproviders association create](#AssociationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAssociationsCreateOrUpdate#Create)|[Example](#ExamplesAssociationsCreateOrUpdate#Create)|
|[az customproviders association update](#AssociationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersAssociationsCreateOrUpdate#Update)|Not Found|
|[az customproviders association delete](#AssociationsDelete)|Delete|[Parameters](#ParametersAssociationsDelete)|[Example](#ExamplesAssociationsDelete)|
|[az customproviders association list-all](#AssociationsListAll)|ListAll|[Parameters](#ParametersAssociationsListAll)|[Example](#ExamplesAssociationsListAll)|

### <a name="CommandsInCustomResourceProvider">Commands in `az customproviders custom-resource-provider` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az customproviders custom-resource-provider list](#CustomResourceProviderListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersCustomResourceProviderListByResourceGroup)|[Example](#ExamplesCustomResourceProviderListByResourceGroup)|
|[az customproviders custom-resource-provider list](#CustomResourceProviderListBySubscription)|ListBySubscription|[Parameters](#ParametersCustomResourceProviderListBySubscription)|[Example](#ExamplesCustomResourceProviderListBySubscription)|
|[az customproviders custom-resource-provider show](#CustomResourceProviderGet)|Get|[Parameters](#ParametersCustomResourceProviderGet)|[Example](#ExamplesCustomResourceProviderGet)|
|[az customproviders custom-resource-provider create](#CustomResourceProviderCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCustomResourceProviderCreateOrUpdate#Create)|[Example](#ExamplesCustomResourceProviderCreateOrUpdate#Create)|
|[az customproviders custom-resource-provider update](#CustomResourceProviderUpdate)|Update|[Parameters](#ParametersCustomResourceProviderUpdate)|[Example](#ExamplesCustomResourceProviderUpdate)|
|[az customproviders custom-resource-provider delete](#CustomResourceProviderDelete)|Delete|[Parameters](#ParametersCustomResourceProviderDelete)|[Example](#ExamplesCustomResourceProviderDelete)|


## COMMAND DETAILS

### group `az customproviders association`
#### <a name="AssociationsGet">Command `az customproviders association show`</a>

##### <a name="ExamplesAssociationsGet">Example</a>
```
az customproviders association show --name "associationName" --scope "scope"
```
##### <a name="ParametersAssociationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|

#### <a name="AssociationsCreateOrUpdate#Create">Command `az customproviders association create`</a>

##### <a name="ExamplesAssociationsCreateOrUpdate#Create">Example</a>
```
az customproviders association create --target-resource-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourc\
eGroups/appRG/providers/Microsoft.Solutions/applications/applicationName" --name "associationName" --scope "scope"
```
##### <a name="ParametersAssociationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association. The scope can be any valid REST resource instance. For example, use '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.Compute/virtualMachines/{vm-name}' for a virtual machine resource.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|
|**--target-resource-id**|string|The REST resource instance of the target resource for this association.|target_resource_id|targetResourceId|

#### <a name="AssociationsCreateOrUpdate#Update">Command `az customproviders association update`</a>

##### <a name="ParametersAssociationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association. The scope can be any valid REST resource instance. For example, use '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.Compute/virtualMachines/{vm-name}' for a virtual machine resource.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|
|**--target-resource-id**|string|The REST resource instance of the target resource for this association.|target_resource_id|targetResourceId|

#### <a name="AssociationsDelete">Command `az customproviders association delete`</a>

##### <a name="ExamplesAssociationsDelete">Example</a>
```
az customproviders association delete --name "associationName" --scope "scope"
```
##### <a name="ParametersAssociationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association.|scope|scope|
|**--association-name**|string|The name of the association.|association_name|associationName|

#### <a name="AssociationsListAll">Command `az customproviders association list-all`</a>

##### <a name="ExamplesAssociationsListAll">Example</a>
```
az customproviders association list-all --scope "scope"
```
##### <a name="ParametersAssociationsListAll">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope of the association.|scope|scope|

### group `az customproviders custom-resource-provider`
#### <a name="CustomResourceProviderListByResourceGroup">Command `az customproviders custom-resource-provider list`</a>

##### <a name="ExamplesCustomResourceProviderListByResourceGroup">Example</a>
```
az customproviders custom-resource-provider list --resource-group "testRG"
```
##### <a name="ParametersCustomResourceProviderListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

#### <a name="CustomResourceProviderListBySubscription">Command `az customproviders custom-resource-provider list`</a>

##### <a name="ExamplesCustomResourceProviderListBySubscription">Example</a>
```
az customproviders custom-resource-provider list
```
##### <a name="ParametersCustomResourceProviderListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CustomResourceProviderGet">Command `az customproviders custom-resource-provider show`</a>

##### <a name="ExamplesCustomResourceProviderGet">Example</a>
```
az customproviders custom-resource-provider show --resource-group "testRG" --resource-provider-name "newrp"
```
##### <a name="ParametersCustomResourceProviderGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|

#### <a name="CustomResourceProviderCreateOrUpdate#Create">Command `az customproviders custom-resource-provider create`</a>

##### <a name="ExamplesCustomResourceProviderCreateOrUpdate#Create">Example</a>
```
az customproviders custom-resource-provider create --resource-group "testRG" --location "eastus" --actions \
name="TestAction" endpoint="https://mytestendpoint/" routing-type="Proxy" --resource-types name="TestResource" \
endpoint="https://mytestendpoint2/" routing-type="Proxy,Cache" --resource-provider-name "newrp"
```
##### <a name="ParametersCustomResourceProviderCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--actions**|array|A list of actions that the custom resource provider implements.|actions|actions|
|**--resource-types**|array|A list of resource types that the custom resource provider implements.|resource_types|resourceTypes|
|**--validations**|array|A list of validations to run on the custom resource provider's requests.|validations|validations|

#### <a name="CustomResourceProviderUpdate">Command `az customproviders custom-resource-provider update`</a>

##### <a name="ExamplesCustomResourceProviderUpdate">Example</a>
```
az customproviders custom-resource-provider update --resource-group "testRG" --resource-provider-name "newrp"
```
##### <a name="ParametersCustomResourceProviderUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|
|**--tags**|dictionary|Resource tags|tags|tags|

#### <a name="CustomResourceProviderDelete">Command `az customproviders custom-resource-provider delete`</a>

##### <a name="ExamplesCustomResourceProviderDelete">Example</a>
```
az customproviders custom-resource-provider delete --resource-group "testRG" --resource-provider-name "newrp"
```
##### <a name="ParametersCustomResourceProviderDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--resource-provider-name**|string|The name of the resource provider.|resource_provider_name|resourceProviderName|
