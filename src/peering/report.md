# Azure CLI Module Creation Report

### peering asn check-service-provider-availability

check-service-provider-availability a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peering-service-location**|string|Gets or sets the peering service location.|peering_service_location|
|**--peering-service-provider**|string|Gets or sets the peering service provider.|peering_service_provider|
### peering asn create

create a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--location**|string|The location of the resource.|location|
|**--sku**|object|The SKU that defines the type of the peering service.|sku|
|**--tags**|dictionary|The resource tags.|tags|
|**--peering-service-location**|string|The PeeringServiceLocation of the Customer.|peering_service_location|
|**--peering-service-provider**|string|The MAPS Provider Name.|peering_service_provider|
### peering asn delete

delete a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
### peering asn list

list a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
### peering asn show

show a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering.|peering_service_name|
### peering asn update

update a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--tags**|dictionary|Gets or sets the tags, a dictionary of descriptors arm object|tags|