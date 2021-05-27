# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az monitor-control-service|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az monitor-control-service` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az monitor data-collection endpoint|DataCollectionEndpoints|[commands](#CommandsInDataCollectionEndpoints)|
|az monitor data-collection rule|DataCollectionRules|[commands](#CommandsInDataCollectionRules)|
|az monitor data-collection rule association|DataCollectionRuleAssociations|[commands](#CommandsInDataCollectionRuleAssociations)|

## COMMANDS
### <a name="CommandsInDataCollectionEndpoints">Commands in `az monitor data-collection endpoint` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az monitor data-collection endpoint list](#DataCollectionEndpointsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDataCollectionEndpointsListByResourceGroup)|[Example](#ExamplesDataCollectionEndpointsListByResourceGroup)|
|[az monitor data-collection endpoint list](#DataCollectionEndpointsListBySubscription)|ListBySubscription|[Parameters](#ParametersDataCollectionEndpointsListBySubscription)|[Example](#ExamplesDataCollectionEndpointsListBySubscription)|
|[az monitor data-collection endpoint show](#DataCollectionEndpointsGet)|Get|[Parameters](#ParametersDataCollectionEndpointsGet)|[Example](#ExamplesDataCollectionEndpointsGet)|
|[az monitor data-collection endpoint delete](#DataCollectionEndpointsDelete)|Delete|[Parameters](#ParametersDataCollectionEndpointsDelete)|[Example](#ExamplesDataCollectionEndpointsDelete)|

### <a name="CommandsInDataCollectionRules">Commands in `az monitor data-collection rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az monitor data-collection rule list](#DataCollectionRulesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDataCollectionRulesListByResourceGroup)|[Example](#ExamplesDataCollectionRulesListByResourceGroup)|
|[az monitor data-collection rule list](#DataCollectionRulesListBySubscription)|ListBySubscription|[Parameters](#ParametersDataCollectionRulesListBySubscription)|[Example](#ExamplesDataCollectionRulesListBySubscription)|
|[az monitor data-collection rule show](#DataCollectionRulesGet)|Get|[Parameters](#ParametersDataCollectionRulesGet)|[Example](#ExamplesDataCollectionRulesGet)|
|[az monitor data-collection rule delete](#DataCollectionRulesDelete)|Delete|[Parameters](#ParametersDataCollectionRulesDelete)|[Example](#ExamplesDataCollectionRulesDelete)|

### <a name="CommandsInDataCollectionRuleAssociations">Commands in `az monitor data-collection rule association` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az monitor data-collection rule association list](#DataCollectionRuleAssociationsListByRule)|ListByRule|[Parameters](#ParametersDataCollectionRuleAssociationsListByRule)|[Example](#ExamplesDataCollectionRuleAssociationsListByRule)|
|[az monitor data-collection rule association list](#DataCollectionRuleAssociationsListByResource)|ListByResource|[Parameters](#ParametersDataCollectionRuleAssociationsListByResource)|[Example](#ExamplesDataCollectionRuleAssociationsListByResource)|
|[az monitor data-collection rule association show](#DataCollectionRuleAssociationsGet)|Get|[Parameters](#ParametersDataCollectionRuleAssociationsGet)|[Example](#ExamplesDataCollectionRuleAssociationsGet)|
|[az monitor data-collection rule association delete](#DataCollectionRuleAssociationsDelete)|Delete|[Parameters](#ParametersDataCollectionRuleAssociationsDelete)|[Example](#ExamplesDataCollectionRuleAssociationsDelete)|


## COMMAND DETAILS
### group `az monitor data-collection endpoint`
#### <a name="DataCollectionEndpointsListByResourceGroup">Command `az monitor data-collection endpoint list`</a>

##### <a name="ExamplesDataCollectionEndpointsListByResourceGroup">Example</a>
```
az monitor data-collection endpoint list --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionEndpointsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DataCollectionEndpointsListBySubscription">Command `az monitor data-collection endpoint list`</a>

##### <a name="ExamplesDataCollectionEndpointsListBySubscription">Example</a>
```
az monitor data-collection endpoint list
```
##### <a name="ParametersDataCollectionEndpointsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="DataCollectionEndpointsGet">Command `az monitor data-collection endpoint show`</a>

##### <a name="ExamplesDataCollectionEndpointsGet">Example</a>
```
az monitor data-collection endpoint show --name "myCollectionEndpoint" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionEndpointsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--data-collection-endpoint-name**|string|The name of the data collection endpoint. The name is case insensitive.|data_collection_endpoint_name|dataCollectionEndpointName|

#### <a name="DataCollectionEndpointsDelete">Command `az monitor data-collection endpoint delete`</a>

##### <a name="ExamplesDataCollectionEndpointsDelete">Example</a>
```
az monitor data-collection endpoint delete --name "myCollectionEndpoint" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionEndpointsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--data-collection-endpoint-name**|string|The name of the data collection endpoint. The name is case insensitive.|data_collection_endpoint_name|dataCollectionEndpointName|

### group `az monitor data-collection rule`
#### <a name="DataCollectionRulesListByResourceGroup">Command `az monitor data-collection rule list`</a>

##### <a name="ExamplesDataCollectionRulesListByResourceGroup">Example</a>
```
az monitor data-collection rule list --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DataCollectionRulesListBySubscription">Command `az monitor data-collection rule list`</a>

##### <a name="ExamplesDataCollectionRulesListBySubscription">Example</a>
```
az monitor data-collection rule list
```
##### <a name="ParametersDataCollectionRulesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="DataCollectionRulesGet">Command `az monitor data-collection rule show`</a>

##### <a name="ExamplesDataCollectionRulesGet">Example</a>
```
az monitor data-collection rule show --name "myCollectionRule" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--data-collection-rule-name**|string|The name of the data collection rule. The name is case insensitive.|data_collection_rule_name|dataCollectionRuleName|

#### <a name="DataCollectionRulesDelete">Command `az monitor data-collection rule delete`</a>

##### <a name="ExamplesDataCollectionRulesDelete">Example</a>
```
az monitor data-collection rule delete --name "myCollectionRule" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--data-collection-rule-name**|string|The name of the data collection rule. The name is case insensitive.|data_collection_rule_name|dataCollectionRuleName|

### group `az monitor data-collection rule association`
#### <a name="DataCollectionRuleAssociationsListByRule">Command `az monitor data-collection rule association list`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsListByRule">Example</a>
```
az monitor data-collection rule association list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRuleAssociationsListByRule">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--data-collection-rule-name**|string|The name of the data collection rule. The name is case insensitive.|data_collection_rule_name|dataCollectionRuleName|

#### <a name="DataCollectionRuleAssociationsListByResource">Command `az monitor data-collection rule association list`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsListByResource">Example</a>
```
az monitor data-collection rule association list --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourc\
eGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsListByResource">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The identifier of the resource.|resource_uri|resourceUri|

#### <a name="DataCollectionRuleAssociationsGet">Command `az monitor data-collection rule association show`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsGet">Example</a>
```
az monitor data-collection rule association show --name "myAssociation" --resource "subscriptions/703362b3-f278-4e4b-91\
79-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The identifier of the resource.|resource_uri|resourceUri|
|**--association-name**|string|The name of the association. The name is case insensitive.|association_name|associationName|

#### <a name="DataCollectionRuleAssociationsDelete">Command `az monitor data-collection rule association delete`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsDelete">Example</a>
```
az monitor data-collection rule association delete --name "myAssociation" --resource "subscriptions/703362b3-f278-4e4b-\
9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The identifier of the resource.|resource_uri|resourceUri|
|**--association-name**|string|The name of the association. The name is case insensitive.|association_name|associationName|
