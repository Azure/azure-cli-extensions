# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareIscsiPathTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareIscsiPathTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_iscsi_path')
    def test_vmware_iscsi_path(self):
        self.kwargs.update({
            'privatecloud': 'cloud1',
            'rg': 'rg1',
            'networkblock': '192.168.48.0/22'
        })

        self.cmd('az vmware iscsi-path create -c {privatecloud} -g {rg} --network-block {networkblock}')

        self.cmd('az vmware iscsi-path list -c {privatecloud} -g {rg}')

        self.cmd('az vmware iscsi-path delete -c {privatecloud} -g {rg} --yes')

        self.cmd('az vmware iscsi-path show -c {privatecloud} -g {rg}')