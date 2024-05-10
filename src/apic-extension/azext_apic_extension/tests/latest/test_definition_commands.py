# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import requests
import json
import os

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicApiPreparer, ApicVersionPreparer, ApicDefinitionPreparer

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
    @ApicDefinitionPreparer()
    def test_definition_update(self):
        self.cmd('az apic api definition update -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --title "Swagger"', checks=[
            self.check('name', '{d}'),
            self.check('title', 'Swagger'),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    @ApicApiPreparer()
    @ApicVersionPreparer()
    @ApicDefinitionPreparer()
    def test_definition_delete(self):
        self.cmd('az apic api definition delete -g {rg} -s {s} --api-id {api} --version-id {v} --definition-id {d} --yes')

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