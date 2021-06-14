# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from knack.util import CLIError
from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ConnectedvmwareScenarioTest(ScenarioTest):

    def test_connectedvmware(self):
        self.kwargs.update({
            'rg': 'azcli-test-rg',
            'loc': 'eastus2euap',
            'cus_loc': 'azcli-test-cl-avs',
            'vc_name': 'azcli-test-vcenter-avs',
            'rp_morefid': 'resgroup-5034',
            'rp_name': 'azcli-test-resource-pool',
            'vnet_morefid': 'network-o761',
            'vnet_name': 'azcli-test-virtual-network',
            'vmtpl_morefid': 'vm-55',
            'vmtpl_name': 'azcli-test-vm-template',
            'vm_name': 'azcli-test-virtual-machine',
            'nic_name': 'nic_1',
            'disk_name': 'disk_1'
        })

        # Validate the show command output with vcenter name.
        self.cmd('az connectedvmware vcenter show -g {rg} --name {vc_name}', checks=[
            self.check('name', '{vc_name}'),
        ])

        # Count the vcenter resources in this resource group with list command
        count = len(self.cmd('az connectedvmware vcenter list -g {rg}').get_output_in_json())
        # vcenter count list should report 1
        self.assertEqual(count, 1, 'vcenter resource count expected to be 1')

        # Create resource-pool resource.
        self.cmd('az connectedvmware resource-pool create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} --mo-ref-id {rp_morefid} --name {rp_name}')

        # Validate the show command output with resource-pool name.
        self.cmd('az connectedvmware resource-pool show -g {rg} --name {rp_name}', checks=[
            self.check('name', '{rp_name}'),
        ])

        # List the resource-pool resources in this resource group.
        resource_list = self.cmd('az connectedvmware resource-pool list -g {rg}').get_output_in_json()
        # At this point there should be 1 resource-pool resource.
        assert len(resource_list) >= 1

        # Create virtual-network resource.
        self.cmd('az connectedvmware virtual-network create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} --mo-ref-id {vnet_morefid} --name {vnet_name}')

        # Validate the show command output with virtual-network name.
        self.cmd('az connectedvmware virtual-network show -g {rg} --name {vnet_name}', checks=[
            self.check('name', '{vnet_name}'),
        ])

        # List the virtual-network resources in this resource group.
        resource_list = self.cmd('az connectedvmware virtual-network list -g {rg}').get_output_in_json()
        # At this point there should be 1 virtual-network resource.
        assert len(resource_list) >= 1

        # Create vm-template resource.
        self.cmd('az connectedvmware vm-template create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} --mo-ref-id {vmtpl_morefid} --name {vmtpl_name}')

        # Validate the show command output with vm-template name.
        self.cmd('az connectedvmware vm-template show -g {rg} --name {vmtpl_name}', checks=[
            self.check('name', '{vmtpl_name}'),
        ])

        # List the vm-template resources in this resource group.
        resource_list = self.cmd('az connectedvmware vm-template list -g {rg}').get_output_in_json()
        # At this point there should be 1 vm-template resource.
        assert len(resource_list) >= 1

        # Validate the show command output with inventory-item name.
        self.cmd('az connectedvmware inventory-item show -g {rg} --vcenter-name {vc_name} --inventory-item {rp_morefid}', checks=[
            self.check('name', '{rp_morefid}'),
        ])

        # Create vm resource.
        self.cmd('az connectedvmware vm create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} --resource-pool {rp_name} --vm-template {vmtpl_name} --name {vm_name}')

        # Validate the show command output with vm name.
        self.cmd('az connectedvmware vm show -g {rg} --name {vm_name}', checks=[
            self.check('name', '{vm_name}'),
        ])

        # List the VM resources in this resource group.
        resource_list = self.cmd('az connectedvmware vm list -g {rg}').get_output_in_json()
        # At this point there should be 1 vm resource.
        assert len(resource_list) >= 1

        # Validate vm nic name.
        self.cmd('az connectedvmware vm nic show -g {rg} --vm-name {vm_name} --name {nic_name}', checks=[
            self.check('name', '{nic_name}'),
        ])

        # List the nic for the vm.
        resource_list = self.cmd('az connectedvmware vm nic list -g {rg} --vm-name {vm_name}').get_output_in_json()
        # At least 1 nic should be there for the vm resource.
        assert len(resource_list) >= 1

        # Validate vm disk name.
        self.cmd('az connectedvmware vm disk show -g {rg} --vm-name {vm_name} --name {disk_name}', checks=[
            self.check('name', '{disk_name}'),
        ])

        # List the disk for the vm.
        resource_list = self.cmd('az connectedvmware vm disk list -g {rg} --vm-name {vm_name}').get_output_in_json()
        # At least 1 disk should be there for the vm resource.
        assert len(resource_list) >= 1

        # Stop VM.
        self.cmd('az connectedvmware vm stop -g {rg} --name {vm_name}')

        # Start VM.
        self.cmd('az connectedvmware vm start -g {rg} --name {vm_name}')

        # Delete the created VM.
        self.cmd('az connectedvmware vm delete -g {rg} --name {vm_name}')

        # Delete the created resource-pool.
        self.cmd('az connectedvmware resource-pool delete -g {rg} --name {rp_name}')

        # Delete the created virtual-network.
        self.cmd('az connectedvmware virtual-network delete -g {rg} --name {vnet_name}')

        # Delete the created vm-template.
        self.cmd('az connectedvmware vm-template delete -g {rg} --name {vmtpl_name}')
