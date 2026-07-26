# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureCustomersScenarioTest(ScenarioTest):
	def test_customers_commands(self):
		self.kwargs.update({
			'account_name': 'edbb014c-80ca-55f8-ffe8-5b0e223f3c96:9e80edc1-bbbf-427e-a185-8a8f50a8a1ca_2019-05-31',
			'profile_name': 'SXJ7-5ZRB-BG7-TGB'
		})

		#list customers by BA
		customers_list = self.cmd('billing customer list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(customers_list)
		customer_name = customers_list[0]['name']
		self.kwargs.update({
			'customer_name': customer_name
		})

		#list customers by BP
		customers_list_by_bp = self.cmd('billing customer list-by-billing-profile --billing-account-name {account_name} --billing-profile-name {profile_name}').get_output_in_json()
		self.assertTrue(customers_list_by_bp)
		
		# get customer by id
		self.cmd('billing customer get --billing-account-name {account_name} --billing-profile-name {profile_name} --customer-name {customer_name}', checks=self.check('name', customer_name))