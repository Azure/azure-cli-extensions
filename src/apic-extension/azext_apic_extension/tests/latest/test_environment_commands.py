# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicEnvironmentPreparer, ApicMetadataPreparer
from .constants import TEST_REGION

class EnvironmentCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_environment_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic environment create -g {rg} -n {s} --environment-id {name} --title "test environment" --type testing', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'testing'),
            self.check('title', 'test environment'),
            self.check('customProperties', '{{}}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_environment_create_with_all_optional_params(self, metadata_name):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'custom_properties': '{{"{}":true}}'.format(metadata_name),
          'onboarding': "{developerPortalUri:['https://developer.contoso.com'],instructions:'instructions markdown'}",
          'server': "{type:'Azure API Management',managementPortalUri:['example.com']}"
        })
        self.cmd('az apic environment create -g {rg} -n {s} --environment-id {name} --title "test environment" --type testing --custom-properties \'{custom_properties}\' --description "environment description" --onboarding "{onboarding}" --server "{server}"', checks=[
            self.check('customProperties.{}'.format(metadata_name), True),
            self.check('description', 'environment description'),
            self.check('kind', 'testing'),
            self.check('name', '{name}'),
            self.check('onboarding.developerPortalUri[0]', 'https://developer.contoso.com'),
            self.check('onboarding.instructions', 'instructions markdown'),
            self.check('server.managementPortalUri[0]', 'example.com'),
            self.check('server.type', 'Azure API Management'),
            self.check('title', 'test environment'),
            self.check('type', 'Microsoft.ApiCenter/services/workspaces/environments')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_environment_show(self):
        self.cmd('az apic environment show -g {rg} -n {s} --environment-id {e}', checks=[
            self.check('name', '{e}'),
            self.check('kind', 'testing'),
            self.check('title', 'test environment'),
            self.check('customProperties', '{{}}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer(parameter_name='environment_name1')
    @ApicEnvironmentPreparer(parameter_name='environment_name2')
    def test_environment_list(self, environment_name1, environment_name2):
        self.cmd('az apic environment list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', environment_name1),
            self.check('@[1].name', environment_name2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer(parameter_name='environment_name1')
    @ApicEnvironmentPreparer(parameter_name='environment_name2')
    def test_environment_list_with_all_optional_params(self, environment_name1):
        self.kwargs.update({
         'environment_name': environment_name1
       })
        self.cmd('az apic environment list -g {rg} -n {s} --filter "name eq \'{environment_name}\'"', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', environment_name1)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_environment_update(self):
        self.cmd('az apic environment update -g {rg} -n {s} --environment-id {e} --title "test environment 2"', checks=[
            self.check('title', 'test environment 2')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    @ApicEnvironmentPreparer()
    def test_environment_update_with_all_optional_params(self, metadata_name):
        self.kwargs.update({
          'custom_properties': '{{"{}":true}}'.format(metadata_name),
          'onboarding': "{developerPortalUri:['https://developer.contoso.com'],instructions:'instructions markdown'}",
          'server': "{type:'Azure API Management',managementPortalUri:['example.com']}"
        })
        self.cmd('az apic environment update -g {rg} -n {s} --environment-id {e} --title "test environment 2" --type testing --custom-properties \'{custom_properties}\' --description "environment description" --onboarding "{onboarding}" --server "{server}"', checks=[
            self.check('customProperties.{}'.format(metadata_name), True),
            self.check('description', 'environment description'),
            self.check('kind', 'testing'),
            self.check('onboarding.developerPortalUri[0]', 'https://developer.contoso.com'),
            self.check('onboarding.instructions', 'instructions markdown'),
            self.check('server.managementPortalUri[0]', 'example.com'),
            self.check('server.type', 'Azure API Management'),
            self.check('title', 'test environment 2'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_environment_delete(self):
        self.cmd('az apic environment delete -g {rg} -n {s} --environment-id {e} --yes')
        self.cmd('az apic environment show -g {rg} -n {s} --environment-id {e}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_create_environment(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic environment create -g {rg} -n {s} --environment-id {name} --title "Public cloud" --type "development"', checks=[
            self.check('name', '{name}'),
            self.check('title', 'Public cloud'),
            self.check('kind', 'development')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_examples_delete_environment(self):
        self.cmd('az apic environment delete -g {rg} -n {s} --environment-id {e} --yes')
        self.cmd('az apic environment show -g {rg} -n {s} --environment-id {e}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer(parameter_name='environment_name1')
    @ApicEnvironmentPreparer(parameter_name='environment_name2')
    def test_examples_list_environments(self, environment_name1, environment_name2):
        self.cmd('az apic environment list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', environment_name1),
            self.check('@[1].name', environment_name2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_examples_show_environment_details(self):
        self.cmd('az apic environment show -g {rg} -n {s} --environment-id {e}', checks=[
            self.check('name', '{e}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicEnvironmentPreparer()
    def test_examples_update_environment(self):
        self.cmd('az apic environment update -g {rg} -n {s} --environment-id {e} --title "Public cloud"', checks=[
            self.check('title', 'Public cloud')
        ])
