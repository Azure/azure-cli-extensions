# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import time
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer, ApimServicePreparer
from .constants import TEST_REGION

class ServiceCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    def test_create_service(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic create -g {rg} --name {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('sku.name', 'Free')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    def test_create_service_multiple_times(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic create -g {rg} --name {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('sku.name', 'Free')
        ])
        self.cmd('az apic create -g {rg} --name {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('sku.name', 'Free')
        ])
    
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    def test_create_service_with_all_optional_params(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic create -g {rg} --name {name} --location westeurope --tags \'{{test:value}}\' --identity \'{{type:SystemAssigned}}\'', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('identity.type', 'SystemAssigned'),
            self.check('location', 'westeurope'),
            self.check('tags.test', 'value'),
            self.check('sku.name', 'Free')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_show_service(self):
        if self.is_live:
            time.sleep(60) # Wait for service to finish provisioning, so dataApiHostname will be provided
        self.cmd('az apic show -g {rg} -n {s}', checks=[
            self.check('name', '{s}'),
            self.check('resourceGroup', '{rg}'),
            self.check('dataApiHostname', '{s}.data.eastus.azure-apicenter.ms'),
            self.check('sku.name', 'Free')
        ])

    @unittest.skip('The Control Plane API has bug')
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer(parameter_name='service_name1')
    @ApicServicePreparer(parameter_name='service_name2')
    def test_list_service(self, service_name1, service_name2):
        self.cmd('az apic list', checks=[
            self.check('length(@)', 2),
            self.check('@[0].name', service_name1),
            self.check('@[1].name', service_name2)
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_list_service_in_rg(self, service_name):
        self.cmd('az apic list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', service_name),
            self.check('@[0].sku.name', 'Free')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_update_service(self):
        self.cmd('az apic update -g {rg} -n {s} --tags "{{test:value}}"', checks=[
            self.check('tags.test', 'value')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_update_service_with_all_optional_params(self):
        self.cmd('az apic update -g {rg} -n {s} --tags "{{test:value}}" --identity "{{type:SystemAssigned}}"', checks=[
            self.check('tags.test', 'value'),
            self.check('identity.type', 'SystemAssigned')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_delete_service(self):
        self.cmd('az apic delete -g {rg} -n {s} --yes')
        self.cmd('az apic show -g {rg} -n {s}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApimServicePreparer()
    def test_import_from_apim(self):
        # Import from APIM
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis *')

        # Check result
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('length(@)', 3)
        ])


    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApimServicePreparer()
    def test_import_from_apim_for_one_api(self):
        # Import from APIM
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis echotest')

        # Wait for import to finish
        if self.is_live:
            asyncio.sleep(10)

        # Check result
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('contains(@[*].title, `Echo API Test`)', True),
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApimServicePreparer()
    def test_import_from_apim_for_multiple_apis(self):
        # Import from APIM
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis [echotest,footest]')

        # Wait for import to finish
        if self.is_live:
            asyncio.sleep(10)

        # Check result
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('contains(@[*].title, `Echo API Test`)', True),
            self.check('contains(@[*].title, `Foo API Test`)', True)
        ])


    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    def test_examples_create_service_1(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic create -g {rg} -n {name} -l eastus', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    def test_examples_create_service_2(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic create --resource-group {rg} --name {name} --location eastus', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_delete_service(self):
        self.cmd('az apic delete -n {s} -g {rg} --yes')
        self.cmd('az apic show -g {rg} -n {s}', expect_failure=True)

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApimServicePreparer()
    def test_examples_import_all_apis_from_apim(self):
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis *')

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApimServicePreparer()
    def test_examples_import_selected_apis_from_apim(self):
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis [echo,foo]')

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_list_services_in_resource_group(self):
        self.cmd('az apic list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', '{s}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_show_service_details(self):
        self.cmd('az apic show -g {rg} -n {s}', checks=[
            self.check('name', '{s}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_examples_update_service_details(self):
        self.cmd('az apic update -g {rg} -n {s}')
