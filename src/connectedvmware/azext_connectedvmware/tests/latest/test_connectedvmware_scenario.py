# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from knack.util import CLIError
from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ConnectedvmwareScenarioTest(ScenarioTest):
    def test_connectedvmware(self):
        self.kwargs.update(
            {
                'rg': 'azcli-contoso-rg',
                'loc': 'eastus',
                'cus_loc': 'azcli-contoso-avs-cl',
                'vc_name': 'azcli-contoso-avs-vc',
                'rp_inventory_item': 'resgroup-251086',
                'rp_name': 'azcli-contoso-resource-pool',
                'cluster_inventory_item': 'domain-c8',
                'cluster_name': 'azcli-contoso-cluster',
                'datastore_inventory_item': 'datastore-13',
                'datastore_name': 'azcli-contoso-datastore',
                'host_inventory_item': 'host-87223',
                'host_name': 'azcli-contoso-host',
                'vnet_inventory_item': 'network-o96',
                'vnet_name': 'azcli-contoso-virtual-network',
                'vmtpl_inventory_item': 'vmtpl-vm-251226',
                'vmtpl_name': 'azcli-contoso-vm-template',
                'vm_name': 'azcli-contoso-vm-0',
                'guest_username': 'azcli-user',
                'guest_password': 'azcli-password',
                'nic_name': 'nic_1',
                'disk_name': 'disk_1',
                'extension_name': 'RunCommand',
                'extension_type': 'CustomScript',
                'publisher': 'Microsoft.Azure.Extensions',
                'command_whoami': '{"commandToExecute": "whoami"}',
                'command_uname': '{"commandToExecute": "uname"}',
            }
        )

        # Validate the show command output with vcenter name.
        vcenter_props = self.cmd(
            'az connectedvmware vcenter show -g {rg} --name {vc_name}',
            checks=[
                self.check('name', '{vc_name}'),
            ],
        ).get_output_in_json()
        vcenter_id = vcenter_props['id']
        self.kwargs.update({'vcenter_id': vcenter_id})

        # Count the vcenter resources in this resource group with list command
        count = len(
            self.cmd('az connectedvmware vcenter list -g {rg}').get_output_in_json()
        )
        # vcenter count list should report 1
        self.assertGreaterEqual(count, 1, 'vcenter resource count expected to be at least 1')

        # Create resource-pool resource.
        self.cmd(
            'az connectedvmware resource-pool create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {rp_inventory_item} --name {rp_name}'
        )

        # Validate the show command output with resource-pool name.
        self.cmd(
            'az connectedvmware resource-pool show -g {rg} --name {rp_name}',
            checks=[
                self.check('name', '{rp_name}'),
            ],
        )

        # List the resource-pool resources in this resource group.
        resource_list = self.cmd(
            'az connectedvmware resource-pool list -g {rg}'
        ).get_output_in_json()
        # At this point there should be 1 resource-pool resource.
        assert len(resource_list) >= 1

        # Create cluster resource.
        self.cmd(
            'az connectedvmware cluster create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {cluster_inventory_item} --name {cluster_name}'
        )

        # Validate the show command output with cluster name.
        self.cmd(
            'az connectedvmware cluster show -g {rg} --name {cluster_name}',
            checks=[
                self.check('name', '{cluster_name}'),
            ],
        )

        # List the cluster resources in this resource group.
        resource_list = self.cmd(
            'az connectedvmware cluster list -g {rg}'
        ).get_output_in_json()
        # At this point there should be 1 cluster resource.
        assert len(resource_list) >= 1

        # Create datastore resource.
        self.cmd(
            'az connectedvmware datastore create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {datastore_inventory_item} --name {datastore_name}'
        )

        # Validate the show command output with datastore name.
        self.cmd(
            'az connectedvmware datastore show -g {rg} --name {datastore_name}',
            checks=[
                self.check('name', '{datastore_name}'),
            ],
        )

        # List the datastore resources in this resource group.
        resource_list = self.cmd(
            'az connectedvmware datastore list -g {rg}'
        ).get_output_in_json()
        # At this point there should be 1 datastore resource.
        assert len(resource_list) >= 1

        # Create host resource.
        self.cmd(
            'az connectedvmware host create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {host_inventory_item} --name {host_name}'
        )

        # Validate the show command output with host name.
        self.cmd(
            'az connectedvmware host show -g {rg} --name {host_name}',
            checks=[
                self.check('name', '{host_name}'),
            ],
        )

        # List the host resources in this resource group.
        resource_list = self.cmd(
            'az connectedvmware host list -g {rg}'
        ).get_output_in_json()
        # At this point there should be 1 host resource.
        assert len(resource_list) >= 1

        # Create virtual-network resource.
        self.cmd(
            'az connectedvmware virtual-network create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {vnet_inventory_item} --name {vnet_name}'
        )

        # Validate the show command output with virtual-network name.
        self.cmd(
            'az connectedvmware virtual-network show -g {rg} --name {vnet_name}',
            checks=[
                self.check('name', '{vnet_name}'),
            ],
        )

        # List the virtual-network resources in this resource group.
        resource_list = self.cmd(
            'az connectedvmware virtual-network list -g {rg}'
        ).get_output_in_json()
        # At this point there should be 1 virtual-network resource.
        assert len(resource_list) >= 1

        # Create vm-template resource.
        self.cmd(
            'az connectedvmware vm-template create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {vmtpl_inventory_item} --name {vmtpl_name}'
        )

        # Validate the show command output with vm-template name.
        self.cmd(
            'az connectedvmware vm-template show -g {rg} --name {vmtpl_name}',
            checks=[
                self.check('name', '{vmtpl_name}'),
            ],
        )

        # List the vm-template resources in this resource group.
        resource_list = self.cmd(
            'az connectedvmware vm-template list -g {rg}'
        ).get_output_in_json()
        # At this point there should be 1 vm-template resource.
        assert len(resource_list) >= 1

        # Validate the inventory-item show command output with resourcepool moRefID.
        self.cmd(
            'az connectedvmware vcenter inventory-item show -g {rg} --vcenter {vc_name} --i {rp_inventory_item}',
            checks=[
                self.check('name', '{rp_inventory_item}'),
            ],
        )

        # Create vm resource.
        self.cmd(
            'az connectedvmware vm create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} --resource-pool {rp_name} --vm-template {vmtpl_name} --name {vm_name}'
        )

        # Validate the show command output with vm name.
        vm = self.cmd(
            'az connectedvmware vm show -g {rg} --name {vm_name}',
            checks=[
                self.check('infrastructureProfile.moName', '{vm_name}'),
            ],
        ).get_output_in_json()
        vm_moRefId = vm['infrastructureProfile']['moRefId']
        self.kwargs.update({'vm_moRefId': vm_moRefId})
        self.assertIsNotNone(vm_moRefId)
        self.assertNotEqual(len(vm_moRefId), 0, 'moRefId of the VM should not be empty')

        # Validate vm nic name.
        self.cmd(
            'az connectedvmware vm nic show -g {rg} --vm-name {vm_name} --name {nic_name}',
            checks=[
                self.check('name', '{nic_name}'),
            ],
        )

        # List the nic for the vm.
        resource_list = self.cmd(
            'az connectedvmware vm nic list -g {rg} --vm-name {vm_name}'
        ).get_output_in_json()
        # At least 1 nic should be there for the vm resource.
        assert len(resource_list) >= 1

        # Validate vm disk name.
        self.cmd(
            'az connectedvmware vm disk show -g {rg} --vm-name {vm_name} --name {disk_name}',
            checks=[
                self.check('name', '{disk_name}'),
            ],
        )

        # List the disk for the vm.
        resource_list = self.cmd(
            'az connectedvmware vm disk list -g {rg} --vm-name {vm_name}'
        ).get_output_in_json()
        # At least 1 disk should be there for the vm resource.
        assert len(resource_list) >= 1

        # Enable guest agent on the vm resource.
        self.cmd(
            'az connectedvmware vm guest-agent enable -g {rg} --vm-name {vm_name} --username {guest_username} --password {guest_password}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ],
        )

        # Create VM extension.
        extension = self.cmd(
            '''
            az connectedvmware vm extension create -l {loc} -g {rg} --vm-name {vm_name} --name {extension_name} --type {extension_type} --publisher {publisher} --settings '{command_whoami}'
            '''.strip(),
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('settings.commandToExecute', 'whoami'),
            ],
        ).get_output_in_json()
        self.assertIn(
            'root',
            extension['instanceView']['status']['message']
        )

        # Update VM extension.
        extension = self.cmd(
            '''
            az connectedvmware vm extension update -g {rg} --vm-name {vm_name} --name {extension_name} --settings '{command_uname}'
            '''.strip(),
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('settings.commandToExecute', 'uname'),
            ],
        ).get_output_in_json()
        self.assertIn(
            'Linux',
            extension['instanceView']['status']['message']
        )

        self.cmd(
            'az connectedvmware vm create-from-machines -g {rg} --name {vm_name} --vcenter-id {vcenter_id}',
        )

        # Stop VM.
        self.cmd('az connectedvmware vm stop -g {rg} --name {vm_name}')

        # Update VM.
        self.cmd(
            'az connectedvmware vm update -g {rg} --name {vm_name} --memory-size 8192 --num-CPUs 4',
            checks=[
                self.check('hardwareProfile.memorySizeMb', '8192'),
                self.check('hardwareProfile.numCpUs', '4'),
            ],
        )

        # Start VM.
        self.cmd('az connectedvmware vm start -g {rg} --name {vm_name}')

        # Disable the VM from azure; delete the ARM resource, retain the VM in vCenter.
        self.cmd('az connectedvmware vm delete -g {rg} --name {vm_name} --retain-machine -y')

        # Enable the VM to azure again.
        self.cmd(
            'az connectedvmware vm create -g {rg} -l {loc} --custom-location {cus_loc} --vcenter {vc_name} -i {vm_moRefId} --name {vm_name}'
        )

        # Delete the created VM.
        self.cmd('az connectedvmware vm delete -g {rg} --name {vm_name} --delete-from-host --delete-machine -y')

        # Delete the created resource-pool.
        self.cmd('az connectedvmware resource-pool delete -g {rg} --name {rp_name} -y')

        # Delete the created cluster.
        self.cmd('az connectedvmware cluster delete -g {rg} --name {cluster_name} -y')

        # Delete the created datastore.
        self.cmd(
            'az connectedvmware datastore delete -g {rg} --name {datastore_name} -y'
        )

        # Delete the created host.
        self.cmd('az connectedvmware host delete -g {rg} --name {host_name} -y')

        # Delete the created virtual-network.
        self.cmd(
            'az connectedvmware virtual-network delete -g {rg} --name {vnet_name} -y'
        )

        # Delete the created vm-template.
        self.cmd('az connectedvmware vm-template delete -g {rg} --name {vmtpl_name} -y')
