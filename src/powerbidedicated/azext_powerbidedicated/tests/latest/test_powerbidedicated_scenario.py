# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, record_only)


class PowerBIDedicatedScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_powerbidedicated')
    def test_powerbidedicated_embedded_capacity(self, resource_group):
        self.kwargs.update({
            'name': self.create_random_name(prefix='clipowerbi', length=24),
            'administrator': "4759ce24-1955-4c57-bc53-357a69cc065f",
            'location': "eastus"
        })

        self.cmd('az powerbi embedded-capacity create --resource-group {rg} --name {name} --sku-name "A1" '
                 '--location {location} --sku-tier "PBIE_Azure" --administration-members "{administrator}" --no-wait')

        self.cmd('az powerbi embedded-capacity wait --resource-group {rg} --name {name} --created')

        self.cmd('az powerbi embedded-capacity list --resource-group {rg}',
                 checks=[
                     self.check('length(@)', 1),
                 ])

        self.cmd('az powerbi embedded-capacity show -g {rg} --name {name}',
                 checks=[
                     self.check('provisioningState', 'Succeeded'),
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A1'),
                     self.check('sku.tier', 'PBIE_Azure'),
                     self.check('administration.members[0]', self.kwargs['administrator']),
                 ])

        self.cmd('az powerbi embedded-capacity update --resource-group {rg} --name {name} --sku-name "A2"',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A2'),
                 ])

        self.cmd('az powerbi embedded-capacity show -g {rg} -n {name}',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('sku.name', 'A2'),
                 ])

        self.cmd('az powerbi embedded-capacity delete -g {rg} -n {name} -y')

        self.cmd('az powerbi embedded-capacity list -g {rg}',
                 checks=[
                     self.check('length(@)', 0)])
