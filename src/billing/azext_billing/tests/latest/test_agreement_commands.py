# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureagreementScenarioTest(ScenarioTest):
	def test_agreement_get_and_list(self):
		# list account
		accounts_list = self.cmd('billing account list --include-all true').get_output_in_json()
		self.assertTrue(accounts_list)
		# get account
		account_name = accounts_list[0]['name']
		self.kwargs.update({
			'account_name': account_name
		})
		agreement_list = self.cmd('billing agreement list-by-billing-account --billing-account-name {account_name}').get_output_in_json()
		self.assertTrue(agreement_list)
		agreement_name = agreement_list[0]['name']
		self.kwargs.update({
			'agreement_name': agreement_name
		})
		self.cmd('billing agreement get --billing-account-name {account_name} --agreement-name {agreement_name}', checks=self.check('name', agreement_name))