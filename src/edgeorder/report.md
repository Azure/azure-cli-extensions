# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az edgeorder|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az edgeorder` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az edgeorder||[commands](#CommandsIn)|

## COMMANDS
### <a name="CommandsIn">Commands in `az edgeorder` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az edgeorder cancel-order-item](#CancelOrderItem)|CancelOrderItem|[Parameters](#ParametersCancelOrderItem)|[Example](#ExamplesCancelOrderItem)|
|[az edgeorder create-address](#CreateAddress)|CreateAddress|[Parameters](#ParametersCreateAddress)|[Example](#ExamplesCreateAddress)|
|[az edgeorder create-order-item](#CreateOrderItem)|CreateOrderItem|[Parameters](#ParametersCreateOrderItem)|[Example](#ExamplesCreateOrderItem)|
|[az edgeorder delete-address](#DeleteAddressByName)|DeleteAddressByName|[Parameters](#ParametersDeleteAddressByName)|[Example](#ExamplesDeleteAddressByName)|
|[az edgeorder delete-order-item](#DeleteOrderItemByName)|DeleteOrderItemByName|[Parameters](#ParametersDeleteOrderItemByName)|[Example](#ExamplesDeleteOrderItemByName)|
|[az edgeorder list-address-at-resource-group-level](#ListAddressesAtResourceGroupLevel)|ListAddressesAtResourceGroupLevel|[Parameters](#ParametersListAddressesAtResourceGroupLevel)|[Example](#ExamplesListAddressesAtResourceGroupLevel)|
|[az edgeorder list-address-at-subscription-level](#ListAddressesAtSubscriptionLevel)|ListAddressesAtSubscriptionLevel|[Parameters](#ParametersListAddressesAtSubscriptionLevel)|[Example](#ExamplesListAddressesAtSubscriptionLevel)|
|[az edgeorder list-configuration](#ListConfigurations)|ListConfigurations|[Parameters](#ParametersListConfigurations)|[Example](#ExamplesListConfigurations)|
|[az edgeorder list-operation](#ListOperations)|ListOperations|[Parameters](#ParametersListOperations)|[Example](#ExamplesListOperations)|
|[az edgeorder list-order-at-resource-group-level](#ListOrderAtResourceGroupLevel)|ListOrderAtResourceGroupLevel|[Parameters](#ParametersListOrderAtResourceGroupLevel)|[Example](#ExamplesListOrderAtResourceGroupLevel)|
|[az edgeorder list-order-at-subscription-level](#ListOrderAtSubscriptionLevel)|ListOrderAtSubscriptionLevel|[Parameters](#ParametersListOrderAtSubscriptionLevel)|[Example](#ExamplesListOrderAtSubscriptionLevel)|
|[az edgeorder list-order-item-at-resource-group-level](#ListOrderItemsAtResourceGroupLevel)|ListOrderItemsAtResourceGroupLevel|[Parameters](#ParametersListOrderItemsAtResourceGroupLevel)|[Example](#ExamplesListOrderItemsAtResourceGroupLevel)|
|[az edgeorder list-order-item-at-subscription-level](#ListOrderItemsAtSubscriptionLevel)|ListOrderItemsAtSubscriptionLevel|[Parameters](#ParametersListOrderItemsAtSubscriptionLevel)|[Example](#ExamplesListOrderItemsAtSubscriptionLevel)|
|[az edgeorder list-product-family](#ListProductFamilies)|ListProductFamilies|[Parameters](#ParametersListProductFamilies)|[Example](#ExamplesListProductFamilies)|
|[az edgeorder list-product-family-metadata](#ListProductFamiliesMetadata)|ListProductFamiliesMetadata|[Parameters](#ParametersListProductFamiliesMetadata)|[Example](#ExamplesListProductFamiliesMetadata)|
|[az edgeorder return-order-item](#ReturnOrderItem)|ReturnOrderItem|[Parameters](#ParametersReturnOrderItem)|[Example](#ExamplesReturnOrderItem)|
|[az edgeorder show-address](#GetAddressByName)|GetAddressByName|[Parameters](#ParametersGetAddressByName)|[Example](#ExamplesGetAddressByName)|
|[az edgeorder show-order](#GetOrderByName)|GetOrderByName|[Parameters](#ParametersGetOrderByName)|[Example](#ExamplesGetOrderByName)|
|[az edgeorder show-order-item](#GetOrderItemByName)|GetOrderItemByName|[Parameters](#ParametersGetOrderItemByName)|[Example](#ExamplesGetOrderItemByName)|
|[az edgeorder update-address](#UpdateAddress)|UpdateAddress|[Parameters](#ParametersUpdateAddress)|[Example](#ExamplesUpdateAddress)|
|[az edgeorder update-order-item](#UpdateOrderItem)|UpdateOrderItem|[Parameters](#ParametersUpdateOrderItem)|[Example](#ExamplesUpdateOrderItem)|


## COMMAND DETAILS
### group `az edgeorder`
#### <a name="CancelOrderItem">Command `az edgeorder cancel-order-item`</a>

##### <a name="ExamplesCancelOrderItem">Example</a>
```
az edgeorder cancel-order-item --reason "Order cancelled" --order-item-name "TestOrderItemName1" --resource-group \
"TestRG"
```
##### <a name="ParametersCancelOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-item-name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--reason**|string|Reason for cancellation.|reason|reason|

#### <a name="CreateAddress">Command `az edgeorder create-address`</a>

##### <a name="ExamplesCreateAddress">Example</a>
```
az edgeorder create-address --address-name "TestMSAddressName" --location "westus" --contact-details \
contact-name="Petr Cech" email-list="testemail@microsoft.com" phone="1234567890" phone-extension="" --shipping-address \
address-type="None" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" \
state-or-province="CA" street-address1="16 TOWNSEND ST" street-address2="UNIT 1" --resource-group "TestRG"
```
##### <a name="ParametersCreateAddress">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--address-name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|

#### <a name="CreateOrderItem">Command `az edgeorder create-order-item`</a>

##### <a name="ExamplesCreateOrderItem">Example</a>
```
az edgeorder create-order-item --order-item-name "TestOrderItemName01" --order-item-resource \
"{\\"location\\":\\"westus\\",\\"tags\\":{\\"carrot\\":\\"vegetable\\",\\"mango\\":\\"fruit\\"},\\"orderItemDetails\\":\
{\\"orderItemType\\":\\"Purchase\\",\\"preferences\\":{\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"Micro\
softManaged\\"}},\\"productDetails\\":{\\"hierarchyInformation\\":{\\"configurationName\\":\\"AzureStackEdgeGPU\\",\\"p\
roductFamilyName\\":\\"AzureStackEdge\\",\\"productLineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdge\
GPU\\"}}},\\"addressDetails\\":{\\"forwardAddress\\":{\\"contactDetails\\":{\\"contactName\\":\\"164 TOWNSEND \
ST\\",\\"emailList\\":[\\"ssemmail@microsoft.com\\",\\"vishwamdir@microsoft.com\\"],\\"phone\\":\\"3213131190\\"},\\"sh\
ippingAddress\\":{\\"addressType\\":\\"Residential\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\
\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND \
ST\\",\\"streetAddress2\\":\\"UNIT 1\\",\\"zipExtendedCode\\":\\"1\\"}}},\\"orderId\\":\\"/subscriptions/fa68082f-8ff7-\
4a25-95c7-ce9da541242f/resourceGroups/TestRG/providers/Microsoft.EdgeOrder/locations/westus/orders/TestOrderItemName01\
\\"}" --resource-group "TestRG"
```
##### <a name="ParametersCreateOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-item-name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--order-item-resource**|object|Order item details from request body.|order_item_resource|orderItemResource|

#### <a name="DeleteAddressByName">Command `az edgeorder delete-address`</a>

##### <a name="ExamplesDeleteAddressByName">Example</a>
```
az edgeorder delete-address --address-name "TestAddressName1" --resource-group "TestRG"
```
##### <a name="ParametersDeleteAddressByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--address-name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DeleteOrderItemByName">Command `az edgeorder delete-order-item`</a>

##### <a name="ExamplesDeleteOrderItemByName">Example</a>
```
az edgeorder delete-order-item --order-item-name "TestOrderItemName01" --resource-group "TestRG"
```
##### <a name="ParametersDeleteOrderItemByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-item-name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ListAddressesAtResourceGroupLevel">Command `az edgeorder list-address-at-resource-group-level`</a>

##### <a name="ExamplesListAddressesAtResourceGroupLevel">Example</a>
```
az edgeorder list-address-at-resource-group-level --resource-group "TestRG"
```
##### <a name="ParametersListAddressesAtResourceGroupLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--filter**|string|$filter is supported to filter based on shipping address properties. Filter supports only equals operation.|filter|$filter|
|**--skip-token**|string|$skipToken is supported on Get list of addresses, which provides the next page in the list of address.|skip_token|$skipToken|

#### <a name="ListAddressesAtSubscriptionLevel">Command `az edgeorder list-address-at-subscription-level`</a>

##### <a name="ExamplesListAddressesAtSubscriptionLevel">Example</a>
```
az edgeorder list-address-at-subscription-level
```
##### <a name="ParametersListAddressesAtSubscriptionLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|$filter is supported to filter based on shipping address properties. Filter supports only equals operation.|filter|$filter|
|**--skip-token**|string|$skipToken is supported on Get list of addresses, which provides the next page in the list of addresses.|skip_token|$skipToken|

#### <a name="ListConfigurations">Command `az edgeorder list-configuration`</a>

##### <a name="ExamplesListConfigurations">Example</a>
```
az edgeorder list-configuration --configuration-filters "[{\\"filterableProperty\\":[{\\"type\\":\\"ShipToCountries\\",\
\\"supportedValues\\":[\\"US\\"]}],\\"hierarchyInformation\\":{\\"productFamilyName\\":\\"AzureStackEdge\\",\\"productL\
ineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}]"
```
##### <a name="ParametersListConfigurations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|$skipToken is supported on list of configurations, which provides the next page in the list of configurations.|skip_token|$skipToken|
|**--configuration-filters**|array|Holds details about product hierarchy information and filterable property.|configuration_filters|configurationFilters|
|**--registered-features**|array|List of registered feature flags for subscription|registered_features|registeredFeatures|
|**--location-placement-id**|string|Location placement Id of a subscription|location_placement_id|locationPlacementId|
|**--quota-id**|string|Quota ID of a subscription|quota_id|quotaId|

#### <a name="ListOperations">Command `az edgeorder list-operation`</a>

##### <a name="ExamplesListOperations">Example</a>
```
az edgeorder list-operation
```
##### <a name="ParametersListOperations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="ListOrderAtResourceGroupLevel">Command `az edgeorder list-order-at-resource-group-level`</a>

##### <a name="ExamplesListOrderAtResourceGroupLevel">Example</a>
```
az edgeorder list-order-at-resource-group-level --resource-group "TestRG"
```
##### <a name="ParametersListOrderAtResourceGroupLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--skip-token**|string|$skipToken is supported on Get list of order, which provides the next page in the list of order.|skip_token|$skipToken|

#### <a name="ListOrderAtSubscriptionLevel">Command `az edgeorder list-order-at-subscription-level`</a>

##### <a name="ExamplesListOrderAtSubscriptionLevel">Example</a>
```
az edgeorder list-order-at-subscription-level
```
##### <a name="ParametersListOrderAtSubscriptionLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|$skipToken is supported on Get list of order, which provides the next page in the list of order.|skip_token|$skipToken|

#### <a name="ListOrderItemsAtResourceGroupLevel">Command `az edgeorder list-order-item-at-resource-group-level`</a>

##### <a name="ExamplesListOrderItemsAtResourceGroupLevel">Example</a>
```
az edgeorder list-order-item-at-resource-group-level --resource-group "TestRG"
```
##### <a name="ParametersListOrderItemsAtResourceGroupLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--filter**|string|$filter is supported to filter based on order id. Filter supports only equals operation.|filter|$filter|
|**--expand**|string|$expand is supported on device details, forward shipping details and reverse shipping details parameters. Each of these can be provided as a comma separated list. Device Details for order item provides details on the devices of the product, Forward and Reverse Shipping details provide forward and reverse shipping details respectively.|expand|$expand|
|**--skip-token**|string|$skipToken is supported on Get list of order items, which provides the next page in the list of order items.|skip_token|$skipToken|

#### <a name="ListOrderItemsAtSubscriptionLevel">Command `az edgeorder list-order-item-at-subscription-level`</a>

##### <a name="ExamplesListOrderItemsAtSubscriptionLevel">Example</a>
```
az edgeorder list-order-item-at-subscription-level
```
##### <a name="ParametersListOrderItemsAtSubscriptionLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|$filter is supported to filter based on order id. Filter supports only equals operation.|filter|$filter|
|**--expand**|string|$expand is supported on device details, forward shipping details and reverse shipping details parameters. Each of these can be provided as a comma separated list. Device Details for order item provides details on the devices of the product, Forward and Reverse Shipping details provide forward and reverse shipping details respectively.|expand|$expand|
|**--skip-token**|string|$skipToken is supported on Get list of order items, which provides the next page in the list of order items.|skip_token|$skipToken|

#### <a name="ListProductFamilies">Command `az edgeorder list-product-family`</a>

##### <a name="ExamplesListProductFamilies">Example</a>
```
az edgeorder list-product-family --filterable-properties azurestackedge={"type":"ShipToCountries","supportedValues":["U\
S"]}
```
##### <a name="ParametersListProductFamilies">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--expand**|string|$expand is supported on configurations parameter for product, which provides details on the configurations for the product.|expand|$expand|
|**--skip-token**|string|$skipToken is supported on list of product families, which provides the next page in the list of product families.|skip_token|$skipToken|
|**--filterable-properties**|dictionary|Dictionary of filterable properties on product family.|filterable_properties|filterableProperties|
|**--registered-features**|array|List of registered feature flags for subscription|registered_features|registeredFeatures|
|**--location-placement-id**|string|Location placement Id of a subscription|location_placement_id|locationPlacementId|
|**--quota-id**|string|Quota ID of a subscription|quota_id|quotaId|

#### <a name="ListProductFamiliesMetadata">Command `az edgeorder list-product-family-metadata`</a>

##### <a name="ExamplesListProductFamiliesMetadata">Example</a>
```
az edgeorder list-product-family-metadata
```
##### <a name="ParametersListProductFamiliesMetadata">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|$skipToken is supported on list of product families metadata, which provides the next page in the list of product families metadata.|skip_token|$skipToken|

#### <a name="ReturnOrderItem">Command `az edgeorder return-order-item`</a>

##### <a name="ExamplesReturnOrderItem">Example</a>
```
az edgeorder return-order-item --order-item-name "TestOrderName1" --resource-group "TestRG" --return-reason "Order \
returned"
```
##### <a name="ParametersReturnOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-item-name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--return-reason**|string|Return Reason.|return_reason|returnReason|
|**--service-tag**|string|Service tag (located on the bottom-right corner of the device)|service_tag|serviceTag|
|**--shipping-box-required**|boolean|Shipping Box required|shipping_box_required|shippingBoxRequired|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|

#### <a name="GetAddressByName">Command `az edgeorder show-address`</a>

##### <a name="ExamplesGetAddressByName">Example</a>
```
az edgeorder show-address --address-name "TestMSAddressName" --resource-group "TestRG"
```
##### <a name="ParametersGetAddressByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--address-name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="GetOrderByName">Command `az edgeorder show-order`</a>

##### <a name="ExamplesGetOrderByName">Example</a>
```
az edgeorder show-order --location "%7B%7B%7Blocation%7D%7D" --order-name "TestOrderItemName901" --resource-group \
"TestRG"
```
##### <a name="ParametersGetOrderByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-name**|string|The name of the order|order_name|orderName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--location**|string|The name of Azure region.|location|location|

#### <a name="GetOrderItemByName">Command `az edgeorder show-order-item`</a>

##### <a name="ExamplesGetOrderItemByName">Example</a>
```
az edgeorder show-order-item --order-item-name "TestOrderItemName01" --resource-group "TestRG"
```
##### <a name="ParametersGetOrderItemByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-item-name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--expand**|string|$expand is supported on device details, forward shipping details and reverse shipping details parameters. Each of these can be provided as a comma separated list. Device Details for order item provides details on the devices of the product, Forward and Reverse Shipping details provide forward and reverse shipping details respectively.|expand|$expand|

#### <a name="UpdateAddress">Command `az edgeorder update-address`</a>

##### <a name="ExamplesUpdateAddress">Example</a>
```
az edgeorder update-address --address-name "TestAddressName2" --contact-details contact-name="Petr Cech" \
email-list="ssemcr@microsoft.com" phone="1234567890" phone-extension="" --shipping-address address-type="None" \
city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" \
street-address1="16 TOWNSEND STT" street-address2="UNIT 1" --tags Hobby="Web Series Added" Name="Smile-Updated" \
WhatElse="Web Series Added" Work="Engineering" --resource-group "TestRG"
```
##### <a name="ParametersUpdateAddress">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--address-name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--if-match**|string|Defines the If-Match condition. The patch will be performed only if the ETag of the job on the server matches this value.|if_match|If-Match|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|

#### <a name="UpdateOrderItem">Command `az edgeorder update-order-item`</a>

##### <a name="ExamplesUpdateOrderItem">Example</a>
```
az edgeorder update-order-item --order-item-name "TestOrderItemName01" --contact-details contact-name="Updated contact \
name" email-list="testemail@microsoft.com" phone="2222200000" --transport-preferences preferred-shipment-type="Customer\
Managed" --tags ant="insect" pigeon="bird" tiger="animal" --resource-group "TestRG"
```
##### <a name="ParametersUpdateOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--order-item-name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--if-match**|string|Defines the If-Match condition. The patch will be performed only if the ETag of the order on the server matches this value.|if_match|If-Match|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--notification-email-list**|array|Additional notification email list.|notification_email_list|notificationEmailList|
|**--notification-preferences**|array|Notification preferences.|notification_preferences|notificationPreferences|
|**--transport-preferences**|object|Preferences related to the shipment logistics of the order.|transport_preferences|transportPreferences|
|**--encryption-preferences**|object|Preferences related to the Encryption.|encryption_preferences|encryptionPreferences|
|**--management-resource-preferences**|object|Preferences related to the Management resource.|management_resource_preferences|managementResourcePreferences|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|
