# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer, ScenarioTest,
                               JMESPathCheck, api_version_constraint)

from .storage_test_util import StorageScenarioMixin, StorageTestFilesPreparer
from ...profiles import CUSTOM_MGMT_STORAGE


class StorageADLSTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2018-02-01')
    @ResourceGroupPreparer()
    def test_storage_adls_blob(self, resource_group):
        storage_account = self.create_random_name(prefix='clitestaldsaccount', length=24)
        self.kwargs.update({
            'sc': storage_account,
            'rg': resource_group
        })
        self.cmd('storage account create -n {sc} -g {rg} --kind StorageV2 --hierarchical-namespace true --https-only ')
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
            .assert_with_checks(JMESPathCheck('length(@)', 1)) \
            .assert_with_checks(JMESPathCheck('[0].metadata.hdi_isfolder', 'true'))
        self.storage_cmd('storage blob directory show -c {} -d {} ', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('metadata.hdi_isfolder', "true"))
        self.storage_cmd('storage blob directory access show -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('permissions', "rwxr-x---"))
        # Argument validation: Throw error when using existing directory name
        with self.assertRaises(SystemExit):
            self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory)

        # Create a storage blob directory with permissions
        directory2 = 'testdirectory2'
        self.storage_cmd('storage blob directory create -c {} -d {} --permissions rwxrwxrwx --umask 0000',
                         account_info, container, directory2)
        self.storage_cmd('storage blob directory show -c {} -d {} ', account_info, container, directory2) \
            .assert_with_checks(JMESPathCheck('metadata.hdi_isfolder', "true"))
        self.storage_cmd('storage blob directory access show -c {} -d {}', account_info, container, directory2) \
            .assert_with_checks(JMESPathCheck('permissions', "rwxrwxrwx"))

        # Storage blob access control
        local_file = self.create_temp_file(128)
        blob = self.create_random_name('blob', 24)
        self.storage_cmd('storage blob upload -c {} -f "{}" -n {}', account_info, container, local_file, blob)

        acl = "user::rwx,group::r--,other::---"
        self.storage_cmd('storage blob access set -c {} -b {} -a "{}"', account_info, container, blob, acl)
        self.storage_cmd('storage blob access show -c {} -b {}', account_info, container, blob) \
            .assert_with_checks(JMESPathCheck('acl', acl))
        self.storage_cmd('storage blob access update -c {} -b {} --permissions "rwxrwxrwx"', account_info,
                         container, blob, acl)
        self.storage_cmd('storage blob access show -c {} -b {}', account_info, container, blob)\
            .assert_with_checks(JMESPathCheck('permissions', "rwxrwxrwx"))

        # Storage blob directory access control
        acl = "user::rwx,group::r--,other::---"
        self.storage_cmd('storage blob directory access set -c {} -d {} -a "{}"', account_info, container, directory, acl)
        self.storage_cmd('storage blob directory access show -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('acl', acl))
        self.storage_cmd('storage blob directory access update -c {} -d {} --permissions "rwxrwxrwx"', account_info,
                         container, directory, acl)
        self.storage_cmd('storage blob directory access show -c {} -d {}', account_info, container,
                         directory).assert_with_checks(JMESPathCheck('permissions', "rwxrwxrwx"))

        # Storage blob directory metadata
        self.storage_cmd('storage blob directory metadata update -c {} -d {} --metadata "tag1=value1"', account_info,
                         container, directory)
        self.storage_cmd('storage blob directory metadata show -c {} -d {} ', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('tag1', "value1"))

        # Remove blob directory
        self.storage_cmd('storage blob directory delete -c {} -d {} --recursive', account_info,
                         container, directory, directory)
        self.storage_cmd('storage blob directory exists -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('exists', False))


class StorageADLSDirectoryMoveTests(StorageScenarioMixin, LiveScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2018-02-01')
    @StorageTestFilesPreparer()
    @ResourceGroupPreparer()
    def test_storage_adls_blob_directory_move(self, resource_group, test_dir):
        storage_account = self.create_random_name(prefix='clitestaldsaccount', length=24)
        self.kwargs.update({
            'sc': storage_account,
            'rg': resource_group
        })
        self.cmd('storage account create -n {sc} -g {rg} -l centralus --kind StorageV2 --hierarchical-namespace true '
                 ' --https-only')
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        directory = 'dir'
        des_directory = 'dir1'

        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory)
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'apple'))
        # Move from a directory to a nonexistent directory
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory move -c {} -d {} -s {}', account_info,
                         container, des_directory, directory)
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 11))

        # Test directory name contains Spaces
        contain_space_dir = 'test move directory'
        # Move directory to contain_space_dir
        self.storage_cmd('storage blob directory exists -c "{}" -d "{}"', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob directory exists -c "{}" -d "{}"', account_info, container, contain_space_dir) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory move -c "{}" -d "{}" -s "{}"', account_info, container,
                         contain_space_dir, des_directory)
        self.storage_cmd('storage blob directory exists -c "{}" -d "{}"', account_info, container, contain_space_dir) \
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob directory exists -c "{}" -d "{}"', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        # Move contain_space_dir back to directory
        self.storage_cmd('storage blob directory move -c "{}" -d "{}" -s "{}"', account_info, container,
                         des_directory, contain_space_dir)
        self.storage_cmd('storage blob directory exists -c "{}" -d "{}"', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob directory exists -c "{}" -d "{}"', account_info, container, contain_space_dir) \
            .assert_with_checks(JMESPathCheck('exists', False))

        # Move from a directory to a existing empty directory
        directory2 = 'dir2'
        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory2)
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', True))
        self.storage_cmd('storage blob directory move -c {} -d {} -s {}', account_info,
                         container, directory2, des_directory)
        self.storage_cmd('storage blob directory exists -c {} -d {} ', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('exists', False))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory2) \
            .assert_with_checks(JMESPathCheck('length(@)', 12))

        # Move from a directory to a existing nonempty directory with mode "legacy"
        directory3 = 'dir3'
        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory3)
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}"', account_info, container, directory3,
                         os.path.join(test_dir, 'readme'))
        self.cmd('storage blob directory move -c {} -d {} -s {} --account-name {} --move-mode legacy'.format(
            container, directory3, directory2, storage_account), expect_failure=True)

        # Move from a directory to a existing nonempty directory with mode "posix"
        self.storage_cmd('storage blob directory move -c {} -d {} -s {} --move-mode posix', account_info,
                         container, directory3, directory2)
        self.storage_cmd('storage blob directory exists -c {} -d {}', account_info, container,
                         '/'.join([directory3, directory2])) \
            .assert_with_checks(JMESPathCheck('exists', True))

        # Move from a subdirectory to a new directory with mode "posix"
        directory4 = "dir4"
        self.storage_cmd('storage blob directory move -c {} -d {} -s {} --move-mode posix', account_info,
                         container, directory4, '/'.join([directory3, directory2]))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory4) \
            .assert_with_checks(JMESPathCheck('length(@)', 12))

        # Argument validation: Throw error when source path is blob name
        with self.assertRaises(SystemExit):
            self.storage_cmd('storage blob directory move -c {} -d {} -s {}', account_info,
                             container, directory4, '/'.join([directory3, 'readme']))


class StorageADLSMoveTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2018-02-01')
    @ResourceGroupPreparer(location="centralus")
    def test_storage_adls_blob_move(self, resource_group):
        storage_account = self.create_random_name(prefix='clitestaldsaccount', length=24)
        self.kwargs.update({
            'sc': storage_account,
            'rg': resource_group
        })
        self.cmd('storage account create -n {sc} -g {rg} --kind StorageV2 --hierarchical-namespace true -l centralus '
                 '--https-only')
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        directory = 'dir'
        des_directory = 'dir1'

        local_file = self.create_temp_file(128)
        blob = self.create_random_name('blob', 24)
        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory)
        self.storage_cmd('storage blob upload -c {} -f "{}" -n {}', account_info, container, local_file,
                         '/'.join([directory, blob]))

        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, des_directory)

        # Move a blob between different directory in a container
        self.storage_cmd('storage blob move -c {} -d {} -s {}', account_info,
                         container, '/'.join([des_directory, blob]), '/'.join([directory, blob]))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 0))

        # Move a blob in a directory
        new_blob = self.create_random_name('blob', 24)
        self.storage_cmd('storage blob move -c {} -d {} -s {}', account_info,
                         container, '/'.join([des_directory, new_blob]), '/'.join([des_directory, blob]))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, des_directory) \
            .assert_with_checks(JMESPathCheck('[0].name', '/'.join([des_directory, new_blob])))

        with self.assertRaises(SystemExit):
            self.storage_cmd('storage blob move -c {} -d {} -s {}', account_info,
                             container, blob, des_directory)


class StorageADLSDirectoryUploadTests(StorageScenarioMixin, LiveScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2018-02-01')
    @StorageTestFilesPreparer()
    @ResourceGroupPreparer()
    def test_storage_adls_blob_directory_upload(self, resource_group, test_dir):
        storage_account = self.create_random_name(prefix='clitestaldsaccount', length=24)
        self.kwargs.update({
            'sc': storage_account,
            'rg': resource_group
        })
        self.cmd('storage account create -n {sc} -g {rg} --kind StorageV2 --hierarchical-namespace true --https-only')
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        directory = 'dir'

        self.storage_cmd('storage blob directory create -c {} -d {}', account_info, container, directory)

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
        self.storage_cmd('storage blob directory list -c {} -d {} --num-results 9', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 9))

        # Upload files in a local directory to the blob directory
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'butter/file_*'))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, directory) \
            .assert_with_checks(JMESPathCheck('length(@)', 22))

        # Upload files in a local directory to the blob directory
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'butter/file_*'))

        # Upload files in a local directory to the blob subdirectory
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         '/'.join([directory, 'subdir']), os.path.join(test_dir, 'butter/file_*'))
        self.storage_cmd('storage blob directory list -c {} -d {}', account_info, container, '/'.join([directory, 'subdir'])) \
            .assert_with_checks(JMESPathCheck('length(@)', 10))

        # Argument validation: Throw error when source path is blob name
        with self.assertRaises(SystemExit):
            self.cmd('storage blob directory upload -c {} -d {} -s {} --account-name {}'.format(
                container, '/'.join([directory, 'readme']), test_dir, storage_account))


class StorageADLSDirectoryDownloadTests(StorageScenarioMixin, LiveScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2018-02-01')
    @StorageTestFilesPreparer()
    @ResourceGroupPreparer()
    def test_storage_adls_blob_directory_download(self, resource_group, test_dir):
        storage_account = self.create_random_name(prefix='clitestaldsaccount', length=24)
        self.kwargs.update({
            'sc': storage_account,
            'rg': resource_group
        })
        self.cmd('storage account create -n {sc} -g {rg} --kind StorageV2 --hierarchical-namespace true --https-only ')
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info)
        directory = 'dir'
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'readme'))
        self.storage_cmd('storage blob directory upload -c {} -d {} -s "{}" --recursive', account_info, container,
                         directory, os.path.join(test_dir, 'apple'))

        local_folder = self.create_temp_dir()
        # Download a single file
        self.storage_cmd('storage blob directory download -c {} -s "{}" -d "{}" --recursive', account_info, container,
                         '/'.join([directory, 'readme']), local_folder)
        self.assertEqual(1, sum(len(f) for r, d, f in os.walk(local_folder)))

        # Download entire directory
        self.storage_cmd('storage blob directory download -c {} -s {} -d "{}" --recursive', account_info, container,
                         directory, local_folder)
        self.assertEqual(2, sum(len(d) for r, d, f in os.walk(local_folder)))
        self.assertEqual(12, sum(len(f) for r, d, f in os.walk(local_folder)))

        # Download an entire subdirectory of a storage blob directory.
        self.storage_cmd('storage blob directory download -c {} -s {} -d "{}" --recursive', account_info, container,
                         '/'.join([directory, 'apple']), local_folder)
        self.assertEqual(3, sum(len(d) for r, d, f in os.walk(local_folder)))


if __name__ == '__main__':
    unittest.main()
