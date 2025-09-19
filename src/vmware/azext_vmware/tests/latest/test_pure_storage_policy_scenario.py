# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class VmwarePureStoragePolicyScenarioTest(ScenarioTest):
    def setUp(self):
        # https://vcrpy.readthedocs.io/en/latest/configuration.html#request-matching
        self.vcr.match_on = ['scheme', 'method', 'path', 'query']  # not 'host', 'port'
        super(VmwarePureStoragePolicyScenarioTest, self).setUp()

    @ResourceGroupPreparer(name_prefix='cli_test_pure_storage_policy_script')
    def test_vmware_pure_storage_policy(self):
        self.kwargs.update({
            'subscription': '00000000-0000-0000-0000-000000000000',
            'privatecloud': 'cloud1',
            'storagePolicyName': "storagePolicy1",
            "storagePolicyDefinition": "Definition1",
            "storagePoolId": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/PureStorage.Block/storagePools/storagePool1"
        })

        # list pure storage policies
        count = len(self.cmd('az vmware pure-storage-policy list -g rg --private-cloud-name a').get_output_in_json())
        self.assertEqual(count, 1, 'count expected to be 1')

        # get a pure storage policy
        self.cmd('az vmware pure-storage-policy show -g rg --private-cloud-name a -n storagePolicyName')
        
        # create a pure storage policy
        self.cmd('az vmware pure-storage-policy create -g rg --private-cloud-name a -n storagePolicyName --storage-policy-definition storagePolicyDefinition --storage-pool-id storagePoolId')
        
        # delete a pure storage policy
        self.cmd('az vmware pure-storage-policy delete -g rg --private-cloud-name a -n storagePolicyName --yes')

