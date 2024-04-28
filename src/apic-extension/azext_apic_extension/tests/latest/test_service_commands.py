# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer

class ServiceCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    def test_create_service(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic service create -g {rg} --name {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_show_service(self):
        self.cmd('az apic service show -g {rg} -s {s}', checks=[
            self.check('name', '{s}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_update_service(self):
        self.cmd('az apic service update -g {rg} -s {s} --tags "{{test:value}}"', checks=[
            self.check('tags.test', 'value')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_delete_service(self):
        self.cmd('az apic service delete -g {rg} -s {s}a --yes')