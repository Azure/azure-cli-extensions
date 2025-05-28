# Azure CLI Module Creation Report

### peering  check-service-provider-availability

check-service-provider-availability a peering .

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peering-service-location**|string|Gets or sets the peering service location.|peering_service_location|
|**--peering-service-provider**|string|Gets or sets the peering service provider.|peering_service_provider|
### peering asn create

create a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peer-asn-name**|string|The peer ASN name.|peer_asn_name|
|**--peer-asn**|integer|The Autonomous System Number (ASN) of the peer.|peer_asn|
|**--peer-contact-detail**|array|The contact details of the peer.|peer_contact_detail|
|**--peer-name**|string|The name of the peer.|peer_name|
|**--validation-state**|choice|The validation state of the ASN associated with the peer.|validation_state|
### peering asn delete

delete a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peer-asn-name**|string|The peer ASN name.|peer_asn_name|
### peering asn list

list a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### peering asn show

show a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peer-asn-name**|string|The peer ASN name.|peer_asn_name|
### peering asn update

create a peering asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peer-asn-name**|string|The peer ASN name.|peer_asn_name|
|**--peer-asn**|integer|The Autonomous System Number (ASN) of the peer.|peer_asn|
|**--peer-contact-detail**|array|The contact details of the peer.|peer_contact_detail|
|**--peer-name**|string|The name of the peer.|peer_name|
|**--validation-state**|choice|The validation state of the ASN associated with the peer.|validation_state|
### peering legacy list

list a peering legacy.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--peering-location**|string|The location of the peering.|peering_location|
|**--kind**|choice|The kind of the peering.|kind|
|**--asn**|integer|The ASN number associated with a legacy peering.|asn|
### peering location list

list a peering location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--kind**|choice|The kind of the peering.|kind|
|**--direct-peering-type**|choice|The type of direct peering.|direct_peering_type|
### peering peering create

create a peering peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--sku**|object|The SKU that defines the tier and kind of the peering.|sku|
|**--kind**|choice|The kind of the peering.|kind|
|**--location**|string|The location of the resource.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--direct**|object|The properties that define a direct peering.|direct|
|**--exchange**|object|The properties that define an exchange peering.|exchange|
|**--peering-location**|string|The location of the peering.|peering_location|
### peering peering delete

delete a peering peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
### peering peering list

list a peering peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
### peering peering show

show a peering peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
### peering peering update

update a peering peering.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--tags**|dictionary|Gets or sets the tags, a dictionary of descriptors arm object|tags|
### peering received-route list

list a peering received-route.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--prefix**|string|The optional prefix that can be used to filter the routes.|prefix|
|**--as-path**|string|The optional AS path that can be used to filter the routes.|as_path|
|**--origin-as-validation-state**|string|The optional origin AS validation state that can be used to filter the routes.|origin_as_validation_state|
|**--rpki-validation-state**|string|The optional RPKI validation state that can be used to filter the routes.|rpki_validation_state|
|**--skip-token**|string|The optional page continuation token that is used in the event of paginated result.|skip_token|
### peering registered-asn create

create a peering registered-asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-asn-name**|string|The name of the ASN.|registered_asn_name|
|**--asn**|integer|The customer's ASN from which traffic originates.|asn|
### peering registered-asn delete

delete a peering registered-asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-asn-name**|string|The name of the registered ASN.|registered_asn_name|
### peering registered-asn list

list a peering registered-asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
### peering registered-asn show

show a peering registered-asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-asn-name**|string|The name of the registered ASN.|registered_asn_name|
### peering registered-asn update

create a peering registered-asn.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-asn-name**|string|The name of the ASN.|registered_asn_name|
|**--asn**|integer|The customer's ASN from which traffic originates.|asn|
### peering registered-prefix create

create a peering registered-prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-prefix-name**|string|The name of the registered prefix.|registered_prefix_name|
|**--prefix**|string|The customer's prefix from which traffic originates.|prefix|
### peering registered-prefix delete

delete a peering registered-prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-prefix-name**|string|The name of the registered prefix.|registered_prefix_name|
### peering registered-prefix list

list a peering registered-prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
### peering registered-prefix show

show a peering registered-prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-prefix-name**|string|The name of the registered prefix.|registered_prefix_name|
### peering registered-prefix update

create a peering registered-prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-name**|string|The name of the peering.|peering_name|
|**--registered-prefix-name**|string|The name of the registered prefix.|registered_prefix_name|
|**--prefix**|string|The customer's prefix from which traffic originates.|prefix|
### peering service country list

list a peering service country.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### peering service create

create a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--location**|string|The location of the resource.|location|
|**--sku**|object|The SKU that defines the type of the peering service.|sku|
|**--tags**|dictionary|The resource tags.|tags|
|**--peering-service-location**|string|The PeeringServiceLocation of the Customer.|peering_service_location|
|**--peering-service-provider**|string|The MAPS Provider Name.|peering_service_provider|
### peering service delete

delete a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
### peering service list

list a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
### peering service location list

list a peering service location.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--country**|string|The country of interest, in which the locations are to be present.|country|
### peering service prefix create

create a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--prefix-name**|string|The name of the prefix.|prefix_name|
|**--prefix**|string|The prefix from which your traffic originates.|prefix|
|**--peering-service-prefix-key**|string|The peering service prefix key|peering_service_prefix_key|
### peering service prefix delete

delete a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--prefix-name**|string|The name of the prefix.|prefix_name|
### peering service prefix list

list a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--expand**|string|The properties to be expanded.|expand|
### peering service prefix show

show a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--prefix-name**|string|The name of the prefix.|prefix_name|
|**--expand**|string|The properties to be expanded.|expand|
### peering service prefix update

create a peering service prefix.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--prefix-name**|string|The name of the prefix.|prefix_name|
|**--prefix**|string|The prefix from which your traffic originates.|prefix|
|**--peering-service-prefix-key**|string|The peering service prefix key|peering_service_prefix_key|
### peering service provider list

list a peering service provider.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
### peering service show

show a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering.|peering_service_name|
### peering service update

update a peering service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group.|resource_group_name|
|**--peering-service-name**|string|The name of the peering service.|peering_service_name|
|**--tags**|dictionary|Gets or sets the tags, a dictionary of descriptors arm object|tags|