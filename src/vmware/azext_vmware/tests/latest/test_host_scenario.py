# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwareHostScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwareHostScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_vmware_script')
    def test_vmware_host(self):
        self.kwargs.update({
            'subscription': '12341234-1234-1234-1234-123412341234',
            'privatecloud': 'cloud1',
            'clustername': 'cluster1',
            'hostname': "esx03-r52.1111111111111111111.westcentralus.prod.azure.com"
        })

        # list hosts in a cluster
        count = len(self.cmd('az vmware cluster host list -g rg --cluster-name {clustername} --private-cloud-name {privatecloud}').get_output_in_json())
        self.assertEqual(count, 3, 'count expected to be 3')

        # get a host
        self.cmd('az vmware cluster host show -g rg --cluster-name {clustername} --private-cloud-name {privatecloud} --host-id {hostname}')
