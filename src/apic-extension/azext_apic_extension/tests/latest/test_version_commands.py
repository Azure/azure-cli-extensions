# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicVersionPreparer

class VersionCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_version_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api version create -g {rg} -s {s} --api-id {api} --version-id {name} --lifecycle-stage production --title "v1.0.0"', checks=[
            self.check('lifecycleStage', 'production'),
            self.check('name', '{name}'),
            self.check('title', 'v1.0.0'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_version_show(self):
        self.cmd('az apic api version show -g {rg} -s {s} --api-id {api} --version-id {v}', checks=[
            self.check('lifecycleStage', 'production'),
            self.check('title', 'v1.0.0'),
            self.check('name', '{v}'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer(parameter_name='version_id1')
    @ApicVersionPreparer(parameter_name='version_id2')
    def test_version_list(self, version_id1, version_id2):
        self.cmd('az apic api version list -g {rg} -s {s} --api-id {api}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', version_id1),
            self.check('@[1].name', version_id2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_version_update(self):
        self.cmd('az apic api version update -g {rg} -s {s} --api-id {api} --version-id {v} --title "v1.0.1"', checks=[
            self.check('title', 'v1.0.1'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_version_delete(self):
        self.cmd('az apic api version delete -g {rg} -s {s} --api-id {api} --version-id {v} --yes')