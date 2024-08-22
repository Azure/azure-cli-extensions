# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, unused-argument
import time

import pytest
from azure.cli.testsdk import LiveScenarioTest, ResourceGroupPreparer
import json
import re

STATUS_SUCCESS = 'SUCCESS'

@pytest.mark.WindowsManaged
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
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 -o json --yes').get_output_in_json()
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

@pytest.mark.WindowsUnmanaged
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
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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


@pytest.mark.linuxManaged
class LinuxManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxManagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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


@pytest.mark.linuxUnmanaged
class LinuxUnmanagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxUnmanagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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

@pytest.mark.WinManagedDiskPubIpRestore
class WindowsManagedDiskCreateRestoreTestwithpublicip(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinManagedCreateRestorePublicIp(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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

@pytest.mark.WinUnmanagedDiskPubIpRestore
class WindowsUnmanagedDiskCreateRestoreTestwithpublicip(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinUnmanagedCreateRestorePublicIp(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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

@pytest.mark.LinuxManagedDiskPubIpRestore
class LinuxManagedDiskCreateRestoreTestwithpublicip(LiveScenarioTest):

    @ResourceGroupPreparer(location='eastus')
    def test_vmrepair_LinuxManagedCreateRestorePublicIp(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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

@pytest.mark.LinuxUnmanagedDiskPubIpRestore
class LinuxUnmanagedDiskCreateRestoreTestwithpublicip(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxUnmanagedCreateRestorePublicIp(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018 --use-unmanaged-disk')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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


@pytest.mark.encryption
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
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True')

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
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm --yes -o json').get_output_in_json()
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


@pytest.mark.linuxencryption
class LinuxSinglepassKekEncryptedManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxSinglepassKekEncryptedManagedDiskCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
            'key': 'key1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True')

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
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm --yes -o json').get_output_in_json()
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

@pytest.mark.WindowsNoKekRestore
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
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv}')

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm --yes -o json').get_output_in_json()
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

@pytest.mark.LinuxNoKekRestore
class LinuxSinglepassNoKekEncryptedManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxSinglepassNoKekEncryptedManagedDiskCreateRestoreTest(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv}')
        # Add buffer time for encryption settings to be set
        time.sleep(300)

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --unlock-encrypted-vm --yes -o json').get_output_in_json()
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

@pytest.mark.WindHelloWorld
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

@pytest.mark.LinHelloWorld
class LinuxRunHelloWorldTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxRunHelloWorld(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Canonical:UbuntuServer:18.04-LTS:latest --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair run -g {rg} -n {vm} --run-id linux-hello-world -o json').get_output_in_json()

        # Check Output
        assert 'Hello World!' in result['output']

@pytest.mark.ManagedDiskGen2
class WindowsManagedDiskCreateRestoreGen2Test(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WinManagedCreateRestoreGen2(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image MicrosoftWindowsServer:windowsserver-gen2preview:2019-datacenter-gen2:2019.0.20190620 --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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

@pytest.mark.linuxKekRHEL
class LinuxSinglepassKekEncryptedManagedDiskWithRHEL8DistroCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxSinglepassKekEncryptedManagedDiskCreateRestoreRHEL8(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
            'key': 'key1'
        })

        # Create test VM
        resultVM = self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018 --size Standard_D2s_v3').get_output_in_json() 
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        getVM = self.cmd('az vm show --name {vm} --resource-group {rg} --output json').get_output_in_json()
        print("PRINTING VMS")
        # print(vms['resourceGroup'])
        # print(resultVM["name"])
        # print(json.dumps(vms, indent=4))
        # Define the regular expressions to match subscription ID, resource group, and VM name  
        vmId = getVM['id']
        sub_re = re.compile(r'/subscriptions/(.*?)/')  
        rg_re = re.compile(r'/resourceGroups/(.*?)/')  
        vm_re = re.compile(r'/virtualMachines/(.*)') 
        # Use the regular expressions to search the string  
        try:
            subscription_id = sub_re.search(vmId).group(1)  
            resource_group = rg_re.search(vmId).group(1)  
            vm_name = vm_re.search(vmId).group(1)
            print('successfully parsed id')
        except AttributeError:
            raise Exception("The VM Id did not match the expected format and could not be parsed!")

        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True')

        # Check keyvault
        subId = self.cmd('az account show --query id --output tsv')
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Create key
        print('trying to create key')
        roleAssignmentCmd = self.cmd('az role assignment create --assignee f90057dd-422f-49fc-a88f-91e965bc00c8 --role "Key Vault Contributor" --scope /subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/virtualMachines/{}'.format(subscription_id, resource_group, vm_name)).get_output_in_json()
        print(roleAssignmentCmd)
        listRoles = self.cmd('az role assignment list --scope /subscriptions/{}/resourceGroups/{}/providers/Microsoft.Compute/virtualMachines/{} --query "[?principalId==\'f90057dd-422f-49fc-a88f-91e965bc00c8\']"'.format(subscription_id, resource_group, vm_name)).get_output_in_json()
        print(listRoles)
        print('listed out role assignments above')
        self.cmd('keyvault key create --vault-name {kv} --name {key} --protection software')

        # Check key
        key = self.cmd('keyvault key list --vault-name {kv} -o json').get_output_in_json()
        assert len(key) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv} --key-encryption-key {key}')
        # Add buffer time for encryption settings to be set
        time.sleep(300)

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --distro rhel8 --unlock-encrypted-vm --yes -o json').get_output_in_json()
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

@pytest.mark.linuxNoKekWithSles
class LinuxSinglepassNoKekEncryptedManagedDiskWithSLES15CreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxSinglepassNoKekEncryptedManagedDiskCreateRestoreTestSLES15(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'kv': self.create_random_name(prefix='cli', length=8),
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018 --size Standard_D2s_v3')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create key vault
        self.cmd('keyvault create -n {kv} -g {rg} --enabled-for-disk-encryption True')

        # Check keyvault
        keyvault = self.cmd('keyvault list -g {rg} -o json').get_output_in_json()
        assert len(keyvault) == 1

        # Enable encryption
        self.cmd('vm encryption enable -g {rg} -n {vm} --disk-encryption-keyvault {kv}')
        # Add buffer time for encryption settings to be set
        time.sleep(300)

        # Test create # SuseSles15SP3
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --distro sles15 --unlock-encrypted-vm --yes -o json').get_output_in_json()
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

@pytest.mark.LinuxManagedPubIpOracle
class LinuxManagedDiskCreateRestoreTestwithOracle8andpublicip(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_LinuxManagedCreateRestoreOracle8PublicIp(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18.04-LTS:latest --admin-username azureadmin --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --distro oracle8 --yes -o json').get_output_in_json()
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

@pytest.mark.WindowsResetNic
class ResetNICWindowsVM(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_ResetNicWindowsVM(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test Reset NIC
        self.cmd('vm repair reset-nic -g {rg} -n {vm} --yes')

        # Mac address should be changed in the Guest OS but no way to assert from here.
        # Assert that the VM is still running afterwards
        vm_instance_view = self.cmd('vm get-instance-view -g {rg} -n {vm} -o json').get_output_in_json()
        vm_power_state = vm_instance_view['instanceView']['statuses'][1]['code']
        assert vm_power_state == 'PowerState/running'


@pytest.mark.repairandrestore
class RepairAndRestoreLinuxVM(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_RepairAndRestoreLinuxVM(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test Repair and restore
        result = self.cmd('vm repair repair-and-restore -g {rg} -n {vm}')
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']


@pytest.mark.arm64
class LinuxARMManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='eastus')
    def test_vmrepair_LinuxARMManagedCreateRestore(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --image Canonical:UbuntuServer:18_04-lts-arm64:latest --admin-username azureadmin --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2018 --yes -o json').get_output_in_json()
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
        
@pytest.mark.ResetNic        
class ResetNICWithASG(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_ResetNicWithASGWindowsVM(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2016Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        #create ASG
        self.cmd('az network asg create \
                  --resource-group myResourceGroup \
                  --name myASG')

        # Test Reset NIC
        self.cmd('vm repair reset-nic -g {rg} -n {vm} --yes')

        # Mac address should be changed in the Guest OS but no way to assert from here.
        # Assert that the VM is still running afterwards
        vm_instance_view = self.cmd('vm get-instance-view -g {rg} -n {vm} -o json').get_output_in_json()
        vm_power_state = vm_instance_view['instanceView']['statuses'][1]['code']
        assert vm_power_state == 'PowerState/running'
