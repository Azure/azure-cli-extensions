# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import ScenarioTest, record_only
import random

class AzureBillingSavingsPlanScenarioTest(ScenarioTest):
    def BILLING_ACCOUNT(self):
        return 'e599e039-711f-52e8-69a0-cb0876584b15:eb5be248-66d2-43f1-abb7-ff3a0f618fb5_2019-05-31'
    def BILLING_PROFILE(self):
        return '/providers/Microsoft.Billing/billingAccounts/e599e039-711f-52e8-69a0-cb0876584b15:eb5be248-66d2-43f1-abb7-ff3a0f618fb5_2019-05-31/billingProfiles/MT3O-U4IM-BG7-TGB'
    def BILLING_PROFILE_NAME(self):
        return 'MT3O-U4IM-BG7-TGB'
    
    def _validate_savings_plan_order(self, savings_plan_order):
        self.assertIsNotNone(savings_plan_order)
        self.assertIsNotNone(savings_plan_order['id'])
        self.assertIsNotNone(savings_plan_order['name'])
        self.assertIsNotNone(savings_plan_order['provisioningState'])
        self.assertIsNotNone(savings_plan_order['savingsPlans'])
        self.assertIsNotNone(savings_plan_order['term'])
        self.assertIsNotNone(savings_plan_order['type'])
        self.assertEqual('microsoft.billing/billingaccounts/savingsplanorders', savings_plan_order['type'].lower())

    def _validate_savings_plan(self, savings_plan):
        self.assertIsNotNone(savings_plan)
        self.assertIsNotNone(savings_plan['id'])
        self.assertIsNotNone(savings_plan['name'])
        self.assertIsNotNone(savings_plan['sku'])
        self.assertIsNotNone(savings_plan['type'])
        self.assertEqual(
            'microsoft.billing/billingaccounts/savingsplanorders/savingsplans', savings_plan['type'].lower())

    def test_list_savings_plan_orders_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plan_order_list = self.cmd('billing savings-plan-order list-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plan_order_list)
        for order in savings_plan_order_list:
            self._validate_savings_plan_order(order)
            self.assertIn(
                '/providers/Microsoft.Billing/billingAccounts', order['id'])

    def test_get_savings_plan_order_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plan_order_list = self.cmd('billing savings-plan-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plan_order_list)
        savings_plan_order_id = savings_plan_order_list[0]['name']
        self.kwargs.update({
            'savings_plan_order': savings_plan_order_id
        })
        savings_plan_order = self.cmd('billing savings-plan-order get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order}').get_output_in_json()
        self._validate_savings_plan_order(savings_plan_order)

    def test_list_savings_plans_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plans_list = self.cmd('billing savings-plan list-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plans_list)
        for savings_plan in savings_plans_list:
            self._validate_savings_plan(savings_plan)

    def test_get_savings_plan_by_savings_plan_order(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plan_order_list = self.cmd('billing savings-plan-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plan_order_list)
        savings_plan_order_id = savings_plan_order_list[0]['name']
        self.kwargs.update({
            'savings_plan_order': savings_plan_order_id
        })
        savings_plan_order = self.cmd('billing savings-plan-order get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order}').get_output_in_json()
        savings_plan_id = savings_plan_order['savingsPlans'][0].split("/savingsPlans/")[1].split("/")[0]
        self.kwargs.update({
            'savings_plan': savings_plan_id
        })
        savings_plan = self.cmd('billing savings-plan get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order} --savings-plan-id {savings_plan}').get_output_in_json()
        self._validate_savings_plan(savings_plan)

    def test_list_savings_plans_by_savings_plan_order(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plan_order_list = self.cmd('billing savings-plan-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plan_order_list)
        savings_plan_order_id = savings_plan_order_list[0]['name']
        self.kwargs.update({
            'savings_plan_order': savings_plan_order_id
        })
        savings_plans_list = self.cmd('billing savings-plan list-by-savings-plan-order --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order}').get_output_in_json()
        for savings_plan in savings_plans_list:
            self._validate_savings_plan(savings_plan)

    def test_update_savings_plan_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plan_order_list = self.cmd('billing savings-plan-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plan_order_list)
        savings_plan_order_id = savings_plan_order_list[3]['name']
        self.kwargs.update({
            'savings_plan_order': savings_plan_order_id
        })
        savings_plan_order = self.cmd('billing savings-plan-order get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order}').get_output_in_json()
        savings_plan_id = savings_plan_order['savingsPlans'][0].split("/savingsPlans/")[1].split("/")[0]
        self.kwargs.update({
            'savings_plan': savings_plan_id
        })
        savings_plan = self.cmd('billing savings-plan get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order} --savings-plan-id {savings_plan}').get_output_in_json()
        name1 = savings_plan['displayName']
        self.kwargs.update({
            'name': "name_" + str(random.randint(2,99))
        })
        updated_savings_plan = self.cmd('billing savings-plan update-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order} --savings-plan-id {savings_plan} --display-name {name}').get_output_in_json()
        self.assertNotEqual(name1, updated_savings_plan['displayName'])

    def test_validate_update_savings_plan_by_billing_account(self):
        self.kwargs.update({
            'billing_account_name': self.BILLING_ACCOUNT(),
            'filter': "properties/billingProfileId eq \'{0}\'".format(self.BILLING_PROFILE())
        })
        savings_plan_order_list = self.cmd('billing savings-plan-order list-by-billing-account --billing-account-name {billing_account_name} '
                                          ' --filter \"{filter}\"').get_output_in_json()
        self.assertIsNotNone(savings_plan_order_list)
        savings_plan_order_id = savings_plan_order_list[3]['name']
        self.kwargs.update({
            'savings_plan_order': savings_plan_order_id
        })
        savings_plan_order = self.cmd('billing savings-plan-order get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order}').get_output_in_json()
        savings_plan_id = savings_plan_order['savingsPlans'][0].split("/savingsPlans/")[1].split("/")[0]
        self.kwargs.update({
            'savings_plan': savings_plan_id
        })
        savings_plan = self.cmd('billing savings-plan get-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order} --savings-plan-id {savings_plan}').get_output_in_json()
        self.kwargs.update({
            'arg': "[{applied-scope-type:Shared}]"
        })
        response = self.cmd('billing savings-plan validate-update-by-billing-account --billing-account-name {billing_account_name} '
                                    ' --savings-plan-order-id {savings_plan_order} --savings-plan-id {savings_plan} --benefits {arg}').get_output_in_json()
        self.assertEqual(True, response['benefits'][0]['valid'])
