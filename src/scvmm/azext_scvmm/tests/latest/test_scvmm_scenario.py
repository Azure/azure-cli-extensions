# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-import

import os
from azure.cli.testsdk import ScenarioTest
import datetime

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ScVmmScenarioTest(ScenarioTest):
    def test_scvmm(self):
        self.kwargs.update(
            {
                'resource_group': 'azcli-test-rg-vmm',
                'location': 'eastus2euap',
                'custom_location': 'azcli-test-cl-vmm',
                'vmmserver_name': 'azcli-test-vmm-vmmserver',
                'icloud_name': 'azcli-test-cloud',
                'icloud_uuid': 'e353c9aa-28e0-4464-ab52-27269d1260f9',
                'cloud_name': 'azcli-test-cloud',
                'ivmt_name': 'azcli-test-vm-template-win19',
                'ivmt_uuid': 'd9a89dc5-0f27-4a5c-afc3-cb2f03edbf1d',
                'vmt_name': 'azcli-test-vm-template-win19',
                'ivnet_name': 'azcli-test-virtual-network',
                'ivnet_uuid': 'd4259487-1e8e-4fb8-a143-16f7418e1efa',
                'vnet_name': 'azcli-test-virtual-network',
                'avset_string': 'avset1',
                'avset_name': 'azcli-test-avset1',
                'vm_name': 'azcli-test-vm-01',
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
                self.check('properties.inventoryItemName', '{icloud_name}'),
                self.check('kind', 'Cloud'),
                self.check('properties.uuid', '{icloud_uuid}'),
            ],
        )

        self.cmd(
            "az scvmm vmmserver inventory-item show -g {resource_group} -v {vmmserver_name}"
            " -i {ivmt_uuid}",
            checks=[
                self.check('properties.inventoryItemName', '{ivmt_name}'),
                self.check('kind', 'VirtualMachineTemplate'),
                self.check('properties.uuid', '{ivmt_uuid}'),
            ],
        )
        self.cmd(
            "az scvmm vmmserver inventory-item show -g {resource_group} -v {vmmserver_name}"
            " -i {ivnet_uuid}",
            checks=[
                self.check('properties.inventoryItemName', '{ivnet_name}'),
                self.check('kind', 'VirtualNetwork'),
                self.check('properties.uuid', '{ivnet_uuid}'),
            ],
        )

        self.cmd(
            'az scvmm cloud create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -i {icloud_uuid} --name {cloud_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm cloud update -g {resource_group} --name {cloud_name} --tags tag1=value1',
            checks=[
                self.check('tags.tag1', 'value1'),
            ],
        )

        self.cmd(
            'az scvmm vm-template create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -i {ivmt_uuid} --name {vmt_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm vm-template update -g {resource_group} --name {vmt_name} --tags tag1=value1',
            checks=[
                self.check('tags.tag1', 'value1'),
            ],
        )

        self.cmd(
            'az scvmm virtual-network create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -i {ivnet_uuid} --name {vnet_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm virtual-network update -g {resource_group} --name {vnet_name} --tags tag1=value1',
            checks=[
                self.check('tags.tag1', 'value1'),
            ],
        )

        self.cmd(
            'az scvmm avset create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -v {vmmserver_name} -a {avset_string} --name {avset_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm avset update -g {resource_group} --name {avset_name} --tags tag1=value1',
            checks=[
                self.check('tags.tag1', 'value1'),
            ],
        )

        self.cmd(
            'az scvmm vm create -g {resource_group} -l {location} --custom-location'
            ' {custom_location} -c {cloud_name} -t {vmt_name} -a {avset_name} -n {vm_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.storageProfile.disks | length(@)', 1),
                self.check('properties.networkProfile.networkInterfaces | length(@)', 1),
            ],
        )

        self.cmd(
            'az scvmm vm disk add -g {resource_group} --vm-name {vm_name}'
            ' --name disk_2 --disk-size 20 --bus 0 --lun 0 --bus-type SCSI --vhd-type Dynamic',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm vm stop -g {resource_group} --name {vm_name} --skip-shutdown'
        )

        self.cmd(
            'az scvmm vm nic add -g {resource_group} --vm-name {vm_name}'
            ' --name="nic_2" --network={vnet_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
            ],
        )

        self.cmd(
            'az scvmm vm nic show -g {resource_group} --vm-name {vm_name} -n nic_2',
            checks=[
                self.check('name', 'nic_2'),
            ],
        )

        self.cmd('az scvmm vm start -g {resource_group} --name {vm_name}')

        self.cmd(
            "az scvmm vm guest-agent enable -g {resource_group} --vm-name {vm_name}"
            " --username {guest_username} --password {guest_password}",
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
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
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.hardwareProfile.cpuCount', 6),
                self.check('properties.hardwareProfile.dynamicMemoryEnabled', 'true'),
            ],
        )

        self.cmd(
            'az scvmm vm create-checkpoint -g {resource_group} --name {vm_name} --checkpoint-name {checkpoint_name} --checkpoint-description {checkpoint_description}',
        )
        alias_sub = self.cmd('az scvmm vm show -g {resource_group} --name {vm_name}',
                        checks=[
                            self.check('properties.provisioningState', 'Succeeded'),
                            self.greater_than('properties.infrastructureProfile.checkpoints | length(@)', 0),                                
                        ]).get_output_in_json()
        checkpoint_id = alias_sub['properties']['infrastructureProfile']['checkpoints'][0]['checkpointId']
        self.kwargs.update({'checkpoint_id': checkpoint_id})

        self.cmd(
            'az scvmm vm nic delete -g {resource_group} --vm-name {vm_name} --nics nic_2 -y'
        )

        self.cmd(
            'az scvmm vm restore-checkpoint -g {resource_group} --name {vm_name} --checkpoint-id {checkpoint_id}',
        )
        self.cmd(
            'az scvmm vm show -g {resource_group} --name {vm_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.networkProfile.networkInterfaces | length(@)', 2),
                self.check('properties.storageProfile.disks | length(@)', 2),
            ]
        )

        self.cmd(
            'az scvmm vm disk list -g {resource_group} --vm-name {vm_name}',
            checks=[
                self.check('length(@)', 2),
            ],
        )

        self.cmd(
            'az scvmm vm nic list -g {resource_group} --vm-name {vm_name}',
            checks=[
                self.check('length(@)', 2),
            ],
        )

        self.cmd(
            'az scvmm vm delete-checkpoint -g {resource_group} --name {vm_name} --checkpoint-id {checkpoint_id}',
        )
        self.cmd(
            'az scvmm vm show -g {resource_group} --name {vm_name}',
            checks=[
                self.check('properties.provisioningState', 'Succeeded'),
                self.check('properties.infrastructureProfile.checkpoints | length(@)', 0),                           
            ]
        )

        self.cmd('az scvmm vm delete -g {resource_group} --name {vm_name} --delete-from-host -y')

        self.cmd('az scvmm avset delete -g {resource_group} --name {avset_name} -y')

        self.cmd(
            'az scvmm virtual-network delete -g {resource_group} --name {vnet_name} -y'
        )

        self.cmd('az scvmm vm-template delete -g {resource_group} --name {vmt_name} -y')

        self.cmd('az scvmm cloud delete -g {resource_group} --name {cloud_name} -y')
