# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureTransactionsScenarioTest(ScenarioTest):
    def test_ea_invoice_transactions_download(self):
		# transactions download by invoice
        self.kwargs.update({
			'account_name': '6575495',
			'invoice_name': 'EA02510779'
		})
        invoice_transactions_download = self.cmd('billing transaction transactions-download-by-invoice --billing-account-name {account_name} --invoice-name {invoice_name}').get_output_in_json()
        self.assertTrue(invoice_transactions_download)
