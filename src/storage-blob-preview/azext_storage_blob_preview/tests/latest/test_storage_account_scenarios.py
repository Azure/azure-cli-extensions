# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from azure.cli.testsdk import (ScenarioTest, LocalContextScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               StorageAccountPreparer, api_version_constraint, live_only, LiveScenarioTest)
from azure.cli.core.profiles import ResourceType
from ..storage_test_util import StorageScenarioMixin
from knack.util import CLIError
from datetime import datetime, timedelta
from azure_devtools.scenario_tests import AllowLargeResponse


@api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2019-06-01')
class BlobServicePropertiesTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer()
    def test_management_policy(self, resource_group):
        import os
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


@api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2019-04-01')
class BlobServicePropertiesTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer(kind='StorageV2')
    def test_storage_account_update_change_feed(self):
        result = self.cmd('storage account blob-service-properties update --enable-change-feed true -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['changeFeed']['enabled'], True)

        result = self.cmd('storage account blob-service-properties update --enable-change-feed false -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['changeFeed']['enabled'], False)

        result = self.cmd('storage account blob-service-properties update --enable-change-feed -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['changeFeed']['enabled'], True)

        result = self.cmd('storage account blob-service-properties show -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['changeFeed']['enabled'], True)

    @ResourceGroupPreparer(name_prefix='cli_storage_account_update_delete_retention_policy')
    @StorageAccountPreparer(kind='StorageV2')
    def test_storage_account_update_delete_retention_policy(self, resource_group, storage_account):
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account blob-service-properties update'
        })

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-delete-retention true -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-delete-retention false --delete-retention-days 365 -n {sa} -g {rg}').get_output_in_json()

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --delete-retention-days 1 -n {sa} -g {rg}').get_output_in_json()

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-delete-retention true --delete-retention-days -1 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-delete-retention true --delete-retention-days 0 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-delete-retention true --delete-retention-days 366 -n {sa} -g {rg}')

        result = self.cmd('{cmd} --enable-delete-retention true --delete-retention-days 1 -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['deleteRetentionPolicy']['enabled'], True)
        self.assertEqual(result['deleteRetentionPolicy']['days'], 1)

        result = self.cmd('{cmd} --enable-delete-retention true --delete-retention-days 100 -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['deleteRetentionPolicy']['enabled'], True)
        self.assertEqual(result['deleteRetentionPolicy']['days'], 100)

        result = self.cmd('{cmd} --enable-delete-retention true --delete-retention-days 365 -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['deleteRetentionPolicy']['enabled'], True)
        self.assertEqual(result['deleteRetentionPolicy']['days'], 365)

        result = self.cmd('{cmd} --enable-delete-retention false -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['deleteRetentionPolicy']['enabled'], False)
        self.assertEqual(result['deleteRetentionPolicy']['days'], None)

    @api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix="cli_test_sa_versioning")
    @StorageAccountPreparer(location="eastus2euap", kind="StorageV2")
    def test_storage_account_update_versioning(self):
        result = self.cmd('storage account blob-service-properties update --enable-versioning true -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['isVersioningEnabled'], True)

        result = self.cmd('storage account blob-service-properties update --enable-versioning false -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['isVersioningEnabled'], False)

        result = self.cmd('storage account blob-service-properties update --enable-versioning -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['isVersioningEnabled'], True)

        result = self.cmd('storage account blob-service-properties show -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['isVersioningEnabled'], True)

    @api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix='cli_storage_account_update_delete_retention_policy')
    @StorageAccountPreparer(kind='StorageV2', name_prefix='clitest', location='eastus2euap')
    def test_storage_account_update_container_delete_retention_policy(self, resource_group, storage_account):
        self.kwargs.update({
            'sa': storage_account,
            'rg': resource_group,
            'cmd': 'storage account blob-service-properties update'
        })

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-container-delete-retention true -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-container-delete-retention false --container-delete-retention-days 365 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --container-delete-retention-days 1 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-container-delete-retention true --container-delete-retention-days -1 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-container-delete-retention true --container-delete-retention-days 0 -n {sa} -g {rg}')

        with self.assertRaises(SystemExit):
            self.cmd('{cmd} --enable-container-delete-retention true --container-delete-retention-days 366 -n {sa} -g {rg}')

        result = self.cmd('{cmd} --enable-container-delete-retention true --container-delete-retention-days 1 -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['containerDeleteRetentionPolicy']['enabled'], True)
        self.assertEqual(result['containerDeleteRetentionPolicy']['days'], 1)

        result = self.cmd('{cmd} --enable-container-delete-retention true --container-delete-retention-days 100 -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['containerDeleteRetentionPolicy']['enabled'], True)
        self.assertEqual(result['containerDeleteRetentionPolicy']['days'], 100)

        result = self.cmd('{cmd} --enable-container-delete-retention true --container-delete-retention-days 365 -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['containerDeleteRetentionPolicy']['enabled'], True)
        self.assertEqual(result['containerDeleteRetentionPolicy']['days'], 365)

        result = self.cmd('{cmd} --enable-container-delete-retention false -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['containerDeleteRetentionPolicy']['enabled'], False)
        self.assertEqual(result['containerDeleteRetentionPolicy']['days'], None)

    @api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix="cli_test_sa_versioning")
    @StorageAccountPreparer(location="eastus2euap", kind="StorageV2")
    def test_storage_account_update_last_access(self):
        result = self.cmd('storage account blob-service-properties update --enable-last-access-tracking true -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['enable'], True)

        result = self.cmd(
            'storage account blob-service-properties show -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['enable'], True)
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['name'], "AccessTimeTracking")
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['trackingGranularityInDays'], 1)
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['blobType'][0], "blockBlob")

        result = self.cmd('storage account blob-service-properties update --enable-last-access-tracking false -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['lastAccessTimeTrackingPolicy'], None)

        result = self.cmd('storage account blob-service-properties update --enable-last-access-tracking -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['enable'], True)

        result = self.cmd('storage account blob-service-properties show -n {sa} -g {rg}').get_output_in_json()
        self.assertEqual(result['lastAccessTimeTrackingPolicy']['enable'], True)
