# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

class WindowsManagedDiskSwapRestoreTest(ScenarioTest):

    @ResourceGroupPreparer()
    def test_swap_disk(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2019Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test swap-disk
        result = self.cmd('vm repair swap-disk -g {rg} -n {vm} --rescue-username azureadmin --rescue-password !Passw0rd2018')

        # Check rescue VM
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        assert len(vms) == 2

        # Check attached data disk
        for vm in vms:
            if vm.name == 'vm1':
                continue

            assert 
