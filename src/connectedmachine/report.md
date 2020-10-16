# Azure CLI Module Creation Report

### connectedmachine machine delete

delete a connectedmachine machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine|Machines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|name|

### connectedmachine machine list

list a connectedmachine machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine|Machines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|

### connectedmachine machine show

show a connectedmachine machine.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine|Machines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the hybrid machine.|machine_name|name|

### connectedmachine machine-extension create

create a connectedmachine machine-extension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine-extension|MachineExtensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
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

### connectedmachine machine-extension delete

delete a connectedmachine machine-extension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine-extension|MachineExtensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine where the extension should be deleted.|machine_name|name|
|**--name**|string|The name of the machine extension.|name|extensionName|

### connectedmachine machine-extension list

list a connectedmachine machine-extension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine-extension|MachineExtensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine containing the extension.|machine_name|name|
|**--expand**|string|The expand expression to apply on the operation.|expand|$expand|

### connectedmachine machine-extension show

show a connectedmachine machine-extension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine-extension|MachineExtensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|resourceGroupName|
|**--machine-name**|string|The name of the machine containing the extension.|machine_name|name|
|**--name**|string|The name of the machine extension.|name|extensionName|

### connectedmachine machine-extension update

update a connectedmachine machine-extension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|connectedmachine machine-extension|MachineExtensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
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
