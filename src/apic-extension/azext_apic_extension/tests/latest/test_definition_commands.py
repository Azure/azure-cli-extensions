# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import requests
import json
import os

from knack.util import CLIError
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicVersionPreparer, ApicDefinitionPreparer
from .constants import TEST_REGION

current_dir = os.path.dirname(os.path.realpath(__file__))
test_assets_dir = os.path.join(current_dir, 'test_assets')

class DefinitionCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_definition_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api definition create -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {name} --title "OpenAPI"', checks=[
            self.check('name', '{name}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_definition_create_with_all_optional_params(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api definition create -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {name} --title "OpenAPI" --description "test description"', checks=[
            self.check('name', '{name}'),
            self.check('title', 'OpenAPI'),
            self.check('description', 'test description'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_show(self):
        self.cmd('az apic api definition show -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d}', checks=[
            self.check('name', '{d}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer(parameter_name="definition_id1")
    @ApicDefinitionPreparer(parameter_name="definition_id2")
    def test_definition_list(self, definition_id1, definition_id2):
        self.cmd('az apic api definition list -g {rg} -n {s} --api-id {api} --version-id {v}', checks=[
            self.check('length(@)', 2),
            self.check('[0].name', definition_id1),
            self.check('[1].name', definition_id2),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer(parameter_name="definition_id1")
    @ApicDefinitionPreparer(parameter_name="definition_id2")
    def test_definition_list_with_all_optional_params(self, definition_id1):
        self.kwargs.update({
          'definition_id': definition_id1
        })
        self.cmd('az apic api definition list -g {rg} -n {s} --api-id {api} --version-id {v} --filter "name eq \'{definition_id}\'"', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', definition_id1)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_update(self):
        self.cmd('az apic api definition update -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --title "Swagger" --description "test description 2"', checks=[
            self.check('name', '{d}'),
            self.check('title', 'Swagger'),
            self.check('description', 'test description 2'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_delete(self):
        self.cmd('az apic api definition delete -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --yes')
        self.cmd('az apic api definition show -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_import_export(self):
        self.kwargs.update({
          'filename': "test_definition_import_export.json",
          'spec_url': "https://petstore3.swagger.io/api/v3/openapi.json",
          'specification': '{"name":"openapi","version":"3.0.2"}'
        })

        self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "link" --specification \'{specification}\' --value "{spec_url}"')

        self.cmd('az apic api definition export-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {filename}')

        try:
            exported_file_path = self.kwargs['filename']
            with open(exported_file_path, 'r') as file:
                exported_content = json.load(file)

            # Get the content from the imported URL
            imported_url = self.kwargs['spec_url']
            response = requests.get(imported_url)
            imported_content = response.json()

            assert exported_content == imported_content, "The exported content is not the same as the imported content."
        finally:
            os.remove(exported_file_path)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_import_inline(self):
        self.kwargs.update({
        'filename': "test_definition_import_inline.json",
        'specification': '{"name":"openapi","version":"3.0.0"}',
        'value': '{"openapi":"3.0.1","info":{"title":"httpbin.org","description":"API Management facade for a very handy and free online HTTP tool.","version":"1.0"}}'
        })

        self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "inline" --specification \'{specification}\' --value \'{value}\'')

        self.cmd('az apic api definition export-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {filename}')

        try:
            exported_file_path = self.kwargs['filename']
            with open(exported_file_path, 'r') as file:
                exported_content = json.load(file)

            imported_content = json.loads(self.kwargs['value'])

            assert exported_content == imported_content, "The exported content is not the same as the imported content."
        finally:
            os.remove(exported_file_path)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_import_from_file(self):
        self.kwargs.update({
        'import_filename': os.path.join(test_assets_dir, 'petstore.json'),
        'export_filename': "test_definition_import_from_file.json",
        'specification': '{"name":"openapi","version":"3.0.0"}'
        })

        self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "inline" --specification \'{specification}\' --value "@{import_filename}"')

        self.cmd('az apic api definition export-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {export_filename}')

        try:
            exported_file_path = self.kwargs['export_filename']
            with open(exported_file_path, 'r') as file:
                exported_content = json.load(file)

            with open(self.kwargs['import_filename'], 'r') as file:
                imported_content = json.load(file)

            assert exported_content == imported_content, "The exported content is not the same as the imported content."
        finally:
            os.remove(exported_file_path)

    def test_definition_import_large_value(self):
        self.kwargs.update({
            'specification': '{"name":"openapi","version":"3.0.0"}',
            'file_name': "test_definition_import_large_value.txt",
            'rg': "mock_resource_group",
            's': 'mock-service-name',
            'api': 'mock-api-id',
            'v': 'mock-version-id',
            'd': 'mock-definition-id'
        })

        try:
            with open(self.kwargs['file_name'], 'w') as file:
                file.write('a' * 4 * 1024 * 1024) # generate a 4MB file

            with self.assertRaisesRegex(CLIError, 'The size of "value" is greater than 3 MB. Please use --format "link" to import the specification from a URL for size greater than 3 mb.') as cm:
                self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "inline" --specification \'{specification}\' --value "@{file_name}"')
        finally:
            os.remove(self.kwargs['file_name'])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_examples_create_api_definition(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api definition create -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {name} --title "OpenAPI"', checks=[
            self.check('name', '{name}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_delete_api_definition(self):
        self.cmd('az apic api definition delete -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --yes')
        self.cmd('az apic api definition show -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer(parameter_name="definition_id1")
    @ApicDefinitionPreparer(parameter_name="definition_id2")
    def test_examples_list_api_definitions(self, definition_id1, definition_id2):
        self.cmd('az apic api definition list -g {rg} -n {s} --api-id {api} --version-id {v}', checks=[
            self.check('length(@)', 2),
            self.check('[0].name', definition_id1),
            self.check('[1].name', definition_id2),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_show_api_definition_details(self):
        self.cmd('az apic api definition show -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d}', checks=[
            self.check('name', '{d}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_update_api_definition(self):
        self.cmd('az apic api definition update -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --title "OpenAPI"', checks=[
            self.check('name', '{d}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_import_specification_example_1(self):
        self.kwargs.update({
          'value': '{"openapi":"3.0.1","info":{"title":"httpbin.org","description":"API Management facade for a very handy and free online HTTP tool.","version":"1.0"}}',
          'specification': '{"name":"openapi","version":"3.0.0"}'
        })
        self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "inline" --value \'{value}\' --specification \'{specification}\'')

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_import_specification_example_2(self):
        self.kwargs.update({
          'value': 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.json',
          'specification': '{"name":"openapi","version":"3.0.0"}'
        })
        self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "link" --value \'{value}\' --specification \'{specification}\'')

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_examples_export_specification(self):
        self.kwargs.update({
          'value': 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.json',
          'specification': '{"name":"openapi","version":"3.0.0"}',
          'filename': "test_examples_export_specification.json"
        })
        # Import a specification first
        self.cmd('az apic api definition import-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --format "link" --value \'{value}\' --specification \'{specification}\'')

        self.cmd('az apic api definition export-specification -g {rg} -n {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {filename}')

        try:
            # Check the exported file exists
            assert os.path.exists(self.kwargs['filename'])
        finally:
            os.remove(self.kwargs['filename'])
