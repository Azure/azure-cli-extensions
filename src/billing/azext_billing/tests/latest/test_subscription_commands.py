# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingSubscriptionsScenarioTest(ScenarioTest):
	def test_read_subscriptions(self):
		self.kwargs.update({
			'account_name': 'e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31',
			'profile_name': 'HWEG-Q6HX-BG7-TGB',
			'invoice_section_name': '3GOG-XYPA-PJA-TGB',
			'subscriptionId': '30d76dc4-93c6-4638-dbcd-8b64f0882e9b',
			'destination_invoice_section': '/providers/Microsoft.Billing/billingAccounts/e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31/billingProfiles/9ea04beecb25435781b6a9c112a4713b/invoiceSections/YB7U-KJHC-PJA-TGB'
		})

		# list subscriptions by billing account_name
		list_subscriptions_by_billing_account = self.cmd('billing subscription list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_subscriptions_by_billing_account)

		# list subscriptions by billing profile
		list_subscriptions_by_billing_profile = self.cmd('billing subscription list-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(list_subscriptions_by_billing_profile)

		# list subscriptions by invoice section
		list_subscriptions_by_invoice_section = self.cmd('billing subscription list-by-invoice-section --billing-account-name {account_name}  --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(list_subscriptions_by_invoice_section)

		#get by id
		subscription = self.cmd('billing subscription get --billing-account-name {account_name} --billing-subscription-name {subscriptionId}').get_output_in_json()
		self.assertTrue(subscription)

		#validate move eligibility
		validate_move_eligibility = self.cmd('billing subscription validate-move-eligibility --billing-account-name {account_name} --billing-subscription-name {subscriptionId} --destination-invoice-section-id {destination_invoice_section}').get_output_in_json()
		self.assertTrue(validate_move_eligibility)

class AzureEaBillingSubscriptionsScenarioTest(ScenarioTest):
	def test_ea_subscriptions_list_and_get(self):
		self.kwargs.update({
			'account_name': '6575495',
			'enrollment_account_name': '307200',
			'subscriptionId': '97930e20-b87f-4f5f-8483-6132adf17c82',
		})

		# list by billing account
		list_subscriptions_by_billing_account = self.cmd('billing subscription list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_subscriptions_by_billing_account)

		# list by enrollment account
		list_subscriptions_by_enrollment_account = self.cmd('billing subscription list-by-enrollment-account --billing-account-name {account_name} --enrollment-account-name {enrollment_account_name}').get_output_in_json()
		self.assertTrue(list_subscriptions_by_enrollment_account)

		# get
		subscription = self.cmd('billing subscription get --billing-account-name {account_name} --billing-subscription-name {subscriptionId}').get_output_in_json()
		self.assertTrue(subscription)
