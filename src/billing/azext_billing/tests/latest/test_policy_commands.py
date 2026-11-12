# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzurePolicyScenarioTest(ScenarioTest):
	def test_account_policy_get_and_update(self):
		# tests are currently failing with error "'get-by-billing-account' is misspelled or unrecognized by the system". same with billing profile policy and customer policy
		# get by billing account
		self.kwargs.update({
			'billing_account_name': '6575495'
		})
		account_policy = self.cmd('billing policy get-by-billing-account --billing-account-name {billing_account_name}')
		self.assertTrue(account_policy)
		# update by billing account
		self.cmd('billing policy update-by-billing-account --billing-account-name {billing_account_name} --enterprise-agreement-policies authentication-type="OrganizationalAccountOnly"',
		    checks=self.check('properties.enterpriseAgreementPolicies.authenticationType', "OrganizationalAccountOnly"))
		