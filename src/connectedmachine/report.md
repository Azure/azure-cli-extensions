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
|az connectedmachine||[commands](#CommandsIn)|
|az connectedmachine extension|MachineExtensions|[commands](#CommandsInMachineExtensions)|
|az connectedmachine private-endpoint-connection|PrivateEndpointConnections|[commands](#CommandsInPrivateEndpointConnections)|
|az connectedmachine private-link-resource|PrivateLinkResources|[commands](#CommandsInPrivateLinkResources)|
|az connectedmachine private-link-scope|PrivateLinkScopes|[commands](#CommandsInPrivateLinkScopes)|

## COMMANDS
### <a name="CommandsInMachines">Commands in `az connectedmachine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine list](#MachinesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMachinesListByResourceGroup)|[Example](#ExamplesMachinesListByResourceGroup)|
|[az connectedmachine list](#MachinesListBySubscription)|ListBySubscription|[Parameters](#ParametersMachinesListBySubscription)|[Example](#ExamplesMachinesListBySubscription)|
|[az connectedmachine show](#MachinesGet)|Get|[Parameters](#ParametersMachinesGet)|[Example](#ExamplesMachinesGet)|
|[az connectedmachine delete](#MachinesDelete)|Delete|[Parameters](#ParametersMachinesDelete)|[Example](#ExamplesMachinesDelete)|

### <a name="CommandsIn">Commands in `az connectedmachine` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine upgrade-extension](#UpgradeExtensions)|UpgradeExtensions|[Parameters](#ParametersUpgradeExtensions)|[Example](#ExamplesUpgradeExtensions)|

### <a name="CommandsInMachineExtensions">Commands in `az connectedmachine extension` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine extension list](#MachineExtensionsList)|List|[Parameters](#ParametersMachineExtensionsList)|[Example](#ExamplesMachineExtensionsList)|
|[az connectedmachine extension show](#MachineExtensionsGet)|Get|[Parameters](#ParametersMachineExtensionsGet)|[Example](#ExamplesMachineExtensionsGet)|
|[az connectedmachine extension create](#MachineExtensionsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMachineExtensionsCreateOrUpdate#Create)|[Example](#ExamplesMachineExtensionsCreateOrUpdate#Create)|
|[az connectedmachine extension update](#MachineExtensionsUpdate)|Update|[Parameters](#ParametersMachineExtensionsUpdate)|[Example](#ExamplesMachineExtensionsUpdate)|
|[az connectedmachine extension delete](#MachineExtensionsDelete)|Delete|[Parameters](#ParametersMachineExtensionsDelete)|[Example](#ExamplesMachineExtensionsDelete)|

### <a name="CommandsInPrivateEndpointConnections">Commands in `az connectedmachine private-endpoint-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine private-endpoint-connection list](#PrivateEndpointConnectionsListByPrivateLinkScope)|ListByPrivateLinkScope|[Parameters](#ParametersPrivateEndpointConnectionsListByPrivateLinkScope)|[Example](#ExamplesPrivateEndpointConnectionsListByPrivateLinkScope)|
|[az connectedmachine private-endpoint-connection show](#PrivateEndpointConnectionsGet)|Get|[Parameters](#ParametersPrivateEndpointConnectionsGet)|[Example](#ExamplesPrivateEndpointConnectionsGet)|
|[az connectedmachine private-endpoint-connection update](#PrivateEndpointConnectionsUpdate)|Update|[Parameters](#ParametersPrivateEndpointConnectionsUpdate)|[Example](#ExamplesPrivateEndpointConnectionsUpdate)|
|[az connectedmachine private-endpoint-connection delete](#PrivateEndpointConnectionsDelete)|Delete|[Parameters](#ParametersPrivateEndpointConnectionsDelete)|[Example](#ExamplesPrivateEndpointConnectionsDelete)|

### <a name="CommandsInPrivateLinkResources">Commands in `az connectedmachine private-link-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine private-link-resource list](#PrivateLinkResourcesListByPrivateLinkScope)|ListByPrivateLinkScope|[Parameters](#ParametersPrivateLinkResourcesListByPrivateLinkScope)|[Example](#ExamplesPrivateLinkResourcesListByPrivateLinkScope)|
|[az connectedmachine private-link-resource show](#PrivateLinkResourcesGet)|Get|[Parameters](#ParametersPrivateLinkResourcesGet)|[Example](#ExamplesPrivateLinkResourcesGet)|

### <a name="CommandsInPrivateLinkScopes">Commands in `az connectedmachine private-link-scope` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connectedmachine private-link-scope list](#PrivateLinkScopesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersPrivateLinkScopesListByResourceGroup)|[Example](#ExamplesPrivateLinkScopesListByResourceGroup)|
|[az connectedmachine private-link-scope list](#PrivateLinkScopesList)|List|[Parameters](#ParametersPrivateLinkScopesList)|[Example](#ExamplesPrivateLinkScopesList)|
|[az connectedmachine private-link-scope show](#PrivateLinkScopesGet)|Get|[Parameters](#ParametersPrivateLinkScopesGet)|[Example](#ExamplesPrivateLinkScopesGet)|
|[az connectedmachine private-link-scope create](#PrivateLinkScopesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersPrivateLinkScopesCreateOrUpdate#Create)|[Example](#ExamplesPrivateLinkScopesCreateOrUpdate#Create)|
|[az connectedmachine private-link-scope update](#PrivateLinkScopesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersPrivateLinkScopesCreateOrUpdate#Update)|[Example](#ExamplesPrivateLinkScopesCreateOrUpdate#Update)|
|[az connectedmachine private-link-scope delete](#PrivateLinkScopesDelete)|Delete|[Parameters](#ParametersPrivateLinkScopesDelete)|[Example](#ExamplesPrivateLinkScopesDelete)|
|[az connectedmachine private-link-scope update-tag](#PrivateLinkScopesUpdateTags)|UpdateTags|[Parameters](#ParametersPrivateLinkScopesUpdateTags)|[Example](#ExamplesPrivateLinkScopesUpdateTags)|


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
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

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
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|machineName|

#### <a name="MachinesDelete">Command `az connectedmachine delete`</a>

##### <a name="ExamplesMachinesDelete">Example</a>
```
az connectedmachine delete --name "myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachinesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|machineName|

### group `az connectedmachine`
#### <a name="UpgradeExtensions">Command `az connectedmachine upgrade-extension`</a>

##### <a name="ExamplesUpgradeExtensions">Example</a>
```
az connectedmachine upgrade-extension --extension-targets "{\\"Microsoft.Azure.Monitoring\\":{\\"targetVersion\\":\\"2.\
0\\"},\\"Microsoft.Compute.CustomScriptExtension\\":{\\"targetVersion\\":\\"1.10\\"}}" --machine-name "myMachine" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersUpgradeExtensions">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|machineName|
|**--extension-targets**|dictionary|Describes the Extension Target Properties.|extension_targets|extensionTargets|

### group `az connectedmachine extension`
#### <a name="MachineExtensionsList">Command `az connectedmachine extension list`</a>

##### <a name="ExamplesMachineExtensionsList">Example</a>
```
az connectedmachine extension list --machine-name "myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachineExtensionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine containing the extension.|machine_name|machineName|
|**--expand**|string|The expand expression to apply on the operation.|expand|$expand|

#### <a name="MachineExtensionsGet">Command `az connectedmachine extension show`</a>

##### <a name="ExamplesMachineExtensionsGet">Example</a>
```
az connectedmachine extension show --name "CustomScriptExtension" --machine-name "myMachine" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersMachineExtensionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine containing the extension.|machine_name|machineName|
|**--name**|string|The name of the machine extension.|name|extensionName|

#### <a name="MachineExtensionsCreateOrUpdate#Create">Command `az connectedmachine extension create`</a>

##### <a name="ExamplesMachineExtensionsCreateOrUpdate#Create">Example</a>
```
az connectedmachine extension create --name "CustomScriptExtension" --location "eastus2euap" --type \
"CustomScriptExtension" --publisher "Microsoft.Compute" --settings "{\\"commandToExecute\\":\\"powershell.exe -c \
\\\\\\"Get-Process | Where-Object { $_.CPU -gt 10000 }\\\\\\"\\"}" --type-handler-version "1.10" --machine-name \
"myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachineExtensionsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be created or updated.|machine_name|machineName|
|**--name**|string|The name of the machine extension.|name|extensionName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--force-update-tag**|string|How the extension handler should be forced to update even if the extension configuration has not changed.|force_update_tag|forceUpdateTag|
|**--publisher**|string|The name of the extension handler publisher.|publisher|publisher|
|**--type**|string|Specifies the type of the extension; an example is "CustomScriptExtension".|type|type|
|**--type-handler-version**|string|Specifies the version of the script handler.|type_handler_version|typeHandlerVersion|
|**--enable-auto-upgrade**|boolean|Indicates whether the extension should be automatically upgraded by the platform if there is a newer version available.|enable_auto_upgrade|enableAutomaticUpgrade|
|**--auto-upgrade-minor**|boolean|Indicates whether the extension should use a newer minor version if one is available at deployment time. Once deployed, however, the extension will not upgrade minor versions unless redeployed, even with this property set to true.|auto_upgrade_minor|autoUpgradeMinorVersion|
|**--settings**|any|Json formatted public settings for the extension.|settings|settings|
|**--protected-settings**|any|The extension can contain either protectedSettings or protectedSettingsFromKeyVault or no protected settings at all.|protected_settings|protectedSettings|
|**--name**|string|The machine extension name.|name|name|
|**--instance-view-type**|string|Specifies the type of the extension; an example is "CustomScriptExtension".|instance_view_type|type|
|**--inst-handler-version**|string|Specifies the version of the script handler.|inst_handler_version|typeHandlerVersion|
|**--status**|object|Instance view status.|status|status|

#### <a name="MachineExtensionsUpdate">Command `az connectedmachine extension update`</a>

##### <a name="ExamplesMachineExtensionsUpdate">Example</a>
```
az connectedmachine extension update --name "CustomScriptExtension" --type "CustomScriptExtension" --publisher \
"Microsoft.Compute" --settings "{\\"commandToExecute\\":\\"powershell.exe -c \\\\\\"Get-Process | Where-Object { \
$_.CPU -lt 100 }\\\\\\"\\"}" --type-handler-version "1.10" --machine-name "myMachine" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersMachineExtensionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be created or updated.|machine_name|machineName|
|**--name**|string|The name of the machine extension.|name|extensionName|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--force-update-tag**|string|How the extension handler should be forced to update even if the extension configuration has not changed.|force_update_tag|forceUpdateTag|
|**--publisher**|string|The name of the extension handler publisher.|publisher|publisher|
|**--type**|string|Specifies the type of the extension; an example is "CustomScriptExtension".|type|type|
|**--type-handler-version**|string|Specifies the version of the script handler.|type_handler_version|typeHandlerVersion|
|**--enable-auto-upgrade**|boolean|Indicates whether the extension should be automatically upgraded by the platform if there is a newer version available.|enable_auto_upgrade|enableAutomaticUpgrade|
|**--auto-upgrade-minor**|boolean|Indicates whether the extension should use a newer minor version if one is available at deployment time. Once deployed, however, the extension will not upgrade minor versions unless redeployed, even with this property set to true.|auto_upgrade_minor|autoUpgradeMinorVersion|
|**--settings**|any|Json formatted public settings for the extension.|settings|settings|
|**--protected-settings**|any|The extension can contain either protectedSettings or protectedSettingsFromKeyVault or no protected settings at all.|protected_settings|protectedSettings|

#### <a name="MachineExtensionsDelete">Command `az connectedmachine extension delete`</a>

##### <a name="ExamplesMachineExtensionsDelete">Example</a>
```
az connectedmachine extension delete --name "MMA" --machine-name "myMachine" --resource-group "myResourceGroup"
```
##### <a name="ParametersMachineExtensionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be deleted.|machine_name|machineName|
|**--name**|string|The name of the machine extension.|name|extensionName|

### group `az connectedmachine private-endpoint-connection`
#### <a name="PrivateEndpointConnectionsListByPrivateLinkScope">Command `az connectedmachine private-endpoint-connection list`</a>

##### <a name="ExamplesPrivateEndpointConnectionsListByPrivateLinkScope">Example</a>
```
az connectedmachine private-endpoint-connection list --resource-group "myResourceGroup" --scope-name \
"myPrivateLinkScope"
```
##### <a name="ParametersPrivateEndpointConnectionsListByPrivateLinkScope">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|

#### <a name="PrivateEndpointConnectionsGet">Command `az connectedmachine private-endpoint-connection show`</a>

##### <a name="ExamplesPrivateEndpointConnectionsGet">Example</a>
```
az connectedmachine private-endpoint-connection show --name "private-endpoint-connection-name" --resource-group \
"myResourceGroup" --scope-name "myPrivateLinkScope"
```
##### <a name="ParametersPrivateEndpointConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection.|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsUpdate">Command `az connectedmachine private-endpoint-connection update`</a>

##### <a name="ExamplesPrivateEndpointConnectionsUpdate">Example</a>
```
az connectedmachine private-endpoint-connection update --connection-state description="Approved by \
johndoe@contoso.com" status="Approved" --name "private-endpoint-connection-name" --resource-group "myResourceGroup" \
--scope-name "myPrivateLinkScope"
```
##### <a name="ParametersPrivateEndpointConnectionsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection.|private_endpoint_connection_name|privateEndpointConnectionName|
|**--connection-state**|object|Connection state of the private endpoint connection.|connection_state|privateLinkServiceConnectionState|
|**--id**|string|Resource id of the private endpoint.|id|id|

#### <a name="PrivateEndpointConnectionsDelete">Command `az connectedmachine private-endpoint-connection delete`</a>

##### <a name="ExamplesPrivateEndpointConnectionsDelete">Example</a>
```
az connectedmachine private-endpoint-connection delete --name "private-endpoint-connection-name" --resource-group \
"myResourceGroup" --scope-name "myPrivateLinkScope"
```
##### <a name="ParametersPrivateEndpointConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection.|private_endpoint_connection_name|privateEndpointConnectionName|

### group `az connectedmachine private-link-resource`
#### <a name="PrivateLinkResourcesListByPrivateLinkScope">Command `az connectedmachine private-link-resource list`</a>

##### <a name="ExamplesPrivateLinkResourcesListByPrivateLinkScope">Example</a>
```
az connectedmachine private-link-resource list --resource-group "myResourceGroup" --scope-name "myPrivateLinkScope"
```
##### <a name="ParametersPrivateLinkResourcesListByPrivateLinkScope">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|

#### <a name="PrivateLinkResourcesGet">Command `az connectedmachine private-link-resource show`</a>

##### <a name="ExamplesPrivateLinkResourcesGet">Example</a>
```
az connectedmachine private-link-resource show --group-name "hybridcompute" --resource-group "myResourceGroup" \
--scope-name "myPrivateLinkScope"
```
##### <a name="ParametersPrivateLinkResourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--group-name**|string|The name of the private link resource.|group_name|groupName|

### group `az connectedmachine private-link-scope`
#### <a name="PrivateLinkScopesListByResourceGroup">Command `az connectedmachine private-link-scope list`</a>

##### <a name="ExamplesPrivateLinkScopesListByResourceGroup">Example</a>
```
az connectedmachine private-link-scope list --resource-group "my-resource-group"
```
##### <a name="ParametersPrivateLinkScopesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="PrivateLinkScopesList">Command `az connectedmachine private-link-scope list`</a>

##### <a name="ExamplesPrivateLinkScopesList">Example</a>
```
az connectedmachine private-link-scope list
```
##### <a name="ParametersPrivateLinkScopesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="PrivateLinkScopesGet">Command `az connectedmachine private-link-scope show`</a>

##### <a name="ExamplesPrivateLinkScopesGet">Example</a>
```
az connectedmachine private-link-scope show --resource-group "my-resource-group" --scope-name "my-privatelinkscope"
```
##### <a name="ParametersPrivateLinkScopesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|

#### <a name="PrivateLinkScopesCreateOrUpdate#Create">Command `az connectedmachine private-link-scope create`</a>

##### <a name="ExamplesPrivateLinkScopesCreateOrUpdate#Create">Example</a>
```
az connectedmachine private-link-scope create --location "westus" --resource-group "my-resource-group" --scope-name \
"my-privatelinkscope"
```
##### <a name="ParametersPrivateLinkScopesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--public-network-access**|choice|Indicates whether machines associated with the private link scope can also use public Azure Arc service endpoints.|public_network_access|publicNetworkAccess|

#### <a name="PrivateLinkScopesCreateOrUpdate#Update">Command `az connectedmachine private-link-scope update`</a>

##### <a name="ExamplesPrivateLinkScopesCreateOrUpdate#Update">Example</a>
```
az connectedmachine private-link-scope update --location "westus" --tags Tag1="Value1" --resource-group \
"my-resource-group" --scope-name "my-privatelinkscope"
```
##### <a name="ParametersPrivateLinkScopesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--public-network-access**|choice|Indicates whether machines associated with the private link scope can also use public Azure Arc service endpoints.|public_network_access|publicNetworkAccess|

#### <a name="PrivateLinkScopesDelete">Command `az connectedmachine private-link-scope delete`</a>

##### <a name="ExamplesPrivateLinkScopesDelete">Example</a>
```
az connectedmachine private-link-scope delete --resource-group "my-resource-group" --scope-name "my-privatelinkscope"
```
##### <a name="ParametersPrivateLinkScopesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|

#### <a name="PrivateLinkScopesUpdateTags">Command `az connectedmachine private-link-scope update-tag`</a>

##### <a name="ExamplesPrivateLinkScopesUpdateTags">Example</a>
```
az connectedmachine private-link-scope update-tag --tags Tag1="Value1" Tag2="Value2" --resource-group \
"my-resource-group" --scope-name "my-privatelinkscope"
```
##### <a name="ParametersPrivateLinkScopesUpdateTags">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--scope-name**|string|The name of the Azure Arc PrivateLinkScope resource.|scope_name|scopeName|
|**--tags**|dictionary|Resource tags|tags|tags|
