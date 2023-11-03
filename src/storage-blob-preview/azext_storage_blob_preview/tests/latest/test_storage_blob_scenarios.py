# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, api_version_constraint)
from azure.cli.core.profiles import ResourceType

from ..storage_test_util import StorageScenarioMixin


@api_version_constraint(ResourceType.MGMT_STORAGE, min_api='2016-12-01')
class StorageBlobUploadTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer(kind='StorageV2')
    def test_storage_blob_soft_delete(self, resource_group, storage_account_info):
        account_info = storage_account_info
        container = self.create_container(account_info)
        import time

        # create a blob
        local_file = self.create_temp_file(1)
        blob_name = self.create_random_name(prefix='blob', length=24)

        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} --type block', account_info,
                         container, local_file, blob_name)
        self.assertEqual(len(self.storage_cmd('storage blob list -c {}',
                                              account_info, container).get_output_in_json()), 1)

        # set delete-policy to enable soft-delete
        self.storage_cmd('storage blob service-properties delete-policy update --enable true --days-retained 2',
                         account_info)
        self.storage_cmd('storage blob service-properties delete-policy show',
                         account_info).assert_with_checks(JMESPathCheck('enabled', True),
                                                          JMESPathCheck('days', 2))
        time.sleep(10)
        # soft-delete and check
        self.storage_cmd('storage blob delete -c {} -n {}', account_info, container, blob_name)
        self.assertEqual(len(self.storage_cmd('storage blob list -c {}',
                                              account_info, container).get_output_in_json()), 0)

        # undelete and check
        time.sleep(60)
        self.storage_cmd('storage blob undelete -c {} -n {}', account_info, container, blob_name)
        self.assertEqual(len(self.storage_cmd('storage blob list -c {}',
                                              account_info, container).get_output_in_json()), 1)

    @ResourceGroupPreparer()
    @StorageAccountPreparer(kind='StorageV2')
    def test_storage_blob_update_service_properties(self, resource_group, storage_account_info):
        account_info = storage_account_info

        self.storage_cmd('storage blob service-properties show', account_info) \
            .assert_with_checks(JMESPathCheck('staticWebsite.enabled', False),
                                JMESPathCheck('hourMetrics.enabled', True),
                                JMESPathCheck('minuteMetrics.enabled', False),
                                JMESPathCheck('minuteMetrics.includeApis', None),
                                JMESPathCheck('logging.delete', False))

        self.storage_cmd('storage blob service-properties update --static-website --index-document index.html '
                         '--404-document error.html', account_info) \
            .assert_with_checks(JMESPathCheck('staticWebsite.enabled', True),
                                JMESPathCheck('staticWebsite.errorDocument_404Path', 'error.html'),
                                JMESPathCheck('staticWebsite.indexDocument', 'index.html'))

        self.storage_cmd('storage blob service-properties update --delete-retention --delete-retention-period 1',
                         account_info) \
            .assert_with_checks(JMESPathCheck('staticWebsite.enabled', True),
                                JMESPathCheck('staticWebsite.errorDocument_404Path', 'error.html'),
                                JMESPathCheck('staticWebsite.indexDocument', 'index.html'),
                                JMESPathCheck('deleteRetentionPolicy.enabled', True),
                                JMESPathCheck('deleteRetentionPolicy.days', 1))

        self.storage_cmd('storage blob service-properties show', account_info) \
            .assert_with_checks(JMESPathCheck('staticWebsite.enabled', True),
                                JMESPathCheck('staticWebsite.errorDocument_404Path', 'error.html'),
                                JMESPathCheck('staticWebsite.indexDocument', 'index.html'),
                                JMESPathCheck('deleteRetentionPolicy.enabled', True),
                                JMESPathCheck('deleteRetentionPolicy.days', 1))


if __name__ == '__main__':
    unittest.main()
