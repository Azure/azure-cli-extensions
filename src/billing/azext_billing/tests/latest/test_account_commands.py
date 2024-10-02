# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingAccountsScenarioTest(ScenarioTest):
	def _validate_account(self, account):
		self.assertIsNotNone(account)
		self.assertEqual(account['type'], 'Microsoft.Billing/accounts')
		self.assertTrue(account['id'] and account['name'])
		self.assertTrue(account['billingProfiles'])
		self.assertTrue(account['enrollmentAccounts'])
		self.assertTrue(account['billingProfileName'])
		self.assertTrue(account['enrollmentAccountName'])

	def test_list_accounts(self):
		# list
		accounts_list = self.cmd('billing account list --include-all true').get_output_in_json()
		self.assertTrue(accounts_list)
		# get
		account_name = accounts_list[0]['name']
		self.kwargs.update({
			'account_name': account_name
		})
		self.cmd('billing account get --billing-account-name {account_name}', checks=self.check('name', account_name))
		# Below api is resulting in InternalServerError
		# invoiceSection_list = self.cmd('billing account list-invoice-sections-with-create-subscription-permission --billng-acount-name {account_name}').get_output_in_json()
		# assert len(invoiceSection_list) > 0
		self.cmd('az billing account update '
             '--billing-account-name {account_name} '
             '--display-name "Account Name Updated Via CLI Test" '
             '--sold-to address-line1="1 Microsoft Way" city="Redmond" company-name="BillingRP CLI" country="US" '
             'postal-code="98052" region="WA"',
             checks=[
                 self.check("name", "{account_name}", case_sensitive=False),
                 self.check("properties.displayName", "Account Name Updated Via CLI Test", case_sensitive=False),
                 self.check("properties.soldTo.addressLine1", "1 Microsoft Way", case_sensitive=False),
                 self.check("properties.soldTo.city", "Redmond", case_sensitive=False),
                 self.check("properties.soldTo.companyName", "BillingRP CLI", case_sensitive=False),
                 self.check("properties.soldTo.country", "US", case_sensitive=False),
                 self.check("properties.soldTo.postalCode", "98052", case_sensitive=False),
                 self.check("properties.soldTo.region", "WA", case_sensitive=False),
             ])