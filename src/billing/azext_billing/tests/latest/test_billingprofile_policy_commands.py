# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingProfilepolicyScenarioTest(ScenarioTest):
	def test_policy_commands(self):
		self.kwargs.update({
			'modern_account_name': 'e00f22a3-bacf-5b74-3aaa-d503043532ea:d6b82951-c3bf-485c-82a2-52da136cb99d_2019-05-31',
			'profile_name': '9ea04beecb25435781b6a9c112a4713b'
			})

		get_billing_profile_policy = self.cmd('billing policy get-by-billing-profile --billing-account-name {modern_account_name} --billing-profile-name {profile_name}')
		self.assertTrue(get_billing_profile_policy)

		# update by billing profile
		self.cmd('billing policy update-by-billing-profile --billing-account-name {modern_account_name} --billing-profile-name {profile_name} --view-charges "NotAllowed"',
		checks=[self.check("properties.viewCharges", "NotAllowed", case_sensitive=False)])