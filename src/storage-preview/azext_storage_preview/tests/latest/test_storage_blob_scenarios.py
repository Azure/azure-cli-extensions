# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer,
                               JMESPathCheck, api_version_constraint)

from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_PREVIEW_STORAGE


@api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-12-01')
class StorageBlobUploadTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(location='westcentralus')
    def test_storage_blob_update_service_properties(self, resource_group):
        storage_account = self.create_random_name(prefix='account', length=24)

        self.cmd('storage account create -n {} -g {} --kind StorageV2 --https-only '.format(storage_account, resource_group))
        account_info = self.get_account_info(resource_group, storage_account)

        self.storage_cmd('storage blob service-properties show', account_info) \
            .assert_with_checks(JMESPathCheck('staticWebsite.enabled', False))

        self.storage_cmd('storage blob service-properties update --static-website --index-document index.html '
                         '--404-document error.html', account_info)

        self.storage_cmd('storage blob service-properties show', account_info) \
            .assert_with_checks(JMESPathCheck('staticWebsite.enabled', True),
                                JMESPathCheck('staticWebsite.errorDocument_404Path', 'error.html'),
                                JMESPathCheck('staticWebsite.indexDocument', 'index.html'))


if __name__ == '__main__':
    unittest.main()
