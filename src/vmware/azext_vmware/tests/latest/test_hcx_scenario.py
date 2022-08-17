# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareHcxScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareHcxScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_hcx')
    def test_vmware_hcx(self):
        self.kwargs.update({
            'loc': 'westcentralus',
            'privatecloud': 'cloud1',
        })

        # create a private cloud
        self.cmd('vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 4 --network-block 192.168.48.0/22 --nsxt-password 5rqdLj4GF3cePUe6( --vcenter-password UpfBXae9ZquZSDXk( --accept-eula')

        # Create a HCX addon
        self.cmd('az vmware addon hcx create -g {rg} -c {privatecloud} --offer "VMware MaaS Cloud Provider"')

        # List all existing addon
        count = len(self.cmd('vmware addon list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'addon count expected to be 1')

        # hcx-enterprise-site list should report 1
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'hcx-enterprise-site count expected to be 1')

        # create authorization
        self.cmd('vmware hcx-enterprise-site create -g {rg} -c {privatecloud} -n myhcx')

        # hcx-enterprise-site list should report 1
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'hcx-enterprise-site count expected to be 1')

        self.cmd('vmware hcx-enterprise-site show -g {rg} -c {privatecloud} -n myhcx')

        self.cmd('vmware hcx-enterprise-site delete -g {rg} -c {privatecloud} -n myhcx --yes')

        # hcx-enterprise-site list should report 1
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'hcx-enterprise-site count expected to be 1')
