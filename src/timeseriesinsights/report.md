# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az timeseriesinsights|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az timeseriesinsights` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az timeseriesinsights reference-data-set|ReferenceDataSets|[commands](#CommandsInReferenceDataSets)|
|az timeseriesinsights access-policy|AccessPolicies|[commands](#CommandsInAccessPolicies)|

## COMMANDS
### <a name="CommandsInAccessPolicies">Commands in `az timeseriesinsights access-policy` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az timeseriesinsights access-policy list](#AccessPoliciesListByEnvironment)|ListByEnvironment|[Parameters](#ParametersAccessPoliciesListByEnvironment)|[Example](#ExamplesAccessPoliciesListByEnvironment)|
|[az timeseriesinsights access-policy show](#AccessPoliciesGet)|Get|[Parameters](#ParametersAccessPoliciesGet)|[Example](#ExamplesAccessPoliciesGet)|
|[az timeseriesinsights access-policy create](#AccessPoliciesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAccessPoliciesCreateOrUpdate#Create)|[Example](#ExamplesAccessPoliciesCreateOrUpdate#Create)|
|[az timeseriesinsights access-policy update](#AccessPoliciesUpdate)|Update|[Parameters](#ParametersAccessPoliciesUpdate)|[Example](#ExamplesAccessPoliciesUpdate)|
|[az timeseriesinsights access-policy delete](#AccessPoliciesDelete)|Delete|[Parameters](#ParametersAccessPoliciesDelete)|[Example](#ExamplesAccessPoliciesDelete)|

### <a name="CommandsInReferenceDataSets">Commands in `az timeseriesinsights reference-data-set` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az timeseriesinsights reference-data-set list](#ReferenceDataSetsListByEnvironment)|ListByEnvironment|[Parameters](#ParametersReferenceDataSetsListByEnvironment)|[Example](#ExamplesReferenceDataSetsListByEnvironment)|
|[az timeseriesinsights reference-data-set show](#ReferenceDataSetsGet)|Get|[Parameters](#ParametersReferenceDataSetsGet)|[Example](#ExamplesReferenceDataSetsGet)|
|[az timeseriesinsights reference-data-set create](#ReferenceDataSetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersReferenceDataSetsCreateOrUpdate#Create)|[Example](#ExamplesReferenceDataSetsCreateOrUpdate#Create)|
|[az timeseriesinsights reference-data-set update](#ReferenceDataSetsUpdate)|Update|[Parameters](#ParametersReferenceDataSetsUpdate)|[Example](#ExamplesReferenceDataSetsUpdate)|
|[az timeseriesinsights reference-data-set delete](#ReferenceDataSetsDelete)|Delete|[Parameters](#ParametersReferenceDataSetsDelete)|[Example](#ExamplesReferenceDataSetsDelete)|


## COMMAND DETAILS

### group `az timeseriesinsights access-policy`
#### <a name="AccessPoliciesListByEnvironment">Command `az timeseriesinsights access-policy list`</a>

##### <a name="ExamplesAccessPoliciesListByEnvironment">Example</a>
```
az timeseriesinsights access-policy list --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|

#### <a name="AccessPoliciesGet">Command `az timeseriesinsights access-policy show`</a>

##### <a name="ExamplesAccessPoliciesGet">Example</a>
```
az timeseriesinsights access-policy show --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|The name of the Time Series Insights access policy associated with the specified environment.|access_policy_name|accessPolicyName|

#### <a name="AccessPoliciesCreateOrUpdate#Create">Command `az timeseriesinsights access-policy create`</a>

##### <a name="ExamplesAccessPoliciesCreateOrUpdate#Create">Example</a>
```
az timeseriesinsights access-policy create --name "ap1" --environment-name "env1" --description "some description" \
--principal-object-id "aGuid" --roles "Reader" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|Name of the access policy.|access_policy_name|accessPolicyName|
|**--principal-object-id**|string|The objectId of the principal in Azure Active Directory.|principal_object_id|principalObjectId|
|**--description**|string|An description of the access policy.|description|description|
|**--roles**|array|The list of roles the principal is assigned on the environment.|roles|roles|

#### <a name="AccessPoliciesUpdate">Command `az timeseriesinsights access-policy update`</a>

##### <a name="ExamplesAccessPoliciesUpdate">Example</a>
```
az timeseriesinsights access-policy update --name "ap1" --roles "Reader" --roles "Contributor" --environment-name \
"env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|The name of the Time Series Insights access policy associated with the specified environment.|access_policy_name|accessPolicyName|
|**--description**|string|An description of the access policy.|description|description|
|**--roles**|array|The list of roles the principal is assigned on the environment.|roles|roles|

#### <a name="AccessPoliciesDelete">Command `az timeseriesinsights access-policy delete`</a>

##### <a name="ExamplesAccessPoliciesDelete">Example</a>
```
az timeseriesinsights access-policy delete --name "ap1" --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersAccessPoliciesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--access-policy-name**|string|The name of the Time Series Insights access policy associated with the specified environment.|access_policy_name|accessPolicyName|

### group `az timeseriesinsights reference-data-set`
#### <a name="ReferenceDataSetsListByEnvironment">Command `az timeseriesinsights reference-data-set list`</a>

##### <a name="ExamplesReferenceDataSetsListByEnvironment">Example</a>
```
az timeseriesinsights reference-data-set list --environment-name "env1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|

#### <a name="ReferenceDataSetsGet">Command `az timeseriesinsights reference-data-set show`</a>

##### <a name="ExamplesReferenceDataSetsGet">Example</a>
```
az timeseriesinsights reference-data-set show --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|The name of the Time Series Insights reference data set associated with the specified environment.|reference_data_set_name|referenceDataSetName|

#### <a name="ReferenceDataSetsCreateOrUpdate#Create">Command `az timeseriesinsights reference-data-set create`</a>

##### <a name="ExamplesReferenceDataSetsCreateOrUpdate#Create">Example</a>
```
az timeseriesinsights reference-data-set create --environment-name "env1" --location "West US" --key-properties \
name="DeviceId1" type="String" --key-properties name="DeviceFloor" type="Double" --name "rds1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|Name of the reference data set.|reference_data_set_name|referenceDataSetName|
|**--location**|string|The location of the resource.|location|location|
|**--key-properties**|array|The list of key properties for the reference data set.|key_properties|keyProperties|
|**--tags**|dictionary|Key-value pairs of additional properties for the resource.|tags|tags|
|**--data-string-comparison-behavior**|choice|The reference data set key comparison behavior can be set using this property. By default, the value is 'Ordinal' - which means case sensitive key comparison will be performed while joining reference data with events or while adding new reference data. When 'OrdinalIgnoreCase' is set, case insensitive comparison will be used.|data_string_comparison_behavior|dataStringComparisonBehavior|

#### <a name="ReferenceDataSetsUpdate">Command `az timeseriesinsights reference-data-set update`</a>

##### <a name="ExamplesReferenceDataSetsUpdate">Example</a>
```
az timeseriesinsights reference-data-set update --environment-name "env1" --name "rds1" --tags someKey="someValue" \
--resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|The name of the Time Series Insights reference data set associated with the specified environment.|reference_data_set_name|referenceDataSetName|
|**--tags**|dictionary|Key-value pairs of additional properties for the reference data set.|tags|tags|

#### <a name="ReferenceDataSetsDelete">Command `az timeseriesinsights reference-data-set delete`</a>

##### <a name="ExamplesReferenceDataSetsDelete">Example</a>
```
az timeseriesinsights reference-data-set delete --environment-name "env1" --name "rds1" --resource-group "rg1"
```
##### <a name="ParametersReferenceDataSetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of an Azure Resource group.|resource_group_name|resourceGroupName|
|**--environment-name**|string|The name of the Time Series Insights environment associated with the specified resource group.|environment_name|environmentName|
|**--reference-data-set-name**|string|The name of the Time Series Insights reference data set associated with the specified environment.|reference_data_set_name|referenceDataSetName|
