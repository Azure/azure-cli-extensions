# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer

class ApiCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_api_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api create -g {rg} -s {s} --api-id {name} --title "Echo API" --type rest', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
            self.check('customProperties', {}),
            self.check('contacts', []),
            self.check('externalDocumentation', [])
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_api_show(self):
        self.cmd('az apic api show -g {rg} -s {s} --api-id {api}', checks=[
            self.check('name', '{api}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
            self.check('customProperties', {}),
            self.check('contacts', []),
            self.check('externalDocumentation', [])
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer(parameter_name='api_id1')
    @ApicApiPreparer(parameter_name='api_id2')
    def test_api_list(self, api_id1, api_id2):
        self.cmd('az apic api list -g {rg} -s {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', api_id1),
            self.check('@[1].name', api_id2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_api_update(self):
        self.cmd('az apic api update -g {rg} -s {s} --api-id {api} --title "Echo API 2"', checks=[
            self.check('title', 'Echo API 2'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_api_delete(self):
        self.cmd('az apic api delete -g {rg} -s {s} --api-id {api} --yes')