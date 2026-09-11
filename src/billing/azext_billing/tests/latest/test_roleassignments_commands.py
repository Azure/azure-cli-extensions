# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

class AzureBillingRoleAssignmentsScenarioTest(ScenarioTest):
	def test_read_roleassignments(self):
		self.kwargs.update({
			'account_name': 'e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31',
			'profile_name': 'HWEG-Q6HX-BG7-TGB',
			'invoice_section_name': '3GOG-XYPA-PJA-TGB',
			'role_assignment_name': '50000000-aaaa-bbbb-cccc-100000000000_9bf312df-5cb8-41b0-b448-1e2fc2d0f03b',
			'profile_role_assignment_name': '40000000-aaaa-bbbb-cccc-100000000000_b139b2d4-4c52-4705-a451-c85656a830b8',
			'invoice_section_role_assignment_name': '3000000030000000-aaaa-bbbb-cccc-100000000000_b866b094-9442-4c60-b2ad-b54e828ddf5a'
		})

		# list role assignments by billing account_name
		list_role_assignments_by_billing_account = self.cmd('billing role-assignment list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_role_assignments_by_billing_account)

		# list role assignments by billing profile
		list_role_assignments_by_billing_profile = self.cmd('billing role-assignment list-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(list_role_assignments_by_billing_profile)

		# list role assignments by invoice section
		list_role_assignments_by_invoice_section = self.cmd('billing role-assignment list-by-invoice-section --billing-account-name {account_name}  --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(list_role_assignments_by_invoice_section)

		#resolve role assignment by billing account
		resolve_role_assignment_by_billing_account = self.cmd('billing role-assignment resolve-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(resolve_role_assignment_by_billing_account)

		#resolve role assignment by billing profile
		resolve_role_assignment_by_billing_profile = self.cmd('billing role-assignment resolve-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(resolve_role_assignment_by_billing_profile)

		#resolve role assignment by invoice section
		resolve_role_assignment_by_invoice_section = self.cmd('billing role-assignment resolve-by-invoice-section --billing-account-name {account_name} --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(resolve_role_assignment_by_invoice_section)

		# get role assignment by billing account
		role_assignment = self.cmd('billing role-assignment get-by-billing-account --billing-account-name {account_name} --billing-role-assignment-name {role_assignment_name}').get_output_in_json()
		self.assertTrue(role_assignment)

		# get role assignment by billing profile
		role_assignment = self.cmd('billing role-assignment get-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name} --billing-role-assignment-name {profile_role_assignment_name}').get_output_in_json()
		self.assertTrue(role_assignment)

		# get role assignment by invoice section
		# role_assignment = self.cmd('billing role-assignment get-by-invoice-section --billing-account-name {account_name} --billing-profile-name {profile_name} --invoice-section-name {invoice_section_name} --billing-role-assignment-name {invoice_section_role_assignment_name}').get_output_in_json()
		# self.assertTrue(role_assignment)

class AzureEaBillingRoleAssignmentsScenarioTest(ScenarioTest):
	# allow large response since pagination is not supported in role-assignment list-* calls from cli, so is $orderby
	@AllowLargeResponse()
	def test_ea_roleassignments_list_and_get(self):
		self.kwargs.update({
			'account_name': '6575495',
			'department_name': '148446',
			'enrollment_account_name': '261569'
		})

		# list by billing account
		list_role_assignments_by_billing_account = self.cmd('billing role-assignment list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(list_role_assignments_by_billing_account)

		# get by billing account
		billing_account_role_assignment_name = list_role_assignments_by_billing_account[0]['name']
		self.kwargs.update({
			'billing_account_role_assignment_name': billing_account_role_assignment_name
		})
		billing_account_role_assignment = self.cmd('billing role-assignment get-by-billing-account --billing-account-name {account_name} --billing-role-assignment-name {billing_account_role_assignment_name}').get_output_in_json()
		self.assertTrue(billing_account_role_assignment)

		# list by department
		list_role_assignments_by_department = self.cmd('billing role-assignment list-by-department --billing-account-name {account_name} --department-name {department_name}').get_output_in_json()
		self.assertTrue(list_role_assignments_by_department)

		# get by department
		department_role_assignment_name = list_role_assignments_by_department[0]['name']
		self.kwargs.update({
			'department_role_assignment_name': department_role_assignment_name
		})
		department_role_assignment = self.cmd('billing role-assignment get-by-department --billing-account-name {account_name} --department-name {department_name} --billing-role-assignment-name {department_role_assignment_name}').get_output_in_json()
		self.assertTrue(department_role_assignment)

		# list by enrollment account
		list_role_assignments_by_enrollment_account = self.cmd('billing role-assignment list-by-enrollment-account --billing-account-name {account_name}  --enrollment-account-name {enrollment_account_name}').get_output_in_json()
		self.assertTrue(list_role_assignments_by_enrollment_account)

		# get by enrollment account
		enrollment_account_role_assignment_name = list_role_assignments_by_enrollment_account[0]['name']
		self.kwargs.update({
			'enrollment_account_role_assignment_name': enrollment_account_role_assignment_name
		})
		enrollment_account_role_assignment = self.cmd('billing role-assignment get-by-enrollment-account --billing-account-name {account_name} --enrollment-account-name {enrollment_account_name} --billing-role-assignment-name {enrollment_account_role_assignment_name}').get_output_in_json()
		self.assertTrue(enrollment_account_role_assignment)