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
        self.assertTrue(reservation_order['type'] == 'microsoft.capacity/reservationOrders')

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
        self.assertTrue(reservation['type'] == 'Microsoft.Capacity/reservationOrders/reservations')

    def _validate_reservation_refund(self, response):
        self.assertIsNotNone(response)
        self.assertIsNotNone(response['id'])
        self.assertIsNotNone(response['properties'])
        self.assertIsNotNone(response['properties']['sessionId'])
        self.assertEqual(1, response['properties']['quantity'])
        self.assertIsNotNone(response['properties']['billingRefundAmount'])
        self.assertEqual('GBP', response['properties']['billingRefundAmount']['currencyCode'])
        self.assertGreater(response['properties']['billingRefundAmount']['amount'], 0)
        self.assertIsNotNone(response['properties']['pricingRefundAmount'])
        self.assertEqual('USD', response['properties']['pricingRefundAmount']['currencyCode'])
        self.assertGreater(response['properties']['pricingRefundAmount']['amount'], 0)
        self.assertIsNotNone(response['properties']['policyResult'])
        self.assertIsNotNone(response['properties']['policyResult']['properties'])
        self.assertIsNotNone(response['properties']['policyResult']['properties']['consumedRefundsTotal'])
        self.assertEqual('USD', response['properties']['policyResult']['properties']['consumedRefundsTotal']['currencyCode'])
        self.assertGreater(response['properties']['policyResult']['properties']['consumedRefundsTotal']['amount'], 0)
        self.assertIsNotNone(response['properties']['policyResult']['properties']['maxRefundLimit'])
        self.assertEqual('USD', response['properties']['policyResult']['properties']['maxRefundLimit']['currencyCode'])
        self.assertEqual(50000, response['properties']['policyResult']['properties']['maxRefundLimit']['amount'])
        self.assertIsNotNone(response['properties']['billingInformation'])
        self.assertEqual('Monthly', response['properties']['billingInformation']['billingPlan'])
        self.assertGreater(response['properties']['billingInformation']['completedTransactions'], 0)
        self.assertGreater(response['properties']['billingInformation']['totalTransactions'], 0)
        self.assertIsNotNone(response['properties']['billingInformation']['billingCurrencyTotalPaidAmount'])
        self.assertEqual('GBP', response['properties']['billingInformation']['billingCurrencyTotalPaidAmount']['currencyCode'])
        self.assertGreater(response['properties']['billingInformation']['billingCurrencyTotalPaidAmount']['amount'], 0)
        self.assertIsNotNone(response['properties']['billingInformation']['billingCurrencyProratedAmount'])
        self.assertEqual('GBP', response['properties']['billingInformation']['billingCurrencyProratedAmount']['currencyCode'])
        self.assertIsNotNone(response['properties']['billingInformation']['billingCurrencyRemainingCommitmentAmount'])
        self.assertEqual('GBP', response['properties']['billingInformation']['billingCurrencyRemainingCommitmentAmount']['currencyCode'])
        self.assertGreater(response['properties']['billingInformation']['billingCurrencyRemainingCommitmentAmount']['amount'], 0)

    def _validate_reservation_exchange(self, response):
        self.assertIsNotNone(response)
        self.assertIn('/providers/Microsoft.Capacity/operationResults/', response['id'])
        self.assertEqual('Succeeded', response['status'])
        self.assertIsNotNone(response['name'])
        self.assertIsNotNone(response['properties'])
        self.assertIsNotNone(response['properties']['sessionId'])
        self.assertIsNotNone(response['properties']['netPayable'])
        self.assertEqual('GBP', response['properties']['netPayable']['currencyCode'])
        self.assertGreater(response['properties']['netPayable']['amount'], 0)
        self.assertIsNotNone(response['properties']['refundsTotal'])
        self.assertEqual('GBP', response['properties']['refundsTotal']['currencyCode'])
        self.assertGreater(response['properties']['refundsTotal']['amount'], 0)        
        self.assertIsNotNone(response['properties']['purchasesTotal'])
        self.assertEqual('GBP', response['properties']['purchasesTotal']['currencyCode'])
        self.assertGreater(response['properties']['purchasesTotal']['amount'], 0)
        self.assertIsNotNone(response['properties']['reservationsToPurchase'])
        self.assertEqual(2, len(response['properties']['reservationsToPurchase']))
        for item in response['properties']['reservationsToPurchase']:
            self.assertIsNotNone(item['properties'])
            self.assertEqual('eastus', item['properties']['location'])
            self.assertIn('/subscriptions/', item['properties']['billingScopeId'])
            self.assertEqual('P1Y', item['properties']['term'])
            self.assertEqual('Shared', item['properties']['appliedScopeType'])
            self.assertEqual('VirtualMachines', item['properties']['reservedResourceType'])
            self.assertGreater(item['properties']['quantity'], 0)
            self.assertIsNotNone(item['properties']['displayName'])
            self.assertIsNotNone(item['properties']['sku'])
            self.assertIsNotNone(item['properties']['sku']['name'])
            self.assertIsNotNone(item['billingCurrencyTotal'])
            self.assertEqual('GBP', item['billingCurrencyTotal']['currencyCode'])
            self.assertGreater(item['billingCurrencyTotal']['amount'], 0)
        
        self.assertIsNotNone(response['properties']['reservationsToExchange'])
        self.assertEqual(2, len(response['properties']['reservationsToExchange']))
        for item in response['properties']['reservationsToExchange']:
            self.assertIn('/providers/microsoft.capacity/reservationOrders/', item['reservationId'])
            self.assertEqual(1, item['quantity'])
            self.assertIsNotNone(item['billingRefundAmount'])
            self.assertEqual('GBP', item['billingRefundAmount']['currencyCode'])
            self.assertGreater(item['billingRefundAmount']['amount'], 0)
            self.assertIsNotNone(item['billingInformation'])
            self.assertIsNotNone(item['billingInformation']['billingCurrencyTotalPaidAmount'])
            self.assertEqual('GBP', item['billingInformation']['billingCurrencyTotalPaidAmount']['currencyCode'])
            self.assertGreater(item['billingInformation']['billingCurrencyTotalPaidAmount']['amount'], 0)
            self.assertIsNotNone(item['billingInformation']['billingCurrencyProratedAmount'])
            self.assertEqual('GBP', item['billingInformation']['billingCurrencyProratedAmount']['currencyCode'])
            self.assertGreaterEqual(item['billingInformation']['billingCurrencyProratedAmount']['amount'], 0)
            self.assertIsNotNone(item['billingInformation']['billingCurrencyRemainingCommitmentAmount'])
            self.assertEqual('GBP', item['billingInformation']['billingCurrencyRemainingCommitmentAmount']['currencyCode'])
            self.assertGreaterEqual(item['billingInformation']['billingCurrencyRemainingCommitmentAmount']['amount'], 0)

    # @record_only()  # This test relies on a subscription id with the existing reservation orders
    # def test_get_applied_reservation_order_ids(self):
    #     self.kwargs.update({
    #         'subscription': '00000000-0000-0000-0000-000000000000'
    #     })
    #     result = self.cmd('reservations reservation-order-id list --subscription-id {subscription}') \
    #         .get_output_in_json()
    #     for order_id in result['reservationOrderIds']['value']:
    #         self.assertIn('/providers/Microsoft.Capacity/reservationorders/', order_id)

    # @record_only()  # This test relies on the existing reservation order
    # def test_list_reservation_order(self):
    #     reservation_order_list = self.cmd('reservations reservation-order list').get_output_in_json()
    #     self.assertIsNotNone(reservation_order_list)
    #     for order in reservation_order_list:
    #         self._validate_reservation_order(order)
    #         self.assertIn('/providers/microsoft.capacity/reservationOrders/', order['id'])
    #         self.assertGreater(order['etag'], 0)
    #         for reservation in order['reservations']:
    #             self.assertTrue(reservation['id'])

    # @record_only()  # This test relies on the existing reservation order
    # def test_get_reservation_order(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '99f340d1-6db4-41b4-b469-cfc499716973'
    #     })
    #     command = 'reservations reservation-order show --reservation-order-id {reservation_order_id}'
    #     reservation_order = self.cmd(command).get_output_in_json()
    #     self._validate_reservation_order(reservation_order)
    #     self.assertIn('/providers/microsoft.capacity/reservationOrders/', reservation_order['id'])
    #     self.assertGreater(reservation_order['etag'], 0)

    # @record_only()  # This test relies on the existing reservation order
    # def test_list_reservation(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '99f340d1-6db4-41b4-b469-cfc499716973'
    #     })
    #     reservation_list = self.cmd('reservations reservation list --reservation-order-id {reservation_order_id}') \
    #         .get_output_in_json()
    #     self.assertIsNotNone(reservation_list)
    #     for reservation in reservation_list:
    #         self.assertGreater(reservation['etag'], 0)
    #         self.assertEqual('microsoft.capacity/reservationOrders/reservations', reservation['type'])

    # @record_only()  # This test relies on the existing reservation order
    # def test_get_reservation(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '99f340d1-6db4-41b4-b469-cfc499716973',
    #         'reservation_id': 'a7d70646-b848-4498-8093-5938128b225c'
    #     })
    #     reservation = self.cmd('reservations reservation show  --reservation-order-id {reservation_order_id} '
    #                            '--reservation-id {reservation_id}').get_output_in_json()
    #     self.assertEqual(self.kwargs['reservation_id'], reservation['name'])
    #     self.assertGreater(reservation['etag'], 0)
    #     self.assertGreater(reservation['properties']['quantity'], 0)
    #     self.assertEqual('microsoft.capacity/reservationOrders/reservations', reservation['type'])

    # @record_only()  # This test relies on the existing reservation order
    # def test_list_reservation_history(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '99f340d1-6db4-41b4-b469-cfc499716973',
    #         'reservation_id': 'a7d70646-b848-4498-8093-5938128b225c'
    #     })
    #     history = self.cmd('reservations reservation list-history --reservation-order-id {reservation_order_id}'
    #                        ' --reservation-id {reservation_id}').get_output_in_json()
    #     self.assertGreater(len(history), 0)
    #     for entry in history:
    #         self.assertGreater(entry['etag'], 0)
    #         self.assertIsNotNone(entry['sku'])
    #         self.assertIsNotNone(entry['id'])
    #         self.assertIsNotNone(entry['properties'])
    #         self.assertIsNotNone(entry['properties']['reservedResourceType'])
    #         self.assertIsNotNone(entry['properties']['appliedScopeType'])
    #         self.assertIsNotNone(entry['properties']['quantity'])
    #         self.assertIsNotNone(entry['properties']['provisioningState'])
    #         self.assertIsNotNone(entry['properties']['displayName'])

    # @record_only()  # This test relies on a subscription with reservation permissions
    # def test_get_catalog(self):
    #     self.kwargs.update({
    #         'subscription': '00000000-0000-0000-0000-000000000000',
    #         'type': 'VirtualMachines',
    #         'location': 'westus'
    #     })
    #     catalog = self.cmd(
    #         'reservations catalog show --subscription-id {subscription} --reserved-resource-type {type} --location {location}').get_output_in_json()
    #     self.assertIsNotNone(catalog)
    #     self.assertIsNotNone(catalog['value'])

    #     for entry in catalog['value']:
    #         self.assertGreater(len(entry['terms']), 0)
    #         self.assertGreater(len(entry['skuProperties']), 0)
    #         self.assertIsNotNone(entry['resourceType'])
    #         self.assertIsNotNone(entry['name'])

    # @record_only()  # This test relies on the existing reservation order
    # def test_update_reservation(self):
    #     self.kwargs.update({
    #         'reservation_order_id': 'c38bef9c-6199-452a-85af-290b5b4616b0',
    #         'reservation_id': 'a132a5c3-51d4-4d6f-b380-f27a4ff7ea84',
    #         'scope': '/subscriptions/00000000-0000-0000-0000-000000000000',
    #         'instance_flexibility': 'Off'
    #     })

    #     shared_reservation = self.cmd('reservations reservation update --reservation-order-id {reservation_order_id} '
    #                                   '--reservation-id {reservation_id} --applied-scope-typ Shared').get_output_in_json()
    #     self.assertEqual('Shared', shared_reservation['properties']['appliedScopeType'])

    #     single_reservation = self.cmd('reservations reservation update --reservation-order-id {reservation_order_id}'
    #                                   ' --reservation-id {reservation_id} --applied-scope-type Single --applied-scopes {scope}'
    #                                   ' --instance-flexibility {instance_flexibility}').get_output_in_json()
    #     self.assertEqual('Single', single_reservation['properties']['appliedScopeType'])

    # @record_only()  # This test relies on the existing reservation order
    # def test_split_and_merge(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '6d1613d2-d4f8-454d-aef3-fe6d5c8bef95',
    #         'reservation_id': '646d427e-a133-4cb6-9f28-3de6157de83e',
    #         'quantities': '[1,1]'
    #     })

    #     original_reservation = self.cmd('reservations reservation show --reservation-order-id {reservation_order_id}'
    #                                     ' --reservation-id {reservation_id}').get_output_in_json()
    #     original_quantity = original_reservation['properties']['quantity']

    #     split_items = self.cmd('reservations reservation split --reservation-order-id {reservation_order_id} '
    #                            '--reservation-id /providers/Microsoft.Capacity/reservationOrders/{reservation_order_id}/reservations/{reservation_id} '
    #                            '--quantities {quantities}').get_output_in_json()
    #     self.assertIsNotNone(split_items)

    #     quantity_sum = 0
    #     split_ids = []
    #     for item in split_items:
    #         self._validate_reservation(item)
    #         if 'Succeeded' in item['properties']['provisioningState']:
    #             item_id = item['name'].split('/')[1]
    #             split_ids.append(item_id)
    #             quantity_sum += item['properties']['quantity']
    #     self.assertEqual(original_quantity, quantity_sum)
    #     self.assertEqual(2, len(split_ids))
    #     self.kwargs.update({
    #         'split_id1': split_ids[0],
    #         'split_id2': split_ids[1],
    #         'sources': '[/providers/Microsoft.Capacity/reservationOrders/{reservation_order_id}/reservations/{split_id1},'
    #                            '/providers/Microsoft.Capacity/reservationOrders/{reservation_order_id}/reservations/{split_id2}]'
    #     })
    #     merge_items = self.cmd('reservations reservation merge --reservation-order-id {reservation_order_id} --sources {sources}').get_output_in_json()
    #     self.assertIsNotNone(merge_items)
    #     for item in merge_items:
    #         self._validate_reservation(item)
    #         if 'Succeeded' in item['properties']['provisioningState']:
    #             self.assertEqual(quantity_sum, item['properties']['quantity'])

    # @record_only()  # This test relies on a subscription with reservation permissions
    # def test_calculate_reservation_order(self):
    #     self.kwargs.update({
    #         'subid': '00000000-0000-0000-0000-000000000000',
    #         'sku': 'standard_b1ls',
    #         'location': 'westus',
    #         'reservedResourceType': 'VirtualMachines',
    #         'term': 'P1Y',
    #         'quantity': '2',
    #         'displayName': 'clitest',
    #         'appliedScopes': 'Shared',
    #         'instanceFlexibility': 'Off',
    #         'billingPlan': 'Monthly',
    #         'appliedScopeType': 'Shared'
    #     })
    #     response = self.cmd('reservations reservation-order calculate --sku {sku} --location {location} --reserved-resource-type {reservedResourceType}'
    #                         ' --billing-scope {subid} --term {term} --billing-plan {billingPlan} --display-name {displayName}'
    #                         ' --quantity {quantity} --applied-scope-type {appliedScopeType}').get_output_in_json()
    #     self.assertIsNotNone(response)
    #     self.assertIsNotNone(response['properties']['billingCurrencyTotal'])
    #     self.assertIsNotNone(response['properties']['pricingCurrencyTotal'])
    #     self.assertIsNotNone(response['properties']['pricingCurrencyTotal']['currencyCode'])
    #     self.assertEqual('USD', response['properties']['pricingCurrencyTotal']['currencyCode'])
    #     self.assertEqual('USD', response['properties']['billingCurrencyTotal']['currencyCode'])
    #     self.assertGreater(response['properties']['pricingCurrencyTotal']['amount'], 0)
    #     self.assertGreater(response['properties']['billingCurrencyTotal']['amount'], 0)
    #     self.assertIsNotNone(response['properties']['reservationOrderId'])
    #     self.assertEqual('standard_b1ls', response['properties']['skuDescription'])

    # @record_only()  # This test relies on a subscription with reservation purchase permissions
    def test_purchase_reservation_order(self):
        self.kwargs.update({
            'subid': 'b0f278e1-1f18-4378-84d7-b44dfa708665',
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
        self.kwargs.update({
            'roid': response['properties']['reservationOrderId']
        })
        response2 = self.cmd('reservations reservation-order purchase --reservation-order-id {roid} --sku {sku} --location {location} --reserved-resource-type {reservedResourceType}'
                            ' --billing-scope {subid} --term {term} --billing-plan {billingPlan} --display-name {displayName}'
                            ' --quantity {quantity} --applied-scope-type {appliedScopeType}').get_output_in_json()
        # self.assertIsNotNone(response2)
        # self.assertGreater(response2['etag'], 0)
        # self.assertEqual("microsoft.capacity/reservationOrders", response2['type'])
        # self.assertEqual("/providers/microsoft.capacity/reservationOrders/f5107528-b559-4a23-a4b2-7dbdff05bd26", response2['id'])
        # self.assertEqual("f5107528-b559-4a23-a4b2-7dbdff05bd26", response2['name'])
        # self.assertEqual("P1Y", response2['term'])
        # self.assertEqual("clitest", response2['displayName'])
        # self.assertEqual(2, response2['originalQuantity'])
        # self.assertEqual('Monthly', response2['billingPlan'])
        # self.assertEqual('PendingCapacity', response2['provisioningState'])
        # self.assertGreater(len(response2['reservations']), 0)

    # @record_only()
    # def test_archive_unarchive_reservation(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '3bd3a6b6-c698-4214-bb72-613688fabfe8',
    #         'reservation_id': 'c23b30c2-9397-4218-97f1-c607051670ff',
    #     })
    #     response = self.cmd('reservations reservation archive --reservation-order-id {reservation_order_id} --reservation-id {reservation_id}')
    #     self.assertIsNotNone(response)
    #     response = self.cmd('reservations reservation unarchive --reservation-order-id {reservation_order_id} --reservation-id {reservation_id}')
    #     self.assertIsNotNone(response)

    # @record_only()
    # def test_reservation_available_scope(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '99f340d1-6db4-41b4-b469-cfc499716973',
    #         'reservation_id': 'a7d70646-b848-4498-8093-5938128b225c',
    #         'subscription_id': '00000000-0000-0000-0000-000000000000'
    #     })
    #     response = self.cmd('reservations reservation list-available-scope --reservation-order-id {reservation_order_id} --reservation-id {reservation_id}'
    #     ' --scopes [/subscriptions/{subscription_id}]').get_output_in_json()

    #     self.assertIsNotNone(response)
    #     self.assertIsNotNone(response['properties'])
    #     self.assertIsNotNone(response['properties']['scopes'])
    #     self.assertEqual(1, len(response['properties']['scopes']))
    #     self.assertIn("/subscriptions/", response['properties']['scopes'][0]['scope'])
    #     self.assertEqual(True, response['properties']['scopes'][0]['valid'])

    # @record_only()
    # def test_reservation_order_change_directory(self):
    #     self.kwargs.update({
    #         'reservation_order_id': '4861c652-9564-4e1c-aba2-5b96f639138c',
    #         'destination_tenant_id': '4adcf5e7-539d-451c-85d5-b6c3b47335d7'
    #     })
    #     response = self.cmd('reservations reservation-order change-directory --reservation-order-id {reservation_order_id} '
    #                            '--destination-tenant-id {destination_tenant_id}').get_output_in_json()
    #     self.assertIsNotNone(response)
    #     self.assertIsNotNone(response['reservationOrder'])
    #     self.assertEqual("4861c652-9564-4e1c-aba2-5b96f639138c", response['reservationOrder']['id'])
    #     self.assertEqual("TestVm1", response['reservationOrder']['name'])
    #     self.assertEqual(True, response['reservationOrder']['isSucceeded'])
    #     self.assertIsNotNone(response['reservations'])
    #     self.assertEqual(1, len(response['reservations']))
    #     self.assertEqual("e52281b9-2e20-4cb2-8611-4b8cbc76a51a", response['reservations'][0]['id'])
    #     self.assertEqual("TestVm1", response['reservations'][0]['name'])
    #     self.assertEqual(True, response['reservations'][0]['isSucceeded'])

    @record_only()
    def test_reservation_refund(self):
        self.kwargs.update({
            'reservation_order_id': 'fade3e0f-aecb-43f8-a109-21bcb62c21d8',
            'reservation_id': '8075741d-8002-412e-b392-64a56baecfa4',
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

    # @record_only()
    # def test_reservation_exchange(self):
    #     reservation_to_exchange1 = '{reservation-id:/providers/microsoft.capacity/reservationOrders/a7a16cae-6a73-443b-a6af-51aebd48af7d/reservations/5c319cf0-daf7-4206-b8bf-3ac0faa34295,quantity:1}'
    #     reservation_to_exchange2 = '{reservation-id:/providers/microsoft.capacity/reservationOrders/b7cf96fb-1573-4623-82e5-dbc70ff826a4/reservations/3ba8978d-cb54-4aa5-8b78-fb2f6116bd7d,quantity:1}'
    #     reservations_to_exchange = '[{},{}]'.format(reservation_to_exchange1, reservation_to_exchange2)

    #     reservation_to_purchase1 = '{reserved-resource-type:VirtualMachines,applied-scope-type:Shared,billing-scope:00000000-0000-0000-0000-000000000000,display-name:exchangeTest2,quantity:3,sku:Standard_B1s,term:P1Y,billing-plan:Upfront,location:eastus}'
    #     reservation_to_purchase2 = '{reserved-resource-type:VirtualMachines,applied-scope-type:Shared,billing-scope:00000000-0000-0000-0000-000000000000,display-name:exchangeTest3,quantity:3,sku:Standard_B1ls,term:P1Y,billing-plan:Monthly,location:eastus}'
    #     reservations_to_purchase = '[{},{}]'.format(reservation_to_purchase1, reservation_to_purchase2)
    #     self.kwargs.update({
    #         'reservations_to_exchange': reservations_to_exchange,
    #         'reservations_to_purchase': reservations_to_purchase,
    #     })
    #     response = self.cmd('reservations calculate-exchange --ris-to-exchange {reservations_to_exchange} --ris-to-purchase {reservations_to_purchase}').get_output_in_json()
    #     self._validate_reservation_exchange(response)
    #     self.kwargs.update({
    #         'session_id': response['properties']['sessionId'],
    #     })
    #     response1 = self.cmd('reservations exchange --session-id {session_id}').get_output_in_json()
    #     self._validate_reservation_exchange(response1)
