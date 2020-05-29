# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from azure.cli.testsdk import LiveScenarioTest, ResourceGroupPreparer

STATUS_SUCCESS = 'SUCCESS'


class WindowsManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinManagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class WindowsUnmanagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinUnmanagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['vhd']['uri'] == result['copied_disk_uri']


class LinuxManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxManagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image UbuntuLTS --admin-username azureadmin --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class LinuxUnmanagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxUnmanagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image UbuntuLTS --admin-username azureadmin --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['vhd']['uri'] == result['copied_disk_uri']


class WindowsSinglepassKekEncryptedManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinSinglepassKekEncryptedManagedDiskCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
            'key': 'key1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True --enable-soft-delete True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Create key
        self.cmd('keyvault key create --vault-name {kv} --name {key} --protection software')

        # Check key
        key = self.cmd('keyvault key list --vault-name {kv} -o json').get_output_in_json()
        assert len(key) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv} --key-encryption-key {key}')

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class LinuxSinglepassKekEncryptedManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxSinglepassKekEncryptedManagedDiskCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
            'key': 'key1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image UbuntuLTS --admin-username azureadmin --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True --enable-soft-delete True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Create key
        self.cmd('keyvault key create --vault-name {kv} --name {key} --protection software')

        # Check key
        key = self.cmd('keyvault key list --vault-name {kv} -o json').get_output_in_json()
        assert len(key) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv} --key-encryption-key {key}')
        # Add buffer time for encryption settings to be set
        time.sleep(300)

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class WindowsSinglepassNoKekEncryptedManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinSinglepassNoKekEncryptedManagedDiskCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True --enable-soft-delete True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv}')

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class LinuxSinglepassNoKekEncryptedManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxSinglepassNoKekEncryptedManagedDiskCreateRestoreTest(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image UbuntuLTS --admin-username azureadmin --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True --enable-soft-delete True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv}')
        # Add buffer time for encryption settings to be set
        time.sleep(300)

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


class WindowsRunHelloWorldTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinRunHelloWorld(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair run -g {rg} -n {vm} --run-id win-hello-world -o json').get_output_in_json()

        # Check Output
        assert 'Hello World!' in result['output']


class LinuxRunHelloWorldTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxRunHelloWorld(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image UbuntuLTS --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair run -g {rg} -n {vm} --run-id linux-hello-world -o json').get_output_in_json()

        # Check Output
        assert 'Hello World!' in result['output']
