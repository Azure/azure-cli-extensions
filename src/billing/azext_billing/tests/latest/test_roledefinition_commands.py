# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingRoleDefinitionScenarioTest(ScenarioTest):
	def test_read_roledefinitions(self):
		self.kwargs.update({
			'account_name': 'e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31',
			'profile_name': 'HWEG-Q6HX-BG7-TGB',
			'invoice_section_name': '3GOG-XYPA-PJA-TGB',
			'role_definition_name': '50000000-aaaa-bbbb-cccc-100000000000',
			'profile_role_definition_name': '40000000-aaaa-bbbb-cccc-100000000000',
			'invoice_section_role_definition_name': '30000000-aaaa-bbbb-cccc-100000000000'
		})

		#list by billing account
		list_by_billing_account = self.cmd('billing role-definition list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_by_billing_account)

		#list by billing profile
		list_by_billing_profile = self.cmd('billing role-definition list-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(list_by_billing_profile)

		#list by invoice section
		list_by_invoice_section = self.cmd('billing role-definition list-by-invoice-section --billing-account-name {account_name}  --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(list_by_invoice_section)

		#get by billing account
		get_by_billing_account = self.cmd('billing role-definition get-by-billing-account --billing-account-name {account_name} --role-definition-name {role_definition_name}').get_output_in_json()
		self.assertTrue(get_by_billing_account)

		#get by billing profile
		get_by_billing_profile = self.cmd('billing role-definition get-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name} --role-definition-name {profile_role_definition_name}').get_output_in_json()
		self.assertTrue(get_by_billing_profile)

		#get by invoice section
		get_by_invoice_section = self.cmd('billing role-definition get-by-invoice-section --billing-account-name {account_name} --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name} --role-definition-name {invoice_section_role_definition_name}').get_output_in_json()
		self.assertTrue(get_by_invoice_section)