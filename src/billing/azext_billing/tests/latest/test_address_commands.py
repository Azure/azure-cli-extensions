# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, record_only

class AzureAddressScenarioTest(ScenarioTest):
	def test_address_validate(self):
		validate_result = self.cmd('billing address validate --address-line1 "1 Microsoft Way" --city "Redmond" --country "US" --postal-code "98052" --region "wa"').get_output_in_json()
		assert validate_result['status'] == 'Valid'