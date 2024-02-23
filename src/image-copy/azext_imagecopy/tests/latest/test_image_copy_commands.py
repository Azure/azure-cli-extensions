# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only
from azure.cli.testsdk.constants import AUX_SUBSCRIPTION


class ImageCopyTests(ScenarioTest):

    @live_only()
    @ResourceGroupPreparer(name_prefix='cli_test_image_copy_', location='westus')
    def test_image_copy(self, resource_group):
        self.kwargs.update({
            'temporary_rg': self.create_random_name(prefix='cli_test_image_copy_tmp_', length=30),
            'rg2': self.create_random_name(prefix='cli_test_image_copy_', length=30),
            'vm': 'vm1',
            'image': 'image1',
            'hyperVGeneration': 'V2',
            'subscription2': AUX_SUBSCRIPTION,
        })

        self.cmd('vm create -g {rg} -n {vm} --image canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:latest'
                 ' --admin-username clitest1 --generate-ssh-key')
        self.cmd('vm run-command invoke -g {rg} -n {vm} --command-id RunShellScript --scripts '
                 '"echo \'sudo waagent -deprovision+user --force\' | at -M now + 1 minutes"')
        time.sleep(70)
        self.cmd('vm deallocate -g {rg} -n {vm}')
        self.cmd('vm generalize -g {rg} -n {vm}')
        self.cmd('image create -g {rg} -n {image} --source {vm} --hyper-v-generation {hyperVGeneration}')
        self.cmd('group create -g {rg2} -l eastus')
        self.cmd('image copy --source-object-name {image} --source-resource-group {rg} --target-location eastus '
                 '--target-resource-group {rg2} --target-name {image} --target-subscription {subscription2} '
                 '--temporary-resource-group-name {temporary_rg} --cleanup --only-show-errors')
        self.cmd('image show -g {rg2} -n {image} --subscription {subscription2}', checks=[
            self.check('name', '{image}'),
            self.check('hyperVGeneration', '{hyperVGeneration}'),
        ])

    # the recoding file does not contain the image copy command, so that this test have to be run in live mode
    @live_only()
    @ResourceGroupPreparer(name_prefix='cli_test_image_copy_loc_', location='westus')
    def test_image_copy_locations(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'image': 'image1',
            'rg2': self.create_random_name(prefix='cli_test_image_copy_loc2_', length=30),
            'loc1': 'southeastasia',
            'loc2': 'australiaeast',
        })

        self.cmd('vm create -g {rg} -n {vm} --admin-username theuser --image OpenLogic:CentOS:7.5:latest --admin-password testPassword0 '
                 '--authentication-type password --nsg-rule NONE')
        time.sleep(70)
        self.cmd('vm deallocate -g {rg} -n {vm}')
        self.cmd('vm generalize -g {rg} -n {vm}')
        self.cmd('image create -g {rg} -n {image} --source {vm}')

        self.cmd('image copy --source-resource-group {rg} --source-object-name {image} --target-location '
                 '{loc1} {loc2} --target-resource-group {rg2} --cleanup --only-show-errors')

        self.kwargs['image_copied_loc1'] = self.kwargs['image'] + '-' + self.kwargs['loc1']
        self.kwargs['image_copied_loc2'] = self.kwargs['image'] + '-' + self.kwargs['loc2']
        self.cmd('image show -g {rg2} -n {image_copied_loc1}', checks=[
            self.check('name', '{image_copied_loc1}')
        ])
        self.cmd('image show -g {rg2} -n {image_copied_loc2}', checks=[
            self.check('name', '{image_copied_loc2}')
        ])
