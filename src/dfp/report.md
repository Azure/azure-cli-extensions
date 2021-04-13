# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az dfp|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az dfp` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az dfp instance|Instances|[commands](#CommandsInInstances)|
|az dfp||[commands](#CommandsIn)|

## COMMANDS
### <a name="CommandsIn">Commands in `az dfp` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dfp list-operation](#ListOperations)|ListOperations|[Parameters](#ParametersListOperations)|[Example](#ExamplesListOperations)|

### <a name="CommandsInInstances">Commands in `az dfp instance` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dfp instance list](#InstancesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersInstancesListByResourceGroup)|[Example](#ExamplesInstancesListByResourceGroup)|
|[az dfp instance list](#InstancesList)|List|[Parameters](#ParametersInstancesList)|[Example](#ExamplesInstancesList)|
|[az dfp instance create](#InstancesCreate)|Create|[Parameters](#ParametersInstancesCreate)|[Example](#ExamplesInstancesCreate)|
|[az dfp instance update](#InstancesUpdate)|Update|[Parameters](#ParametersInstancesUpdate)|[Example](#ExamplesInstancesUpdate)|
|[az dfp instance delete](#InstancesDelete)|Delete|[Parameters](#ParametersInstancesDelete)|[Example](#ExamplesInstancesDelete)|
|[az dfp instance show-detail](#InstancesGetDetails)|GetDetails|[Parameters](#ParametersInstancesGetDetails)|[Example](#ExamplesInstancesGetDetails)|


## COMMAND DETAILS

### group `az dfp`
#### <a name="ListOperations">Command `az dfp list-operation`</a>

##### <a name="ExamplesListOperations">Example</a>
```
az dfp list-operation
```
##### <a name="ParametersListOperations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az dfp instance`
#### <a name="InstancesListByResourceGroup">Command `az dfp instance list`</a>

##### <a name="ExamplesInstancesListByResourceGroup">Example</a>
```
az dfp instance list --resource-group "TestRG"
```
##### <a name="ParametersInstancesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Azure Resource group of which a given DFP instance is part. This name must be at least 1 character in length, and no more than 90.|resource_group_name|resourceGroupName|

#### <a name="InstancesList">Command `az dfp instance list`</a>

##### <a name="ExamplesInstancesList">Example</a>
```
az dfp instance list
```
##### <a name="ParametersInstancesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="InstancesCreate">Command `az dfp instance create`</a>

##### <a name="ExamplesInstancesCreate">Example</a>
```
az dfp instance create --name "azsdktest" --location "West US" --administration members="azsdktest@microsoft.com" \
members="azsdktest2@microsoft.com" --tags testKey="testValue" --resource-group "TestRG"
```
##### <a name="ParametersInstancesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Azure Resource group of which a given DFP instance is part. This name must be at least 1 character in length, and no more than 90.|resource_group_name|resourceGroupName|
|**--instance-name**|string|The name of the DFP instances. It must be a minimum of 3 characters, and a maximum of 63.|instance_name|instanceName|
|**--location**|string|Location of the DFP resource.|location|location|
|**--tags**|dictionary|Key-value pairs of additional resource provisioning properties.|tags|tags|
|**--administration**|object|A collection of DFP instance administrators|administration|administration|

#### <a name="InstancesUpdate">Command `az dfp instance update`</a>

##### <a name="ExamplesInstancesUpdate">Example</a>
```
az dfp instance update --name "azsdktest" --administration members="azsdktest@microsoft.com" \
members="azsdktest2@microsoft.com" --tags testKey="testValue" --resource-group "TestRG"
```
##### <a name="ParametersInstancesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Azure Resource group of which a given DFP instance is part. This name must be at least 1 character in length, and no more than 90.|resource_group_name|resourceGroupName|
|**--instance-name**|string|The name of the DFP instance. It must be at least 3 characters in length, and no more than 63.|instance_name|instanceName|
|**--tags**|dictionary|Key-value pairs of additional provisioning properties.|tags|tags|
|**--administration**|object|A collection of DFP instance administrators|administration|administration|

#### <a name="InstancesDelete">Command `az dfp instance delete`</a>

##### <a name="ExamplesInstancesDelete">Example</a>
```
az dfp instance delete --name "azsdktest" --resource-group "TestRG"
```
##### <a name="ParametersInstancesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Azure Resource group of which a given DFP instance is part. This name must be at least 1 character in length, and no more than 90.|resource_group_name|resourceGroupName|
|**--instance-name**|string|The name of the DFP instance. It must be at least 3 characters in length, and no more than 63.|instance_name|instanceName|

#### <a name="InstancesGetDetails">Command `az dfp instance show-detail`</a>

##### <a name="ExamplesInstancesGetDetails">Example</a>
```
az dfp instance show-detail --name "azsdktest" --resource-group "TestRG"
```
##### <a name="ParametersInstancesGetDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Azure Resource group of which a given DFP instance is part. This name must be at least 1 character in length, and no more than 90.|resource_group_name|resourceGroupName|
|**--instance-name**|string|The name of the instance. It must be a minimum of 3 characters, and a maximum of 63.|instance_name|instanceName|
