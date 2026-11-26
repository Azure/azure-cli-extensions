# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingProfilessScenarioTest(ScenarioTest):
	def test_list_profiles(self):
		accounts_list = self.cmd('billing account list --include-all true').get_output_in_json()
		self.assertTrue(accounts_list)
		# get
		account_name = accounts_list[0]['name']
		self.kwargs.update({
			'account_name': account_name
		})
		# list
		profiles_list = self.cmd('billing profile list --account-name {account_name}').get_output_in_json()
		self.assertTrue(profiles_list)
		# get
		profile_name = profiles_list[0]['name']
		self.kwargs.update({
			'profile_name': profile_name
		})
		self.cmd('billing profile get --billing-account-name {account_name} --billing-profile-name {profile_name}', checks=self.check('name', profile_name))