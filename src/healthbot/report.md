# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az healthbot|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az healthbot` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az healthbot bot|Bots|[commands](#CommandsInBots)|

## COMMANDS
### <a name="CommandsInBots">Commands in `az healthbot bot` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthbot bot list](#BotsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersBotsListByResourceGroup)|[Example](#ExamplesBotsListByResourceGroup)|
|[az healthbot bot list](#BotsList)|List|[Parameters](#ParametersBotsList)|[Example](#ExamplesBotsList)|
|[az healthbot bot show](#BotsGet)|Get|[Parameters](#ParametersBotsGet)|[Example](#ExamplesBotsGet)|
|[az healthbot bot create](#BotsCreate)|Create|[Parameters](#ParametersBotsCreate)|[Example](#ExamplesBotsCreate)|
|[az healthbot bot update](#BotsUpdate)|Update|[Parameters](#ParametersBotsUpdate)|[Example](#ExamplesBotsUpdate)|
|[az healthbot bot delete](#BotsDelete)|Delete|[Parameters](#ParametersBotsDelete)|[Example](#ExamplesBotsDelete)|


## COMMAND DETAILS

### group `az healthbot bot`
#### <a name="BotsListByResourceGroup">Command `az healthbot bot list`</a>

##### <a name="ExamplesBotsListByResourceGroup">Example</a>
```
az healthbot bot list --resource-group "OneResourceGroupName"
```
##### <a name="ParametersBotsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|

#### <a name="BotsList">Command `az healthbot bot list`</a>

##### <a name="ExamplesBotsList">Example</a>
```
az healthbot bot list
```
##### <a name="ParametersBotsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="BotsGet">Command `az healthbot bot show`</a>

##### <a name="ExamplesBotsGet">Example</a>
```
az healthbot bot show --name "samplebotname" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|

#### <a name="BotsCreate">Command `az healthbot bot create`</a>

##### <a name="ExamplesBotsCreate">Example</a>
```
az healthbot bot create --name "samplebotname" --location "East US" --sku name="F0" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--sku**|object|SKU of the HealthBot.|sku|sku|

#### <a name="BotsUpdate">Command `az healthbot bot update`</a>

##### <a name="ExamplesBotsUpdate">Example</a>
```
az healthbot bot update --name "samplebotname" --sku name="F0" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|
|**--tags**|dictionary|Tags for a HealthBot.|tags|tags|
|**--sku**|object|SKU of the HealthBot.|sku|sku|

#### <a name="BotsDelete">Command `az healthbot bot delete`</a>

##### <a name="ExamplesBotsDelete">Example</a>
```
az healthbot bot delete --name "samplebotname" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|
