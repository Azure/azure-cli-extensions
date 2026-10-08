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

class AzureEaBillingRoleDefinitionScenarioTest(ScenarioTest):
	def test_ea_roledefinition_list_and_get(self):
		self.kwargs.update({
			'account_name': '6575495',
			'department_name': '148446',
			'enrollment_account_name': '261569',
			'enrollment_admin_role_definition_name': '9f1983cb-2574-400c-87e9-34cf8e2280db',
			'department_admin_role_definition_name': 'fb2cf67f-be5b-42e7-8025-4683c668f840',
			'account_owner_role_definition_name': 'c15c22c0-9faf-424c-9b7e-bd91c06a240b'
		})

		#list by billing account
		list_by_billing_account = self.cmd('billing role-definition list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_by_billing_account)

		#list by department
		list_by_department = self.cmd('billing role-definition list-by-department --billing-account-name {account_name} --department-name {department_name}').get_output_in_json()
		self.assertTrue(list_by_department)

		#list by enrollment_account
		list_by_enrollment_account = self.cmd('billing role-definition list-by-enrollment-account --billing-account-name {account_name}  --enrollment-account-name {enrollment_account_name}').get_output_in_json()
		self.assertTrue(list_by_enrollment_account)

		#get by billing account
		get_by_billing_account = self.cmd('billing role-definition get-by-billing-account --billing-account-name {account_name} --role-definition-name {enrollment_admin_role_definition_name}').get_output_in_json()
		self.assertTrue(get_by_billing_account)

		#get by department
		get_by_department = self.cmd('billing role-definition get-by-department --billing-account-name {account_name} --department-name {department_name} --role-definition-name {department_admin_role_definition_name}').get_output_in_json()
		self.assertTrue(get_by_department)

		#get by enrollment account
		get_by_enrollment_account = self.cmd('billing role-definition get-by-enrollment-account --billing-account-name {account_name} --enrollment-account-name {enrollment_account_name} --role-definition-name {account_owner_role_definition_name}').get_output_in_json()
		self.assertTrue(get_by_enrollment_account)