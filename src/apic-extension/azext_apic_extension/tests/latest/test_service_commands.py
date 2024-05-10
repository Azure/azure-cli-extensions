# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .utils import ApicServicePreparer

class ServiceCommandsTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    def test_create_service(self, resource_group):
        self.kwargs.update({
          'name': self.create_random_name(prefix='cli', length=24),
          'rg': resource_group
        })
        self.cmd('az apic service create -g {rg} --name {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_show_service(self):
        self.cmd('az apic service show -g {rg} -s {s}', checks=[
            self.check('name', '{s}'),
            self.check('resourceGroup', '{rg}')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_update_service(self):
        self.cmd('az apic service update -g {rg} -s {s} --tags "{{test:value}}"', checks=[
            self.check('tags.test', 'value')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer()
    def test_delete_service(self):
        self.cmd('az apic service delete -g {rg} -s {s}a --yes')

    @unittest.skip('The Control Plane API has bug')
    @ResourceGroupPreparer(name_prefix="clirg", location='eastus', random_name_length=32)
    @ApicServicePreparer(enable_system_assigned_identity=True)
    def test_import_from_apim(self, identity_id):
        self.kwargs.update({
          'apim_name': self.create_random_name(prefix='cli', length=24),
          'identity_id': identity_id
        })
        apim_service = self.cmd('az apim create -g {rg} --name {apim_name} --publisher-name test --publisher-email test@example.com --sku-name Consumption').get_output_in_json()
        self.cmd('az apim api create -g {rg} --service-name {apim_name} --api-id echo --display-name "Echo API" --path "/echo"')
        self.cmd('az apim api operation create -g {rg} --service-name {apim_name} --api-id echo --url-template "/echo" --method "GET" --display-name "GetOperation"')
        apim_id = apim_service['id']
        self.kwargs.update({
            'apim_id': apim_id
        })
        self.cmd('az role assignment create --role "API Management Service Reader Role" --assignee-object-id {identity_id} --assignee-principal-type ServicePrincipal --scope {apim_id}')
        self.cmd('az apic service import-from-apim -g {rg} --service-name {s} --source-resource-ids {apim_id}/apis/*')

        # TODO: check result