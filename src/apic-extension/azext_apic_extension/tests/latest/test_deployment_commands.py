# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicVersionPreparer, ApicDefinitionPreparer, ApicEnvironmentPreparer, ApicDeploymentPreparer

class DeploymentCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_deployment_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'server': '{"runtimeUri":["https://example.com"]}',
        })
        self.cmd('az apic api deployment create -g {rg} -s {s} --api-id {api} --definition-id /workspaces/default/apis/{api}/versions/{v}/definitions/{d} --environment-id /workspaces/default/environments/{e} --deployment-id {name} --title "test deployment" --server \'{server}\'', checks=[
            self.check('name', '{name}'),
            self.check('title', 'test deployment'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
            self.check('customProperties', {}),
            self.check('definitionId', '/workspaces/default/apis/{api}/versions/{v}/definitions/{d}'),
            self.check('environmentId', '/workspaces/default/environments/{e}'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_deployment_show(self):
        self.cmd('az apic api deployment show -g {rg} -s {s} --api-id {api} --deployment-id {dep}', checks=[
            self.check('name', '{dep}'),
            self.check('title', 'test deployment'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
            self.check('customProperties', {}),
            self.check('definitionId', '/workspaces/default/apis/{api}/versions/{v}/definitions/{d}'),
            self.check('environmentId', '/workspaces/default/environments/{e}'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer(parameter_name='deployment_id1')
    @ApicDeploymentPreparer(parameter_name='deployment_id2')
    def test_deployment_list(self, deployment_id1, deployment_id2):
        self.cmd('az apic api deployment list -g {rg} -s {s} --api-id {api}', checks=[
            self.check('length(@)', 2),
            self.check('[0].name', deployment_id1),
            self.check('[1].name', deployment_id2),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_deployment_update(self):
        self.cmd('az apic api deployment update -g {rg} -s {s} --api-id {api} --deployment-id {dep} --title "updated deployment"', checks=[
            self.check('title', 'updated deployment'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_deployment_delete(self):
        self.cmd('az apic api deployment delete -g {rg} -s {s} --api-id {api} --deployment-id {dep} --yes')
        self.cmd('az apic api deployment show -g {rg} -s {s} --api-id {api} --deployment-id {dep}', expect_failure=True)