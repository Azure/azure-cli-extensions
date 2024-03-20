# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import

import os
from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ScVmmScenarioTest(ScenarioTest):
    def test_scvmm(self):
        self.kwargs.update(
            {
                'resource_group': 'azcli-test-rg-vmm',
                'location': 'eastus2euap',
                'custom_location': 'azcli-test-cl',
                'vmmserver_name': 'azcli-test-vmmserver',
                'icloud_name': 'azcli-test-cloud',
                'icloud_uuid': 'e27d3a99-8369-4748-a7f0-9526aa8a010e',
                'cloud_name': 'azcli-test-cloud',
                'ivmt_name': 'azcli-test-vm-template-win19',
                'ivmt_uuid': '6f8f6517-8f3b-41b2-8b60-8d91a672bf1f',
                'vmt_name': 'azcli-test-vm-template-win19',
                'ivnet_name': 'azcli-test-virtual-network',
                'ivnet_uuid': '5e1432af-6099-4a9f-b33d-b6a6ce93a526',
                'vnet_name': 'azcli-test-virtual-network',
                'avset_string': 'avset1',
                'avset_name': 'azcli-test-avset1',
                'vm_name': 'azcli-test-vm-1',
                'disk_name': 'disk_1',
                'nic_name': 'nic_1',
                'checkpoint_name': 'azcli-test-checkpoint',
                'checkpoint_description': 'azcli-test-checkpoint',
                'guest_username': 'Administrator',
                'guest_password': 'Password~1',
                'extension_name': 'RunCommand',
                'extension_type': 'CustomScriptExtension',
                'publisher': 'Microsoft.Compute',
                'command_whoami': '{"commandToExecute": "whoami"}',
                'command_sysroot': '{"commandToExecute": "echo %SYSTEMROOT%"}',
            }
        )

        self.cmd(
            'az scvmm vmmserver show -g {resource_group} --name {vmmserver_name}',
            checks=[
                self.check('name', '{vmmserver_name}'),
            ],
        )

        self.cmd(
            'az scvmm vmmserver list -g {resource_group}',
            checks=[self.greater_than('length(@)', 0)],
        )

        self.cmd(
            "az scvmm vmmserver inventory-item show -g {resource_group} -v {vmmserver_name}"
            " -i {icloud_uuid}",
            checks=[
                self.check('inventoryItemName', '{icloud_name}'),
                self.check('kind', 'Cloud'),
                self.check('uuid', '{icloud_uuid}'),
            ],
        )

        self.cmd(
            "az scvmm vmmserver inventory-item show -g {resource_group} -v {vmmserver_name}"
            " -i {ivmt_uuid}",
            checks=[
                self.check('inventoryItemName', '{ivmt_name}'),
                self.check('kind', 'VirtualMachineTemplate'),
                self.check('uuid', '{ivmt_uuid}'),
            ],
        )
        self.cmd(
            "az scvmm vmmserver inventory-item show -g {resource_group} -v {vmmserver_name}"
            " -i {ivnet_uuid}",
            checks=[
                self.check('inventoryItemName', '{ivnet_name}'),
                self.check('kind', 'VirtualNetwork'),
                self.check('uuid', '{ivnet_uuid}'),
            ],
        )

        self.cmd(
            'az scvmm cloud create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -i {icloud_uuid} --name {cloud_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm vm-template create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -i {ivmt_uuid} --name {vmt_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm virtual-network create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -i {ivnet_uuid} --name {vnet_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm avset create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -a {avset_string} --name {avset_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm vm create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -c {cloud_name} -t {vmt_name} -a {avset_name} -n {vm_name} --disk'
            ' name={disk_name} disk-size=2 bus=0 --nic name={nic_name} network={vnet_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.greater_than('storageProfile.disks | length(@)', 0),
                self.check('networkProfile.networkInterfaces | length(@)', 1),
            ],
        )

        self.cmd(
            'az scvmm vm disk show -g {resource_group} --vm-name {vm_name} -n {disk_name}',
            checks=[
                self.check('name', '{disk_name}'),
            ],
        )

        self.cmd(
            'az scvmm vm nic show -g {resource_group} --vm-name {vm_name} -n {nic_name}',
            checks=[
                self.check('name', '{nic_name}'),
            ],
        )

        self.cmd('az scvmm vm start -g {resource_group} --name {vm_name}')

        self.cmd(
            "az scvmm vm guest-agent enable -g {resource_group} --vm-name {vm_name}"
            " --username {guest_username} --password {guest_password}",
            checks=[
                self.check('provisioningState', 'Succeeded'),
            ],
        )

        extension = self.cmd(
            "az scvmm vm extension create -l {location} -g {resource_group} --vm-name {vm_name}"
            " --name {extension_name} --type {extension_type} --publisher {publisher}"
            " --settings '{command_whoami}'",
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('settings.commandToExecute', 'whoami'),
            ],
        ).get_output_in_json()
        self.assertIn(
            'nt authority\\system',
            extension['instanceView']['status']['message'].lower()
        )

        extension = self.cmd(
            "az scvmm vm extension update -g {resource_group} --vm-name {vm_name}"
            " --name {extension_name} --settings '{command_sysroot}'",
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('settings.commandToExecute', 'echo %SYSTEMROOT%'),
            ],
        ).get_output_in_json()
        self.assertIn(
            'C:\\Windows'.lower(),
            extension['instanceView']['status']['message'].lower()
        )

        self.cmd(
            'az scvmm vm stop -g {resource_group} --name {vm_name} --skip-shutdown'
        )

        self.cmd(
            'az scvmm vm update -g {resource_group} -n {vm_name}'
            ' --cpu-count 6 --dynamic-memory-enabled true',
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('hardwareProfile.cpuCount', 6),
                self.check('hardwareProfile.dynamicMemoryEnabled', 'true'),
            ],
        )

        self.cmd(
            'az scvmm vm create-checkpoint -g {resource_group} --name {vm_name} --checkpoint-name {checkpoint_name} --checkpoint-description {checkpoint_description}',
        )
        alias_sub = self.cmd('az scvmm vm show -g {resource_group} --name {vm_name}',
                             checks=[
                                 self.check('provisioningState', 'Succeeded'),
                                 self.greater_than('infrastructureProfile.checkpoints | length(@)', 0),                                
                             ]).get_output_in_json()
        checkpoint_id = alias_sub['infrastructureProfile']['checkpoints'][0]['checkpointId']
        self.kwargs.update({'checkpoint_id': checkpoint_id})

        self.cmd(
            'az scvmm vm restore-checkpoint -g {resource_group} --name {vm_name} --checkpoint-id {checkpoint_id}',
        )
        self.cmd(
            'az scvmm vm show -g {resource_group} --name {vm_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),                           
            ]
        )

        self.cmd(
            'az scvmm vm delete-checkpoint -g {resource_group} --name {vm_name} --checkpoint-id {checkpoint_id}',
        )
        self.cmd(
            'az scvmm vm show -g {resource_group} --name {vm_name}',
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('infrastructureProfile.checkpoints | length(@)', 0),                           
            ]
        )

        self.cmd('az scvmm vm delete -g {resource_group} --name {vm_name} --delete-from-host -y')

        self.cmd('az scvmm avset delete -g {resource_group} --name {avset_name} -y')

        self.cmd(
            'az scvmm virtual-network delete -g {resource_group} --name {vnet_name} -y'
        )

        self.cmd('az scvmm vm-template delete -g {resource_group} --name {vmt_name} -y')

        self.cmd('az scvmm cloud delete -g {resource_group} --name {cloud_name} -y')
