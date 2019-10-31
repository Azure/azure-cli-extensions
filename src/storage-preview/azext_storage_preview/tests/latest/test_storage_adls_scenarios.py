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

        # Upload a single blob to the blob directory
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}"', account_info, container, directory,
                         os.path.join(test_dir, 'readme'))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        # Upload a local directory to the blob directory
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'apple'))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 12))

        # Upload files in a local directory to the blob directory
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'butter/file_*'))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 22))

        local_folder = self.create_temp_dir()
        # Download a single file
        self.storage_cmd('storage blob directory download -c {} -s "{}" -d "{}" --recursive', account_info, container,
                         os.path.join(directory, 'readme'), local_folder)
        self.assertEqual(1, sum(len(f) for r, d, f in os.walk(local_folder)))

        # Download entire directory
        self.storage_cmd('storage blob directory download -c {} -s {} -d "{}" --recursive', account_info, container,
                         directory, local_folder)
        self.assertEqual(2, sum(len(d) for r, d, f in os.walk(local_folder)))
        self.assertEqual(22, sum(len(f) for r, d, f in os.walk(local_folder)))

        # Download an entire subdirectory of a storage blob directory.
        self.storage_cmd('storage blob directory download -c {} -s {} -d "{}" --recursive', account_info, container,
                         '/'.join([directory, 'apple']), local_folder)
        self.assertEqual(3, sum(len(d) for r, d, f in os.walk(local_folder)))
        self.assertEqual(32, sum(len(f) for r, d, f in os.walk(local_folder)))

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
            .assert_with_checks(JMESPathCheck('length(@)', 22))

        # Storage blob directory access control
        acl = "user::rwx,group::r--,other::---"
        self.storage_cmd('storage blob directory access set -c {} -d {} -a "{}"', account_info, container, des_directory, acl)
        self.storage_cmd('storage blob directory access show -c {} -d {}', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('acl', acl))
        self.storage_cmd('storage blob directory access update -c {} -d {} --permissions "rwxrwxrwx"', account_info,
                         container, des_directory, acl)
        self.storage_cmd('storage blob directory access show -c {} -d {}', account_info, container,
                         des_directory).assert_with_checks(JMESPathCheck('permissions', "rwxrwxrwx"))

        # Storage blob directory metadata
        self.storage_cmd('storage blob directory metadata update -c {} -d {} --metadata "tag1=value1"', account_info,
                         container, des_directory)
        self.storage_cmd('storage blob directory metadata show -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('tag1', "value1"))

        # Remove blob directory
        self.storage_cmd('storage blob directory delete -c {} -d {} --recursive', account_info,
                         container, des_directory, directory)
        self.storage_cmd('storage blob directory exists -c {} -d {}', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', False))


if __name__ == '__main__':
    unittest.main()
