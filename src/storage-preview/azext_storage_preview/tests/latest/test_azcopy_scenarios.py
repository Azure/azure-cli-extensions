# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import shutil
from azure.cli.testsdk import (StorageAccountPreparer, LiveScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint)
from .storage_test_util import StorageScenarioMixin, StorageTestFilesPreparer
from ...profiles import CUSTOM_MGMT_PREVIEW_STORAGE


class StorageAzcopyTests(StorageScenarioMixin, LiveScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    @StorageTestFilesPreparer()
    def test_azcopy_flow(self, resource_group, storage_account_info, test_dir):
        storage_account, _ = storage_account_info
        container = self.create_container(storage_account_info)

        # upload one blob
        blob = 'blob'
        self.cmd('storage azcopy blob upload -s "{}" -c {} -d {} --account-name {}'.format(
            os.path.join(test_dir, 'readme'), container, blob, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 1))
        self.cmd('storage azcopy blob delete -c {} --account-name {} -t {}'.format(
            container, storage_account, blob))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 0))

        # upload multiple blobs
        self.cmd('storage azcopy blob upload -s "{}" -c {} --account-name {} --recursive'.format(
            os.path.join(test_dir, '*'), container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 41))

        self.cmd('storage azcopy blob delete -c {} --account-name {} -t {}'.format(
            container, storage_account, 'readme'))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 40))
        self.cmd('storage azcopy blob delete -c {} --account-name {} -t {}'.format(
            container, storage_account, 'butter'))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 30))

        self.cmd('storage azcopy blob delete -c {} --account-name {} --recursive'.format(
            container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 0))

        # repopulate container
        self.cmd('storage azcopy blob upload -s "{}" -c {} --account-name {} --recursive'.format(
            os.path.join(test_dir, '*'), container, storage_account))

        # download a blob
        download_path = os.path.join(test_dir, 'downloads')
        os.mkdir(download_path)
        self.cmd('storage azcopy blob download -s readme -c {} --account-name {} -d "{}"'.format(
            container, storage_account, download_path))
        self.assertEqual(len(os.listdir(download_path)), 1)

        # download multiple blobs
        self.cmd('storage azcopy blob download -s * -c {} --account-name {} -d "{}"'.format(
            container, storage_account, download_path))
        self.assertEqual(len(os.listdir(download_path)), 1)
        self.cmd('storage azcopy blob download -s * -c {} --account-name {} -d "{}" --recursive'.format(
            container, storage_account, download_path))
        # 1 file(readme), 3 directories(apple, butter, duff)
        self.assertEqual(len(os.listdir(download_path)), 4)
        # 10 files in apple
        self.assertEqual(len(os.listdir(os.path.join(download_path, 'apple'))), 10)
        # 10 files, 1 directory(charlie) in butter
        self.assertEqual(len(os.listdir(os.path.join(download_path, 'butter'))), 11)

        self.cmd('storage azcopy blob delete -c {} --account-name {} --recursive'.format(
            container, storage_account))

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    @StorageTestFilesPreparer()
    def test_azcopy_sync(self, resource_group, storage_account_info, test_dir):
        storage_account, _ = storage_account_info
        container = self.create_container(storage_account_info)

        # sync directory
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {}'.format(
            test_dir, container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 41))

        self.cmd('storage azcopy blob delete -c {} --account-name {} --recursive'.format(
            container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 0))

        # resync container
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {}'.format(
            test_dir, container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 41))

        # update file
        with open(os.path.join(test_dir, 'readme'), 'w') as f:
            f.write('updated.')
        # sync one blob
        self.cmd('storage blob list -c {} --account-name {} --prefix readme'.format(
            container, storage_account), checks=JMESPathCheck('[0].properties.contentLength', 87))
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {} -d readme'.format(
            os.path.join(test_dir, 'readme'), container, storage_account))
        self.cmd('storage blob list -c {} --account-name {} --prefix readme'.format(
            container, storage_account), checks=JMESPathCheck('[0].properties.contentLength', 8))

        # delete one file and sync
        os.remove(os.path.join(test_dir, 'readme'))
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {}'.format(
            test_dir, container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 40))

        # delete one folder and sync
        shutil.rmtree(os.path.join(test_dir, 'apple'))
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {}'.format(
            test_dir, container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 30))

        # syn with another folder
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {}'.format(
            os.path.join(test_dir, 'butter'), container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 20))

        # empty the folder and sync
        shutil.rmtree(os.path.join(test_dir, 'butter'))
        shutil.rmtree(os.path.join(test_dir, 'duff'))
        self.cmd('storage azcopy blob sync -s "{}" -c {} --account-name {}'.format(
            test_dir, container, storage_account))
        self.cmd('storage blob list -c {} --account-name {}'.format(
            container, storage_account), checks=JMESPathCheck('length(@)', 0))
