# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApicMetadataPreparer
from .constants import TEST_REGION

current_dir = os.path.dirname(os.path.realpath(__file__))
test_assets_dir = os.path.join(current_dir, 'test_assets')

class MetadataCommandsTests(ScenarioTest):


    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_metadata_create(self):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'schema': '{"type":"boolean", "title":"Public Facing"}',
          'assignments': '[{entity:api,required:true,deprecated:false}]'
        })
        self.cmd('az apic metadata create -g {rg} -n {s} --metadata-name {name} --schema \'{schema}\' --assignments \'{assignments}\'', checks=[
            self.check('name', '{name}'),
            self.check('assignedTo[0].entity', 'api'),
            self.check('assignedTo[0].required', True),
            self.check('assignedTo[0].deprecated', False),
            self.check('schema', '{schema}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_metadata_create_with_file(self):
        schema_file = os.path.join(test_assets_dir, 'metadata_schema.json')
        with open(schema_file, 'r') as f:
          expected_result = f.read()

        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'assignments': '[{entity:api,required:true,deprecated:false}]',
          'schema_file': schema_file,
          'expected_result': expected_result
        })


        self.cmd('az apic metadata create -g {rg} -n {s} --metadata-name {name} --schema "@{schema_file}" --assignments \'{assignments}\'', checks=[
            self.check('name', '{name}'),
            self.check('assignedTo[0].entity', 'api'),
            self.check('assignedTo[0].required', True),
            self.check('assignedTo[0].deprecated', False),
            self.check('schema', '{expected_result}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_metadata_show(self):
       self.cmd('az apic metadata show -g {rg} -n {s} --metadata-name {m}', checks=[
            self.check('name', '{m}'),
            self.check('assignedTo[0].entity', 'api'),
            self.check('assignedTo[0].required', True),
            self.check('assignedTo[0].deprecated', False),
            self.check('schema', '{{"type":"boolean", "title":"Public Facing"}}')
        ])
       
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer(parameter_name='metadata_name1')
    @ApicMetadataPreparer(parameter_name='metadata_name2')
    def test_metadata_list(self, metadata_name1, metadata_name2):
       self.cmd('az apic metadata list -g {rg} -n {s}', checks=[
           self.check('length(@)', 2),
           self.check('@[0].name', metadata_name1),
           self.check('@[1].name', metadata_name2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer(parameter_name='metadata_name1')
    @ApicMetadataPreparer(parameter_name='metadata_name2')
    def test_metadata_list_with_all_optional_params(self, metadata_name1):
       self.kwargs.update({
         'metadata_name': metadata_name1
       })
       self.cmd('az apic metadata list -g {rg} -n {s} --filter "name eq \'{metadata_name}\'"', checks=[
           self.check('length(@)', 1),
           self.check('@[0].name', metadata_name1),
        ])
       
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_metadata_update(self):
       self.kwargs.update({
          'schema': '{"type":"boolean", "title":"Updated Title"}',
        })
       self.cmd('az apic metadata update -g {rg} -n {s} --metadata-name {m} --schema \'{schema}\'', checks=[
            self.check('name', '{m}'),
            self.check('schema', '{schema}')
        ])
       
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_metadata_delete(self):
       self.cmd('az apic metadata delete -g {rg} -n {s} --metadata-name {m} --yes')
       self.cmd('az apic metadata show -g {rg} -n {s} --metadata-name {m}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_metadata_export(self):
        self.kwargs.update({
          'filename': 'metadata_export.json'
        })
        self.cmd('az apic metadata export -g {rg} -n {s} --assignments api --file-name {filename}')
        
        try:
          with open(self.kwargs['filename'], 'r') as f:
            data = json.load(f)

          assert 'properties' in data, "properties not found in the exported file"
          assert 'customProperties' in data['properties'], "customProperties not found in the exported file"
          assert 'properties' in data['properties']['customProperties'], "properties not found in customProperties"
          assert len(data['properties']['customProperties']['properties']) == 1, "The number of properties in customProperties does not match the expected number"
        finally:
          os.remove(self.kwargs['filename'])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_create_metadata_1(self):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'schema': '{"type":"string", "title":"First name", "pattern": "^[a-zA-Z0-9]+$"}',
            'assignments': '[{entity:api,required:true,deprecated:false}]'
        })
        self.cmd('az apic metadata create --resource-group {rg} --service-name {s} --metadata-name {name} --schema \'{schema}\' --assignments \'{assignments}\'', checks=[
            self.check('name', '{name}'),
            self.check('schema', '{schema}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_create_metadata_2(self):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'schema': '{"type":"string","title":"testregion","oneOf":[{"const":"Region1","description":""},{"const":"Region2","description":""},{"const":"Region3","description":""}]}',
            'assignments': '[{entity:api,required:true,deprecated:false},{entity:environment,required:true,deprecated:false}]'
        })
        self.cmd('az apic metadata create --resource-group {rg} --service-name {s} --metadata-name {name} --schema \'{schema}\' --assignments \'{assignments}\'', checks=[
            self.check('name', '{name}'),
            self.check('schema', '{schema}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_delete_metadata_1(self):
        self.cmd('az apic metadata delete --resource-group {rg} --service-name {s} --metadata-name {m} --yes')
        self.cmd('az apic metadata show --resource-group {rg} --service-name {s} --metadata-name {m}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_delete_metadata_2(self):
        self.cmd('az apic metadata delete -g {rg} -n {s} --metadata-name {m} --yes')
        self.cmd('az apic metadata show -g {rg} -n {s} --metadata-name {m}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_export_metadata_assigned_to_api(self):
        self.kwargs.update({
            'filename': 'test_examples_export_metadata_assigned_to_api.json'
        })
        self.cmd('az apic metadata export -g {rg} -n {s} --assignments api --file-name {filename}')

        os.remove(self.kwargs['filename'])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_export_metadata_assigned_to_deployment(self):
        self.kwargs.update({
            'filename': 'test_examples_export_metadata_assigned_to_deployment.json'
        })
        self.cmd('az apic metadata export -g {rg} -n {s} --assignments deployment --file-name {filename}')

        os.remove(self.kwargs['filename'])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_export_metadata_assigned_to_environment(self):
        self.kwargs.update({
            'filename': 'test_examples_export_metadata_assigned_to_environment.json'
        })
        self.cmd('az apic metadata export -g {rg} -n {s} --assignments environment --file-name {filename}')

        os.remove(self.kwargs['filename'])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer(parameter_name='metadata_name1')
    @ApicMetadataPreparer(parameter_name='metadata_name2')
    def test_examples_list_metadata(self, metadata_name1, metadata_name2):
        self.cmd('az apic metadata list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', metadata_name1),
            self.check('@[1].name', metadata_name2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_show_metadata_1(self):
        self.cmd('az apic metadata show -g {rg} -n {s} --metadata-name {m}', checks=[
            self.check('name', '{m}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_show_metadata_2(self):
        self.cmd('az apic metadata show --resource-group {rg} --service-name {s} --metadata-name {m}', checks=[
            self.check('name', '{m}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApicMetadataPreparer()
    def test_examples_update_metadata(self):
        self.kwargs.update({
            'schema': '{"type": "string", "title":"Last name", "pattern": "^[a-zA-Z0-9]+$"}'
        })
        self.cmd('az apic metadata update --resource-group {rg} --service-name {s} --metadata-name {m} --schema \'{schema}\'', checks=[
            self.check('name', '{m}'),
            self.check('schema', '{schema}')
        ])