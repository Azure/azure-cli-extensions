# Azure CLI Module Creation Report

### windowsiotservices service check-device-service-name-availability

check-device-service-name-availability a windowsiotservices service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|windowsiotservices service|Services|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|check-device-service-name-availability|CheckDeviceServiceNameAvailability|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the Windows IoT Device Service to check.|name|name|

### windowsiotservices service create

create a windowsiotservices service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|windowsiotservices service|Services|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
|**--if-match**|string|ETag of the Windows IoT Device Service. Do not specify for creating a new Windows IoT Device Service. Required to update an existing Windows IoT Device Service.|if_match|If-Match|
|**--notes**|string|Windows IoT Device Service notes.|notes|notes|
|**--quantity**|integer|Windows IoT Device Service device allocation,|quantity|quantity|
|**--billing-domain-name**|string|Windows IoT Device Service ODM AAD domain|billing_domain_name|billingDomainName|
|**--admin-domain-name**|string|Windows IoT Device Service OEM AAD domain|admin_domain_name|adminDomainName|

### windowsiotservices service delete

delete a windowsiotservices service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|windowsiotservices service|Services|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|

### windowsiotservices service list

list a windowsiotservices service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|windowsiotservices service|Services|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|

### windowsiotservices service show

show a windowsiotservices service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|windowsiotservices service|Services|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|

### windowsiotservices service update

update a windowsiotservices service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|windowsiotservices service|Services|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group that contains the Windows IoT Device Service.|resource_group_name|resourceGroupName|
|**--device-name**|string|The name of the Windows IoT Device Service.|device_name|deviceName|
|**--if-match**|string|ETag of the Windows IoT Device Service. Do not specify for creating a brand new Windows IoT Device Service. Required to update an existing Windows IoT Device Service.|if_match|If-Match|
|**--notes**|string|Windows IoT Device Service notes.|notes|notes|
|**--quantity**|integer|Windows IoT Device Service device allocation,|quantity|quantity|
|**--billing-domain-name**|string|Windows IoT Device Service ODM AAD domain|billing_domain_name|billingDomainName|
|**--admin-domain-name**|string|Windows IoT Device Service OEM AAD domain|admin_domain_name|adminDomainName|
