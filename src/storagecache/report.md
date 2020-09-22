# Azure CLI Module Creation Report

### storagecache asc-operation show

show a storagecache asc-operation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache asc-operation|AscOperations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The region name which the operation will lookup into.|location|location|
|**--operation-id**|string|The operation id which uniquely identifies the asynchronous operation.|operation_id|operationId|

### storagecache cache create

create a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--tags**|any|ARM tags as name/value pairs.|tags|tags|
|**--location**|string|Region name string.|location|location|
|**--sku-name**|string|SKU name for this Cache.|name|name|
|**--cache-size-gb**|integer|The size of this Cache, in GB.|cache_size_gb|cacheSizeGB|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--subnet**|string|Subnet used for the Cache.|subnet|subnet|
|**--network-settings**|object|Specifies network settings of the cache.|network_settings|networkSettings|
|**--encryption-settings**|object|Specifies encryption settings of the cache.|encryption_settings|encryptionSettings|
|**--security-settings**|object|Specifies security settings of the cache.|security_settings|securitySettings|
|**--identity-type**|sealed-choice|The type of identity used for the cache|type|type|

### storagecache cache delete

delete a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache cache flush

flush a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|flush|Flush|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache cache list

list a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|

### storagecache cache show

show a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache cache start

start a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start|Start|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache cache stop

stop a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|stop|Stop|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache cache update

update a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--tags**|any|ARM tags as name/value pairs.|tags|tags|
|**--location**|string|Region name string.|location|location|
|**--sku-name**|string|SKU name for this Cache.|name|name|
|**--cache-size-gb**|integer|The size of this Cache, in GB.|cache_size_gb|cacheSizeGB|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--subnet**|string|Subnet used for the Cache.|subnet|subnet|
|**--network-settings**|object|Specifies network settings of the cache.|network_settings|networkSettings|
|**--encryption-settings**|object|Specifies encryption settings of the cache.|encryption_settings|encryptionSettings|
|**--security-settings**|object|Specifies security settings of the cache.|security_settings|securitySettings|
|**--identity-type**|sealed-choice|The type of identity used for the cache|type|type|

### storagecache cache upgrade-firmware

upgrade-firmware a storagecache cache.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache cache|Caches|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|upgrade-firmware|UpgradeFirmware|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache sku list

list a storagecache sku.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache sku|Skus|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### storagecache storage-target create

create a storagecache storage-target.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache storage-target|StorageTargets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of the Storage Target. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|storage_target_name|storageTargetName|
|**--junctions**|array|List of Cache namespace junctions to target for namespace associations.|junctions|junctions|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--nfs3**|object|Properties when targetType is nfs3.|nfs3|nfs3|
|**--clfs**|object|Properties when targetType is clfs.|clfs|clfs|
|**--unknown**|object|Properties when targetType is unknown.|unknown|unknown|

### storagecache storage-target delete

delete a storagecache storage-target.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache storage-target|StorageTargets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|storageTargetName|

### storagecache storage-target list

list a storagecache storage-target.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache storage-target|StorageTargets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByCache|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|

### storagecache storage-target show

show a storagecache storage-target.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache storage-target|StorageTargets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of the Storage Target. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|storage_target_name|storageTargetName|

### storagecache storage-target update

update a storagecache storage-target.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache storage-target|StorageTargets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|resourceGroupName|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|cacheName|
|**--storage-target-name**|string|Name of the Storage Target. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|storage_target_name|storageTargetName|
|**--junctions**|array|List of Cache namespace junctions to target for namespace associations.|junctions|junctions|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|provisioningState|
|**--nfs3**|object|Properties when targetType is nfs3.|nfs3|nfs3|
|**--clfs**|object|Properties when targetType is clfs.|clfs|clfs|
|**--unknown**|object|Properties when targetType is unknown.|unknown|unknown|

### storagecache usage-model list

list a storagecache usage-model.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagecache usage-model|UsageModels|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
