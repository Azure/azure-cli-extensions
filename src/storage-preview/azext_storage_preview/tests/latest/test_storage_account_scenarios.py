# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint)
from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_STORAGE


@api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2016-12-01')
class StorageAccountTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_create_storage_account_with_assigned_identity(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        cmd = 'az storage account create -n {} -g {} --sku Standard_LRS --assign-identity'.format(name, resource_group)
        result = self.cmd(cmd).get_output_in_json()

        self.assertIn('identity', result)
        self.assertTrue(result['identity']['principalId'])
        self.assertTrue(result['identity']['tenantId'])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_update_storage_account_with_assigned_identity(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} --sku Standard_LRS'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('identity', None)])

        update_cmd = 'az storage account update -n {} -g {} --assign-identity'.format(name, resource_group)
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('identity', result)
        self.assertTrue(result['identity']['principalId'])
        self.assertTrue(result['identity']['tenantId'])

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_create_storage_account(self, resource_group, location):
        name = self.create_random_name(prefix='cli', length=24)

        self.cmd('az storage account create -n {} -g {} --sku {} -l {}'.format(
            name, resource_group, 'Standard_LRS', location))

        self.cmd('storage account check-name --name {}'.format(name), checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

        self.cmd('storage account list -g {}'.format(resource_group), checks=[
            JMESPathCheck('[0].location', 'westus'),
            JMESPathCheck('[0].sku.name', 'Standard_LRS'),
            JMESPathCheck('[0].resourceGroup', resource_group)
        ])

        self.cmd('az storage account show -n {} -g {}'.format(name, resource_group), checks=[
            JMESPathCheck('name', name),
            JMESPathCheck('location', location),
            JMESPathCheck('sku.name', 'Standard_LRS'),
            JMESPathCheck('kind', 'Storage')
        ])

        self.cmd('az storage account show -n {}'.format(name), checks=[
            JMESPathCheck('name', name),
            JMESPathCheck('location', location),
            JMESPathCheck('sku.name', 'Standard_LRS'),
            JMESPathCheck('kind', 'Storage')
        ])

        self.cmd('storage account show-connection-string -g {} -n {} --protocol http'.format(
            resource_group, name), checks=[
                JMESPathCheck("contains(connectionString, 'https')", False),
                JMESPathCheck("contains(connectionString, '{}')".format(name), True)])

        self.cmd('storage account update -g {} -n {} --tags foo=bar cat'
                 .format(resource_group, name),
                 checks=JMESPathCheck('tags', {'cat': '', 'foo': 'bar'}))
        self.cmd('storage account update -g {} -n {} --sku Standard_GRS --tags'
                 .format(resource_group, name),
                 checks=[JMESPathCheck('tags', {}),
                         JMESPathCheck('sku.name', 'Standard_GRS')])
        self.cmd('storage account update -g {} -n {} --set tags.test=success'
                 .format(resource_group, name),
                 checks=JMESPathCheck('tags', {'test': 'success'}))
        self.cmd('storage account delete -g {} -n {} --yes'.format(resource_group, name))
        self.cmd('storage account check-name --name {}'.format(name),
                 checks=JMESPathCheck('nameAvailable', True))

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2017-10-01')
    @ResourceGroupPreparer(parameter_name_for_location='location', location='westus2')
    def test_create_storage_account_hierarchical_namespace(self, resource_group, location):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'loc': location
        })

        self.cmd('storage account create -n {name} -g {rg} -l {loc} --kind StorageV2 --hierarchical-namespace',
                 checks=[JMESPathCheck('kind', 'StorageV2'),
                         JMESPathCheck('isHnsEnabled', True)])

        self.cmd('storage account check-name --name {name}', checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_create_storage_account_file_aad(self, resource_group, location):
        self.kwargs.update({
            'name': self.create_random_name(prefix='cli', length=24),
            'loc': location
        })

        self.cmd('storage account create -n {name} -g {rg} -l {loc} --kind StorageV2 --file-aad',
                 checks=[JMESPathCheck('kind', 'StorageV2'),
                         JMESPathCheck('enableAzureFilesAadIntegration', True)])

        self.cmd('storage account check-name --name {name}', checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

        self.cmd('storage account update -n {name} -g {rg} --file-aad false',
                 checks=[JMESPathCheck('enableAzureFilesAadIntegration', False)])

    @ResourceGroupPreparer(parameter_name_for_location='location', location='northeurope')
    def test_create_storage_account_premium_sku(self, resource_group, location):
        self.kwargs.update({
            'name1': self.create_random_name(prefix='cli', length=24),
            'name2': self.create_random_name(prefix='cli', length=24),
            'sku': 'Premium_LRS'
        })

        self.cmd('storage account create -n {name1} -g {rg} --kind BlockBlobStorage --sku {sku}',
                 checks=[JMESPathCheck('kind', 'BlockBlobStorage'),
                         JMESPathCheck('sku.name', 'Premium_LRS')])

        self.cmd('storage account check-name --name {name1}', checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

        self.cmd('storage account create -n {name2} -g {rg} --kind FileStorage --sku {sku}', checks=[
            JMESPathCheck('kind', 'FileStorage'),
            JMESPathCheck('sku.name', 'Premium_LRS')])

        self.cmd('storage account check-name --name {name2}', checks=[
            JMESPathCheck('nameAvailable', False),
            JMESPathCheck('reason', 'AlreadyExists')
        ])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2016-01-01')
    @ResourceGroupPreparer(location='southcentralus')
    def test_storage_create_default_sku(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {}'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('sku.name', 'Standard_RAGRS')])

    def test_show_usage(self):
        self.cmd('storage account show-usage -l westus', checks=JMESPathCheck('name.value', 'StorageAccounts'))

    @ResourceGroupPreparer(location='eastus2euap')
    def test_management_policy(self, resource_group):
        import os
        from msrestazure.azure_exceptions import CloudError
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        policy_file = os.path.join(curr_dir, 'mgmt_policy.json').replace('\\', '\\\\')

        storage_account = self.create_random_name(prefix='cli', length=24)

        self.kwargs = {'rg': resource_group, 'sa': storage_account, 'policy': policy_file}
        self.cmd('storage account create -g {rg} -n {sa} --kind StorageV2')
        self.cmd('storage account management-policy create --account-name {sa} -g {rg} --policy @"{policy}"')
        self.cmd('storage account management-policy update --account-name {sa} -g {rg}'
                 ' --set "policy.rules[0].name=newname"')
        self.cmd('storage account management-policy show --account-name {sa} -g {rg}',
                 checks=JMESPathCheck('policy.rules[0].name', 'newname'))
        self.cmd('storage account management-policy delete --account-name {sa} -g {rg}')
        self.cmd('storage account management-policy show --account-name {sa} -g {rg}', expect_failure=True)
