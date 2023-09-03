# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ScenarioTest, record_only

class AzureReservationsTests(ScenarioTest):
    def _validate_reservation_order(self, reservation_order):
        self.assertIsNotNone(reservation_order)
        self.assertIsNotNone(reservation_order['etag'])
        self.assertIsNotNone(reservation_order['id'])
        self.assertIsNotNone(reservation_order['name'])
        self.assertIsNotNone(reservation_order['originalQuantity'])
        self.assertIsNotNone(reservation_order['provisioningState'])
        self.assertIsNotNone(reservation_order['requestDateTime'])
        self.assertIsNotNone(reservation_order['reservations'])
        self.assertIsNotNone(reservation_order['term'])
        self.assertIsNotNone(reservation_order['type'])
        self.assertEqual('microsoft.capacity/reservationorders', reservation_order['type'].lower())

    def _validate_reservation(self, reservation):
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation['location'])
        self.assertGreater(len(reservation['location']), 0)
        self.assertIsNotNone(reservation['etag'])
        self.assertGreater(reservation['etag'], 0)
        self.assertIsNotNone(reservation['id'])
        self.assertIsNotNone(reservation['name'])
        self.assertIsNotNone(reservation['sku'])
        self.assertIsNotNone(reservation['properties'])
        self.assertIsNotNone(reservation['type'])
        self.assertEqual(
            'microsoft.capacity/reservationorders/reservations', reservation['type'].lower())

    def _validate_reservation_refund(self, response):
        self.assertIsNotNone(response)
        self.assertIsNotNone(response['id'])
        self.assertIsNotNone(response['properties'])
        self.assertIsNotNone(response['properties']['sessionId'])
        self.assertEqual(1, response['properties']['quantity'])
        self.assertIsNotNone(response['properties']['billingRefundAmount'])
        self.assertEqual(
            'GBP', response['properties']['billingRefundAmount']['currencyCode'])
        self.assertGreater(response['properties']
                           ['billingRefundAmount']['amount'], 0)
        self.assertIsNotNone(response['properties']['pricingRefundAmount'])
        self.assertEqual(
            'USD', response['properties']['pricingRefundAmount']['currencyCode'])
        self.assertGreater(response['properties']
                           ['pricingRefundAmount']['amount'], 0)
        self.assertIsNotNone(response['properties']['policyResult'])
        self.assertIsNotNone(
            response['properties']['policyResult']['properties'])
        self.assertIsNotNone(
            response['properties']['policyResult']['properties']['consumedRefundsTotal'])
        self.assertEqual('USD', response['properties']['policyResult']
                         ['properties']['consumedRefundsTotal']['currencyCode'])
        self.assertGreater(response['properties']['policyResult']
                           ['properties']['consumedRefundsTotal']['amount'], 0)
        self.assertIsNotNone(
            response['properties']['policyResult']['properties']['maxRefundLimit'])
        self.assertEqual('USD', response['properties']['policyResult']
                         ['properties']['maxRefundLimit']['currencyCode'])
        self.assertEqual(
            50000, response['properties']['policyResult']['properties']['maxRefundLimit']['amount'])
        self.assertIsNotNone(response['properties']['billingInformation'])
        self.assertEqual(
            'Monthly', response['properties']['billingInformation']['billingPlan'])
        self.assertGreater(
            response['properties']['billingInformation']['completedTransactions'], 0)
        self.assertGreater(
            response['properties']['billingInformation']['totalTransactions'], 0)
        self.assertIsNotNone(
            response['properties']['billingInformation']['billingCurrencyTotalPaidAmount'])
        self.assertEqual('GBP', response['properties']['billingInformation']
                         ['billingCurrencyTotalPaidAmount']['currencyCode'])
        self.assertGreater(response['properties']['billingInformation']
                           ['billingCurrencyTotalPaidAmount']['amount'], 0)
        self.assertIsNotNone(
            response['properties']['billingInformation']['billingCurrencyProratedAmount'])
        self.assertEqual('GBP', response['properties']['billingInformation']
                         ['billingCurrencyProratedAmount']['currencyCode'])
        self.assertIsNotNone(
            response['properties']['billingInformation']['billingCurrencyRemainingCommitmentAmount'])
        self.assertEqual('GBP', response['properties']['billingInformation']
                         ['billingCurrencyRemainingCommitmentAmount']['currencyCode'])
        self.assertGreater(response['properties']['billingInformation']
                           ['billingCurrencyRemainingCommitmentAmount']['amount'], 0)

    def _validate_reservation_exchange(self, response):
        self.assertIsNotNone(response)
        self.assertIn(
            '/providers/Microsoft.Capacity/operationResults/', response['id'])
        self.assertEqual('Succeeded', response['status'])
        self.assertIsNotNone(response['name'])
        self.assertIsNotNone(response['properties'])
        self.assertIsNotNone(response['properties']['sessionId'])
        self.assertIsNotNone(response['properties']['netPayable'])
        self.assertEqual(
            'GBP', response['properties']['netPayable']['currencyCode'])
        self.assertGreater(response['properties']['netPayable']['amount'], 0)
        self.assertIsNotNone(response['properties']['refundsTotal'])
        self.assertEqual(
            'GBP', response['properties']['refundsTotal']['currencyCode'])
        self.assertGreater(response['properties']['refundsTotal']['amount'], 0)
        self.assertIsNotNone(response['properties']['purchasesTotal'])
        self.assertEqual(
            'GBP', response['properties']['purchasesTotal']['currencyCode'])
        self.assertGreater(response['properties']
                           ['purchasesTotal']['amount'], 0)
        self.assertIsNotNone(response['properties']['reservationsToPurchase'])
        self.assertEqual(
            2, len(response['properties']['reservationsToPurchase']))
        for item in response['properties']['reservationsToPurchase']:
            self.assertIsNotNone(item['properties'])
            self.assertEqual('eastus', item['properties']['location'])
            self.assertIn('/subscriptions/',
                          item['properties']['billingScopeId'])
            self.assertEqual('P1Y', item['properties']['term'])
            self.assertEqual('Shared', item['properties']['appliedScopeType'])
            self.assertEqual('VirtualMachines',
                             item['properties']['reservedResourceType'])
            self.assertGreater(item['properties']['quantity'], 0)
            self.assertIsNotNone(item['properties']['displayName'])
            self.assertIsNotNone(item['properties']['sku'])
            self.assertIsNotNone(item['properties']['sku']['name'])
            self.assertIsNotNone(item['billingCurrencyTotal'])
            self.assertEqual(
                'GBP', item['billingCurrencyTotal']['currencyCode'])
            self.assertGreater(item['billingCurrencyTotal']['amount'], 0)

        self.assertIsNotNone(response['properties']['reservationsToExchange'])
        self.assertEqual(
            2, len(response['properties']['reservationsToExchange']))
        for item in response['properties']['reservationsToExchange']:
            self.assertIn(
                '/providers/microsoft.capacity/reservationOrders/', item['reservationId'])
            self.assertEqual(1, item['quantity'])
            self.assertIsNotNone(item['billingRefundAmount'])
            self.assertEqual(
                'GBP', item['billingRefundAmount']['currencyCode'])
            self.assertGreater(item['billingRefundAmount']['amount'], 0)
            self.assertIsNotNone(item['billingInformation'])
            self.assertIsNotNone(
                item['billingInformation']['billingCurrencyTotalPaidAmount'])
            self.assertEqual('GBP', item['billingInformation']
                             ['billingCurrencyTotalPaidAmount']['currencyCode'])
            self.assertGreater(
                item['billingInformation']['billingCurrencyTotalPaidAmount']['amount'], 0)
            self.assertIsNotNone(
                item['billingInformation']['billingCurrencyProratedAmount'])
            self.assertEqual('GBP', item['billingInformation']
                             ['billingCurrencyProratedAmount']['currencyCode'])
            self.assertGreaterEqual(
                item['billingInformation']['billingCurrencyProratedAmount']['amount'], 0)
            self.assertIsNotNone(
                item['billingInformation']['billingCurrencyRemainingCommitmentAmount'])
            self.assertEqual('GBP', item['billingInformation']
                             ['billingCurrencyRemainingCommitmentAmount']['currencyCode'])
            self.assertGreaterEqual(
                item['billingInformation']['billingCurrencyRemainingCommitmentAmount']['amount'], 0)

    @record_only()  # This test relies on a subscription id with the existing reservation orders
    def test_get_applied_reservation_order_ids(self):
        self.kwargs.update({
            'subscription': '00000000-0000-0000-0000-000000000000'
        })
        result = self.cmd('reservations reservation-order-id list --subscription-id {subscription}') \
            .get_output_in_json()
        for order_id in result['reservationOrderIds']['value']:
            self.assertIn(
                '/providers/Microsoft.Capacity/reservationorders/', order_id)

    @record_only()  # This test relies on the existing reservation order
    def test_list_reservation_order(self):
        reservation_order_list = self.cmd(
            'reservations reservation-order list').get_output_in_json()
        self.assertIsNotNone(reservation_order_list)
        for order in reservation_order_list:
            self._validate_reservation_order(order)
            self.assertIn(
                '/providers/microsoft.capacity/reservationOrders/', order['id'])
            self.assertGreater(order['etag'], 0)
            for reservation in order['reservations']:
                self.assertTrue(reservation['id'])

    @record_only()  # This test relies on the existing reservation order
    def test_get_reservation_order(self):
        self.kwargs.update({
            'reservation_order_id': '73e63333-9b94-442c-8a5d-9403ba0e8b87'
        })
        command = 'reservations reservation-order show --reservation-order-id {reservation_order_id}'
        reservation_order = self.cmd(command).get_output_in_json()
        self._validate_reservation_order(reservation_order)
        self.assertIn(
            '/providers/microsoft.capacity/reservationOrders/', reservation_order['id'])
        self.assertGreater(reservation_order['etag'], 0)

    @record_only()  # This test relies on the existing reservation order
    def test_list_reservations_in_order(self):
        self.kwargs.update({
            'reservation_order_id': '73e63333-9b94-442c-8a5d-9403ba0e8b87'
        })
        reservation_list = self.cmd('reservations reservation list --reservation-order-id {reservation_order_id}') \
            .get_output_in_json()
        self.assertIsNotNone(reservation_list)
        for reservation in reservation_list:
            self._validate_reservation(reservation)
            self.assertGreater(reservation['etag'], 0)
            self.assertEqual(
                'microsoft.capacity/reservationOrders/reservations', reservation['type'])
            
    @record_only()  # This test relies on the existing reservation order
    def test_list_reservations(self):
        reservation_list = self.cmd('reservations list').get_output_in_json()
        self.assertIsNotNone(reservation_list)
        for reservation in reservation_list:
            self._validate_reservation(reservation)

        self.kwargs.update({
            'state': 'Cancelled'
        })
        reservation_list1 = self.cmd('reservations list --selected-state {state}').get_output_in_json()
        for reservation in reservation_list1:
            self.assertEqual("Cancelled", reservation['properties']['displayProvisioningState'])

        self.kwargs.update({
            'filter': "properties/reservedResourceType eq \'SuseLinux\'"
        })
        reservation_list2 = self.cmd('reservations list --filter \"{filter}\"').get_output_in_json()
        for reservation in reservation_list2:
            self.assertEqual("SuseLinux", reservation['properties']['reservedResourceType'])

        self.kwargs.update({
            'orderby': 'properties/quantity desc'
        })
        reservation_list3 = self.cmd('reservations list --orderby \'{orderby}\'').get_output_in_json()
        index = 1
        while index < len(reservation_list3):
            self.assertTrue(reservation_list3[index-1]['properties']['quantity'] >= reservation_list3[index]['properties']['quantity'])
            index += 1

    @record_only()  # This test relies on the existing reservation order
    def test_get_reservation(self):
        self.kwargs.update({
            'reservation_order_id': '73e63333-9b94-442c-8a5d-9403ba0e8b87',
            'reservation_id': 'ab9761bb-324c-474a-b96c-3471bd643328'
        })
        reservation = self.cmd('reservations reservation show  --reservation-order-id {reservation_order_id} '
                               '--reservation-id {reservation_id}').get_output_in_json()
        self.assertEqual(self.kwargs['reservation_id'], reservation['name'])
        self.assertGreater(reservation['etag'], 0)
        self.assertGreater(reservation['properties']['quantity'], 0)
        self.assertEqual(
            'microsoft.capacity/reservationOrders/reservations', reservation['type'])

    @record_only()  # This test relies on the existing reservation order
    def test_list_reservation_history(self):
        self.kwargs.update({
            'reservation_order_id': '73e63333-9b94-442c-8a5d-9403ba0e8b87',
            'reservation_id': 'ab9761bb-324c-474a-b96c-3471bd643328'
        })
        history = self.cmd('reservations reservation list-history --reservation-order-id {reservation_order_id}'
                           ' --reservation-id {reservation_id}').get_output_in_json()
        self.assertGreater(len(history), 0)
        for entry in history:
            self.assertGreater(entry['etag'], 0)
            self.assertIsNotNone(entry['sku'])
            self.assertIsNotNone(entry['id'])
            self.assertIsNotNone(entry['properties'])
            self.assertIsNotNone(entry['properties']['reservedResourceType'])
            self.assertIsNotNone(entry['properties']['appliedScopeType'])
            self.assertIsNotNone(entry['properties']['quantity'])
            self.assertIsNotNone(entry['properties']['provisioningState'])
            self.assertIsNotNone(entry['properties']['displayName'])

    @record_only()  # This test relies on a subscription with reservation permissions
    def test_get_catalog(self):
        self.kwargs.update({
            'subscription': '00000000-0000-0000-0000-000000000000',
            'type': 'VirtualMachines',
            'location': 'westus'
        })
        catalog = self.cmd(
            'reservations catalog show --subscription-id {subscription} --reserved-resource-type {type} --location {location}').get_output_in_json()
        self.assertIsNotNone(catalog)
        self.assertIsNotNone(catalog['value'])

        for entry in catalog['value']:
            self.assertGreater(len(entry['terms']), 0)
            self.assertGreater(len(entry['skuProperties']), 0)
            self.assertIsNotNone(entry['resourceType'])
            self.assertIsNotNone(entry['name'])

    @record_only()  # This test relies on the existing reservation order
    def test_update_reservation(self):
        renew_properties = '{applied-scope-type:Shared,billing-plan:Monthly,billing-scope-id:/subscriptions/00000000-0000-0000-0000-000000000000,display-name:TestRenewalCLI,instance-flexibility:On,quantity:5,term:P1Y,reserved-resource-type:VirtualMachines,sku:Standard_B1ls,Location:eastus}'
        self.kwargs.update({
            'reservation_order_id': 'a3896858-3f6c-4ce6-bf6c-003a31325fdd',
            'reservation_id': 'f8887b7e-e8bf-4ddb-8290-405928206191',
            'scope': '/subscriptions/00000000-0000-0000-0000-000000000000',
            'instance_flexibility': 'Off',
            'new_name': 'NewRIName',
            'renew': 'true',
            'renew_properties': renew_properties
        })

        # Change RI to Shared scope
        reservation = self.cmd('reservations reservation update --reservation-order-id {reservation_order_id} '
                                      '--reservation-id {reservation_id} --applied-scope-type Shared').get_output_in_json()
        self.assertEqual(
            'Shared', reservation['properties']['appliedScopeType'])

        # Change RI to Single scope
        reservation = self.cmd('reservations reservation update --reservation-order-id {reservation_order_id}'
                                      ' --reservation-id {reservation_id} --applied-scope-type Single --applied-scopes {scope}'
                                      ' --instance-flexibility {instance_flexibility}').get_output_in_json()
        self.assertEqual(
            'Single', reservation['properties']['appliedScopeType'])
        self.assertEqual(
            'Off', reservation['properties']['instanceFlexibility'])

        # Renaming RI
        reservation = self.cmd('reservations reservation update --reservation-order-id {reservation_order_id} '
                                      '--reservation-id {reservation_id} --name {new_name}').get_output_in_json()
        self.assertEqual(
            'NewRIName', reservation['properties']['displayName'])

        # Turn on auto renewal
        self.cmd('reservations reservation update --reservation-order-id {reservation_order_id} '
                                      '--reservation-id {reservation_id} --renew {renew} --renewal-properties {renew_properties}').get_output_in_json()
        reservation = self.cmd('reservations reservation show --reservation-id {reservation_id} --reservation-order-id {reservation_order_id} --expand renewProperties').get_output_in_json()
        self.assertEqual(
            'On', reservation['properties']['userFriendlyRenewState'])
        purchaseProperties = reservation['properties']['renewProperties']['purchaseProperties']
        self.assertEqual(
            'Standard_B1ls', purchaseProperties['sku']['name'])
        self.assertEqual(
            'eastus', purchaseProperties['location'])
        self.assertEqual(
            'P1Y', purchaseProperties['term'])
        self.assertEqual(
            'Monthly', purchaseProperties['billingPlan'])
        self.assertEqual(
            5, purchaseProperties['quantity'])
        self.assertEqual(
            'TestRenewalCLI', purchaseProperties['displayName'])
        self.assertEqual(
            'Shared', purchaseProperties['appliedScopeType'])
        self.assertEqual(
            'VirtualMachines', purchaseProperties['reservedResourceType'])
        self.assertEqual(
            'On', purchaseProperties['reservedResourceProperties']['instanceFlexibility'])

    @record_only()  # This test relies on the existing reservation order
    def test_split_and_merge(self):
        self.kwargs.update({
            'reservation_order_id': '66c42073-5bd1-475d-87d9-e9e6ac95cce7',
            'reservation_id': '7d1acf3c-3fb0-4240-9a75-d158f112adfe',
            'quantities': '[1,1]'
        })

        original_reservation = self.cmd('reservations reservation show --reservation-order-id {reservation_order_id}'
                                        ' --reservation-id {reservation_id}').get_output_in_json()
        original_quantity = original_reservation['properties']['quantity']

        split_items = self.cmd('reservations reservation split --reservation-order-id {reservation_order_id} '
                               '--reservation-id /providers/Microsoft.Capacity/reservationOrders/{reservation_order_id}/reservations/{reservation_id} '
                               '--quantities {quantities}').get_output_in_json()
        self.assertIsNotNone(split_items)

        quantity_sum = 0
        split_ids = []
        for item in split_items:
            self._validate_reservation(item)
            if 'Cancelled' in item['properties']['provisioningState']:
                for i in item['properties']['splitProperties']['splitDestinations']:
                    split_ids.append(i)
            elif 'Succeeded' in item['properties']['provisioningState']:
                quantity_sum += item['properties']['quantity']

        self.assertEqual(original_quantity, quantity_sum)
        self.kwargs.update({
            'split_id1': split_ids[0],
            'split_id2': split_ids[1]
        })
        merge_items = self.cmd(
            'reservations reservation merge --reservation-order-id {reservation_order_id} --sources [{split_id1},{split_id2}]').get_output_in_json()
        self.assertIsNotNone(merge_items)
        for item in merge_items:
            self._validate_reservation(item)
            if 'Succeeded' in item['properties']['provisioningState']:
                self.assertEqual(quantity_sum, item['properties']['quantity'])

    @record_only()  # This test relies on a subscription with reservation permissions
    def test_calculate_reservation_order(self):
        self.kwargs.update({
            'subid': '00000000-0000-0000-0000-000000000000',
            'sku': 'standard_b1ls',
            'location': 'westus',
            'reservedResourceType': 'VirtualMachines',
            'term': 'P1Y',
            'quantity': '2',
            'displayName': 'clitest',
            'appliedScopes': 'Shared',
            'instanceFlexibility': 'Off',
            'billingPlan': 'Monthly',
            'appliedScopeType': 'Shared'
        })
        response = self.cmd('reservations reservation-order calculate --sku {sku} --location {location} --reserved-resource-type {reservedResourceType}'
                            ' --billing-scope {subid} --term {term} --billing-plan {billingPlan} --display-name {displayName}'
                            ' --quantity {quantity} --applied-scope-type {appliedScopeType}').get_output_in_json()
        self.assertIsNotNone(response)
        self.assertIsNotNone(response['properties']['billingCurrencyTotal'])
        self.assertIsNotNone(response['properties']['pricingCurrencyTotal'])
        self.assertIsNotNone(
            response['properties']['pricingCurrencyTotal']['currencyCode'])
        self.assertEqual(
            'GBP', response['properties']['pricingCurrencyTotal']['currencyCode'])
        self.assertEqual(
            'GBP', response['properties']['billingCurrencyTotal']['currencyCode'])
        self.assertGreater(response['properties']
                           ['pricingCurrencyTotal']['amount'], 0)
        self.assertGreater(response['properties']
                           ['billingCurrencyTotal']['amount'], 0)
        self.assertIsNotNone(response['properties']['reservationOrderId'])
        self.assertEqual(
            'standard_b1ls', response['properties']['skuDescription'])

    @record_only()  # This test relies on a subscription with reservation purchase permissions
    def test_purchase_reservation_order(self):
        self.kwargs.update({
            'subid': '00000000-0000-0000-0000-000000000000',
            'sku': 'standard_b1ls',
            'location': 'westus',
            'reservedResourceType': 'VirtualMachines',
            'term': 'P1Y',
            'quantity': '2',
            'displayName': 'clitest2',
            'appliedScopes': 'Shared',
            'instanceFlexibility': 'Off',
            'billingPlan': 'Monthly',
            'appliedScopeType': 'Shared'
        })
        response = self.cmd('reservations reservation-order calculate --sku {sku} --location {location} --reserved-resource-type {reservedResourceType}'
                            ' --billing-scope {subid} --term {term} --billing-plan {billingPlan} --display-name {displayName}'
                            ' --quantity {quantity} --applied-scope-type {appliedScopeType}').get_output_in_json()
        self.kwargs.update({
            'roid': response['properties']['reservationOrderId']
        })
        response2 = self.cmd('reservations reservation-order purchase --reservation-order-id {roid} --sku {sku} --location {location} --reserved-resource-type {reservedResourceType}'
                             ' --billing-scope {subid} --term {term} --billing-plan {billingPlan} --display-name {displayName}'
                             ' --quantity {quantity} --applied-scope-type {appliedScopeType}').get_output_in_json()
        self.assertIsNotNone(response2)
        self.assertGreater(response2['etag'], 0)
        self.assertEqual(
            "microsoft.capacity/reservationOrders", response2['type'])
        self.assertEqual(
            "/providers/microsoft.capacity/reservationOrders/dbbcc369-214d-44e3-bd7f-d019c07e9eea", response2['id'])
        self.assertEqual(
            "dbbcc369-214d-44e3-bd7f-d019c07e9eea", response2['name'])
        self.assertEqual("P1Y", response2['term'])
        self.assertEqual("clitest2", response2['displayName'])
        self.assertEqual(2, response2['originalQuantity'])
        self.assertEqual('Monthly', response2['billingPlan'])
        self.assertEqual('PendingCapacity', response2['provisioningState'])
        self.assertGreater(len(response2['reservations']), 0)

    @record_only()
    def test_archive_unarchive_reservation(self):
        self.kwargs.update({
            'reservation_order_id': 'cbf65207-851e-4999-9eee-a1996989a7de',
            'reservation_id': 'd896dea2-a685-46cd-88d8-b3561cb0bf3d',
        })
        response = self.cmd(
            'reservations reservation archive --reservation-order-id {reservation_order_id} --reservation-id {reservation_id}')
        self.assertIsNotNone(response)
        response = self.cmd(
            'reservations reservation unarchive --reservation-order-id {reservation_order_id} --reservation-id {reservation_id}')
        self.assertIsNotNone(response)

    @record_only()
    def test_reservation_available_scope(self):
        self.kwargs.update({
            'reservation_order_id': '85334623-a4b6-4b61-a3f4-e78ff02c33de',
            'reservation_id': 'a21526d3-1b94-4b43-a6b3-6f496e893251',
            'subscription_id': '00000000-0000-0000-0000-000000000000'
        })
        response = self.cmd('reservations reservation list-available-scope --reservation-order-id {reservation_order_id} --reservation-id {reservation_id}'
                            ' --scopes [/subscriptions/{subscription_id}]').get_output_in_json()

        self.assertIsNotNone(response)
        self.assertIsNotNone(response['properties'])
        self.assertIsNotNone(response['properties']['scopes'])
        self.assertEqual(1, len(response['properties']['scopes']))
        self.assertIn("/subscriptions/",
                      response['properties']['scopes'][0]['scope'])
        self.assertEqual(True, response['properties']['scopes'][0]['valid'])

    @record_only()
    def test_reservation_order_change_directory(self):
        self.kwargs.update({
            'reservation_order_id': 'e346ad58-5aa6-41ff-bac6-9ce2740ecf17',
            'destination_tenant_id': '4adcf5e7-539d-451c-85d5-b6c3b47335d7'
        })
        response = self.cmd('reservations reservation-order change-directory --reservation-order-id {reservation_order_id} '
                            '--destination-tenant-id {destination_tenant_id}').get_output_in_json()
        self.assertIsNotNone(response)
        self.assertIsNotNone(response['reservationOrder'])
        self.assertEqual("e346ad58-5aa6-41ff-bac6-9ce2740ecf17",
                         response['reservationOrder']['id'])
        self.assertEqual("VM_RI_02-10-2023_15-15",
                         response['reservationOrder']['name'])
        self.assertEqual(True, response['reservationOrder']['isSucceeded'])
        self.assertIsNotNone(response['reservations'])
        self.assertEqual(19, len(response['reservations']))
        self.assertEqual("6e367b50-24a9-435a-b7d2-9b653c2c44fe",
                         response['reservations'][0]['id'])
        self.assertEqual("VM_RI_02-10-2023_15-15",
                         response['reservations'][0]['name'])
        self.assertEqual(True, response['reservations'][0]['isSucceeded'])

    @record_only()
    def test_reservation_refund(self):
        self.kwargs.update({
            'reservation_order_id': '62069b8a-8f84-49ab-9a4a-f69009390876',
            'reservation_id': '9cb27776-afb6-43f6-8493-70dd3cd9321f',
            'scope': 'Reservation',
            'quantity': '1'
        })
        response = self.cmd('reservations reservation-order calculate-refund --reservation-order-id {reservation_order_id}'
                            ' --id /providers/microsoft.capacity/reservationOrders/{reservation_order_id} --scope {scope}'
                            ' --quantity {quantity} --reservation-id /providers/microsoft.capacity/reservationOrders/{reservation_order_id}/reservations/{reservation_id}').get_output_in_json()
        self._validate_reservation_refund(response)
        self.kwargs.update({
            'reason': 'testing',
            'session_id': response['properties']['sessionId']
        })
        response1 = self.cmd('reservations reservation-order return --reservation-order-id {reservation_order_id}'
                             ' --return-reason {reason} --scope {scope} --session-id {session_id}'
                             ' --quantity {quantity} --reservation-id /providers/microsoft.capacity/reservationOrders/{reservation_order_id}/reservations/{reservation_id}').get_output_in_json()
        self._validate_reservation_order(response1)

    @record_only()
    def test_reservation_exchange(self):
        reservation_to_exchange1 = '{reservation-id:/providers/microsoft.capacity/reservationOrders/85334623-a4b6-4b61-a3f4-e78ff02c33de/reservations/a21526d3-1b94-4b43-a6b3-6f496e893251,quantity:1}'
        reservation_to_exchange2 = '{reservation-id:/providers/microsoft.capacity/reservationOrders/66c42073-5bd1-475d-87d9-e9e6ac95cce7/reservations/257c402b-3c6f-4979-9ab7-31f88d0ce1fe,quantity:1}'
        reservations_to_exchange = '[{},{}]'.format(
            reservation_to_exchange1, reservation_to_exchange2)

        reservation_to_purchase1 = '{reserved-resource-type:VirtualMachines,applied-scope-type:Shared,billing-scope:00000000-0000-0000-0000-000000000000,display-name:exchangeTest1,quantity:3,sku:Standard_B1s,term:P1Y,billing-plan:Upfront,location:eastus}'
        reservation_to_purchase2 = '{reserved-resource-type:VirtualMachines,applied-scope-type:Shared,billing-scope:00000000-0000-0000-0000-000000000000,display-name:exchangeTest2,quantity:3,sku:Standard_B2s,term:P1Y,billing-plan:Monthly,location:eastus}'
        reservations_to_purchase = '[{},{}]'.format(
            reservation_to_purchase1, reservation_to_purchase2)
        self.kwargs.update({
            'reservations_to_exchange': reservations_to_exchange,
            'reservations_to_purchase': reservations_to_purchase,
        })
        response = self.cmd(
            'reservations calculate-exchange --ris-to-exchange {reservations_to_exchange} --ris-to-purchase {reservations_to_purchase}').get_output_in_json()
        self._validate_reservation_exchange(response)
        self.kwargs.update({
            'session_id': response['properties']['sessionId'],
        })
        response1 = self.cmd(
            'reservations exchange --session-id {session_id}').get_output_in_json()
        self._validate_reservation_exchange(response1)
