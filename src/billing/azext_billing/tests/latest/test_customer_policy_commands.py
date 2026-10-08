# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureCustomerpolicyScenarioTest(ScenarioTest):
	def test_policy_commands(self):
		self.kwargs.update({
			'account_name': 'edbb014c-80ca-55f8-ffe8-5b0e223f3c96:9e80edc1-bbbf-427e-a185-8a8f50a8a1ca_2019-05-31',
			'customer_name': 'da904b39-8d5f-420f-9d2c-c3b3923d78fe'
			})

		get_billing_profile_policy = self.cmd('billing policy get-by-customer-at-billing-account --billing-account-name {account_name} --customer-name {customer_name}')
		self.assertTrue(get_billing_profile_policy)

		# update by customer
		self.cmd('billing policy update-by-customer-at-billing-account --billing-account-name {account_name} --customer-name {customer_name} --view-charges "Allowed"',
		checks=[self.check("properties.viewCharges", "Allowed", case_sensitive=False)])