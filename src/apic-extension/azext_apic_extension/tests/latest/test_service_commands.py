# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer
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
    @ApicServicePreparer(enable_system_assigned_identity=True)
    def test_import_from_apim(self):
        self.kwargs.update({
          'apim_name': self.create_random_name(prefix='cli', length=24)
        })
        self._prepare_apim()
        # Import from APIM
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis *')

        # Check result
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2)
        ])


    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer(enable_system_assigned_identity=True)
    def test_import_from_apim_for_one_api(self):
        self.kwargs.update({
          'apim_name': self.create_random_name(prefix='cli', length=24)
        })
        self._prepare_apim()
        # Import from APIM
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis echo')

        # Check result
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].title', 'Echo API')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer(enable_system_assigned_identity=True)
    def test_import_from_apim_for_multiple_apis(self):
        self.kwargs.update({
          'apim_name': self.create_random_name(prefix='cli', length=24)
        })
        self._prepare_apim()
        # Import from APIM
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis [echo,foo]')

        # Check result
        self.cmd('az apic api list -g {rg} -n {s}', checks=[
            self.check('length(@)', 2),
            self.check('contains(@[*].title, `Echo API`)', True),
            self.check('contains(@[*].title, `Foo API`)', True)
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
    @ApicServicePreparer(enable_system_assigned_identity=True)
    def test_examples_import_all_apis_from_apim(self):
        self.kwargs.update({
          'apim_name': self.create_random_name(prefix='cli', length=24)
        })
        self._prepare_apim()
        self.cmd('az apic import-from-apim -g {rg} --service-name {s} --apim-name {apim_name} --apim-apis *')

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer(enable_system_assigned_identity=True)
    def test_examples_import_selected_apis_from_apim(self):
        self.kwargs.update({
          'apim_name': self.create_random_name(prefix='cli', length=24)
        })
        self._prepare_apim()
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

    def _prepare_apim(self):
        if self.is_live:
            # Only setup APIM in live mode
            # Get system assigned identity id for API Center
            apic_service = self.cmd('az apic show -g {rg} -n {s}').get_output_in_json()
            self.kwargs.update({
                'identity_id': apic_service['identity']['principalId']
            })
            # Create APIM service
            apim_service = self.cmd('az apim create -g {rg} --name {apim_name} --publisher-name test --publisher-email test@example.com --sku-name Consumption').get_output_in_json()
            # Add echo api
            self.cmd('az apim api create -g {rg} --service-name {apim_name} --api-id echo --display-name "Echo API" --path "/echo"')
            self.cmd('az apim api operation create -g {rg} --service-name {apim_name} --api-id echo --url-template "/echo" --method "GET" --display-name "GetOperation"')
            # Add foo api
            self.cmd('az apim api create -g {rg} --service-name {apim_name} --api-id foo --display-name "Foo API" --path "/foo"')
            self.cmd('az apim api operation create -g {rg} --service-name {apim_name} --api-id foo --url-template "/foo" --method "GET" --display-name "GetOperation"')
            apim_id = apim_service['id']
            self.kwargs.update({
                'apim_id': apim_id
            })
            # Grant system assigned identity of API Center access to APIM
            self.cmd('az role assignment create --role "API Management Service Reader Role" --assignee-object-id {identity_id} --assignee-principal-type ServicePrincipal --scope {apim_id}')
