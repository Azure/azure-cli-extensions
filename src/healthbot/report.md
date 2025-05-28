# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az healthbot|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az healthbot` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az healthbot|Bots|[commands](#CommandsInBots)|

## COMMANDS
### <a name="CommandsInBots">Commands in `az healthbot` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az healthbot list](#BotsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersBotsListByResourceGroup)|[Example](#ExamplesBotsListByResourceGroup)|
|[az healthbot list](#BotsList)|List|[Parameters](#ParametersBotsList)|[Example](#ExamplesBotsList)|
|[az healthbot show](#BotsGet)|Get|[Parameters](#ParametersBotsGet)|[Example](#ExamplesBotsGet)|
|[az healthbot create](#BotsCreate)|Create|[Parameters](#ParametersBotsCreate)|[Example](#ExamplesBotsCreate)|
|[az healthbot update](#BotsUpdate)|Update|[Parameters](#ParametersBotsUpdate)|[Example](#ExamplesBotsUpdate)|
|[az healthbot delete](#BotsDelete)|Delete|[Parameters](#ParametersBotsDelete)|[Example](#ExamplesBotsDelete)|


## COMMAND DETAILS

### group `az healthbot`
#### <a name="BotsListByResourceGroup">Command `az healthbot list`</a>

##### <a name="ExamplesBotsListByResourceGroup">Example</a>
```
az healthbot list --resource-group "OneResourceGroupName"
```
##### <a name="ParametersBotsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|

#### <a name="BotsList">Command `az healthbot list`</a>

##### <a name="ExamplesBotsList">Example</a>
```
az healthbot list
```
##### <a name="ParametersBotsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="BotsGet">Command `az healthbot show`</a>

##### <a name="ExamplesBotsGet">Example</a>
```
az healthbot show --name "samplebotname" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|

#### <a name="BotsCreate">Command `az healthbot create`</a>

##### <a name="ExamplesBotsCreate">Example</a>
```
az healthbot create --name "samplebotname" --location "East US" --sku "F0" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--sku**|sealed-choice|The name of the HealthBot SKU|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="BotsUpdate">Command `az healthbot update`</a>

##### <a name="ExamplesBotsUpdate">Example</a>
```
az healthbot update --name "samplebotname" --sku "F0" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|
|**--tags**|dictionary|Tags for a HealthBot.|tags|tags|
|**--sku**|sealed-choice|The name of the HealthBot SKU|

#### <a name="BotsDelete">Command `az healthbot delete`</a>

##### <a name="ExamplesBotsDelete">Example</a>
```
az healthbot delete --name "samplebotname" --resource-group "healthbotClient"
```
##### <a name="ParametersBotsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Bot resource group in the user subscription.|resource_group_name|resourceGroupName|
|**--bot-name**|string|The name of the Bot resource.|bot_name|botName|
