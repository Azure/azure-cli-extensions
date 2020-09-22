# Azure CLI Module Creation Report

### hardware-security-modules dedicated-hsm create

create a hardware-security-modules dedicated-hsm.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|hardware-security-modules dedicated-hsm|DedicatedHsm|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the resource belongs.|resource_group_name|resourceGroupName|
|**--name**|string|Name of the dedicated Hsm|name|name|
|**--location**|string|The supported Azure location where the dedicated HSM should be created.|location|location|
|**--zones**|array|The Dedicated Hsm zones.|zones|zones|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--stamp-id**|string|This field will be used when RP does not support Availability zones.|stamp_id|stampId|
|**--network-profile-subnet**|object|Specifies the identifier of the subnet.|subnet|subnet|
|**--network-profile-network-interfaces**|array|Specifies the list of resource Ids for the network interfaces associated with the dedicated HSM.|network_interfaces|networkInterfaces|

### hardware-security-modules dedicated-hsm delete

delete a hardware-security-modules dedicated-hsm.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|hardware-security-modules dedicated-hsm|DedicatedHsm|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated HSM belongs.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the dedicated HSM to delete|name|name|

### hardware-security-modules dedicated-hsm list

list a hardware-security-modules dedicated-hsm.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|hardware-security-modules dedicated-hsm|DedicatedHsm|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated HSM belongs.|resource_group_name|resourceGroupName|
|**--top**|integer|Maximum number of results to return.|top|$top|

### hardware-security-modules dedicated-hsm show

show a hardware-security-modules dedicated-hsm.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|hardware-security-modules dedicated-hsm|DedicatedHsm|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated hsm belongs.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the dedicated HSM.|name|name|

### hardware-security-modules dedicated-hsm update

update a hardware-security-modules dedicated-hsm.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|hardware-security-modules dedicated-hsm|DedicatedHsm|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the Resource Group to which the server belongs.|resource_group_name|resourceGroupName|
|**--name**|string|Name of the dedicated HSM|name|name|
|**--tags**|dictionary|Resource tags|tags|tags|
