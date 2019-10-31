# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class WindowsManagedDiskCreateRestoreTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_create_restore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018').get_output_in_json()

        # Check repair VM
        repair_vms = self.cmd('vm list -g {}'.format(result['repair_resouce_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class WindowsUnmanagedDiskCreateRestoreTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_create_restore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018').get_output_in_json()

        # Check repair VM
        repair_vms = self.cmd('vm list -g {}'.format(result['repair_resouce_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['vhd']['uri'] == result['copied_disk_uri']


class LinuxManagedDiskCreateRestoreTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_create_restore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image UbuntuLTS --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-password !Passw0rd2018').get_output_in_json()

        # Check repair VM
        repair_vms = self.cmd('vm list -g {}'.format(result['repair_resouce_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class LinuxUnmanagedDiskCreateRestoreTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_create_restore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image UbuntuLTS --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-password !Passw0rd2018').get_output_in_json()

        # Check repair VM
        repair_vms = self.cmd('vm list -g {}'.format(result['repair_resouce_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['vhd']['uri'] == result['copied_disk_uri']


class WindowsRunHelloWorldTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_win_hello_world(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair run -g {rg} -n {vm} --run-id win-hello-world').get_output_in_json()

        # Check Output
        assert 'Hello World!' in result['output']


class LinuxRunHelloWorldTest(ScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_linux_hello_world(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image UbuntuLTS --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg}').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair run -g {rg} -n {vm} --run-id linux-hello-world').get_output_in_json()

        # Check Output
        assert 'Hello World!' in result['output']
