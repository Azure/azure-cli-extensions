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
|[az edgeorder address show](#GetAddressByName)|GetAddressByName|[Parameters](#ParametersGetAddressByName)|[Example](#ExamplesGetAddressByName)|
|[az edgeorder order show](#GetOrderByName)|GetOrderByName|[Parameters](#ParametersGetOrderByName)|[Example](#ExamplesGetOrderByName)|
|[az edgeorder order-item show](#GetOrderItemByName)|GetOrderItemByName|[Parameters](#ParametersGetOrderItemByName)|[Example](#ExamplesGetOrderItemByName)|
|[az edgeorder address create](#CreateAddress)|CreateAddress|[Parameters](#ParametersCreateAddress)|[Example](#ExamplesCreateAddress)|
|[az edgeorder order-item create](#CreateOrderItem)|CreateOrderItem|[Parameters](#ParametersCreateOrderItem)|[Example](#ExamplesCreateOrderItem)|
|[az edgeorder address update](#UpdateAddress)|UpdateAddress|[Parameters](#ParametersUpdateAddress)|[Example](#ExamplesUpdateAddress)|
|[az edgeorder order-item update](#UpdateOrderItem)|UpdateOrderItem|[Parameters](#ParametersUpdateOrderItem)|[Example](#ExamplesUpdateOrderItem)|
|[az edgeorder address delete](#DeleteAddressByName)|DeleteAddressByName|[Parameters](#ParametersDeleteAddressByName)|[Example](#ExamplesDeleteAddressByName)|
|[az edgeorder order-item delete](#DeleteOrderItemByName)|DeleteOrderItemByName|[Parameters](#ParametersDeleteOrderItemByName)|[Example](#ExamplesDeleteOrderItemByName)|
|[az edgeorder address rg-list](#ListAddressesAtResourceGroupLevel)|ListAddressesAtResourceGroupLevel|[Parameters](#ParametersListAddressesAtResourceGroupLevel)|[Example](#ExamplesListAddressesAtResourceGroupLevel)|
|[az edgeorder address sub-list](#ListAddressesAtSubscriptionLevel)|ListAddressesAtSubscriptionLevel|[Parameters](#ParametersListAddressesAtSubscriptionLevel)|[Example](#ExamplesListAddressesAtSubscriptionLevel)|
|[az edgeorder list-config](#ListConfigurations)|ListConfigurations|[Parameters](#ParametersListConfigurations)|[Example](#ExamplesListConfigurations)|
|[az edgeorder list-family](#ListProductFamilies)|ListProductFamilies|[Parameters](#ParametersListProductFamilies)|[Example](#ExamplesListProductFamilies)|
|[az edgeorder list-metadata](#ListProductFamiliesMetadata)|ListProductFamiliesMetadata|[Parameters](#ParametersListProductFamiliesMetadata)|[Example](#ExamplesListProductFamiliesMetadata)|
|[az edgeorder list-operation](#ListOperations)|ListOperations|[Parameters](#ParametersListOperations)|[Example](#ExamplesListOperations)|
|[az edgeorder order rg-list](#ListOrderAtResourceGroupLevel)|ListOrderAtResourceGroupLevel|[Parameters](#ParametersListOrderAtResourceGroupLevel)|[Example](#ExamplesListOrderAtResourceGroupLevel)|
|[az edgeorder order sub-list](#ListOrderAtSubscriptionLevel)|ListOrderAtSubscriptionLevel|[Parameters](#ParametersListOrderAtSubscriptionLevel)|[Example](#ExamplesListOrderAtSubscriptionLevel)|
|[az edgeorder order-item cancel](#CancelOrderItem)|CancelOrderItem|[Parameters](#ParametersCancelOrderItem)|[Example](#ExamplesCancelOrderItem)|
|[az edgeorder order-item return](#ReturnOrderItem)|ReturnOrderItem|[Parameters](#ParametersReturnOrderItem)|[Example](#ExamplesReturnOrderItem)|
|[az edgeorder order-item rg-list](#ListOrderItemsAtResourceGroupLevel)|ListOrderItemsAtResourceGroupLevel|[Parameters](#ParametersListOrderItemsAtResourceGroupLevel)|[Example](#ExamplesListOrderItemsAtResourceGroupLevel)|
|[az edgeorder order-item sub-list](#ListOrderItemsAtSubscriptionLevel)|ListOrderItemsAtSubscriptionLevel|[Parameters](#ParametersListOrderItemsAtSubscriptionLevel)|[Example](#ExamplesListOrderItemsAtSubscriptionLevel)|


## COMMAND DETAILS
### group `az edgeorder`
#### <a name="GetAddressByName">Command `az edgeorder address show`</a>

##### <a name="ExamplesGetAddressByName">Example</a>
```
az edgeorder address show --name "TestMSAddressName" --resource-group "TestRG"
```
##### <a name="ParametersGetAddressByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="GetOrderByName">Command `az edgeorder order show`</a>

##### <a name="ExamplesGetOrderByName">Example</a>
```
az edgeorder order show --location "%7B%7B%7Blocation%7D%7D" --name "TestOrderItemName901" --resource-group "TestRG"
```
##### <a name="ParametersGetOrderByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order|order_name|orderName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--location**|string|The name of Azure region.|location|location|

#### <a name="GetOrderItemByName">Command `az edgeorder order-item show`</a>

##### <a name="ExamplesGetOrderItemByName">Example</a>
```
az edgeorder order-item show --name "TestOrderItemName01" --resource-group "TestRG"
```
##### <a name="ParametersGetOrderItemByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--expand**|string|$expand is supported on device details, forward shipping details and reverse shipping details parameters. Each of these can be provided as a comma separated list. Device Details for order item provides details on the devices of the product, Forward and Reverse Shipping details provide forward and reverse shipping details respectively.|expand|$expand|

#### <a name="CreateAddress">Command `az edgeorder address create`</a>

##### <a name="ExamplesCreateAddress">Example</a>
```
az edgeorder address create --name "TestMSAddressName" --location "westus" --contact-details contact-name="Petr Cech" \
email-list="testemail@microsoft.com" phone="1234567890" phone-extension="" --shipping-address address-type="None" \
city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" \
street-address1="16 TOWNSEND ST" street-address2="UNIT 1" --resource-group "TestRG"
```
##### <a name="ParametersCreateAddress">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|

#### <a name="CreateOrderItem">Command `az edgeorder order-item create`</a>

##### <a name="ExamplesCreateOrderItem">Example</a>
```
az edgeorder order-item create --name "TestOrderItemName01" --resource "{\\"location\\":\\"westus\\",\\"tags\\":{\\"car\
rot\\":\\"vegetable\\",\\"mango\\":\\"fruit\\"},\\"orderItemDetails\\":{\\"orderItemType\\":\\"Purchase\\",\\"preferenc\
es\\":{\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftManaged\\"}},\\"productDetails\\":{\\"hierar\
chyInformation\\":{\\"configurationName\\":\\"AzureStackEdgeGPU\\",\\"productFamilyName\\":\\"AzureStackEdge\\",\\"prod\
uctLineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}},\\"addressDetails\\":{\\"forwardAddres\
s\\":{\\"contactDetails\\":{\\"contactName\\":\\"164 TOWNSEND ST\\",\\"emailList\\":[\\"ssemmail@microsoft.com\\",\\"vi\
shwamdir@microsoft.com\\"],\\"phone\\":\\"3213131190\\"},\\"shippingAddress\\":{\\"addressType\\":\\"Residential\\",\\"\
city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"st\
ateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND ST\\",\\"streetAddress2\\":\\"UNIT \
1\\",\\"zipExtendedCode\\":\\"1\\"}}},\\"orderId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGrou\
ps/TestRG/providers/Microsoft.EdgeOrder/locations/westus/orders/TestOrderItemName01\\"}" --resource-group "TestRG"
```
##### <a name="ParametersCreateOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--resource**|object|Order item details from request body.|order_item_resource|orderItemResource|

#### <a name="UpdateAddress">Command `az edgeorder address update`</a>

##### <a name="ExamplesUpdateAddress">Example</a>
```
az edgeorder address update --name "TestAddressName2" --contact-details contact-name="Petr Cech" \
email-list="ssemcr@microsoft.com" phone="1234567890" phone-extension="" --shipping-address address-type="None" \
city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" \
street-address1="16 TOWNSEND STT" street-address2="UNIT 1" --tags Hobby="Web Series Added" Name="Smile-Updated" \
WhatElse="Web Series Added" Work="Engineering" --resource-group "TestRG"
```
##### <a name="ParametersUpdateAddress">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--if-match**|string|Defines the If-Match condition. The patch will be performed only if the ETag of the job on the server matches this value.|if_match|If-Match|
|**--tags**|dictionary|The list of key value pairs that describe the resource. These tags can be used in viewing and grouping this resource (across resource groups).|tags|tags|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|

#### <a name="UpdateOrderItem">Command `az edgeorder order-item update`</a>

##### <a name="ExamplesUpdateOrderItem">Example</a>
```
az edgeorder order-item update --name "TestOrderItemName01" --contact-details contact-name="Updated contact name" \
email-list="testemail@microsoft.com" phone="2222200000" --transport-preferences preferred-shipment-type="CustomerManage\
d" --tags ant="insect" pigeon="bird" tiger="animal" --resource-group "TestRG"
```
##### <a name="ParametersUpdateOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order item|order_item_name|orderItemName|
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

#### <a name="DeleteAddressByName">Command `az edgeorder address delete`</a>

##### <a name="ExamplesDeleteAddressByName">Example</a>
```
az edgeorder address delete --name "TestAddressName1" --resource-group "TestRG"
```
##### <a name="ParametersDeleteAddressByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the address Resource within the specified resource group. address names must be between 3 and 24 characters in length and use any alphanumeric and underscore only|address_name|addressName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DeleteOrderItemByName">Command `az edgeorder order-item delete`</a>

##### <a name="ExamplesDeleteOrderItemByName">Example</a>
```
az edgeorder order-item delete --name "TestOrderItemName01" --resource-group "TestRG"
```
##### <a name="ParametersDeleteOrderItemByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ListAddressesAtResourceGroupLevel">Command `az edgeorder address rg-list`</a>

##### <a name="ExamplesListAddressesAtResourceGroupLevel">Example</a>
```
az edgeorder address rg-list --resource-group "TestRG"
```
##### <a name="ParametersListAddressesAtResourceGroupLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--filter**|string|$filter is supported to filter based on shipping address properties. Filter supports only equals operation.|filter|$filter|
|**--skip-token**|string|$skipToken is supported on Get list of addresses, which provides the next page in the list of address.|skip_token|$skipToken|

#### <a name="ListAddressesAtSubscriptionLevel">Command `az edgeorder address sub-list`</a>

##### <a name="ExamplesListAddressesAtSubscriptionLevel">Example</a>
```
az edgeorder address sub-list
```
##### <a name="ParametersListAddressesAtSubscriptionLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|$filter is supported to filter based on shipping address properties. Filter supports only equals operation.|filter|$filter|
|**--skip-token**|string|$skipToken is supported on Get list of addresses, which provides the next page in the list of addresses.|skip_token|$skipToken|

#### <a name="ListConfigurations">Command `az edgeorder list-config`</a>

##### <a name="ExamplesListConfigurations">Example</a>
```
az edgeorder list-config --configuration-filters "[{\\"filterableProperty\\":[{\\"type\\":\\"ShipToCountries\\",\\"supp\
ortedValues\\":[\\"US\\"]}],\\"hierarchyInformation\\":{\\"productFamilyName\\":\\"AzureStackEdge\\",\\"productLineName\
\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}]"
```
##### <a name="ParametersListConfigurations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|$skipToken is supported on list of configurations, which provides the next page in the list of configurations.|skip_token|$skipToken|
|**--configuration-filters**|array|Holds details about product hierarchy information and filterable property.|configuration_filters|configurationFilters|
|**--registered-features**|array|List of registered feature flags for subscription|registered_features|registeredFeatures|
|**--location-placement-id**|string|Location placement Id of a subscription|location_placement_id|locationPlacementId|
|**--quota-id**|string|Quota ID of a subscription|quota_id|quotaId|

#### <a name="ListProductFamilies">Command `az edgeorder list-family`</a>

##### <a name="ExamplesListProductFamilies">Example</a>
```
az edgeorder list-family --filterable-properties azurestackedge={"type":"ShipToCountries","supportedValues":["US"]}
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

#### <a name="ListProductFamiliesMetadata">Command `az edgeorder list-metadata`</a>

##### <a name="ExamplesListProductFamiliesMetadata">Example</a>
```
az edgeorder list-metadata
```
##### <a name="ParametersListProductFamiliesMetadata">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|$skipToken is supported on list of product families metadata, which provides the next page in the list of product families metadata.|skip_token|$skipToken|

#### <a name="ListOperations">Command `az edgeorder list-operation`</a>

##### <a name="ExamplesListOperations">Example</a>
```
az edgeorder list-operation
```
##### <a name="ParametersListOperations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="ListOrderAtResourceGroupLevel">Command `az edgeorder order rg-list`</a>

##### <a name="ExamplesListOrderAtResourceGroupLevel">Example</a>
```
az edgeorder order rg-list --resource-group "TestRG"
```
##### <a name="ParametersListOrderAtResourceGroupLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--skip-token**|string|$skipToken is supported on Get list of order, which provides the next page in the list of order.|skip_token|$skipToken|

#### <a name="ListOrderAtSubscriptionLevel">Command `az edgeorder order sub-list`</a>

##### <a name="ExamplesListOrderAtSubscriptionLevel">Example</a>
```
az edgeorder order sub-list
```
##### <a name="ParametersListOrderAtSubscriptionLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|$skipToken is supported on Get list of order, which provides the next page in the list of order.|skip_token|$skipToken|

#### <a name="CancelOrderItem">Command `az edgeorder order-item cancel`</a>

##### <a name="ExamplesCancelOrderItem">Example</a>
```
az edgeorder order-item cancel --reason "Order cancelled" --name "TestOrderItemName1" --resource-group "TestRG"
```
##### <a name="ParametersCancelOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--reason**|string|Reason for cancellation.|reason|reason|

#### <a name="ReturnOrderItem">Command `az edgeorder order-item return`</a>

##### <a name="ExamplesReturnOrderItem">Example</a>
```
az edgeorder order-item return --name "TestOrderName1" --resource-group "TestRG" --return-reason "Order returned"
```
##### <a name="ParametersReturnOrderItem">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--name**|string|The name of the order item|order_item_name|orderItemName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--return-reason**|string|Return Reason.|return_reason|returnReason|
|**--service-tag**|string|Service tag (located on the bottom-right corner of the device)|service_tag|serviceTag|
|**--shipping-box-required**|boolean|Shipping Box required|shipping_box_required|shippingBoxRequired|
|**--shipping-address**|object|Shipping details for the address|shipping_address|shippingAddress|
|**--contact-details**|object|Contact details for the address|contact_details|contactDetails|

#### <a name="ListOrderItemsAtResourceGroupLevel">Command `az edgeorder order-item rg-list`</a>

##### <a name="ExamplesListOrderItemsAtResourceGroupLevel">Example</a>
```
az edgeorder order-item rg-list --resource-group "TestRG"
```
##### <a name="ParametersListOrderItemsAtResourceGroupLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--filter**|string|$filter is supported to filter based on order id. Filter supports only equals operation.|filter|$filter|
|**--expand**|string|$expand is supported on device details, forward shipping details and reverse shipping details parameters. Each of these can be provided as a comma separated list. Device Details for order item provides details on the devices of the product, Forward and Reverse Shipping details provide forward and reverse shipping details respectively.|expand|$expand|
|**--skip-token**|string|$skipToken is supported on Get list of order items, which provides the next page in the list of order items.|skip_token|$skipToken|

#### <a name="ListOrderItemsAtSubscriptionLevel">Command `az edgeorder order-item sub-list`</a>

##### <a name="ExamplesListOrderItemsAtSubscriptionLevel">Example</a>
```
az edgeorder order-item sub-list
```
##### <a name="ParametersListOrderItemsAtSubscriptionLevel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|$filter is supported to filter based on order id. Filter supports only equals operation.|filter|$filter|
|**--expand**|string|$expand is supported on device details, forward shipping details and reverse shipping details parameters. Each of these can be provided as a comma separated list. Device Details for order item provides details on the devices of the product, Forward and Reverse Shipping details provide forward and reverse shipping details respectively.|expand|$expand|
|**--skip-token**|string|$skipToken is supported on Get list of order items, which provides the next page in the list of order items.|skip_token|$skipToken|
