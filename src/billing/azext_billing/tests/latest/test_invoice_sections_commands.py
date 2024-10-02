# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureInvoiceSectionScenarioTest(ScenarioTest):
	def test_list_invoice_sections(self):
		self.kwargs.update({
			'account_name': 'e261ef40-3517-515d-3680-8be4252ae148:0790f1fc-f274-4457-afc3-f3b0c90850ba_2019-05-31',
			'billing_profile_id': 'B5LA-FLMV-BG7-M77W-SGB'
		})
		list_invoice_section = self.cmd('billing invoice-section list-by-billing-profile '
		'--billing-account-name {account_name} '
		'--billing-profile-name {billing_profile_id}').get_output_in_json()
		self.assertTrue(list_invoice_section)
		invoice_section = list_invoice_section[0]
		invoice_section_name = invoice_section['name']
		self.kwargs.update({
			'invoice_section_name': invoice_section_name
		})
		invoice_section = self.cmd('billing invoice-section get '
		'--billing-account-name {account_name} --billing-profile-name {billing_profile_id} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertEqual(invoice_section['name'], invoice_section_name)
		validate_delete_eligibility = self.cmd('billing invoice-section validate-delete-eligibility '
		'--billing-account-name {account_name} --billing-profile-name {billing_profile_id} --invoice-section-name {invoice_section_name}').get_output_in_json()
		self.assertTrue(validate_delete_eligibility)
		self.kwargs.update({
			'create_invoice_section_name': 'InvoiceSectionViaCLI'
		})
		self.cmd('billing invoice-section create '
		'--billing-account-name {account_name} --billing-profile-name {billing_profile_id} '
		'--invoice-section-name {create_invoice_section_name} --display-name "Invoice Section 1"'
		,checks=self.check("name", "InvoiceSectionViaCLI", case_sensitive=False))

		update = self.cmd('billing invoice-section create '
		'--billing-account-name {account_name} --billing-profile-name {billing_profile_id} '
		'--invoice-section-name {create_invoice_section_name} --display-name "Invoice Section Updated"').get_output_in_json()
		properties = update['properties']
		self.assertEqual(properties['displayName'], 'Invoice Section Updated')
		
		# self.cmd('billing invoice-section delete '
		# '--billing-account-name {account_name} --billing-profile-name {billing_profile_id} --invoice-section-name {create_invoice_section_name}')