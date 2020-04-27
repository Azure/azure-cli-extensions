# Azure CLI Module Creation Report

## -

## peering

### peering create

create a peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering.|peering_name|peeringName|
|**--kind**|str|The kind of the peering.|/kind|/kind|
|**--location**|str|The location of the resource.|/location|/location|
|--sku-name|str|The name of the peering SKU.|/sku/name|/sku/name|
|--sku-tier|str|The tier of the peering SKU.|/sku/tier|/sku/tier|
|--sku-family|str|The family of the peering SKU.|/sku/family|/sku/family|
|--sku-size|str|The size of the peering SKU.|/sku/size|/sku/size|
|--direct-connections|dict|The set of connections that constitute a direct peering.|/direct/connections|/properties/direct/connections|
|--direct-peer-asn|dict|The reference of the peer ASN.|/direct/peer_asn|/properties/direct/peerAsn|
|--direct-direct-peering-type|str|The type of direct peering.|/direct/direct_peering_type|/properties/direct/directPeeringType|
|--exchange-connections|dict|The set of connections that constitute an exchange peering.|/exchange/connections|/properties/exchange/connections|
|--exchange-peer-asn|dict|The reference of the peer ASN.|/exchange/peer_asn|/properties/exchange/peerAsn|
|--peering-location|str|The location of the peering.|/peering_location|/properties/peeringLocation|
|--tags|dictionary|The resource tags.|/tags|/tags|

**Example: Create a direct peering**

```
peering create --resource-group MyResourceGroup
        --name MyPeering
        --sku-name Basic_Direct_Free
        --kind Direct
        --direct-direct-peering-type Edge
        --peering-location peeringLocation0
        --location eastus
```

**Example: Create an exchange peering**

```
peering create --resource-group MyResourceGroup
        --name MyPeering
        --sku-name Basic_Exchange_Free
        --kind Exchange
        --peering-location peeringLocation0
        --location eastus
```
### peering update

update a peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering.|peering_name|peeringName|
|**--kind**|str|The kind of the peering.|/kind|/kind|
|**--location**|str|The location of the resource.|/location|/location|
|--sku-name|str|The name of the peering SKU.|/sku/name|/sku/name|
|--sku-tier|str|The tier of the peering SKU.|/sku/tier|/sku/tier|
|--sku-family|str|The family of the peering SKU.|/sku/family|/sku/family|
|--sku-size|str|The size of the peering SKU.|/sku/size|/sku/size|
|--direct-connections|dict|The set of connections that constitute a direct peering.|/direct/connections|/properties/direct/connections|
|--direct-peer-asn|dict|The reference of the peer ASN.|/direct/peer_asn|/properties/direct/peerAsn|
|--direct-direct-peering-type|str|The type of direct peering.|/direct/direct_peering_type|/properties/direct/directPeeringType|
|--exchange-connections|dict|The set of connections that constitute an exchange peering.|/exchange/connections|/properties/exchange/connections|
|--exchange-peer-asn|dict|The reference of the peer ASN.|/exchange/peer_asn|/properties/exchange/peerAsn|
|--peering-location|str|The location of the peering.|/peering_location|/properties/peeringLocation|
|--tags|dictionary|The resource tags.|/tags|/tags|

**Example: Update peering tags**

```
peering update --resource-group MyResourceGroup
        --name MyPeering
```
### peering delete

delete a peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering.|peering_name|peeringName|

**Example: Delete a peering**

```
peering delete --resource-group MyResourceGroup
        --name MyPeering
```
### peering list

list a peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
### peering show

show a peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering.|peering_name|peeringName|
## peering asn

### peering asn create

create a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The peer ASN name.|peer_asn_name|peerAsnName|
|--peer-asn|number|The Autonomous System Number (ASN) of the peer.|/peer_asn|/properties/peerAsn|
|--emails|str|The list of email addresses.|/peer_contact_info/emails|/properties/peerContactInfo/emails|
|--phone|str|The list of contact numbers.|/peer_contact_info/phone|/properties/peerContactInfo/phone|
|--peer-name|str|The name of the peer.|/peer_name|/properties/peerName|
|--validation-state|str|The validation state of the ASN associated with the peer.|/validation_state|/properties/validationState|

**Example: Create a peer ASN**

```
peering asn create --name MyPeerAsn
        --peer-asn 65000
        --emails abc@contoso.com,xyz@contoso.com
        --phone "+1 (234) 567-8900"
        --peer-name Contoso
```
### peering asn update

update a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The peer ASN name.|peer_asn_name|peerAsnName|
|--peer-asn|number|The Autonomous System Number (ASN) of the peer.|/peer_asn|/properties/peerAsn|
|--emails|str|The list of email addresses.|/peer_contact_info/emails|/properties/peerContactInfo/emails|
|--phone|str|The list of contact numbers.|/peer_contact_info/phone|/properties/peerContactInfo/phone|
|--peer-name|str|The name of the peer.|/peer_name|/properties/peerName|
|--validation-state|str|The validation state of the ASN associated with the peer.|/validation_state|/properties/validationState|
### peering asn delete

delete a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The peer ASN name.|peer_asn_name|peerAsnName|

**Example: Delete a peer ASN**

```
peering asn delete --name MyPeerAsn
```
### peering asn list

list a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### peering asn show

show a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--name**|str|The peer ASN name.|peer_asn_name|peerAsnName|
## peering legacy

### peering legacy list

list a peering legacy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|--peering-location|str|The location of the peering.|peering_location|peeringLocation|
|--kind|str|The kind of the peering.|kind|kind|
## peering location

### peering location list

list a peering location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|--kind|str|The kind of the peering.|kind|kind|
|--direct-peering-type|str|The type of direct peering.|direct_peering_type|directPeeringType|
## peering service

### peering service create

create a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
|**--location**|str|The location of the resource.|/location|/location|
|--peering-service-location|str|The PeeringServiceLocation of the Customer.|/peering_service_location|/properties/peeringServiceLocation|
|--peering-service-provider|str|The MAPS Provider Name.|/peering_service_provider|/properties/peeringServiceProvider|
|--tags|dictionary|The resource tags.|/tags|/tags|

**Example: Create a  peering service**

```
peering service create --resource-group MyResourceGroup
        --name MyPeeringService
        --peering-service-location state1
        --peering-service-provider serviceProvider1
        --location eastus
```
### peering service update

update a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
|**--location**|str|The location of the resource.|/location|/location|
|--peering-service-location|str|The PeeringServiceLocation of the Customer.|/peering_service_location|/properties/peeringServiceLocation|
|--peering-service-provider|str|The MAPS Provider Name.|/peering_service_provider|/properties/peeringServiceProvider|
|--tags|dictionary|The resource tags.|/tags|/tags|

**Example: Update peering service tags**

```
peering service update --resource-group MyResourceGroup
        --name MyPeeringService
```
### peering service delete

delete a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering service.|peering_service_name|peeringServiceName|

**Example: Delete a peering service**

```
peering service delete --resource-group MyResourceGroup
        --name MyPeeringService
```
### peering service list

list a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
### peering service show

show a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
## peering service location

### peering service location list

list a peering service location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
## peering service prefix

### peering service prefix create

create a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--peering-service-name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
|**--name**|str|The name of the prefix.|prefix_name|prefixName|
|--prefix|str|The prefix from which your traffic originates.|/prefix|/properties/prefix|

**Example: Create or update a prefix for the peering service**

```
peering service prefix create --resource-group MyResourceGroup
        --peering-service-name MyPeeringService
        --name MyPeeringServicePrefix
        --prefix 192.168.1.0/24
```
### peering service prefix update

update a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--peering-service-name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
|**--name**|str|The name of the prefix.|prefix_name|prefixName|
|--prefix|str|The prefix from which your traffic originates.|/prefix|/properties/prefix|
### peering service prefix delete

delete a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--peering-service-name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
|**--name**|str|The name of the prefix.|prefix_name|prefixName|

**Example: Delete a prefix associated with the peering service**

```
peering service prefix delete --resource-group MyResourceGroup
        --peering-service-name MyPeeringService
        --name MyPeeringServicePrefix
```
### peering service prefix list

list a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--peering-service-name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
### peering service prefix show

show a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group**|str|The name of the resource group.|resource_group_name|resourceGroupName|
|**--peering-service-name**|str|The name of the peering service.|peering_service_name|peeringServiceName|
|**--name**|str|The name of the prefix.|prefix_name|prefixName|
## peering service provider

### peering service provider list

list a peering service provider.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|