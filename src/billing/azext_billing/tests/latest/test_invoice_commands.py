# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureInvoiceScenarioTest(ScenarioTest):
	def test_list_invoices(self):
		self.kwargs.update({
			'account_name': 'e261ef40-3517-515d-3680-8be4252ae148:0790f1fc-f274-4457-afc3-f3b0c90850ba_2019-05-31',
			'billing_profile_id': 'B5LA-FLMV-BG7-M77W-SGB',
			'subscription_id': '5040c0e6-3e00-46e8-aee6-ab270d9365cf'
		})
		invoices_list_by_billing_account = self.cmd('billing invoice list-by-billing-account '
		'--billing-account-name {account_name} --period-start-date 2024-01-01 --period-end-date 2024-09-30').get_output_in_json()
		self.assertTrue(invoices_list_by_billing_account)		
		invoice = invoices_list_by_billing_account[0]
		invoice_name = invoice['name']
		self.kwargs.update({
			'invoice_name': invoice_name
		})
		invoices_list_by_billing_profile = self.cmd('billing invoice list-by-billing-profile '
		'--billing-account-name {account_name} '
		'--billing-profile-name {billing_profile_id} --period-start-date 2024-01-01 --period-end-date 2024-09-30').get_output_in_json()
		self.assertTrue(invoices_list_by_billing_profile)
		invoices_list_by_billing_subscription = self.cmd('billing invoice list-by-billing-subscription '
		'--period-start-date 2024-01-01 --period-end-date 2024-09-30').get_output_in_json()
		# No invoices for the modern subscription as they exist at billing profile scope
		self.assertEqual(len(invoices_list_by_billing_subscription), 0)
		# get by billing account name
		self.cmd('billing invoice get-by-billing-account --billing-account-name {account_name} --invoice-name {invoice_name}', checks=self.check("name", invoice_name, case_sensitive=False))
		# get invoice by id
		invoice = self.cmd('billing invoice get --invoice-name {invoice_name}').get_output_in_json()
		self.assertEqual(invoice['name'], invoice_name)
		properties = invoice['properties']
		documents = properties['documents']
		document = documents[0]
		document_name = document['name']
		self.kwargs.update({
			'document_name': document_name
		})
		# download invoice by billing account
		download_by_billing_account = self.cmd('billing invoice download-by-billing-account '
		'--billing-account-name {account_name} --invoice-name {invoice_name} --document-name {document_name}').get_output_in_json()
		self.assertTrue(download_by_billing_account)
		#download by billing subscription
		# doc1 = '{document-name:"{document_name}",invoice-name:"{invoice_name}"}'
		# parameters = '{}'.format(doc1)
		# self.kwargs.update({
		# 	'parameters': parameters
		# })
		# multiple_download_by_billing_account = self.cmd('az billing invoice download-document-by-billing-account '
		# '--billing-account-name {account_name} '
		# '--parameters {parameters}')
		# self.assertTrue(multiple_download_by_billing_account)