# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               StorageAccountPreparer, api_version_constraint)
from azure.cli.core.profiles import ResourceType
from ..storage_test_util import StorageScenarioMixin
from knack.util import CLIError


class FileServicePropertiesTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_file_soft_delete')
    @StorageAccountPreparer(name_prefix='filesoftdelete', kind='StorageV2', location='eastus2euap')
    def test_storage_account_file_delete_retention_policy(self, resource_group, storage_account):
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account file-service-properties'
        })
        self.cmd('{cmd} show --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy', None))

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} update --enable-delete-retention true -n {sa} -g {rg}')

        with self.assertRaisesRegexp(CLIError, "Delete Retention Policy hasn't been enabled,"):
            self.cmd('{cmd} update --delete-retention-days 1 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} update --enable-delete-retention false --delete-retention-days 1')

        self.cmd(
            '{cmd} update --enable-delete-retention true --delete-retention-days 10 -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 10))

        self.cmd('{cmd} update --delete-retention-days 1 -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', True),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 1))

        self.cmd('{cmd} update --enable-delete-retention false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', None))

        self.cmd(
            '{cmd} update --set shareDeleteRetentionPolicy.enabled=false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', None))

        self.cmd('{cmd} show -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('shareDeleteRetentionPolicy.enabled', False),
            JMESPathCheck('shareDeleteRetentionPolicy.days', 0))

    @api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix='cli_file_smb')
    @StorageAccountPreparer(name_prefix='filesmb', kind='FileStorage', sku='Premium_LRS', location='centraluseuap')
    def test_storage_account_file_smb_multichannel(self, resource_group, storage_account):
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account file-service-properties'
        })
        self.cmd('{cmd} show --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd(
            '{cmd} update --enable-smb-multichannel -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', True))

        self.cmd(
            '{cmd} update --enable-smb-multichannel false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd(
            '{cmd} update --enable-smb-multichannel true -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', True))

        self.cmd(
            '{cmd} update --set protocolSettings.smb.multichannel.enabled=false -n {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))

        self.cmd('{cmd} show --account-name {sa} -g {rg}').assert_with_checks(
            JMESPathCheck('protocolSettings.smb.multichannel.enabled', False))
