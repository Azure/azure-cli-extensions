# Azure CLI edgeorder Extension #
This is the extension for edgeorder

### How to use ###
Install this extension using the below CLI command
```
az extension add --name edgeorder
```

### Included Features ###
#### edgeorder ####
##### Create-address #####
```
az edgeorder create-address --address-name "TestMSAddressName" --location "westus" \
    --contact-details contact-name="Petr Cech" email-list="testemail@microsoft.com" phone="1234567890" phone-extension="" \
    --shipping-address address-type="None" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" street-address1="16 TOWNSEND ST" street-address2="UNIT 1" \
    --resource-group "TestRG" 
```
##### Create-order-item #####
```
az edgeorder create-order-item --order-item-name "TestOrderItemName01" \
    --order-item-resource "{\\"location\\":\\"westus\\",\\"tags\\":{\\"carrot\\":\\"vegetable\\",\\"mango\\":\\"fruit\\"},\\"orderItemDetails\\":{\\"orderItemType\\":\\"Purchase\\",\\"preferences\\":{\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftManaged\\"}},\\"productDetails\\":{\\"hierarchyInformation\\":{\\"configurationName\\":\\"AzureStackEdgeGPU\\",\\"productFamilyName\\":\\"AzureStackEdge\\",\\"productLineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}},\\"addressDetails\\":{\\"forwardAddress\\":{\\"contactDetails\\":{\\"contactName\\":\\"164 TOWNSEND ST\\",\\"emailList\\":[\\"ssemmail@microsoft.com\\",\\"vishwamdir@microsoft.com\\"],\\"phone\\":\\"3213131190\\"},\\"shippingAddress\\":{\\"addressType\\":\\"Residential\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND ST\\",\\"streetAddress2\\":\\"UNIT 1\\",\\"zipExtendedCode\\":\\"1\\"}}},\\"orderId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/TestRG/providers/Microsoft.EdgeOrder/locations/westus/orders/TestOrderItemName01\\"}" \
    --resource-group "TestRG" 
```
##### Cancel-order-item #####
```
az edgeorder cancel-order-item --reason "Order cancelled" --order-item-name "TestOrderItemName1" \
    --resource-group "TestRG" 
```
##### List-address-at-resource-group-level #####
```
az edgeorder list-address-at-resource-group-level --resource-group "TestRG"
```
##### List-address-at-subscription-level #####
```
az edgeorder list-address-at-subscription-level
```
##### List-configuration #####
```
az edgeorder list-configuration \
    --configuration-filters "[{\\"filterableProperty\\":[{\\"type\\":\\"ShipToCountries\\",\\"supportedValues\\":[\\"US\\"]}],\\"hierarchyInformation\\":{\\"productFamilyName\\":\\"AzureStackEdge\\",\\"productLineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}]" 
```
##### List-operation #####
```
az edgeorder list-operation
```
##### List-order-at-resource-group-level #####
```
az edgeorder list-order-at-resource-group-level --resource-group "TestRG"
```
##### List-order-at-subscription-level #####
```
az edgeorder list-order-at-subscription-level
```
##### List-order-item-at-resource-group-level #####
```
az edgeorder list-order-item-at-resource-group-level --resource-group "TestRG"
```
##### List-order-item-at-subscription-level #####
```
az edgeorder list-order-item-at-subscription-level
```
##### List-product-family #####
```
az edgeorder list-product-family \
    --filterable-properties azurestackedge={"type":"ShipToCountries","supportedValues":["US"]} 
```
##### List-product-family-metadata #####
```
az edgeorder list-product-family-metadata
```
##### Return-order-item #####
```
az edgeorder return-order-item --order-item-name "TestOrderName1" --resource-group "TestRG" \
    --return-reason "Order returned" 
```
##### Show-address #####
```
az edgeorder show-address --address-name "TestMSAddressName" --resource-group "TestRG"
```
##### Show-order #####
```
az edgeorder show-order --location "%7B%7B%7Blocation%7D%7D" --order-name "TestOrderItemName901" \
    --resource-group "TestRG" 
```
##### Show-order-item #####
```
az edgeorder show-order-item --order-item-name "TestOrderItemName01" --resource-group "TestRG"
```
##### Update-address #####
```
az edgeorder update-address --address-name "TestAddressName2" \
    --contact-details contact-name="Petr Cech" email-list="ssemcr@microsoft.com" phone="1234567890" phone-extension="" \
    --shipping-address address-type="None" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" street-address1="16 TOWNSEND STT" street-address2="UNIT 1" \
    --tags Hobby="Web Series Added" Name="Smile-Updated" WhatElse="Web Series Added" Work="Engineering" \
    --resource-group "TestRG" 
```
##### Update-order-item #####
```
az edgeorder update-order-item --order-item-name "TestOrderItemName01" \
    --contact-details contact-name="Updated contact name" email-list="testemail@microsoft.com" phone="2222200000" \
    --transport-preferences preferred-shipment-type="CustomerManaged" --tags ant="insect" pigeon="bird" tiger="animal" \
    --resource-group "TestRG" 
```
##### Delete-address #####
```
az edgeorder delete-address --address-name "TestAddressName1" --resource-group "TestRG"
```
##### Delete-order-item #####
```
az edgeorder delete-order-item --order-item-name "TestOrderItemName01" --resource-group "TestRG"
```