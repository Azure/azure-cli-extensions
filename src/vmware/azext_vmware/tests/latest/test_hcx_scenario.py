# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from msrestazure.azure_exceptions import CloudError


class VmwareHcxScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareHcxScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_hcx')
    def test_vmware_hcx(self):

        # create a private cloud
        self.cmd('vmware private-cloud create -g {rg} -n {privatecloud} --location {loc} --sku av20 --cluster-size 4 --network-block 192.168.48.0/22 --nsxt-password 5rqdLj4GF3cePUe6( --vcenter-password UpfBXae9ZquZSDXk( --accept-eula')

        count = len(self.cmd('vmware private-cloud list -g {rg}').get_output_in_json())
        self.assertEqual(count, 1, 'private cloud count expected to be 1')

        # hcx-enterprise-site list should report 0
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 0, 'hcx-enterprise-site count expected to be 0')

        # create authorization
        self.cmd('vmware hcx-enterprise-site create -g {rg} -c {privatecloud} -n myhcx')

        # hcx-enterprise-site list should report 1
        count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'hcx-enterprise-site count expected to be 0')

        self.cmd('vmware hcx-enterprise-site show -g {rg} -c {privatecloud} -n myhcx')

        self.cmd('vmware hcx-enterprise-site delete -g {rg} -c {privatecloud} -n myhcx')

        # bug 7470537
        # hcx-enterprise-site list should report 0
        # count = len(self.cmd('vmware hcx-enterprise-site list -g {rg} -c {privatecloud}').get_output_in_json())
        # self.assertEqual(count, 0, 'hcx-enterprise-site count expected to be 0')
