# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
from azure.cli.testsdk import (StorageAccountPreparer, LiveScenarioTest, JMESPathCheck, ResourceGroupPreparer,
                               api_version_constraint)
from .storage_test_util import StorageScenarioMixin, StorageTestFilesPreparer
from ...profiles import CUSTOM_MGMT_STORAGE


class StorageAzcopyTests(StorageScenarioMixin, LiveScenarioTest):
    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    @StorageTestFilesPreparer()
    def test_azcopy_flow(self, resource_group, storage_account_info, test_dir):
        storage_account, _ = storage_account_info
        src_container = self.create_container(storage_account_info)
    # def test_azcopy_flow(self, test_dir):
    #     storage_account = 'wilxstorage'
    #     container = 'wilxcontainer'

        # # remove this
        # self.cmd('storage azcopy blob delete -c {} --account-name {} --recursive'.format(
        #     container, storage_account))

        # upload one blob
        blob = 'blob'
        self.cmd('storage azcopy blob upload -s "{}" -c {} -d {} --account-name {}'.format(
            os.path.join(test_dir, 'readme') , container, blob, storage_account))
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
        # self.cmd('storage azcopy blob delete -c {} --account-name {} -t {}'.format(
        #     container, storage_account, '*'))
        # self.cmd('storage blob list -c {} --account-name {}'.format(
        #     container, storage_account), checks=JMESPathCheck('length(@)', 40))
        # self.cmd('storage azcopy blob delete -c {} --account-name {} -t {}'.format(
        #     container, storage_account, 'butter/*'))
        # self.cmd('storage blob list -c {} --account-name {}'.format(
        #     container, storage_account), checks=JMESPathCheck('length(@)', 30))
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
        self.assertEqual(len(os.listdir(download_path)), 41)

        self.cmd('storage azcopy blob delete -c {} --account-name {} --recursive'.format(
            container, storage_account))
