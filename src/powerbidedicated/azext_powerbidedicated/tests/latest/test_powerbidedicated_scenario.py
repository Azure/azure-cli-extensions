# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


class PowerBIDedicatedScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_powerbidedicated')
    def test_powerbidedicated(self, resource_group):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli_powerbi', length=24),
        })

        self.cmd('az powerbi embedded-capacity create '
                 '--resource-group {rg} '
                 '--name {name} '
                 '--sku-name "A1" '
                 '--sku-tier "PBIE_Azure" '
                 '--administration-members "azsdktest@microsoft.com,azsdktest2@microsoft.com"',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A1'),
                     self.check('sku.tier', 'PBIE_Azure'),
                     self.check('administration.members[0]', 'PBIE_Azure'),
                 ])

        self.cmd('az powerbi embedded-capacity list --resource-group {rg}',
                 checks=[
                     self.check('length(@)', 1),
                 ])

        self.cmd('az powerbi embedded-capacity show',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A1'),
                     self.check('sku.tier', 'PBIE_Azure'),
                     self.check('administration.members[0]', 'PBIE_Azure'),
                 ])

        self.cmd('az powerbi embedded-capacity update '
                 '--resource-group {rg} '
                 '--name {name} '
                 '--sku-name "A2" ',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A2'),
                 ])

        self.cmd('az powerbi embedded-capacity show',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A2'),
                 ])

        self.cmd('az powerbi embedded-capacity delete',
                 checks=[])

        self.cmd('az powerbi embedded-capacity list -g {rg}',
                 checks=[])
