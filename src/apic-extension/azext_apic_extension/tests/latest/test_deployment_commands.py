# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicVersionPreparer, ApicDefinitionPreparer, ApicEnvironmentPreparer, ApicDeploymentPreparer, ApicMetadataPreparer
from .constants import TEST_REGION

class DeploymentCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
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
        self.cmd('az apic api deployment create -g {rg} -n {s} --api-id {api} --definition-id /workspaces/default/apis/{api}/versions/{v}/definitions/{d} --environment-id /workspaces/default/environments/{e} --deployment-id {name} --title "test deployment" --server \'{server}\'', checks=[
            self.check('name', '{name}'),
            self.check('title', 'test deployment'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
            self.check('customProperties', {}),
            self.check('definitionId', '/workspaces/default/apis/{api}/versions/{v}/definitions/{d}'),
            self.check('environmentId', '/workspaces/default/environments/{e}'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicMetadataPreparer()
    def test_deployment_create_with_all_optional_params(self, metadata_name):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'server': '{"runtimeUri":["https://example.com"]}',
          'customProperties': '{{"{}":true}}'.format(metadata_name),
        })
        self.cmd('az apic api deployment create -g {rg} -n {s} --api-id {api} --definition-id /workspaces/default/apis/{api}/versions/{v}/definitions/{d} --environment-id /workspaces/default/environments/{e} --deployment-id {name} --title "test deployment" --server \'{server}\' --description "deployment description" --custom-properties \'{customProperties}\'', checks=[
            self.check('name', '{name}'),
            self.check('title', 'test deployment'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
            self.check('customProperties.{}'.format(metadata_name), True),
            self.check('definitionId', '/workspaces/default/apis/{api}/versions/{v}/definitions/{d}'),
            self.check('environmentId', '/workspaces/default/environments/{e}'),
            self.check('description', 'deployment description'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_deployment_show(self):
        self.cmd('az apic api deployment show -g {rg} -n {s} --api-id {api} --deployment-id {dep}', checks=[
            self.check('name', '{dep}'),
            self.check('title', 'test deployment'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
            self.check('customProperties', {}),
            self.check('definitionId', '/workspaces/default/apis/{api}/versions/{v}/definitions/{d}'),
            self.check('environmentId', '/workspaces/default/environments/{e}'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer(parameter_name='deployment_id1')
    @ApicDeploymentPreparer(parameter_name='deployment_id2')
    def test_deployment_list(self, deployment_id1, deployment_id2):
        self.cmd('az apic api deployment list -g {rg} -n {s} --api-id {api}', checks=[
            self.check('length(@)', 2),
            self.check('[0].name', deployment_id1),
            self.check('[1].name', deployment_id2),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer(parameter_name='deployment_id1')
    @ApicDeploymentPreparer(parameter_name='deployment_id2')
    def test_deployment_list_with_all_optional_params(self, deployment_id1):
        self.kwargs.update({
          'deployment_id': deployment_id1
        })
        self.cmd('az apic api deployment list -g {rg} -n {s} --api-id {api} --filter "name eq \'{deployment_id}\'"', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', deployment_id1)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_deployment_update(self):
        self.cmd('az apic api deployment update -g {rg} -n {s} --api-id {api} --deployment-id {dep} --title "updated deployment"', checks=[
            self.check('title', 'updated deployment'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    @ApicMetadataPreparer()
    def test_deployment_update_with_all_optional_params(self, metadata_name):
        self.kwargs.update({
          'server': '{"runtimeUri":["https://example2.com"]}',
          'customProperties': '{{"{}":true}}'.format(metadata_name),
        })
        self.cmd('az apic api deployment update -g {rg} -n {s} --api-id {api} --definition-id /workspaces/default/apis/{api}/versions/{v}/definitions/{d} --environment-id /workspaces/default/environments/{e} --deployment-id {dep} --title "updated deployment" --server \'{server}\' --description "deployment description" --custom-properties \'{customProperties}\'', checks=[
            self.check('title', 'updated deployment'),
            self.check('server.runtimeUri[0]', 'https://example2.com'),
            self.check('customProperties.{}'.format(metadata_name), True),
            self.check('definitionId', '/workspaces/default/apis/{api}/versions/{v}/definitions/{d}'),
            self.check('environmentId', '/workspaces/default/environments/{e}'),
            self.check('description', 'deployment description'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_deployment_delete(self):
        self.cmd('az apic api deployment delete -g {rg} -n {s} --api-id {api} --deployment-id {dep} --yes')
        self.cmd('az apic api deployment show -g {rg} -n {s} --api-id {api} --deployment-id {dep}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_create_deployment(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'server': '{"runtimeUri":["https://example.com"]}',
        })
        self.cmd('az apic api deployment create -g {rg} -n {s} --deployment-id {name} --title "Production deployment" --description "Public cloud production deployment." --api-id {api} --environment-id "/workspaces/default/environments/{e}" --definition-id "/workspaces/default/apis/{api}/versions/{v}/definitions/{d}" --server \'{server}\'', checks=[
            self.check('name', '{name}'),
            self.check('title', 'Production deployment'),
            self.check('description', 'Public cloud production deployment.'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_examples_delete_api_deployment(self):
        self.cmd('az apic api deployment delete -g {rg} -n {s} --deployment-id {dep} --api-id {api} --yes')
        self.cmd('az apic api deployment show -g {rg} -n {s} --api-id {api} --deployment-id {dep}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer(parameter_name='deployment_id1')
    @ApicDeploymentPreparer(parameter_name='deployment_id2')
    def test_examples_list_api_deployments(self, deployment_id1, deployment_id2):
        self.cmd('az apic api deployment list -g {rg} -n {s} --api-id {api}', checks=[
            self.check('length(@)', 2),
            self.check('[0].name', deployment_id1),
            self.check('[1].name', deployment_id2),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_examples_show_api_deployment_details(self):
        self.cmd('az apic api deployment show -g {rg} -n {s} --deployment-id {dep} --api-id {api}', checks=[
            self.check('name', '{dep}'),
            self.check('title', 'test deployment'),
            self.check('server.runtimeUri[0]', 'https://example.com'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    @ApicDeploymentPreparer()
    def test_examples_update_api_deployment(self):
        self.cmd('az apic api deployment update -g {rg} -n {s} --deployment-id {dep} --title "Production deployment" --api-id {api}', checks=[
            self.check('title', 'Production deployment'),
        ])