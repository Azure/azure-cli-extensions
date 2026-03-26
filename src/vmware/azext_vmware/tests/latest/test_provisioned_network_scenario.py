# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareProvisionedNetworkScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareProvisionedNetworkScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_provisioned_network_script')
    def test_vmware_host(self):
        self.kwargs.update({
            'subscription': '00000000-0000-0000-0000-000000000000',
            'privatecloud': 'cloud1',
            'provisionednetworkname': "esx03-r52.1111111111111111111.westcentralus.prod.azure.com"
        })

        # list provisioned networks
        count = len(self.cmd('az vmware provisioned-network list -g rg --private-cloud-name {privatecloud}').get_output_in_json())
        self.assertEqual(count, 3, 'count expected to be 3')

        # get a provisioned network
        self.cmd('az vmware provisioned-network show -g rg --private-cloud-name {privatecloud} --n {provisionednetworkname}')
