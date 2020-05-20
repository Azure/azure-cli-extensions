# Azure CLI Module Creation Report

### hardware-security-modules dedicated-hsm create

create a hardware-security-modules dedicated-hsm.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the Resource Group to which the resource belongs.|resource_group_name|
|**--name**|string|Name of the dedicated Hsm|name|
|**--location**|string|The supported Azure location where the dedicated HSM should be created.|location|
|**--sku**|object|SKU details|sku|
|**--zones**|array|The Dedicated Hsm zones.|zones|
|**--tags**|dictionary|Resource tags|tags|
|**--stamp-id**|string|This field will be used when RP does not support Availability zones.|stamp_id|
|**--network-profile-subnet**|object|Specifies the identifier of the subnet.|subnet|
|**--network-profile-network-interfaces**|array|Specifies the list of resource Ids for the network interfaces associated with the dedicated HSM.|network_interfaces|
### hardware-security-modules dedicated-hsm delete

delete a hardware-security-modules dedicated-hsm.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated HSM belongs.|resource_group_name|
|**--name**|string|The name of the dedicated HSM to delete|name|
### hardware-security-modules dedicated-hsm list

list a hardware-security-modules dedicated-hsm.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated HSM belongs.|resource_group_name|
|**--top**|integer|Maximum number of results to return.|top|
### hardware-security-modules dedicated-hsm show

show a hardware-security-modules dedicated-hsm.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the Resource Group to which the dedicated hsm belongs.|resource_group_name|
|**--name**|string|The name of the dedicated HSM.|name|
### hardware-security-modules dedicated-hsm update

update a hardware-security-modules dedicated-hsm.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the Resource Group to which the server belongs.|resource_group_name|
|**--name**|string|Name of the dedicated HSM|name|
|**--tags**|dictionary|Resource tags|tags|