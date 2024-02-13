# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, JMESPathCheckExists, ResourceGroupPreparer, StorageAccountPreparer,
                               api_version_constraint)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_STORAGE


class StorageAccountTests(StorageScenarioMixin, ScenarioTest):
    @AllowLargeResponse()
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2021-09-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_account_dns_et')
    def test_storage_account_dns_endpoint_type(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'sa1': self.create_random_name(prefix='cli', length=24),
            'sa2': self.create_random_name(prefix='cli', length=24),
            'loc': 'eastus2euap'
        })
        self.cmd('storage account create -n {sa1} -g {rg} -l {loc} --hns true --dns-endpoint-type Standard',
                 checks=[JMESPathCheck('dnsEndpointType', 'Standard')])
        self.cmd('storage account create -n {sa2} -g {rg} -l {loc} --hns true --dns-endpoint-type AzureDnsZone',
                 checks=[JMESPathCheck('dnsEndpointType', 'AzureDnsZone')])

    @AllowLargeResponse()
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2021-08-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_account_sftp')
    def test_storage_account_sftp(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'sa': self.create_random_name(prefix='cli', length=24),
            'loc': 'centraluseuap'
        })
        self.cmd('storage account create -n {sa} -g {rg} -l {loc} --sku Standard_LRS --hns true '
                 '--enable-sftp true --enable-nfs-v3 false --enable-local-user true',
                 checks=[JMESPathCheck('isSftpEnabled', True), JMESPathCheck('isLocalUserEnabled', True)])
        self.cmd('storage account update -n {sa} --enable-sftp false',
                 checks=[JMESPathCheck('isSftpEnabled', False), JMESPathCheck('isLocalUserEnabled', True)])
        self.cmd('storage account update -n {sa} --enable-local-user false',
                 checks=[JMESPathCheck('isSftpEnabled', False), JMESPathCheck('isLocalUserEnabled', False)])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2021-08-01')
    @ResourceGroupPreparer()
    def test_storage_account_with_files_adds_sam_account_name(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'rg': resource_group,
            'sc': name,
            'domain_name': 'mydomain.com',
            'net_bios_domain_name': 'mydomain.com',
            'forest_name': 'mydomain.com',
            'domain_guid': '12345678-1234-1234-1234-123456789012',
            'domain_sid': 'S-1-5-21-1234567890-1234567890-1234567890',
            'azure_storage_sid': 'S-1-5-21-1234567890-1234567890-1234567890-1234',
            'sam_account_name': self.create_random_name(prefix='samaccount', length=48)
        })
        create_cmd = """storage account create -n {sc} -g {rg} -l eastus2euap --enable-files-adds --domain-name
        {domain_name} --net-bios-domain-name {net_bios_domain_name} --forest-name {forest_name} --domain-guid
        {domain_guid} --domain-sid {domain_sid} --azure-storage-sid {azure_storage_sid} 
        --sam-account-name {sam_account_name} --account-type User"""
        result = self.cmd(create_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AD')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['samAccountName'], self.kwargs['sam_account_name'])
        self.assertEqual(activeDirectoryProperties['accountType'], "User")
        self.assertEqual(activeDirectoryProperties['azureStorageSid'], self.kwargs['azure_storage_sid'])
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])
        self.assertEqual(activeDirectoryProperties['domainSid'], self.kwargs['domain_sid'])
        self.assertEqual(activeDirectoryProperties['forestName'], self.kwargs['forest_name'])
        self.assertEqual(activeDirectoryProperties['netBiosDomainName'], self.kwargs['net_bios_domain_name'])

        self.kwargs.update({
            'sam_account_name': self.create_random_name(prefix='newsamaccount', length=48)
        })
        update_cmd = """storage account update -n {sc} -g {rg} --enable-files-adds --domain-name {domain_name}
        --net-bios-domain-name {net_bios_domain_name} --forest-name {forest_name} --domain-guid {domain_guid}
        --domain-sid {domain_sid} --azure-storage-sid {azure_storage_sid} 
        --sam-account-name {sam_account_name} --account-type Computer"""
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AD')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['samAccountName'], self.kwargs['sam_account_name'])
        self.assertEqual(activeDirectoryProperties['accountType'], "Computer")
        self.assertEqual(activeDirectoryProperties['azureStorageSid'], self.kwargs['azure_storage_sid'])
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])
        self.assertEqual(activeDirectoryProperties['domainSid'], self.kwargs['domain_sid'])
        self.assertEqual(activeDirectoryProperties['forestName'], self.kwargs['forest_name'])
        self.assertEqual(activeDirectoryProperties['netBiosDomainName'], self.kwargs['net_bios_domain_name'])


    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2022-05-01')
    @ResourceGroupPreparer()
    def test_create_storage_account_with_files_aadkerb(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'rg': resource_group,
            'sc': name,
            'domain_name': 'mydomain.com',
            'domain_guid': '12345678-1234-1234-1234-123456789012'
        })
        create_cmd = 'storage account create -n {sc} -g {rg} -l eastus2euap --sku Standard_LRS ' \
                     '--enable-files-aadkerb --domain-name {domain_name} --domain-guid {domain_guid}'
        result = self.cmd(create_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AADKERB')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2022-05-01')
    @ResourceGroupPreparer()
    def test_create_storage_account_with_files_aadkerb_false(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'rg': resource_group,
            'sc': name
        })
        result = self.cmd(
            "storage account create -n {sc} -g {rg} -l eastus2euap --enable-files-aadkerb false").get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'None')

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2022-05-01')
    @ResourceGroupPreparer()
    def test_create_storage_account_with_files_aadkerb_true(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'rg': resource_group,
            'sc': name,
            'domain_name': 'mydomain.com',
            'domain_guid': '12345678-1234-1234-1234-123456789012'
        })
        create_cmd = 'storage account create -n {sc} -g {rg} -l eastus2euap --sku Standard_LRS ' \
                     '--enable-files-aadkerb true --domain-name {domain_name} --domain-guid {domain_guid}'
        result = self.cmd(create_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AADKERB')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2022-05-01')
    @ResourceGroupPreparer()
    def test_update_storage_account_with_files_aadkerb(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} -l eastus2euap'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('azureFilesIdentityBasedAuthentication', None)])
        self.kwargs.update({
            'rg': resource_group,
            'sc': name,
            'domain_name': 'mydomain.com',
            'domain_guid': '12345678-1234-1234-1234-123456789012'
        })
        update_cmd = 'storage account update -n {sc} -g {rg} --enable-files-aadkerb'
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AADKERB')

        update_cmd = 'storage account update -n {sc} -g {rg} --enable-files-aadkerb ' \
                     '--domain-name {domain_name} --domain-guid {domain_guid}'
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AADKERB')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2022-05-01')
    @ResourceGroupPreparer()
    def test_update_storage_account_with_files_aadkerb_false(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} -l eastus2euap'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('azureFilesIdentityBasedAuthentication', None)])

        update_cmd = 'az storage account update -n {} -g {} --enable-files-aadkerb false'.format(name, resource_group)
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'None')

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2019-04-01')
    @ResourceGroupPreparer()
    def test_update_storage_account_with_files_aadkerb_true(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        create_cmd = 'az storage account create -n {} -g {} -l eastus2euap'.format(name, resource_group)
        self.cmd(create_cmd, checks=[JMESPathCheck('azureFilesIdentityBasedAuthentication', None)])
        self.kwargs.update({
            'rg': resource_group,
            'sc': name,
            'domain_name': 'mydomain.com',
            'domain_guid': '12345678-1234-1234-1234-123456789012'
        })
        update_cmd = 'storage account update -n {sc} -g {rg} --enable-files-aadkerb true ' \
                     '--domain-name {domain_name} --domain-guid {domain_guid}'
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AADKERB')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2021-08-01')
    @ResourceGroupPreparer()
    def test_storage_account_with_files_adds_sam_account_name(self, resource_group):
        name = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'rg': resource_group,
            'sc': name,
            'domain_name': 'mydomain.com',
            'net_bios_domain_name': 'mydomain.com',
            'forest_name': 'mydomain.com',
            'domain_guid': '12345678-1234-1234-1234-123456789012',
            'domain_sid': 'S-1-5-21-1234567890-1234567890-1234567890',
            'azure_storage_sid': 'S-1-5-21-1234567890-1234567890-1234567890-1234',
            'sam_account_name': self.create_random_name(prefix='samaccount', length=48)
        })
        create_cmd = """storage account create -n {sc} -g {rg} -l eastus2euap --enable-files-adds --domain-name
            {domain_name} --net-bios-domain-name {net_bios_domain_name} --forest-name {forest_name} --domain-guid
            {domain_guid} --domain-sid {domain_sid} --azure-storage-sid {azure_storage_sid} 
            --sam-account-name {sam_account_name} --account-type User"""
        result = self.cmd(create_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AD')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['samAccountName'], self.kwargs['sam_account_name'])
        self.assertEqual(activeDirectoryProperties['accountType'], "User")
        self.assertEqual(activeDirectoryProperties['azureStorageSid'], self.kwargs['azure_storage_sid'])
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])
        self.assertEqual(activeDirectoryProperties['domainSid'], self.kwargs['domain_sid'])
        self.assertEqual(activeDirectoryProperties['forestName'], self.kwargs['forest_name'])
        self.assertEqual(activeDirectoryProperties['netBiosDomainName'], self.kwargs['net_bios_domain_name'])

        self.kwargs.update({
            'sam_account_name': self.create_random_name(prefix='newsamaccount', length=48)
        })
        update_cmd = """storage account update -n {sc} -g {rg} --enable-files-adds --domain-name {domain_name}
            --net-bios-domain-name {net_bios_domain_name} --forest-name {forest_name} --domain-guid {domain_guid}
            --domain-sid {domain_sid} --azure-storage-sid {azure_storage_sid} 
            --sam-account-name {sam_account_name} --account-type Computer"""
        result = self.cmd(update_cmd).get_output_in_json()

        self.assertIn('azureFilesIdentityBasedAuthentication', result)
        self.assertEqual(result['azureFilesIdentityBasedAuthentication']['directoryServiceOptions'], 'AD')
        activeDirectoryProperties = result['azureFilesIdentityBasedAuthentication']['activeDirectoryProperties']
        self.assertEqual(activeDirectoryProperties['samAccountName'], self.kwargs['sam_account_name'])
        self.assertEqual(activeDirectoryProperties['accountType'], "Computer")
        self.assertEqual(activeDirectoryProperties['azureStorageSid'], self.kwargs['azure_storage_sid'])
        self.assertEqual(activeDirectoryProperties['domainGuid'], self.kwargs['domain_guid'])
        self.assertEqual(activeDirectoryProperties['domainName'], self.kwargs['domain_name'])
        self.assertEqual(activeDirectoryProperties['domainSid'], self.kwargs['domain_sid'])
        self.assertEqual(activeDirectoryProperties['forestName'], self.kwargs['forest_name'])
        self.assertEqual(activeDirectoryProperties['netBiosDomainName'], self.kwargs['net_bios_domain_name'])

    @ResourceGroupPreparer(location='eastus2euap')
    def test_storage_account_migration(self, resource_group):
        self.kwargs.update({
            'sa': self.create_random_name('samigration', 24)
        })
        self.cmd('az storage account create -n {sa} -g {rg} -l eastus2euap --sku Standard_LRS')
        self.cmd('az storage account migration start --account-name {sa} -g {rg} --sku Standard_ZRS --no-wait')
        # other status would take days to months
        self.cmd('az storage account migration show -n default -g {rg} --account-name {sa}',
                 checks=[JMESPathCheck('migrationStatus', 'SubmittedForConversion')])
