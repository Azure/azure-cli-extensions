# Azure CLI Module Creation Report

### asn check-service-provider-availability

check-service-provider-availability a asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peering-service-location**|string|Gets or sets the peering service location.|peering_service_location|
|**--peering-service-provider**|string|Gets or sets the peering service provider.|peering_service_provider|
### asn create

create a asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--location**|string|The location of the resource.|location|
|**--sku**|object|The SKU that defines the type of the peering service.|sku|
|**--tags**|dictionary|The resource tags.|tags|
|**--peering-service-location**|string|The PeeringServiceLocation of the Customer.|peering_service_location|
|**--peering-service-provider**|string|The MAPS Provider Name.|peering_service_provider|
### asn delete

delete a asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
### asn list

list a asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
### asn show

show a asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering.|peering_service_name|
### asn update

update a asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--tags**|dictionary|Gets or sets the tags, a dictionary of descriptors arm object|tags|