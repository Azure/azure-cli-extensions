# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import *


class HealthModelScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_crud', location='centralus')
    def test_healthmodel_crud_cycle(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'model': self.create_random_name('clihm', 24),
            'entity': self.create_random_name('client', 24),
            'location': 'centralus',
        })

        self.cmd('monitor health-models create -g {rg} -n {model} -l {location}', checks=[
            self.check('name', '{model}'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('location', '{location}')
        ])
        self.cmd('monitor health-models show -g {rg} -n {model}', checks=[
            self.check('name', '{model}')
        ])
        self.cmd('monitor health-models update -g {rg} -n {model} --tags env=test owner=cli', checks=[
            self.check('tags.env', 'test'),
            self.check('tags.owner', 'cli')
        ])
        self.cmd('monitor health-models list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{model}')
        ])

        self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} -n {entity} '
                 '--display-name "CLI Test Entity" --impact Standard', checks=[
            self.check('name', '{entity}'),
            self.check('properties.displayName', 'CLI Test Entity'),
            self.check('properties.impact', 'Standard')
        ])
        self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} -n {entity}', checks=[
            self.check('name', '{entity}')
        ])
        self.cmd('monitor health-models entity list -g {rg} --health-model-name {model}', checks=[
            self.greater_than('length(@)', 0)
        ])
        self.cmd('monitor health-models entity delete -g {rg} --health-model-name {model} -n {entity} --yes')

        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')

    def test_healthmodel_list_recorded(self):
        self.cmd('monitor health-models list', checks=[self.check('type(@)', 'array')])
