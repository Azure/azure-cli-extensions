# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingProductsScenarioTest(ScenarioTest):
	def test_products_commands(self):
		self.kwargs.update({
			'account_name': 'e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31',
			'profile_name': 'HWEG-Q6HX-BG7-TGB',
			'invoice_section_name': '3GOG-XYPA-PJA-TGB',
			'product_name': '30d76dc4-93c6-4638-dbcd-8b64f0882e9b'
		})

		# list products by billing account_name
		list_products_by_billing_account = self.cmd('billing product list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_products_by_billing_account)

		# list products by billing profile
		list_products_by_billing_profile = self.cmd('billing product list-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(list_products_by_billing_profile)

		#list by invoice section
		list_products_by_invoice_section = self.cmd('billing product list-by-invoice-section --billing-account-name {account_name}  --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(list_products_by_invoice_section)

		#get by product_name
		product = self.cmd('billing product get --billing-account-name {account_name} --product-name {product_name}').get_output_in_json()
		self.assertTrue(product)

		self.kwargs.update({
			'destination_invoice_section_id': '/providers/Microsoft.Billing/billingAccounts/e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31/billingProfiles/9ea04beecb25435781b6a9c112a4713b/invoiceSections/YB7U-KJHC-PJA-TGB'
		})
		#validate move eligibility
		validate = self.cmd('billing product validate-move-eligibility --billing-account-name {account_name} --product-name {product_name} --destination-invoice-section-id {destination_invoice_section_id}').get_output_in_json()
		self.assertTrue(validate)