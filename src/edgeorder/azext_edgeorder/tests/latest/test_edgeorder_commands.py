# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json

from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest
)


class EdgeOrderClientTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="cli_test_edgeorder_", location="eastus")
    def test_edgeorder_address_crud(self):
        self.kwargs.update({
            "name": "Petr Cech",
            "email": "testemail@microsoft.com",
            "phone": "1234567890",
            "city": "San Francisco",
            "company": "Microsoft",
            "country": "US",
            "code": "94107",
            "state": "CA",
            "address1": "16 TOWNSEND ST",
            "address2": "UNIT 1"
        })
        self.cmd(
            "edgeorder address create -n TestAddressName -g {rg} "
            "--contact-details contact-name='{name}' email-list={email} phone={phone} phone-extension='' "
            "--shipping-address address-type='None' city='{city}' company-name={company} country={country} postal-code={code} state-or-province={state} street-address1='{address1}' street-address2='{address2}'",
            checks=[
                self.check("name", "TestAddressName"),
                self.check("type", "Microsoft.EdgeOrder/addresses")
            ]
        )
        self.cmd(
            "edgeorder address show -n TestAddressName -g {rg}",
            checks=[
                self.check("name", "TestAddressName"),
                self.check("type", "Microsoft.EdgeOrder/addresses")
            ]
        )
        self.cmd(
            "edgeorder address update -n TestAddressName -g {rg} "
            "--contact-details contact-name='{name}' email-list=ssemcr@microsoft.com phone={phone} phone-extension='' "
            "--shipping-address address-type='None' city='{city}' company-name={company} country={country} postal-code={code} state-or-province={state} street-address1='{address1}' street-address2='{address2}'"
        )
        self.cmd(
            "edgeorder address list -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].contactDetails.emailList[0]", "ssemcr@microsoft.com")
            ]
        )
        self.cmd("edgeorder address delete -n TestAddressName -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_edgeorder_", location="eastus")
    def test_edgeorder_order_crud(self):
        self.kwargs.update({
            "order1": "TestOrderItemName01",
            "order2": "TestOrderItemName02",
        })

        # obtain order IDs
        self.kwargs["order_id1"] = f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{self.kwargs['rg']}/providers/Microsoft.EdgeOrder/locations/eastus/orders/{self.kwargs['order1']}"
        self.kwargs["order_id2"] = f"/subscriptions/{self.get_subscription_id()}/resourceGroups/{self.kwargs['rg']}/providers/Microsoft.EdgeOrder/locations/eastus/orders/{self.kwargs['order2']}"

        resource_props = {
            "location": "eastus",
            "tags": {},
            "orderItemDetails": {
                "orderItemType": "Purchase",
                "preferences": {
                    "transportPreferences": {
                        "preferredShipmentType": "MicrosoftManaged"
                    }
                },
                "productDetails": {
                    "hierarchyInformation": {
                        "productFamilyName": "azurestackedge",
                        "productLineName": "azurestackedge",
                        "productName": "azurestackedgegpu",
                        "configurationName": "edgep_base"
                    }
                }
            },
            "addressDetails": {
                "forwardAddress": {
                    "shippingAddress": {
                        "streetAddress1": "16 TOWNSEND ST",
                        "streetAddress2": "UNIT 1",
                        "city": "San Francisco",
                        "stateOrProvince": "CA",
                        "country": "US",
                        "postalCode": "94107",
                        "companyName": "Microsoft",
                        "addressType": "None"
                    },
                    "contactDetails": {
                        "contactName": "Petr Cech",
                        "phone": "1234567890",
                        "phoneExtension": "",
                        "emailList": [
                            "testemail@microsoft.com"
                        ]
                    }
                }
            },
            "orderId": self.kwargs["order_id1"]
        }

        # obtain resource JSON strings
        self.kwargs["resource1"] = json.dumps(resource_props)
        resource_props["orderId"] = self.kwargs["order_id2"]
        self.kwargs["resource2"] = json.dumps(resource_props)

        # create two order items
        self.cmd(
            "edgeorder order-item create -n {order1} -g {rg} --order-item-resource '{resource1}'",
            checks=[
                self.check("name", self.kwargs["order1"]),
                self.check("type", "Microsoft.EdgeOrder/orderItems")
            ]
        )
        self.cmd("edgeorder order-item create -n {order2} -g {rg} --order-item-resource '{resource2}'")
        self.cmd(
            "edgeorder order-item list -g {rg}",
            checks=[
                self.check("length(@)", 2),
                self.check("@[0].name", self.kwargs["order1"]),
                self.check("@[1].name", self.kwargs["order2"])
            ]
        )

        self.cmd(
            "edgeorder order list -g {rg}",
            checks=[
                self.check("length(@)", 2),
                self.check("@[0].name", self.kwargs["order1"]),
                self.check("@[1].name", self.kwargs["order2"])
            ]
        )
        self.cmd(
            "edgeorder order show -g {rg} --name {order1} --location eastus",
            checks=[
                self.check("name", "{order1}"),
                self.check("type", "Microsoft.EdgeOrder/orders")
            ]
        )

        # delete one of the order items
        self.cmd("edgeorder order-item cancel -n {order2} -g {rg} --reason 'Order cancelled'")
        self.cmd("edgeorder order-item delete -n {order2} -g {rg} --yes")
        self.cmd(
            "edgeorder order-item list -g {rg}",
            checks=[
                self.check("length(@)", 1),
                self.check("@[0].name", self.kwargs["order1"])
            ]
        )

        self.cmd(
            "edgeorder order-item update -n {order1} -g {rg} --transport-preferences preferred-shipment-type='CustomerManaged'",
            checks=[
                self.check("name", "{order1}"),
                self.check("orderItemDetails.preferences.transportPreferences.preferredShipmentType", "CustomerManaged")
            ]
        )
        self.cmd("edgeorder order-item cancel -n {order1} -g {rg} --reason 'Order cancelled'")
        self.cmd("edgeorder order-item delete -n {order1} -g {rg} --yes")

    @ResourceGroupPreparer(name_prefix="cli_test_edgeorder_", location="eastus")
    def test_edgeorder_list(self):
        self.kwargs.update({
            "name": "azurestackedgegpu",
            "line_name": "azurestackedge",
            "family_name": "azurestackedge"
        })

        metadata_list = self.cmd("edgeorder list-metadata").get_output_in_json()
        assert isinstance(metadata_list, list)
        assert "filterableProperties" in metadata_list[0]
        assert "hierarchyInformation" in metadata_list[0]

        # obtain JSON string
        filters_props = [{
            "filterableProperty": [{
                "type": "ShipToCountries",
                "supportedValues": ["US"]
            }],
            "hierarchyInformation": {
                "productFamilyName": self.kwargs["family_name"],
                "productLineName": self.kwargs["line_name"],
                "productName": self.kwargs["name"]
            }
        }]
        self.kwargs["filters"] = json.dumps(filters_props)

        config_list = self.cmd("edgeorder list-config --configuration-filters '{filters}'").get_output_in_json()
        assert isinstance(config_list, list)
        assert "filterableProperties" in config_list[0]
        assert "hierarchyInformation" in config_list[0]

        # obtain JSON string
        filters_props = {
            "type": "ShipToCountries",
            "supportedValues": ["US"]
        }
        self.kwargs["filters"] = json.dumps(filters_props)

        family_list = self.cmd("edgeorder list-family --filterable-properties azurestackedge='{filters}'").get_output_in_json()
        assert isinstance(family_list, list)
        assert "filterableProperties" in family_list[0]
        assert "productLines" in family_list[0]
