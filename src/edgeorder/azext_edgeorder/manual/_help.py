# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['edgeorder'] = '''
    type: group
    short-summary: Manage Edge Order
'''

helps['edgeorder order'] = """
    type: group
    short-summary: Manage order with Edge Order
"""

helps['edgeorder order show'] = """
    type: command
    short-summary: "Get an order."
    examples:
      - name: GetOrderByName
        text: |-
               az edgeorder order show --location "TestLocation" --name "TestOrderItemName901" \
--resource-group "TestRG"
"""

helps['edgeorder list-config'] = """
    type: command
    short-summary: "This method provides the list of configurations for the given product family, product line and \
product under subscription."
    parameters:
      - name: --registered-features
        short-summary: "List of registered feature flags for subscription"
        long-summary: |
            Usage: --registered-features name=XX state=XX

            name: Name of subscription registered feature
            state: State of subscription registered feature

            Multiple actions can be specified by using more than one --registered-features argument.
    examples:
      - name: ListConfigurations
        text: |-
               az edgeorder list-config --configuration-filters "[{\\"filterableProperty\\":[{\\"type\\":\\"ShipToCount\
ries\\",\\"supportedValues\\":[\\"US\\"]}],\\"hierarchyInformation\\":{\\"productFamilyName\\":\\"AzureStackEdge\\",\\"\
productLineName\\":\\"AzureStackEdge\\",\\"productName\\":\\"AzureStackEdgeGPU\\"}}]"
"""

helps['edgeorder list-family'] = """
    type: command
    short-summary: "This method provides the list of product families for the given subscription."
    parameters:
      - name: --registered-features
        short-summary: "List of registered feature flags for subscription"
        long-summary: |
            Usage: --registered-features name=XX state=XX

            name: Name of subscription registered feature
            state: State of subscription registered feature

            Multiple actions can be specified by using more than one --registered-features argument.
    examples:
      - name: ListProductFamilies
        text: |-
               az edgeorder list-family --filterable-properties azurestackedge="{\\"type\\":\\"ShipToCountries\\",\
               \\"supportedValues\\":[\\"US\\"]}"
"""

helps['edgeorder list-metadata'] = """
    type: command
    short-summary: "This method provides the list of product families metadata for the given subscription."
    examples:
      - name: ListProductFamiliesMetadata
        text: |-
               az edgeorder list-metadata
"""

helps['edgeorder address'] = """
    type: group
    short-summary: Manage address with Edge Order
"""

helps['edgeorder address list'] = """
    type: command
    short-summary: "List all the addresses available under the given resource group. And List all the addresses \
available under the subscription."
    examples:
      - name: ListAddressesAtResourceGroupLevel
        text: |-
               az edgeorder address list --resource-group "TestRG"
      - name: ListAddressesAtSubscriptionLevel
        text: |-
               az edgeorder address list
"""

helps['edgeorder address'] = """
    type: group
    short-summary: Manage address with edgeorder sub group address
"""

helps['edgeorder address show'] = """
    type: command
    short-summary: "Get information about the specified address."
    examples:
      - name: GetAddressByName
        text: |-
               az edgeorder address show --name "TestMSAddressName" --resource-group "TestRG"
"""

helps['edgeorder address create'] = """
    type: command
    short-summary: "Create a new address with the specified parameters. Existing address can be updated with this \
API."
    parameters:
      - name: --shipping-address
        short-summary: "Shipping details for the address"
        long-summary: |
            Usage: --shipping-address street-address1=XX street-address2=XX street-address3=XX city=XX \
state-or-province=XX country=XX postal-code=XX zip-extended-code=XX company-name=XX address-type=XX

            street-address1: Required. Street Address line 1.
            street-address2: Street Address line 2.
            street-address3: Street Address line 3.
            city: Name of the City.
            state-or-province: Name of the State or Province.
            country: Required. Name of the Country.
            postal-code: Postal code.
            zip-extended-code: Extended Zip Code.
            company-name: Name of the company.
            address-type: Type of address.
      - name: --contact-details
        short-summary: "Contact details for the address"
        long-summary: |
            Usage: --contact-details contact-name=XX phone=XX phone-extension=XX mobile=XX email-list=XX

            contact-name: Required. Contact name of the person.
            phone: Required. Phone number of the contact person.
            phone-extension: Phone extension number of the contact person.
            mobile: Mobile number of the contact person.
            email-list: Required. List of Email-ids to be notified about job progress.
    examples:
      - name: CreateAddress
        text: |-
               az edgeorder address create --name "TestMSAddressName" --location "eastus" --contact-details \
contact-name="Petr Cech" email-list="testemail@microsoft.com" phone="1234567890" phone-extension="" --shipping-address \
address-type="None" city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" \
state-or-province="CA" street-address1="16 TOWNSEND ST" street-address2="UNIT 1" --resource-group "TestRG"
"""

helps['edgeorder address update'] = """
    type: command
    short-summary: "Update the properties of an existing address."
    parameters:
      - name: --shipping-address
        short-summary: "Shipping details for the address"
        long-summary: |
            Usage: --shipping-address street-address1=XX street-address2=XX street-address3=XX city=XX \
state-or-province=XX country=XX postal-code=XX zip-extended-code=XX company-name=XX address-type=XX

            street-address1: Required. Street Address line 1.
            street-address2: Street Address line 2.
            street-address3: Street Address line 3.
            city: Name of the City.
            state-or-province: Name of the State or Province.
            country: Required. Name of the Country.
            postal-code: Postal code.
            zip-extended-code: Extended Zip Code.
            company-name: Name of the company.
            address-type: Type of address.
      - name: --contact-details
        short-summary: "Contact details for the address"
        long-summary: |
            Usage: --contact-details contact-name=XX phone=XX phone-extension=XX mobile=XX email-list=XX

            contact-name: Required. Contact name of the person.
            phone: Required. Phone number of the contact person.
            phone-extension: Phone extension number of the contact person.
            mobile: Mobile number of the contact person.
            email-list: Required. List of Email-ids to be notified about job progress.
    examples:
      - name: UpdateAddress
        text: |-
               az edgeorder address update --name "TestAddressName2" --contact-details contact-name="Petr Cech" \
email-list="ssemcr@microsoft.com" phone="1234567890" phone-extension="" --shipping-address address-type="None" \
city="San Francisco" company-name="Microsoft" country="US" postal-code="94107" state-or-province="CA" \
street-address1="16 TOWNSEND STT" street-address2="UNIT 1" --tags Hobby="Web Series Added" Name="Smile-Updated" \
WhatElse="Web Series Added" Work="Engineering" --resource-group "TestRG"
"""

helps['edgeorder address delete'] = """
    type: command
    short-summary: "Delete an address."
    examples:
      - name: DeleteAddressByName
        text: |-
               az edgeorder address delete --name "TestAddressName1" --resource-group "TestRG"
"""

helps['edgeorder order'] = """
    type: group
    short-summary: Manage order with edgeorder sub group order
"""

helps['edgeorder order list'] = """
    type: command
    short-summary: "List order at resource group level. And List order at subscription level."
    examples:
      - name: ListOrderAtResourceGroupLevel
        text: |-
               az edgeorder order list --resource-group "TestRG"
      - name: ListOrderAtSubscriptionLevel
        text: |-
               az edgeorder order list
"""

helps['edgeorder order-item'] = """
    type: group
    short-summary: Manage order item with edgeorder
"""

helps['edgeorder order-item list'] = """
    type: command
    short-summary: "List order item at resource group level. And List order item at subscription level."
    examples:
      - name: ListOrderItemsAtResourceGroupLevel
        text: |-
               az edgeorder order-item list --resource-group "TestRG"
      - name: ListOrderItemsAtSubscriptionLevel
        text: |-
               az edgeorder order-item list
"""

helps['edgeorder order-item'] = """
    type: group
    short-summary: Manage order item with edgeorder sub group order-item
"""

helps['edgeorder order-item show'] = """
    type: command
    short-summary: "Get an order item."
    examples:
      - name: GetOrderItemByName
        text: |-
               az edgeorder order-item show --name "TestOrderItemName01" --resource-group "TestRG"
"""

helps['edgeorder order-item create'] = """
    type: command
    short-summary: "Create an order item. Existing order item cannot be updated with this api and should instead be \
updated with the Update order item API."
    examples:
      - name: CreateOrderItem
        text: |-
               az edgeorder order-item create --name "TestOrderItemName01" --order-item-resource "{\\"location\\":\\"eastus\\",\\"\
tags\\":{\\"carrot\\":\\"vegetable\\",\\"mango\\":\\"fruit\\"},\\"orderItemDetails\\":{\\"orderItemType\\":\\"Purchase\
\\",\\"preferences\\":{\\"transportPreferences\\":{\\"preferredShipmentType\\":\\"MicrosoftManaged\\"}},\\"productDetai\
ls\\":{\\"hierarchyInformation\\":{\\"configurationName\\":\\"edgep_base\\",\\"productFamilyName\\":\\"azurestackedge\
\\",\\"productLineName\\":\\"azurestackedge\\",\\"productName\\":\\"azurestackedgegpu\\"}}},\\"addressDetails\\":{\
\\"forwardAddress\\":{\\"contactDetails\\":{\\"contactName\\":\\"Petr Cech\\",\\"emailList\\":[\\"ssemmail@microsoft.co\
m\\",\\"vishwamdir@microsoft.com\\"],\\"phone\\":\\"3213131190\\",\\"phoneExtension\\":\\"\\"},\\"shippingAddress\\":{\
\\"addressType\\":\\"None\\",\\"city\\":\\"San Francisco\\",\\"companyName\\":\\"Microsoft\\",\\"country\\":\\"US\\",\
\\"postalCode\\":\\"94107\\",\\"stateOrProvince\\":\\"CA\\",\\"streetAddress1\\":\\"16 TOWNSEND ST\\",\\"streetAddress2\
\\":\\"UNIT 1\\"}}},\\"orderId\\":\\"/subscriptions/fa68082f-8ff7-4a25-95c7-ce9da541242f/resourceGroups/TestRG/provider\
s/Microsoft.EdgeOrder/locations/eastus/orders/TestOrderItemName01\\"}" --resource-group "TestRG"
"""

helps['edgeorder order-item update'] = """
    type: command
    short-summary: "Update the properties of an existing order item."
    parameters:
      - name: --notif-preferences
        short-summary: "Notification preferences."
        long-summary: |
            Usage: --notif-preferences stage-name=XX send-notification=XX

            stage-name: Required. Name of the stage.
            send-notification: Required. Notification is required or not.

            Multiple actions can be specified by using more than one --notification-preferences argument.
      - name: --transport-preferences
        short-summary: "Preferences related to the shipment logistics of the order."
        long-summary: |
            Usage: --transport-preferences preferred-shipment-type=XX

            preferred-shipment-type: Required. Indicates Shipment Logistics type that the customer preferred.
      - name: --encryption-preferences
        short-summary: "Preferences related to the Encryption."
        long-summary: |
            Usage: --encryption-preferences double-encryption-status=XX

            double-encryption-status: Double encryption status as entered by the customer. It is compulsory to give \
this parameter if the 'Deny' or 'Disabled' policy is configured.
      - name: --mgmt-preferences
        short-summary: "Preferences related to the Management resource."
        long-summary: |
            Usage: --mgmt-preferences preferred-management-resource-id=XX

            preferred-management-resource-id: Customer preferred Management resource ARM ID
      - name: --shipping-address
        short-summary: "Shipping details for the address"
        long-summary: |
            Usage: --shipping-address street-address1=XX street-address2=XX street-address3=XX city=XX \
state-or-province=XX country=XX postal-code=XX zip-extended-code=XX company-name=XX address-type=XX

            street-address1: Required. Street Address line 1.
            street-address2: Street Address line 2.
            street-address3: Street Address line 3.
            city: Name of the City.
            state-or-province: Name of the State or Province.
            country: Required. Name of the Country.
            postal-code: Postal code.
            zip-extended-code: Extended Zip Code.
            company-name: Name of the company.
            address-type: Type of address.
      - name: --contact-details
        short-summary: "Contact details for the address"
        long-summary: |
            Usage: --contact-details contact-name=XX phone=XX phone-extension=XX mobile=XX email-list=XX

            contact-name: Required. Contact name of the person.
            phone: Required. Phone number of the contact person.
            phone-extension: Phone extension number of the contact person.
            mobile: Mobile number of the contact person.
            email-list: Required. List of Email-ids to be notified about job progress.
    examples:
      - name: UpdateOrderItem
        text: |-
               az edgeorder order-item update --name "TestOrderItemName01" --contact-details contact-name="Updated \
contact name" email-list="testemail@microsoft.com" phone="2222200000" --transport-preferences \
preferred-shipment-type="CustomerManaged" --tags ant="insect" pigeon="bird" tiger="animal" --resource-group "TestRG"
"""

helps['edgeorder order-item delete'] = """
    type: command
    short-summary: "Delete an order item."
    examples:
      - name: DeleteOrderItemByName
        text: |-
               az edgeorder order-item delete --name "TestOrderItemName01" --resource-group "TestRG"
"""

helps['edgeorder order-item cancel'] = """
    type: command
    short-summary: "Cancel order item."
    examples:
      - name: CancelOrderItem
        text: |-
               az edgeorder order-item cancel --reason "Order cancelled" --name "TestOrderItemName1" --resource-group \
"TestRG"
"""

helps['edgeorder order-item return'] = """
    type: command
    short-summary: "Return order item."
    parameters:
      - name: --shipping-address
        short-summary: "Shipping details for the address"
        long-summary: |
            Usage: --shipping-address street-address1=XX street-address2=XX street-address3=XX city=XX \
state-or-province=XX country=XX postal-code=XX zip-extended-code=XX company-name=XX address-type=XX

            street-address1: Required. Street Address line 1.
            street-address2: Street Address line 2.
            street-address3: Street Address line 3.
            city: Name of the City.
            state-or-province: Name of the State or Province.
            country: Required. Name of the Country.
            postal-code: Postal code.
            zip-extended-code: Extended Zip Code.
            company-name: Name of the company.
            address-type: Type of address.
      - name: --contact-details
        short-summary: "Contact details for the address"
        long-summary: |
            Usage: --contact-details contact-name=XX phone=XX phone-extension=XX mobile=XX email-list=XX

            contact-name: Required. Contact name of the person.
            phone: Required. Phone number of the contact person.
            phone-extension: Phone extension number of the contact person.
            mobile: Mobile number of the contact person.
            email-list: Required. List of Email-ids to be notified about job progress.
    examples:
      - name: ReturnOrderItem
        text: |-
               az edgeorder order-item return --name "TestOrderName1" --resource-group "TestRG" --return-reason "Order \
returned"
"""

helps['edgeorder address wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the address is met.
    parameters:
      - name: --address-name
        short-summary: "The name of the address Resource within the specified resource group."
"""

helps['edgeorder order-item wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the order-item is met.
    parameters:
      - name: --expand
        short-summary: "$expand is supported on device details, forward shipping details and reverse shipping details parameters."
      - name: --order-item-name
        short-summary: "The name of the order item."
"""
