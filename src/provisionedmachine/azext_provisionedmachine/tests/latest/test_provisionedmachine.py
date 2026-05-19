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
