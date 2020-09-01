# Azure CLI Module Creation Report

### storagecache asc-operation show

show a storagecache asc-operation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The region name which the operation will lookup into.|location|
|**--operation-id**|string|The operation id which uniquely identifies the asynchronous operation.|operation_id|
### storagecache cache create

create a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
|**--tags**|any|ARM tags as name/value pairs.|tags|
|**--location**|string|Region name string.|location|
|**--sku-name**|string|SKU name for this Cache.|name_sku_name|
|**--cache-size-gb**|integer|The size of this Cache, in GB.|cache_size_gb|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|
|**--subnet**|string|Subnet used for the Cache.|subnet|
|**--network-settings**|object|Specifies network settings of the cache.|network_settings|
|**--encryption-settings**|object|Specifies encryption settings of the cache.|encryption_settings|
|**--security-settings**|object|Specifies security settings of the cache.|security_settings|
|**--identity-type**|sealed-choice|The type of identity used for the cache|type_identity_type|
### storagecache cache delete

delete a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache cache flush

flush a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache cache list

list a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
### storagecache cache show

show a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache cache start

start a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache cache stop

stop a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache cache update

update a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
|**--tags**|any|ARM tags as name/value pairs.|tags|
|**--location**|string|Region name string.|location|
|**--sku-name**|string|SKU name for this Cache.|name_sku_name|
|**--cache-size-gb**|integer|The size of this Cache, in GB.|cache_size_gb|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|
|**--subnet**|string|Subnet used for the Cache.|subnet|
|**--network-settings**|object|Specifies network settings of the cache.|network_settings|
|**--encryption-settings**|object|Specifies encryption settings of the cache.|encryption_settings|
|**--security-settings**|object|Specifies security settings of the cache.|security_settings|
|**--identity-type**|sealed-choice|The type of identity used for the cache|type_identity_type|
### storagecache cache upgrade-firmware

upgrade-firmware a storagecache cache.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache sku list

list a storagecache sku.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### storagecache storage-target create

create a storagecache storage-target.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
|**--storage-target-name**|string|Name of the Storage Target. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|storage_target_name|
|**--junctions**|array|List of Cache namespace junctions to target for namespace associations.|junctions|
|**--target-type**|choice|Type of the Storage Target.|target_type|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|
|**--nfs3**|object|Properties when targetType is nfs3.|nfs3|
|**--clfs**|object|Properties when targetType is clfs.|clfs|
|**--unknown**|object|Properties when targetType is unknown.|unknown|
### storagecache storage-target delete

delete a storagecache storage-target.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
|**--storage-target-name**|string|Name of Storage Target.|storage_target_name|
### storagecache storage-target list

list a storagecache storage-target.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
### storagecache storage-target show

show a storagecache storage-target.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
|**--storage-target-name**|string|Name of the Storage Target. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|storage_target_name|
### storagecache storage-target update

create a storagecache storage-target.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|Target resource group.|resource_group_name|
|**--cache-name**|string|Name of Cache. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|cache_name|
|**--storage-target-name**|string|Name of the Storage Target. Length of name must be not greater than 80 and chars must be in list of [-0-9a-zA-Z_] char class.|storage_target_name|
|**--junctions**|array|List of Cache namespace junctions to target for namespace associations.|junctions|
|**--target-type**|choice|Type of the Storage Target.|target_type|
|**--provisioning-state**|choice|ARM provisioning state, see https://github.com/Azure/azure-resource-manager-rpc/blob/master/v1.0/Addendum.md#provisioningstate-property|provisioning_state|
|**--nfs3**|object|Properties when targetType is nfs3.|nfs3|
|**--clfs**|object|Properties when targetType is clfs.|clfs|
|**--unknown**|object|Properties when targetType is unknown.|unknown|
### storagecache usage-model list

list a storagecache usage-model.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|