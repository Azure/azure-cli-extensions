# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicEnvironmentPreparer

class EnvironmentCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_environment_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic environment create -g {rg} -s {s} --environment-id {name} --title "test environment" --type testing', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'testing'),
            self.check('title', 'test environment'),
            self.check('customProperties', '{{}}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_environment_show(self):
        self.cmd('az apic environment show -g {rg} -s {s} --environment-id {e}', checks=[
            self.check('name', '{e}'),
            self.check('kind', 'testing'),
            self.check('title', 'test environment'),
            self.check('customProperties', '{{}}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer(parameter_name='environment_name1')
    @ApicEnvironmentPreparer(parameter_name='environment_name2')
    def test_environment_list(self, environment_name1, environment_name2):
        self.cmd('az apic environment list -g {rg} -s {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', environment_name1),
            self.check('@[1].name', environment_name2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_environment_update(self):
        self.cmd('az apic environment update -g {rg} -s {s} --environment-id {e} --title "test environment 2"', checks=[
            self.check('title', 'test environment 2')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_environment_delete(self):
        self.cmd('az apic environment delete -g {rg} -s {s} --environment-id {e} --yes')