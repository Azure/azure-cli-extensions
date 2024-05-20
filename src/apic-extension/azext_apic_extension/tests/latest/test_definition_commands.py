# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import requests
import json
import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicVersionPreparer, ApicDefinitionPreparer

current_dir = os.path.dirname(os.path.realpath(__file__))
test_assets_dir = os.path.join(current_dir, 'test_assets')

class VersionCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_definition_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api definition create -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {name} --title "OpenAPI"', checks=[
            self.check('name', '{name}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    def test_definition_create_with_all_optional_params(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24)
        })
        self.cmd('az apic api definition create -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {name} --title "OpenAPI" --description "test description"', checks=[
            self.check('name', '{name}'),
            self.check('title', 'OpenAPI'),
            self.check('description', 'test description'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_show(self):
        self.cmd('az apic api definition show -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d}', checks=[
            self.check('name', '{d}'),
            self.check('title', 'OpenAPI'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer(parameter_name="definition_id1")
    @ApicDefinitionPreparer(parameter_name="definition_id2")
    def test_definition_list(self, definition_id1, definition_id2):
        self.cmd('az apic api definition list -g {rg} -s {s} --api-id {api} --version-id {v}', checks=[
            self.check('length(@)', 2),
            self.check('[0].name', definition_id1),
            self.check('[1].name', definition_id2),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer(parameter_name="definition_id1")
    @ApicDefinitionPreparer(parameter_name="definition_id2")
    def test_definition_list_with_all_optional_params(self, definition_id1):
        self.kwargs.update({
          'definition_id': definition_id1
        })
        self.cmd('az apic api definition list -g {rg} -s {s} --api-id {api} --version-id {v} --filter "name eq \'{definition_id}\'"', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', definition_id1)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_update(self):
        self.cmd('az apic api definition update -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --title "Swagger" --description "test description 2"', checks=[
            self.check('name', '{d}'),
            self.check('title', 'Swagger'),
            self.check('description', 'test description 2'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_delete(self):
        self.cmd('az apic api definition delete -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --yes')
        self.cmd('az apic api definition show -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
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

        self.cmd('az apic api definition import-specification -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --format "link" --specification \'{specification}\' --value "{spec_url}"')

        self.cmd('az apic api definition export-specification -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {filename}')

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

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
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

        self.cmd('az apic api definition import-specification -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --format "inline" --specification \'{specification}\' --value \'{value}\'')

        self.cmd('az apic api definition export-specification -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {filename}')

        try:
            exported_file_path = self.kwargs['filename']
            with open(exported_file_path, 'r') as file:
                exported_content = json.load(file)

            imported_content = json.loads(self.kwargs['value'])

            assert exported_content == imported_content, "The exported content is not the same as the imported content."
        finally:
            os.remove(exported_file_path)

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
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

        self.cmd('az apic api definition import-specification -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --format "inline" --specification \'{specification}\' --value "@{import_filename}"')

        self.cmd('az apic api definition export-specification -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --file-name {export_filename}')

        try:
            exported_file_path = self.kwargs['export_filename']
            with open(exported_file_path, 'r') as file:
                exported_content = json.load(file)

            with open(self.kwargs['import_filename'], 'r') as file:
                imported_content = json.load(file)

            assert exported_content == imported_content, "The exported content is not the same as the imported content."
        finally:
            os.remove(exported_file_path)