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
                'resource_group': 'aadk8test',
                'location': 'eastus2euap',
                'custom_location': 'arcvmm-azcli-test-cl',
                'vmmserver_name': 'arcvmm-azcli-test-vmmserver',
                'icloud_name': 'sojilani',
                'icloud_uuid': 'ca912988-afcf-4c2e-b3c1-b1ddc8392f6b',
                'cloud_name': 'arcvmm-azcli-test-sojilani',
                'ivmt_name': 'vmt-win',
                'ivmt_uuid': '97df5464-106e-4f82-8508-1ac3767adde6',
                'vmt_name': 'arcvmm-azcli-test-vmt-win',
                'ivnet_name': 'vnet-562',
                'ivnet_uuid': 'a6f9432f-23d7-4124-9887-11c3ab173463',
                'vnet_name': 'arcvmm-azcli-test-vnet-562',
                'avset_string': 'avset1',
                'avset_name': 'arcvmm-azcli-test-avset1',
                'vm_name': 'arcvmm-azcli-test-vm-1',
                'disk_name': 'disk_1',
                'nic_name': 'nic_1',
                'checkpoint_name': 'arcvmm-azcli-checkpoint',
                'checkpoint_description': 'arcvmm-azcli-checkpoint',
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
            'az scvmm vm update -g {resource_group} -n {vm_name}'
            ' --cpu-count 2 --dynamic-memory-enabled true --tags client=azcli',
            checks=[
                self.check('provisioningState', 'Succeeded'),
                self.check('hardwareProfile.cpuCount', 2),
                self.check('hardwareProfile.dynamicMemoryEnabled', 'true'),
                self.check('tags.client', 'azcli'),
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
            'az scvmm vm stop -g {resource_group} --name {vm_name} --skip-shutdown'
        )

        self.cmd(
            'az scvmm vm create-checkpoint -g {resource_group} --name {vm_name} --checkpoint-name {checkpoint_name} --checkpoint-description {checkpoint_description}',
        )
        alias_sub = self.cmd('az scvmm vm show -g {resource_group} --name {vm_name}',
                             checks=[
                                 self.check('provisioningState', 'Succeeded'),
                                 self.greater_than('checkpoints | length(@)', 0),                                
                             ]).get_output_in_json()
        checkpoint_id = alias_sub['checkpoints'][0]['checkpointId']
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
                self.check('checkpoints | length(@)', 0),                           
            ]
        )

        self.cmd('az scvmm vm delete -g {resource_group} --name {vm_name} --deleteFromHost -y')

        self.cmd('az scvmm avset delete -g {resource_group} --name {avset_name} -y')

        self.cmd(
            'az scvmm virtual-network delete -g {resource_group} --name {vnet_name} -y'
        )

        self.cmd('az scvmm vm-template delete -g {resource_group} --name {vmt_name} -y')

        self.cmd('az scvmm cloud delete -g {resource_group} --name {cloud_name} -y')
