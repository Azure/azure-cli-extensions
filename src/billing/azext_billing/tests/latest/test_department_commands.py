# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureDepartmentScenarioTest(ScenarioTest):
	def test_department_list_and_get(self):
		# list by billing account
		self.kwargs.update({
			'billing_account_name': '6575495'
		})
		list_department = self.cmd('billing department list-by-billing-account --billing-account-name {billing_account_name}').get_output_in_json()
		self.assertTrue(list_department)
		# get
		department_name = list_department[0]['name']
		self.kwargs.update({
			'department_name': department_name
		})
		self.cmd('billing department get --billing-account-name {billing_account_name} --department-name {department_name}', checks=self.check('name', department_name))
		