# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer,
                               JMESPathCheck, api_version_constraint)

from .storage_test_util import StorageScenarioMixin, StorageTestFilesPreparer
from ...profiles import CUSTOM_MGMT_STORAGE


@api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2016-12-01')
class StorageBlobDirectoryTests(StorageScenarioMixin, ScenarioTest):
    @StorageTestFilesPreparer()
    @ResourceGroupPreparer(location='westcentralus')
    def test_storage_blob_directory(self, resource_group, test_dir):
        storage_account = self.create_random_name(prefix='clitestaldsaccount', length=24)
        self.kwargs.update({
            'sc': storage_account,
            'rg': resource_group
        })
        self.cmd('storage account create -n {sc} -g {rg} --kind StorageV2 --hierarchical-namespace true')
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        directory = 'testdirectory'

        # Create a storage blob directory and check its existence
        self.storage_cmd('storage blob directory exists -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory)
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, directory)\
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob list -c {}', account_info, container) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.storage_cmd('storage blob directory show -c {} -d {} ', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('metadata.hdi_isfolder', "true"))

        # TODO: Upload to the directory

        # TODO: Download from the directory

        # Move the blob directory to another directory
        des_directory = 'desdirectory'
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory move -c {} -d {} -s {}', account_info,
                         container, des_directory, directory)
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 0))

        #TODO: Storage blob directory access control


        # Remove blob directory
        self.storage_cmd('storage blob directory delete -c {} -d {}', account_info,
                         container, des_directory, directory)
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', False))


if __name__ == '__main__':
    unittest.main()
