# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
from azure.cli.testsdk import LiveScenarioTest, StorageAccountPreparer, ResourceGroupPreparer, JMESPathCheck
from ..storage_test_util import StorageScenarioMixin, StorageTestFilesPreparer


class StorageFileBatchOperationScenarios(StorageScenarioMixin, LiveScenarioTest):

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    @StorageTestFilesPreparer()
    def test_storage_file_batch_upload_scenarios_v2(self, test_dir, storage_account_info):
        # upload without pattern
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --max-connections 3', storage_account_info,
                         test_dir, src_share)
        self.storage_cmd('storage file download-batch -s {} -d "{}"', storage_account_info, src_share, local_folder)
        self.assertEqual(41, sum(len(f) for r, d, f in os.walk(local_folder)))

        # upload with pattern apple/*
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --pattern apple/*', storage_account_info, test_dir,
                         src_share)
        self.storage_cmd('storage file download-batch -s {} -d "{}"', storage_account_info, src_share, local_folder)
        self.assertEqual(10, sum(len(f) for r, d, f in os.walk(local_folder)))

        # upload with pattern */file_0
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        share_url = self.storage_cmd('storage file url -s {} -p \'\' -otsv', storage_account_info,
                                     src_share).output.strip()[:-1]
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --pattern */file_0', storage_account_info, test_dir,
                         share_url)
        self.storage_cmd('storage file download-batch -s {} -d "{}"', storage_account_info, src_share, local_folder)
        self.assertEqual(4, sum(len(f) for r, d, f in os.walk(local_folder)))

        # upload with pattern nonexists/*
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --pattern nonexists/*', storage_account_info,
                         test_dir, src_share)
        self.storage_cmd('storage file download-batch -s {} -d "{}"', storage_account_info, src_share, local_folder)
        self.assertEqual(0, sum(len(f) for r, d, f in os.walk(local_folder)))

        # upload while specifying share path
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        share_url = self.storage_cmd('storage file url -s {} -p \'\' -otsv', storage_account_info,
                                     src_share).output.strip()[:-1]
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --pattern */file_0 --destination-path some_dir',
                         storage_account_info, test_dir, share_url)
        self.storage_cmd('storage file download-batch -s {} -d "{}" --pattern some_dir*', storage_account_info,
                         src_share, local_folder)
        self.assertEqual(4, sum(len(f) for r, d, f in os.walk(local_folder)))

        # upload to specifying share path
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        sub_dir = 'test_dir/sub_dir'
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --pattern */file_0 --destination-path {} ',
                         storage_account_info, test_dir, src_share, sub_dir)
        self.storage_cmd('storage file download-batch -s {} -d "{}"', storage_account_info, src_share + "/" + sub_dir,
                         local_folder)
        self.assertEqual(4, sum(len(f) for r, d, f in os.walk(local_folder)))

        # upload with content settings
        src_share = self.create_share(storage_account_info)
        local_folder = self.create_temp_dir()
        self.storage_cmd('storage file upload-batch -s "{}" -d {} --pattern apple/file_0 '
                         '--content-cache-control no-cache '
                         '--content-disposition attachment '
                         '--content-encoding compress '
                         '--content-language en-US '
                         '--content-type "multipart/form-data;" '
                         '--metadata key=val', storage_account_info, test_dir, src_share)
        self.storage_cmd('storage file show -s {} -p "{}" ', storage_account_info, src_share, 'apple/file_0').\
            assert_with_checks(JMESPathCheck('name', 'file_0'),
                               JMESPathCheck('properties.contentSettings.cacheControl', 'no-cache'),
                               JMESPathCheck('properties.contentSettings.contentDisposition', 'attachment'),
                               JMESPathCheck('properties.contentSettings.contentEncoding', 'compress'),
                               JMESPathCheck('properties.contentSettings.contentLanguage', 'en-US'),
                               JMESPathCheck('properties.contentSettings.contentType', 'multipart/form-data;'),
                               JMESPathCheck('metadata', {'key': 'val'}))
