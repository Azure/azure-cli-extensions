# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicMetadataPreparer
from .constants import TEST_REGION

class ApiCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_api_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api create -g {rg} -n {s} --api-id {name} --title "Echo API" --type rest', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
            self.check('customProperties', {}),
            self.check('contacts', []),
            self.check('externalDocumentation', [])
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_api_create_with_all_optional_params(self, metadata_name):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'contacts': '[{email:contact@example.com,name:test,url:example.com}]',
            'customProperties': '{{"{}":true}}'.format(metadata_name),
            'externalDocumentation': '[{title:\'onboarding docs\',url:example.com}]',
            'license': '{url:example.com}',
        })
        self.cmd('az apic api create -g {rg} -n {s} --api-id {name} --title "test api" --type rest --contacts "{contacts}" --custom-properties \'{customProperties}\' --description "API description" --external-documentation "{externalDocumentation}" --license "{license}" --summary "summary"', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'rest'),
            self.check('title', 'test api'),
            self.check('contacts', [{"email":"contact@example.com","name":"test","url":"example.com"}]),
            self.check('customProperties.{}'.format(metadata_name), True),
            self.check('description', 'API description'),
            self.check('externalDocumentation', [{"title":"onboarding docs","url":"example.com"}]),
            self.check('license', {"url":"example.com"}),
            self.check('summary', 'summary')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_api_show(self):
        self.cmd('az apic api show -g {rg} -n {s} --api-id {api}', checks=[
            self.check('name', '{api}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
            self.check('customProperties', {}),
            self.check('contacts', []),
            self.check('externalDocumentation', [])
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer(parameter_name='api_id1')
    @ApicApiPreparer(parameter_name='api_id2')
    def test_api_list(self, api_id1, api_id2):
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', api_id1),
            self.check('@[1].name', api_id2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer(parameter_name='api_id1')
    @ApicApiPreparer(parameter_name='api_id2')
    def test_api_list_with_all_optional_params(self, api_id1):
        self.kwargs.update({
          'api_id': api_id1
        })
        self.cmd('az apic api list -g {rg} -n {s} --filter "name eq \'{api_id}\'"', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', api_id1),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_api_update(self):
        self.cmd('az apic api update -g {rg} -n {s} --api-id {api} --title "Echo API 2"', checks=[
            self.check('title', 'Echo API 2'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicMetadataPreparer()
    def test_api_update_with_all_optional_params(self, metadata_name):
        self.kwargs.update({
            'contacts': '[{email:contact@example.com,name:test,url:example.com}]',
            'customProperties': '{{"{}":true}}'.format(metadata_name),
            'externalDocumentation': '[{title:\'onboarding docs\',url:example.com}]',
            'license': '{url:example.com}',
        })
        self.cmd('az apic api update -g {rg} -n {s} --api-id {api} --title "test api 2" --type rest --contacts "{contacts}" --custom-properties \'{customProperties}\' --description "API description" --external-documentation "{externalDocumentation}" --license "{license}" --summary "summary"', checks=[
            self.check('kind', 'rest'),
            self.check('title', 'test api 2'),
            self.check('contacts', [{"email":"contact@example.com","name":"test","url":"example.com"}]),
            self.check('customProperties.{}'.format(metadata_name), True),
            self.check('description', 'API description'),
            self.check('externalDocumentation', [{"title":"onboarding docs","url":"example.com"}]),
            self.check('license', {"url":"example.com"}),
            self.check('summary', 'summary')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_api_delete(self):
        self.cmd('az apic api delete -g {rg} -n {s} --api-id {api} --yes')
        self.cmd('az apic api show -g {rg} -n {s} --api-id {api}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_create_api(self):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api create -g {rg} -n {s} --api-id {name} --title "Echo API" --type REST', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_create_api_with_custom_properties(self, metadata_name):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'customProperties': '{{"{}":true}}'.format(metadata_name),
        })
        self.cmd('az apic api create -g {rg} -n {s} --api-id {name} --title "Echo API" --type rest --custom-properties \'{customProperties}\'', checks=[
            self.check('name', '{name}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
            self.check('customProperties.{}'.format(metadata_name), True),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_examples_delete_api(self):
        self.cmd('az apic api delete -g {rg} -n {s} --api-id {api} --yes')
        self.cmd('az apic api show -g {rg} -n {s} --api-id {api}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer(parameter_name='api_id1')
    @ApicApiPreparer(parameter_name='api_id2')
    def test_examples_list_apis(self, api_id1, api_id2):
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', api_id1),
            self.check('@[1].name', api_id2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_examples_show_api_details(self):
        self.cmd('az apic api show -g {rg} -n {s} --api-id {api}', checks=[
            self.check('name', '{api}'),
            self.check('kind', 'rest'),
            self.check('title', 'Echo API'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    def test_examples_update_api(self):
        self.cmd('az apic api update -g {rg} -n {s} --api-id {api} --summary "Basic REST API service"', checks=[
            self.check('summary', 'Basic REST API service'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicMetadataPreparer()
    def test_examples_update_custom_properties(self, metadata_name):
        self.kwargs.update({
            'customProperties': '{{"{}":true}}'.format(metadata_name),
        })
        self.cmd('az apic api update -g {rg} -n {s} --api-id {api} --custom-properties \'{customProperties}\'', checks=[
            self.check('customProperties.{}'.format(metadata_name), True),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer(parameter_name='api_id1')
    @ApicApiPreparer(parameter_name='api_id2')
    def test_examples_list_apis_with_filter(self, api_id1, api_id2):
        self.cmd('az apic api list -g {rg} -n {s} --filter "kind eq \'rest\'"', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', api_id1),
            self.check('@[1].name', api_id2)
        ])