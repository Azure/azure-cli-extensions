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
import uuid
import secrets
import string

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
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2022Datacenter --admin-password !Passw0rd2018 --use-unmanaged-disk')
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

    @ResourceGroupPreparer(location='westus2')
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

        # Test create SUSE
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

@pytest.mark.repairbutton
class RepairButtonLinuxVM(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_RepairAndRestoreLinuxVM(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1'
        })

        # Create test VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --image Win2022Datacenter --admin-password !Passw0rd2018')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test Repair and restore
        result = self.cmd('vm repair repair-button -g {rg} -n {vm} --button-command initrd')
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']

@pytest.mark.arm64
class LinuxARMManagedDiskCreateRestoreTest(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
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

@pytest.mark.ConfVM
class WindowsConfidentialVMRepair(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_ConfidentialVMAndUnlockDisk(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',  
            'rg': resource_group  
        })

        # Create test VM
        # need to create a cvm
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --admin-password !Passw0rd2024 --image Win2022Datacenter')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2024 --unlock-encrypted-vm --encrypt-recovery-key !Passw0rd2024 --yes --verbose -o json').get_output_in_json()
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


@pytest.mark.winTrustedLaunchVMFlag
class WindowsTrustedLaunchVMFlag(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_TrustedLaunchVMFlag(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',  
            'rg': resource_group  
        })

        # Create test VM
        # need to create a TL VM
        self.cmd('vm create -g {rg} -n {vm} --admin-username azureadmin --admin-password !Passw0rd2024 --image Win2022Datacenter')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Test create
        result = self.cmd('vm repair create -g {rg} -n {vm} --repair-username azureadmin --repair-password !Passw0rd2024 --yes  --unlock-encrypted-vm --encrypt-recovery-key !Passw0rd2024 --disable-trusted-launch --verbose -o json').get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        print("Printing repair VM Output")
        print(repair_vm)
        security_profile_repair_vm = repair_vm.get("securityProfile")  
        assert security_profile_repair_vm is None
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']

        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')

        # Check swapped OS disk
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']

@pytest.mark.RepairVMIdAPIChange
class WindowsRunWithRepairVMId(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WindowsRunWithRepairIdAPIChange(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',  
            'rg': resource_group  
        })

        rgname = resource_group
        vmname = 'vm1'

        # Create test VM
        self.cmd('vm create -g {} -n {} --admin-username azureadmin --admin-password !Passw0rd2024 --image Win2022Datacenter'.format(rgname, vmname))
        vms = self.cmd('vm list -g {} -o json'.format(rgname)).get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create repair vm
        result = self.cmd('vm repair create -g {} -n {} --repair-username azureadmin --repair-password !Passw0rd2024 --unlock-encrypted-vm --encrypt-recovery-key !Passw0rd2024 --yes --distro Win2022Datacenter --verbose -o json'.format(rgname, vmname)).get_output_in_json()
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Check repair VM
        repair_vms = self.cmd('vm list -g {} -o json'.format(result['repair_resource_group'])).get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        # Check attached data disk
        assert repair_vm['storageProfile']['dataDisks'][0]['name'] == result['copied_disk_name']
        repair_vm_id = repair_vm['id']
        resourceGroup = resource_group
        # az vm repair run -g $rgname -n $vmname --run-id win-hello-world --run-on-repair --repair-vm-id $resourceId --verbose --debug;
        run_result = self.cmd('vm repair run -g {} -n {} --run-id win-crowdstrike-fix-bootloop-v2 --run-on-repair --repair-vm-id {}'.format(rgname, vmname, repair_vm_id))
        assert result['status'] == STATUS_SUCCESS, result['error_message']

        # Call Restore
        self.cmd('vm repair restore -g {} -n {} --yes'.format(rgname, vmname))

        # Check swapped OS disk
        vms = self.cmd('vm list -g {} -o json'.format(rgname)).get_output_in_json()
        source_vm = vms[0]
        assert source_vm['storageProfile']['osDisk']['name'] == result['copied_disk_name']
        
        
        

@pytest.mark.winNoPublicIPByDefault
class WindowsNoPubIPByDefault(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WindowsNoPublicIPByDefault(self, resource_group):
        base_password = "Passw0rd2024"
        guid_suffix = str(uuid.uuid4())
        secure_password = base_password + guid_suffix
        username_length = 8
        secure_username = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(username_length))
        self.kwargs.update({
            'vm': 'vm1',
            'admin_password': secure_password,
            'admin_username': secure_username
        })

        # Create test VM without public IP
        self.cmd('vm create -g {rg} -n {vm} --admin-username {admin_username} --admin-password {admin_password} --image MicrosoftWindowsServer:windowsserver:2022-datacenter:latest')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create Repair VM
        repair_vm = self.cmd('vm repair create -g {rg} -n {vm} --repair-username {admin_username} --repair-password {admin_password} --yes -o json').get_output_in_json()
        assert repair_vm['status'] == STATUS_SUCCESS, repair_vm['error_message']
        # Check repair VM
        self.kwargs.update({
            'vm': 'vm1',
            'admin_password': secure_password,
            'admin_username': secure_username,
            'repair_resource_group': repair_vm['repair_resource_group']
        })
        # need to verify there is no public ip on the vm
        public_ip_list = self.cmd('network public-ip list -g {repair_resource_group} -o json').get_output_in_json()
        assert len(public_ip_list) == 0
        
        repair_vms = self.cmd('vm list -g {repair_resource_group} -o json').get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        repair_vm_id = repair_vm['id']
        self.kwargs.update({
            'vm': 'vm1',
            'admin_password': secure_password,
            'admin_username': secure_username,
            'repair_vm_id': repair_vm_id
        })
        
        # Run a script for testing repair-vm-id
        result_run = self.cmd('vm repair run -g {rg} -n {vm} --run-id win-hello-world --repair-vm-id {repair_vm_id} --run-on-repair -o json').get_output_in_json()
        assert result_run['status'] == STATUS_SUCCESS, result_run['error_message']
        
        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes')


@pytest.mark.winPublicIPWithParameter
class WindowsPublicIPWithParameter(LiveScenarioTest):

    @ResourceGroupPreparer(location='westus2')
    def test_vmrepair_WindowsPublicIPWithParameter(self, resource_group):

        base_password = "Passw0rd2024"
        guid_suffix = str(uuid.uuid4())
        secure_password = base_password + guid_suffix
        username_length = 8
        secure_username = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(username_length))
        self.kwargs.update({
            'vm': 'vm1',
            'admin_password': secure_password,
            'admin_username': secure_username
        })
        
        # Create test VM with public IP
        self.cmd('vm create -g {rg} -n {vm} --admin-username {admin_username} --admin-password {admin_password} --image MicrosoftWindowsServer:windowsserver:2022-datacenter:latest')
        vms = self.cmd('vm list -g {rg} -o json').get_output_in_json()
        # Something wrong with vm create command if it fails here
        assert len(vms) == 1

        # Create Repair VM
        repair_vm = self.cmd('vm repair create -g {rg} -n {vm} --repair-username {admin_username} --repair-password {admin_password} --debug --verbose --associate-public-ip --yes -o json').get_output_in_json()
        assert repair_vm['status'] == STATUS_SUCCESS, repair_vm['error_message']
        # Check repair VM
        self.kwargs.update({
            'vm': 'vm1',
            'admin_password': secure_password,
            'admin_username': secure_username,
            'repair_resource_group': repair_vm['repair_resource_group']
        })
        # need to verify there is no public ip on the vm
        public_ip_list = self.cmd('network public-ip list -g {repair_resource_group} --debug --verbose -o json').get_output_in_json()
        assert len(public_ip_list) == 1
        
        repair_vms = self.cmd('vm list -g {repair_resource_group} -o json').get_output_in_json()
        assert len(repair_vms) == 1
        repair_vm = repair_vms[0]
        repair_vm_id = repair_vm['id']
        self.kwargs.update({
            'vm': 'vm1',
            'admin_password': secure_password,
            'admin_username': secure_username,
            'repair_vm_id': repair_vm_id
        })
        
        # Run a script for testing repair-vm-id
        result_run = self.cmd('vm repair run -g {rg} -n {vm} --run-id win-hello-world --repair-vm-id {repair_vm_id} --run-on-repair --debug --verbose -o json').get_output_in_json()
        assert result_run['status'] == STATUS_SUCCESS, result_run['error_message']
        
        # Call Restore
        self.cmd('vm repair restore -g {rg} -n {vm} --yes') 