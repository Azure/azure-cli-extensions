# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingPermissionScenarioTest(ScenarioTest):
	def test_permission_commands(self):
		self.kwargs.update({
			'account_name': 'e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31',
			'profile_name': '9ea04beecb25435781b6a9c112a4713b',
			'invoice_section_name': 'YB7U-KJHC-PJA-TGB'
		})

		#check access by billing account
		check_access_by_billing_account = self.cmd('billing permission check-access-by-billing-account --billing-account-name {account_name} --actions "[Microsoft.Billing/billingAccounts/read]"').get_output_in_json()
		self.assertTrue(check_access_by_billing_account)

		#check access by billing profile
		check_access_by_billing_profile = self.cmd('billing permission check-access-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name} --actions "[Microsoft.Billing/billingAccounts/billingProfiles/read]"').get_output_in_json()
		self.assertTrue(check_access_by_billing_profile)

		#check access by invoice section
		check_access_by_invoice_section = self.cmd('billing permission check-access-by-invoice-section --billing-account-name {account_name} --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name} --actions "[Microsoft.Billing/billingAccounts/billingProfiles/invoiceSections/read]"').get_output_in_json()
		self.assertTrue(check_access_by_invoice_section)

		#list by billing account
		list_by_billing_account = self.cmd('billing permission list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_by_billing_account)

		#list by billing profile
		list_by_billing_profile = self.cmd('billing permission list-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(list_by_billing_profile)

		#list by invoice section
		list_by_invoice_section = self.cmd('billing permission list-by-invoice-section --billing-account-name {account_name} --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(list_by_invoice_section)

class AzureEaBillingPermissionScenarioTest(ScenarioTest):
	def test_billing_permission_list_and_check_access(self):
		self.kwargs.update({
			'account_name': '6575495',
			'department_name': '148446',
			'enrollment_account_name': '261569'
		})

		# list by billing account
		list_by_billing_account = self.cmd('billing permission list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_by_billing_account)

		#check access by billing account
		account_action = list_by_billing_account[0]['actions'][0]
		self.kwargs.update({
			'account_action': account_action,
			'account_no_action': 'Microsoft.Billing/billingAccounts/noAction'
		})
		print(account_action)
		self.cmd('billing permission check-access-by-billing-account --billing-account-name {account_name} --actions "[{account_action},{account_no_action}]"',
		   checks=[self.check("[0].accessDecision", "Allowed"), self.check("[1].accessDecision", "NotAllowed")])

		# list by department
		list_by_department = self.cmd('billing permission list-by-department --billing-account-name {account_name} --department-name {department_name}').get_output_in_json()
		self.assertTrue(list_by_department)

		# check access by department
		department_action = list_by_department[0]['actions'][0]
		self.kwargs.update({
			'department_action': department_action,
			'department_no_action': 'Microsoft.Billing/billingAccounts/departments/noAction'
		})		
		self.cmd('billing permission check-access-by-department --billing-account-name {account_name} --department-name {department_name} --actions "[{department_action},{department_no_action}]"',
		   checks=[self.check("[0].accessDecision", "Allowed"), self.check("[1].accessDecision", "NotAllowed")])

		# list by enrollment account
		list_by_enrollment_account = self.cmd('billing permission list-by-enrollment-account --billing-account-name {account_name} --enrollment-account-name {enrollment_account_name}').get_output_in_json()
		self.assertTrue(list_by_enrollment_account)

		# check access by enrollment account
		enrollment_account_action = list_by_enrollment_account[0]['actions'][0]
		self.kwargs.update({
			'enrollment_account_action': enrollment_account_action,
			'enrollment_account_no_action': 'Microsoft.Billing/billingAccounts/enrollmentAccounts/noAction'
		})
		self.cmd('billing permission check-access-by-enrollment-account --billing-account-name {account_name} --enrollment-account-name {enrollment_account_name} --actions "[{enrollment_account_action},{enrollment_account_no_action}]"',
		   checks=[self.check("[0].accessDecision", "Allowed"), self.check("[1].accessDecision", "NotAllowed")])
