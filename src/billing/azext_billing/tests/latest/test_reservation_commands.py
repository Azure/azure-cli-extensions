# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingReservationScenarioTest(ScenarioTest):
    def BILLING_ACCOUNT(self):
        return 'e599e039-711f-52e8-69a0-cb0876584b15:eb5be248-66d2-43f1-abb7-ff3a0f618fb5_2019-05-31'
    def BILLING_PROFILE(self):
        return '/providers/Microsoft.Billing/billingAccounts/e599e039-711f-52e8-69a0-cb0876584b15:eb5be248-66d2-43f1-abb7-ff3a0f618fb5_2019-05-31/billingProfiles/MT3O-U4IM-BG7-TGB'
    def BILLING_PROFILE_NAME(self):
        return 'MT3O-U4IM-BG7-TGB'
    
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
        self.assertEqual('microsoft.billing/billingaccounts/reservationorders', reservation_order['type'].lower())

    def _validate_reservation(self, reservation):
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation['location'])
        self.assertGreater(len(reservation['location']), 0)
        self.assertIsNotNone(reservation['etag'])
        self.assertGreater(reservation['etag'], 0)
        self.assertIsNotNone(reservation['id'])
        self.assertIsNotNone(reservation['name'])
        self.assertIsNotNone(reservation['sku'])
        self.assertIsNotNone(reservation['type'])
        self.assertEqual(
            'microsoft.billing/billingaccounts/reservationorders/reservations', reservation['type'].lower())

    def test_list_reservation_orders_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        reservation_order_list = self.cmd('billing reservation-order list-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(reservation_order_list)
        for order in reservation_order_list:
            self._validate_reservation_order(order)
            self.assertIn(
                '/providers/Microsoft.Billing/billingAccounts', order['id'])
            self.assertGreater(order['etag'], 0)
            for reservation in order['reservations']:
                self.assertTrue(reservation['id'])
    
    def test_get_reservation_order_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        reservation_order_list = self.cmd('billing reservation-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(reservation_order_list)
        reservation_order_id = reservation_order_list[0]['name']
        self.kwargs.update({
            'reservation_order': reservation_order_id
        })
        reservation_order = self.cmd('billing reservation-order get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --reservation-order-id {reservation_order}').get_output_in_json()
        self._validate_reservation_order(reservation_order)

    def test_list_reservations_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        reservation_list = self.cmd('billing reservation list-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(reservation_list)
        for reservation in reservation_list:
            self._validate_reservation(reservation)

    def test_list_reservations_by_billing_profile(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'billing_profile_name': self.BILLING_PROFILE_NAME()
        })
        reservation_list = self.cmd('billing reservation list-by-billing-profile --billing-account-name {billing_account_name} --billing-profile-name {billing_profile_name}').get_output_in_json()
        self.assertIsNotNone(reservation_list)
        for reservation in reservation_list:
            self._validate_reservation(reservation)

    def test_get_reservation_by_reservation_order(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        reservation_order_list = self.cmd('billing reservation-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(reservation_order_list)
        reservation_order_id = reservation_order_list[0]['name']
        self.kwargs.update({
            'reservation_order': reservation_order_id
        })
        reservation_order = self.cmd('billing reservation-order get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --reservation-order-id {reservation_order}').get_output_in_json()
        reservation_id = reservation_order['reservations'][0]['id'].split("/reservations/")[1].split("/")[0]
        self.kwargs.update({
            'reservation': reservation_id
        })
        reservation = self.cmd('billing reservation get-by-reservation-order --billing-account-name {billing_account_name} '
                                    ' --reservation-order-id {reservation_order} --reservation-id {reservation}').get_output_in_json()
        self._validate_reservation(reservation)

    def test_list_reservation_by_reservation_order(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        reservation_order_list = self.cmd('billing reservation-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(reservation_order_list)
        reservation_order_id = reservation_order_list[0]['name']
        self.kwargs.update({
            'reservation_order': reservation_order_id
        })
        reservation_list = self.cmd('billing reservation list-by-reservation-order --billing-account-name {billing_account_name} '
                                    ' --reservation-order-id {reservation_order}').get_output_in_json()
        for reservation in reservation_list:
            self._validate_reservation(reservation)
