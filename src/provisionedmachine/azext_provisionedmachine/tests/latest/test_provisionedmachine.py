# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class ProvisionedMachineTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_provisionedmachine')
    def test_provisionedmachine_list_by_rg(self, resource_group):
        """Test listing edge machines by resource group."""
        self.cmd(
            'az provisionedmachine list -g {rg}',
            checks=[
                self.check('type(@)', 'array'),
            ]
        )

    def test_provisionedmachine_list_by_subscription(self):
        """Test listing edge machines by subscription."""
        self.cmd(
            'az provisionedmachine list',
            checks=[
                self.check('type(@)', 'array'),
            ]
        )

    @ResourceGroupPreparer(name_prefix='cli_test_provisionedmachine')
    def test_provisionedmachine_show_status(self, resource_group):
        """Test showing lifecycle status of a provisioned machine."""
        self.kwargs.update({
            'name': self.create_random_name('pm-', 10),
        })

        # show-status on a non-existent machine should fail
        with self.assertRaises(Exception):
            self.cmd('az provisionedmachine show-status -n {name} -g {rg}')

    def test_provisionedmachine_os_image_list(self):
        """Test listing OS images with default location (eastus)."""
        self.cmd(
            'az provisionedmachine os-image list --os-image-type HCI',
            checks=[
                self.check('type(@)', 'array'),
            ]
        )

    def test_provisionedmachine_os_image_list_azurelinux(self):
        """Test listing AzureLinux OS images with explicit location."""
        self.cmd(
            'az provisionedmachine os-image list --location eastus --os-image-type AzureLinux',
            checks=[
                self.check('type(@)', 'array'),
            ]
        )

    @ResourceGroupPreparer(name_prefix='cli_test_provisionedmachine')
    def test_provisionedmachine_install_os_missing_auth(self, resource_group):
        """Test install-os fails with missing auth args (fast fail before network calls)."""
        self.kwargs.update({
            'name': self.create_random_name('pm-', 10),
        })

        # AzureLinux without ssh-public-key should fail
        with self.assertRaises(Exception):
            self.cmd('az provisionedmachine install-os -g {rg} -n {name} --os-image-type AzureLinux')

        # HCI without key-vault-secret-id should fail
        with self.assertRaises(Exception):
            self.cmd('az provisionedmachine install-os -g {rg} -n {name} --os-image-type HCI')
