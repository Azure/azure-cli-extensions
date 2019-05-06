# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

class WindowsManagedDiskSwapRestoreTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
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
        result = self.cmd('vm repair swap-disk -g {rg} -n {vm} --rescue-username azureadmin --rescue-password !Passw0rd2018').get_output_in_json()

        # Check rescue VM
        rescue_vms = self.cmd('vm list -g {}'.format(result['rescueResouceGroup'])).get_output_in_json()
        assert len(rescue_vms) == 1
        rescue_vm = rescue_vms[0]
        # Check attached data disk
        assert rescue_vm['storageProfile']['dataDisks'][0]['name'] == result['copiedDiskName']
        
        # Call Restore
        result2 = self.cmd('vm repair restore-swap -g {rg} -n {vm}')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        targetVm = vms[0]
        assert targetVm['storageProfile']['osDisk']['name'] == result['copiedDiskName']
        # Check rescue VM deleted
        exists = self.cmd('group exists --name {}'.format(result['rescueResouceGroup'])).get_output_in_json()
        assert exists == False
        