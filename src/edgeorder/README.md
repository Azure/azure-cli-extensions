# Azure CLI edgeorder Extension #
This is the extension for edgeorder

### How to use ###
Install this extension using the below CLI command
```
az extension add --name edgeorder
```

### Included Features ###
##### Create an address #####
```
az edgeorder address create --name "TestMSAddressName" --location "eastus" \
    --contact-details contact-name="Petr Cech" email-list="testemail@microsoft.com" phone="1234567890" phone-extension="" \
    --shipping-address address-type="None" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" street-address1="16 TOWNSEND ST" street-address2="UNIT 1" \
    --resource-group "TestRG" 
```
##### Create an order item #####
```
az edgeorder order-item create --name "TestOrderItemName01" \
    --order-item-resource "{\\"location\\":\\"eastus\\",\\"tags\\":{\\"carrot\\":\\"vegetable\\",\\"mango\\":\\"fruit\\"},\\"orderItemDetails\\":{\\"orderItemType\\":\\"Purchase\\",\\"preferences\\":{\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftManaged\\"}},\\"productDetails\\":{\\"hierarchyInformation\\":{\\"configurationName\\":\\"edgep_base\\",\\"productFamilyName\\":\\"azurestackedge\\",\\"productLineName\\":\\"azurestackedge\\",\\"productName\\":\\"azurestackedgegpu\\"}}},\\"addressDetails\\":{\\"forwardAddress\\":{\\"contactDetails\\":{\\"contactName\\":\\"Petr Cech\\",\\"emailList\\":[\\"testemail@microsoft.com\\"],\\"phone\\":\\"3213131190\\",\\"phoneExtension\\":\\"\\"},\\"shippingAddress\\":{\\"addressType\\":\\"None\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND ST\\",\\"streetAddress2\\":\\"UNIT 1\\"}}},\\"orderId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/TestRG/providers/Microsoft.EdgeOrder/locations/eastus/orders/TestOrderItemName01\\"}" \
    --resource-group "TestRG" 
```
##### Cancel an order item #####
```
az edgeorder order-item cancel --reason "Order cancelled" --name "TestOrderItemName1" \
    --resource-group "TestRG" 
```
##### List addresses at resource group level #####
```
az edgeorder address list --resource-group "TestRG"
```
##### List addresses at subscription level #####
```
az edgeorder address list
```
##### List configurations #####
```
az edgeorder list-config \
    --configuration-filters "[{\\"filterableProperty\\":[{\\"type\\":\\"ShipToCountries\\",\\"supportedValues\\":[\\"US\\"]}],\\"hierarchyInformation\\":{\\"productFamilyName\\":\\"AzureStackEdge\\",\\"productLineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}]" 
```
##### List operations #####
```
az edgeorder list-operation
```
##### List orders at resource group level #####
```
az edgeorder order list --resource-group "TestRG"
```
##### List orders at subscription level #####
```
az edgeorder order list
```
##### List order items at resource group level #####
```
az edgeorder order-item list --resource-group "TestRG"
```
##### List order items at subscription level #####
```
az edgeorder order-item list
```
##### List product families #####
```
az edgeorder list-family \
    --filterable-properties azurestackedge="{\\"type\\":\\"ShipToCountries\\",\\"supportedValues\\":[\\"US\\"]}"
```
##### List product family metadata #####
```
az edgeorder list-metadata
```
##### Return an order item #####
```
az edgeorder order-item return --name "TestOrderName1" --resource-group "TestRG" \
    --return-reason "Order returned" 
```
##### Show an address #####
```
az edgeorder address show --name "TestMSAddressName" --resource-group "TestRG"
```
##### Show an order #####
```
az edgeorder order show --location "location" --name "TestOrderItemName901" \
    --resource-group "TestRG" 
```
##### Show an order item #####
```
az edgeorder order-item show --name "TestOrderItemName01" --resource-group "TestRG"
```
##### Update an address #####
```
az edgeorder address update --name "TestAddressName2" \
    --contact-details contact-name="Petr Cech" email-list="ssemcr@microsoft.com" phone="1234567890" phone-extension="" \
    --shipping-address address-type="None" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" street-address1="16 TOWNSEND STT" street-address2="UNIT 1" \
    --tags Hobby="Web Series Added" Name="Smile-Updated" WhatElse="Web Series Added" Work="Engineering" \
    --resource-group "TestRG" 
```
##### Update an order item #####
```
az edgeorder order-item update --name "TestOrderItemName01" \
    --contact-details contact-name="Updated contact name" email-list="testemail@microsoft.com" phone="2222200000" \
    --transport-preferences preferred-shipment-type="CustomerManaged" --tags ant="insect" pigeon="bird" tiger="animal" \
    --resource-group "TestRG" 
```
##### Delete an address #####
```
az edgeorder address delete --name "TestAddressName1" --resource-group "TestRG"
```
##### Delete an order item #####
```
az edgeorder order-item delete --name "TestOrderItemName01" --resource-group "TestRG"
```
