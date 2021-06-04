# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az connectedmachine|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az connectedmachine` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az connectedmachine|Machines|[commands](#CommandsInMachines)|
|az connectedmachine extension|MachineExtensions|[commands](#CommandsInMachineExtensions)|

## COMMANDS
### <a name="CommandsInMachines">Commands in `az connectedmachine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine list](#MachinesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMachinesListByResourceGroup)|[Example](#ExamplesMachinesListByResourceGroup)|
|[az connectedmachine list](#MachinesListBySubscription)|ListBySubscription|[Parameters](#ParametersMachinesListBySubscription)|[Example](#ExamplesMachinesListBySubscription)|
|[az connectedmachine show](#MachinesGet)|Get|[Parameters](#ParametersMachinesGet)|[Example](#ExamplesMachinesGet)|
|[az connectedmachine delete](#MachinesDelete)|Delete|[Parameters](#ParametersMachinesDelete)|[Example](#ExamplesMachinesDelete)|

### <a name="CommandsInMachineExtensions">Commands in `az connectedmachine extension` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine extension list](#MachineExtensionsList)|List|[Parameters](#ParametersMachineExtensionsList)|[Example](#ExamplesMachineExtensionsList)|
|[az connectedmachine extension show](#MachineExtensionsGet)|Get|[Parameters](#ParametersMachineExtensionsGet)|[Example](#ExamplesMachineExtensionsGet)|
|[az connectedmachine extension create](#MachineExtensionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMachineExtensionsCreateOrUpdate#Create)|[Example](#ExamplesMachineExtensionsCreateOrUpdate#Create)|
|[az connectedmachine extension update](#MachineExtensionsUpdate)|Update|[Parameters](#ParametersMachineExtensionsUpdate)|[Example](#ExamplesMachineExtensionsUpdate)|
|[az connectedmachine extension delete](#MachineExtensionsDelete)|Delete|[Parameters](#ParametersMachineExtensionsDelete)|[Example](#ExamplesMachineExtensionsDelete)|


## COMMAND DETAILS

### group `az connectedmachine`
#### <a name="MachinesListByResourceGroup">Command `az connectedmachine list`</a>

##### <a name="ExamplesMachinesListByResourceGroup">Example</a>
```
az connectedmachine list --resource-group "myResourceGroup"
```
##### <a name="ParametersMachinesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

#### <a name="MachinesListBySubscription">Command `az connectedmachine list`</a>

##### <a name="ExamplesMachinesListBySubscription">Example</a>
```
az connectedmachine list
```
##### <a name="ParametersMachinesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="MachinesGet">Command `az connectedmachine show`</a>

##### <a name="ExamplesMachinesGet">Example</a>
```
az connectedmachine show --name "myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachinesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|name|

#### <a name="MachinesDelete">Command `az connectedmachine delete`</a>

##### <a name="ExamplesMachinesDelete">Example</a>
```
az connectedmachine delete --name "myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachinesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|name|

### group `az connectedmachine extension`
#### <a name="MachineExtensionsList">Command `az connectedmachine extension list`</a>

##### <a name="ExamplesMachineExtensionsList">Example</a>
```
az connectedmachine extension list --machine-name "myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachineExtensionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine containing the extension.|machine_name|name|
|**--expand**|string|The expand expression to apply on the operation.|expand|$expand|

#### <a name="MachineExtensionsGet">Command `az connectedmachine extension show`</a>

##### <a name="ExamplesMachineExtensionsGet">Example</a>
```
az connectedmachine extension show --machine-name "myMachine" --n "CustomScriptExtension" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersMachineExtensionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine containing the extension.|machine_name|name|
|**--name**|string|The name of the machine extension.|name|extensionName|

#### <a name="MachineExtensionsCreateOrUpdate#Create">Command `az connectedmachine extension create`</a>

##### <a name="ExamplesMachineExtensionsCreateOrUpdate#Create">Example</a>
```
az connectedmachine extension create --machine-name "myMachine" --n "CustomScriptExtension" --location "eastus2euap" \
--type "CustomScriptExtension" --publisher "Microsoft.Compute" --settings "{\\"commandToExecute\\":\\"powershell.exe \
-c \\\\\\"Get-Process | Where-Object { $_.CPU -gt 10000 }\\\\\\"\\"}" --type-handler-version "1.10" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersMachineExtensionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be created or updated.|machine_name|name|
|**--name**|string|The name of the machine extension.|name|extensionName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--force-update-tag**|string|How the extension handler should be forced to update even if the extension configuration has not changed.|force_update_tag|forceUpdateTag|
|**--publisher**|string|The name of the extension handler publisher.|publisher|publisher|
|**--type**|string|Specifies the type of the extension; an example is "CustomScriptExtension".|type|type|
|**--type-handler-version**|string|Specifies the version of the script handler.|type_handler_version|typeHandlerVersion|
|**--auto-upgrade-minor-version**|boolean|Indicates whether the extension should use a newer minor version if one is available at deployment time. Once deployed, however, the extension will not upgrade minor versions unless redeployed, even with this property set to true.|auto_upgrade_minor_version|autoUpgradeMinorVersion|
|**--settings**|any|Json formatted public settings for the extension.|settings|settings|
|**--protected-settings**|any|The extension can contain either protectedSettings or protectedSettingsFromKeyVault or no protected settings at all.|protected_settings|protectedSettings|

#### <a name="MachineExtensionsUpdate">Command `az connectedmachine extension update`</a>

##### <a name="ExamplesMachineExtensionsUpdate">Example</a>
```
az connectedmachine extension update --machine-name "myMachine" --n "CustomScriptExtension" --type \
"CustomScriptExtension" --publisher "Microsoft.Compute" --settings "{\\"commandToExecute\\":\\"powershell.exe -c \
\\\\\\"Get-Process | Where-Object { $_.CPU -lt 100 }\\\\\\"\\"}" --type-handler-version "1.10" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersMachineExtensionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be created or updated.|machine_name|name|
|**--name**|string|The name of the machine extension.|name|extensionName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--force-update-tag**|string|How the extension handler should be forced to update even if the extension configuration has not changed.|force_update_tag|forceUpdateTag|
|**--publisher**|string|The name of the extension handler publisher.|publisher|publisher|
|**--type**|string|Specifies the type of the extension; an example is "CustomScriptExtension".|type|type|
|**--type-handler-version**|string|Specifies the version of the script handler.|type_handler_version|typeHandlerVersion|
|**--auto-upgrade-minor-version**|boolean|Indicates whether the extension should use a newer minor version if one is available at deployment time. Once deployed, however, the extension will not upgrade minor versions unless redeployed, even with this property set to true.|auto_upgrade_minor_version|autoUpgradeMinorVersion|
|**--settings**|any|Json formatted public settings for the extension.|settings|settings|
|**--protected-settings**|any|The extension can contain either protectedSettings or protectedSettingsFromKeyVault or no protected settings at all.|protected_settings|protectedSettings|

#### <a name="MachineExtensionsDelete">Command `az connectedmachine extension delete`</a>

##### <a name="ExamplesMachineExtensionsDelete">Example</a>
```
az connectedmachine extension delete --machine-name "myMachine" --n "MMA" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachineExtensionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be deleted.|machine_name|name|
|**--name**|string|The name of the machine extension.|name|extensionName|
