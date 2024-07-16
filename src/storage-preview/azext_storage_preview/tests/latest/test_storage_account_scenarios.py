# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, JMESPathCheckExists, ResourceGroupPreparer, StorageAccountPreparer,
                               api_version_constraint)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.core.exceptions import HttpResponseError
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

    @ResourceGroupPreparer(location='eastus2euap')
    def test_storage_account_task_assignment(self, resource_group):
        self.kwargs.update({
            'sa': self.create_random_name('sataskassignment', 24),
            "task_name": self.create_random_name('task', 18),
            "task_assignment_name": self.create_random_name('taskassignment', 24)
        })
        self.cmd('az storage account create -n {sa} -g {rg} -l eastus2euap')

        # need to create storage-actions task manually
        # task_id = self.cmd("az storage-actions task create -g {rg} -n {task_name} --identity {{type:SystemAssigned}} "
        #                    "--tags {{key1:value1}} --action {{if:{{condition:\\'
        #                    [[equals(AccessTier,\\'/Cool\\'/)]]\\',"
        #                    "operations:[{{name:'SetBlobTier',parameters:{{tier:'Hot'}},"
        #                    "onSuccess:'continue',onFailure:'break'}}]}},"
        #                    "else:{{operations:[{{name:'DeleteBlob',onSuccess:'continue',onFailure:'break'}}]}}}} "
        #                    "--description StorageTask1 --enabled true").get_output_in_json()["id"]
        task_id = 'taskid'
        self.kwargs.update({"task_id": task_id})
        # server error return accepted but also error
        with self.assertRaises(HttpResponseError):
            self.cmd("az storage account task-assignment create -g {rg} -n {task_assignment_name} --account-name {sa} "
                     "--description 'My Storage task assignment' --enabled false --task-id '{task_id}' "
                     "--report {{prefix:container1}} "
                     "--execution-context {{trigger:{{type:OnSchedule,parameters:"
                     "{{start-from:\\'2024-08-14T21:52:47Z\\',"
                     "end-by:\\'2024-09-04T21:52:47.203074Z\\',interval:10,interval-unit:Days}}}},"
                     "target:{{prefix:[prefix1,prefix2],exclude-prefix:[prefix3]}}}}")
        with self.assertRaises(HttpResponseError):
            self.cmd("az storage account task-assignment update -g {rg} -n {task_assignment_name} --account-name {sa} "
                     "--description 'My Storage task assignment' --enabled false --task-id '{task_id}'"
                     " --report {{prefix:container1}} "
                     "--execution-context {{trigger:{{type:OnSchedule,parameters:"
                     "{{start-from:\\'2024-08-15T21:52:47Z\\',"
                     "end-by:\\'2024-09-05T21:52:47.203074Z\\',interval:10,interval-unit:Days}}}},"
                     "target:{{prefix:[prefix1,prefix2],exclude-prefix:[prefix3]}}}}")
        self.cmd("az storage account task-assignment show -g {rg} -n {task_assignment_name} --account-name {sa}")
        self.cmd("az storage account task-assignment list -g {rg} --account-name {sa}")
        self.cmd("az storage account task-assignment list-report -g {rg} -n {task_assignment_name} --account-name {sa}")
        with self.assertRaises(HttpResponseError):
            self.cmd("az storage account task-assignment delete -g {rg} -n {task_assignment_name} --account-name {sa} "
                     "-y")


class StorageAccountLocalUserTests(StorageScenarioMixin, ScenarioTest):
    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='cli_storage_account_local_user')
    @StorageAccountPreparer(name_prefix='storagelocaluser', kind='StorageV2', location='eastus2euap')
    def test_storage_account_local_user(self, resource_group, storage_account):
        username = self.create_random_name(prefix='cli', length=24)
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account local-user',
            'username': username,
            'username2': self.create_random_name(prefix='notcli', length=24)
        })

        self.cmd('{cmd} create --account-name {sa} -g {rg} -n {username} --home-directory home '
                 '--permission-scope permissions=r service=blob resource-name=container1 '
                 '--permission-scope permissions=rw service=file resource-name=share2 '
                 '--has-ssh-key false --has-shared-key false --group-id 1 '
                 '--allow-acl-authorization true').assert_with_checks(
            JMESPathCheck('hasSharedKey', False),
            JMESPathCheck('hasSshKey', False),
            JMESPathCheck('hasSshPassword', None),
            JMESPathCheck('homeDirectory', 'home'),
            JMESPathCheck('name', username),
            JMESPathCheck('length(permissionScopes)', 2),
            JMESPathCheck('permissionScopes[0].permissions', 'r'),
            JMESPathCheck('permissionScopes[0].service', 'blob'),
            JMESPathCheck('permissionScopes[0].resourceName', 'container1'),
            JMESPathCheck('groupId', 1),
            JMESPathCheck('allowAclAuthorization', True)
        )

        self.cmd('{cmd} update --account-name {sa} -g {rg} -n {username} --home-directory home2 '
                 '--permission-scope permissions=rw service=file resource-name=share2 --group-id 2 '
                 '--allow-acl-authorization false').assert_with_checks(
            JMESPathCheck('homeDirectory', 'home2'),
            JMESPathCheck('length(permissionScopes)', 1),
            JMESPathCheck('permissionScopes[0].permissions', 'rw'),
            JMESPathCheck('permissionScopes[0].service', 'file'),
            JMESPathCheck('permissionScopes[0].resourceName', 'share2'),
            JMESPathCheck('groupId', 2),
            JMESPathCheck('allowAclAuthorization', False)
        )

        self.cmd('{cmd} list --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('[0].hasSshKey', False),
            JMESPathCheck('[0].hasSshPassword', False),
            JMESPathCheck('[0].homeDirectory', 'home2'),
            JMESPathCheck('[0].length(permissionScopes)', 1),
            JMESPathCheck('[0].sshAuthorizedKeys', None)
        )

        self.cmd('{cmd} create --account-name {sa} -g {rg} -n {username2} --home-directory home '
                 '--permission-scope permissions=r service=blob resource-name=container1 '
                 '--permission-scope permissions=rw service=file resource-name=share2 '
                 '--has-ssh-key false --has-shared-key false --group-id 2 '
                 '--allow-acl-authorization true')

        self.cmd('{cmd} list --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('length(@)', 2)
        )
        self.cmd('{cmd} list --account-name {sa} -g {rg} --filter "startswith(name, cli)"').assert_with_checks(
            JMESPathCheck('length(@)', 1)
        )

        self.cmd('{cmd} show --account-name {sa} -g {rg} -n {username}').assert_with_checks(
            JMESPathCheck('hasSshKey', False),
            JMESPathCheck('hasSshPassword', False),
            JMESPathCheck('homeDirectory', 'home2'),
            JMESPathCheck('length(permissionScopes)', 1),
            JMESPathCheck('permissionScopes[0].permissions', 'rw'),
            JMESPathCheck('permissionScopes[0].service', 'file'),
            JMESPathCheck('permissionScopes[0].resourceName', 'share2'),
            JMESPathCheck('sshAuthorizedKeys', None)
        )

        self.cmd('{cmd} update --account-name {sa} -g {rg} -n {username} '
                 '--ssh-authorized-key key="ssh-rsa a2V5" ')

        self.cmd('{cmd} list-keys --account-name {sa} -g {rg} -n {username}').assert_with_checks(
            JMESPathCheck('sshAuthorizedKeys', None)
        )

        self.cmd('{cmd} regenerate-password --account-name {sa} -g {rg} -n {username}').assert_with_checks(
            JMESPathCheck('sshAuthorizedKeys', None),
            JMESPathCheckExists('sshPassword')
        )

        self.cmd('{cmd} delete --account-name {sa} -g {rg} -n {username}')

        for i in range(5):
            username = self.create_random_name(prefix='cli', length=24)
            self.kwargs.update({
                'username': username
            })
            self.cmd('{cmd} create --account-name {sa} -g {rg} -n {username} --home-directory home '
                     '--permission-scope permissions=r service=blob resource-name=container1 '
                     '--permission-scope permissions=rw service=file resource-name=share2 '
                     '--has-ssh-key false --has-shared-key false --group-id 1 '
                     '--allow-acl-authorization true')
        self.cmd('{cmd} list --account-name {sa} -g {rg} --maxpagesize 3').assert_with_checks(
            JMESPathCheck('length(@)', 3)
        )
