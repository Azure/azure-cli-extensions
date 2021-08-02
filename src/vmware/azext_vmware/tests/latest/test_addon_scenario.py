# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from msrestazure.azure_exceptions import CloudError


class VmwareAddonScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareAddonScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_addon')
    def test_vmware_addon(self):
        self.kwargs.update({
            'loc': 'northcentralus',
            'privatecloud': 'mycloud1'
        })

        # create a private cloud
        self.cmd('vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 4 --network-block 192.168.48.0/22 --accept-eula')

        # List all existing addon
        count = len(self.cmd('vmware addon list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 0, 'addon count expected to be 0')

        # Create a VR addon
        self.cmd('az vmware addon vr create -g {rg} -c {privatecloud} --vrs-count 1')

        # List all existing addon
        count = len(self.cmd('vmware addon list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'addon count expected to be 1')

        # Show a VR addon
        self.cmd('az vmware addon vr show -g {rg} -c {privatecloud}')

        # Delete a VR addon
        self.cmd('az vmware addon vr delete -g {rg} -c {privatecloud}')

        # List all existing addon
        count = len(self.cmd('vmware addon list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 0, 'addon count expected to be 0')

        # Create a SRM addon
        self.cmd('az vmware addon srm create -g {rg} -c {privatecloud} --license-key "41915-178A8-FF4A4-DB683-6D735"')

        # List all existing addon
        count = len(self.cmd('vmware addon list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'addon count expected to be 1')

        # Show a SRM addon
        self.cmd('az vmware addon srm show -g {rg} -c {privatecloud}')

        # Delete a SRM addon
        self.cmd('az vmware addon srm delete -g {rg} -c {privatecloud}')

        # List all existing addon
        count = len(self.cmd('vmware addon list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 0, 'addon count expected to be 0')
