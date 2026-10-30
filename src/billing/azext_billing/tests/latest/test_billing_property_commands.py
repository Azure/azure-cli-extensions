# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureBillingPropertyScenarioTest(ScenarioTest):
	def test_get_billing_prooperty(self):
		billing_property = self.cmd('billing billing-property get').get_output_in_json()
		self.assertTrue(billing_property)

	def test_update_billing_prooperty(self):
		self.cmd('billing billing-property update --cost-center "P10109641"', checks=self.check("properties.costCenter", "P10109641", case_sensitive=False))