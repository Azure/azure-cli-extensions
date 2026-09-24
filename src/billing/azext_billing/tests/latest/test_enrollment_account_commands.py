# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureEnrollmentAccountScenarioTest(ScenarioTest):
	def test_enrollment_account_list_and_get(self):
		# list by billing account
		self.kwargs.update({
			'billing_account_name': '6575495'
		})
		list_enrollment_account = self.cmd('billing enrollment-account list-by-billing-account --billing-account-name {billing_account_name}').get_output_in_json()
		self.assertTrue(list_enrollment_account)
		# get
		enrollment_account_name = list_enrollment_account[0]['name']
		self.kwargs.update({
			'enrollment_account_name': enrollment_account_name
		})
		self.cmd('billing enrollment-account get --billing-account-name {billing_account_name} --enrollment-account-name {enrollment_account_name}', checks=self.check('name', enrollment_account_name))
		# list by department
		self.kwargs.update({
            'department_name': '148446'
        })
		list_enrollment_account_by_department = self.cmd('billing enrollment-account list-by-department --billing-account-name {billing_account_name} --department-name {department_name}').get_output_in_json()
		self.assertTrue(list_enrollment_account_by_department)
		# get by department
		enrollment_account_name = list_enrollment_account_by_department[0]['name']
		self.kwargs.update({
            'enrollment_account_name': enrollment_account_name
        })
		self.cmd('billing enrollment-account get-by-department --billing-account-name {billing_account_name} --department-name {department_name} --enrollment-account-name {enrollment_account_name}',
		    checks=[self.check('name', enrollment_account_name), self.check('properties.departmentId', '{department_name}')])
		