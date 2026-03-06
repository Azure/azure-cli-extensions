# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareLicenseScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareLicenseScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_license')
    def test_vmware_license(self):
        self.kwargs.update({
            'rg': 'cli_test_vmware_license',
            'privatecloud': 'cloud1',
            'license_name': 'VmwareFirewall',
            'broadcom_contract_number': '12345',
            'broadcom_site_id': 'site123',
            'cores': '100',
            'end_date': '2027-01-01T00:00:00Z',
            'license_key': 'XXXXX-XXXXX-XXXXX-XXXXX-XXXXX',
        })

        # List all licenses for a private cloud
        self.cmd('az vmware license list --resource-group {rg} --private-cloud-name {privatecloud}')

        # Create a new license
        self.cmd('az vmware license create --resource-group {rg} --private-cloud-name {privatecloud} --license-name {license_name} --vmware-firewall contract-number={broadcom_contract_number} site-id={broadcom_site_id} cores={cores} end-date={end_date} license-key={license_key}')

        # Show the license
        self.cmd('az vmware license show --resource-group {rg} --private-cloud-name {privatecloud} --license-name {license_name}')

        # Get license properties and check if license_key is returned
        license_properties = self.cmd('az vmware license get-property --resource-group {rg} --private-cloud-name {privatecloud} --license-name {license_name}')
        self.assertIn('licenseKey', license_properties.get_output_in_json())

        # Update the license
        self.cmd('az vmware license update --resource-group {rg} --private-cloud-name {privatecloud} --license-name {license_name} --vmware-firewall contract-number={broadcom_contract_number} site-id={broadcom_site_id} cores=150 end-date={end_date}')
