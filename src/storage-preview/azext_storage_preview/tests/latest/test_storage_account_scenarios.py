# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, JMESPathCheckExists, ResourceGroupPreparer, StorageAccountPreparer,
                               api_version_constraint)
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_STORAGE
from knack.util import CLIError


class StorageAccountTests(StorageScenarioMixin, ScenarioTest):
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


@api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2016-12-01')
class StorageAccountNetworkRuleTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_network_rules(self, resource_group):
        kwargs = {
            'rg': resource_group,
            'acc': self.create_random_name(prefix='cli', length=24),
            'vnet': 'vnet1',
            'subnet': 'subnet1'
        }
        self.cmd('storage account create -g {rg} -n {acc} --bypass Metrics --default-action Deny --https-only'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Metrics'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])
        self.cmd('storage account update -g {rg} -n {acc} --bypass Logging --default-action Allow'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Allow')])
        self.cmd('storage account update -g {rg} -n {acc} --set networkRuleSet.default_action=deny'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])

        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name {subnet}'.format(**kwargs))
        self.cmd(
            'network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} --service-endpoints Microsoft.Storage'.format(
                **kwargs))

        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        # test network-rule add idempotent
        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.2.0.0/24'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 1),
            JMESPathCheck('length(virtualNetworkRules)', 0)
        ])

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_resource_access_rules(self, resource_group, storage_account):
        self.kwargs = {
            'rg': resource_group,
            'sa': storage_account,
            'rid1': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace1",
            'rid2': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace2",
            'rid3': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace3",
            'tid1': "72f988bf-86f1-41af-91ab-2d7cd011db47",
            'tid2': "72f988bf-86f1-41af-91ab-2d7cd011db47"
        }

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add more
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid3} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 3)
        ])

        # remove network-rule
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])


class FileServicePropertiesTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_file_soft_delete')
    @StorageAccountPreparer(name_prefix='filesoftdelete', kind='StorageV2', location='eastus2euap')
    def test_storage_account_file_delete_retention_policy(self, resource_group, storage_account):
        from azure.cli.core.azclierror import ValidationError
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account file-service-properties'
        })
        self.cmd('{cmd} show --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 7))

        # Test update without properties
        self.cmd('{cmd} update --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 7))

        self.cmd('{cmd} update --enable-delete-retention false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', None))

        self.cmd('{cmd} show -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 0))

        # Test update without properties
        self.cmd('{cmd} update --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', None))

        with self.assertRaises(ValidationError):
            self.cmd('{cmd} update --enable-delete-retention true -n {sa} -g {rg}')

        with self.assertRaisesRegexp(ValidationError, "Delete Retention Policy hasn't been enabled,"):
            self.cmd('{cmd} update --delete-retention-days 1 -n {sa} -g {rg} -n {sa} -g {rg}')

        with self.assertRaises(ValidationError):
            self.cmd('{cmd} update --enable-delete-retention false --delete-retention-days 1 -n {sa} -g {rg}')

        self.cmd(
            '{cmd} update --enable-delete-retention true --delete-retention-days 10 -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 10))

        self.cmd('{cmd} update --delete-retention-days 1 -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 1))

    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_file_smb')
    @StorageAccountPreparer(parameter_name='storage_account1', name_prefix='filesmb1', kind='FileStorage',
                            sku='Premium_LRS', location='centraluseuap')
    @StorageAccountPreparer(parameter_name='storage_account2', name_prefix='filesmb2', kind='StorageV2')
    def test_storage_account_file_smb_multichannel(self, resource_group, storage_account1, storage_account2):

        from azure.core.exceptions import ResourceExistsError
        self.kwargs.update({
            'sa': storage_account1,
            'sa2': storage_account2,
            'rg': resource_group,
            'cmd': 'storage account file-service-properties'
        })

        with self.assertRaisesRegexp(ResourceExistsError, "SMB Multichannel is not supported for the account."):
            self.cmd('{cmd} update --mc -n {sa2} -g {rg}')

        self.cmd('{cmd} show -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 7),
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd('{cmd} show -n {sa2} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 7),
            JMESPathCheck('protocolSettings.smb.multichannel', None))

        self.cmd(
            '{cmd} update --enable-smb-multichannel -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', True))

        self.cmd(
            '{cmd} update --enable-smb-multichannel false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd(
            '{cmd} update --enable-smb-multichannel true -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', True))


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
            'username': username
        })

        self.cmd('{cmd} create --account-name {sa} -g {rg} -n {username} --home-directory home '
                 '--permission-scope permissions=r service=blob resource-name=container1 '
                 '--permission-scope permissions=rw service=file resource-name=share2 '
                 '--has-ssh-key false --has-shared-key false').assert_with_checks(
            JMESPathCheck('hasSharedKey', False),
            JMESPathCheck('hasSshKey', False),
            JMESPathCheck('hasSshPassword', None),
            JMESPathCheck('homeDirectory', 'home'),
            JMESPathCheck('name', username),
            JMESPathCheck('length(permissionScopes)', 2),
            JMESPathCheck('permissionScopes[0].permissions', 'r'),
            JMESPathCheck('permissionScopes[0].service', 'blob'),
            JMESPathCheck('permissionScopes[0].resourceName', 'container1')
        )

        self.cmd('{cmd} update --account-name {sa} -g {rg} -n {username} --home-directory home2 '
                 '--permission-scope permissions=rw service=file resource-name=share2').assert_with_checks(
            JMESPathCheck('homeDirectory', 'home2'),
            JMESPathCheck('length(permissionScopes)', 1),
            JMESPathCheck('permissionScopes[0].permissions', 'rw'),
            JMESPathCheck('permissionScopes[0].service', 'file'),
            JMESPathCheck('permissionScopes[0].resourceName', 'share2')
        )

        self.cmd('{cmd} list --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('value[0].hasSshKey', False),
            JMESPathCheck('value[0].hasSshPassword', False),
            JMESPathCheck('value[0].homeDirectory', 'home2'),
            JMESPathCheck('value[0].length(permissionScopes)', 1),
            JMESPathCheck('value[0].sshAuthorizedKeys', None)
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
