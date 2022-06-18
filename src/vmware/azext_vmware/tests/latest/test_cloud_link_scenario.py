# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareCloudLinkScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareCloudLinkScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_hcx')
    def test_vmware_cloud_link(self):
        self.kwargs.update({
            'privatecloud': 'cloud1',
            'cloud_link': 'cloudLink1',
            'linked_cloud': '/subscriptions/12341234-1234-1234-1234-123412341234/resourceGroups/mygroup/providers/Microsoft.AVS/privateClouds/cloud2',
        })

        rsp = self.cmd('az vmware cloud-link create -g {rg} -c {privatecloud} -n {cloud_link} --linked-cloud {linked_cloud}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/cloudLinks')
        self.assertEqual(rsp['name'], self.kwargs.get('cloud_link'))

        count = len(self.cmd('az vmware cloud-link list -g {rg} -c {privatecloud}').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        self.cmd('vmware cloud-link show -g {rg} -c {privatecloud} -n {cloud_link}').get_output_in_json()
        self.assertEqual(rsp['type'], 'Microsoft.AVS/privateClouds/cloudLinks')
        self.assertEqual(rsp['name'], self.kwargs.get('cloud_link'))

        rsp = self.cmd('vmware cloud-link delete -g {rg} -c {privatecloud} -n {cloud_link} --yes').output
        self.assertEqual(len(rsp), 0)
