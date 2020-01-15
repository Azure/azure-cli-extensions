# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, live_only


class ImageCopyTests(ScenarioTest):

    @live_only()
    @ResourceGroupPreparer(name_prefix='cli_test_image_copy_', location='westus')
    def test_image_copy(self, resource_group):
        self.kwargs.update({
            'vm': 'vm1',
            'image': 'image1',
            'rg2': self.create_random_name(prefix='cli_test_image_copy_', length=30)
        })

        self.cmd('vm create -g {rg} -n {vm} --image ubuntults --admin-username clitest1 --generate-ssh-key')
        self.cmd('vm run-command invoke -g {rg} -n {vm} --command-id RunShellScript --scripts '
                 '"echo \'sudo waagent -deprovision+user --force\' | at -M now + 1 minutes"')
        time.sleep(70)
        self.cmd('vm deallocate -g {rg} -n {vm}')
        self.cmd('vm generalize -g {rg} -n {vm}')
        self.cmd('image create -g {rg} -n {image} --source {vm}')
        self.cmd('group create -g {rg2} -l eastus')
        self.cmd('image copy --source-object-name {image} --source-resource-group {rg} '
                 '--target-location eastus --target-resource-group {rg2} --target-name {image}')
        self.cmd('image show -g {rg2} -n {image}', checks=[self.check('name', '{image}')])
