# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os

from azure.cli.testsdk import (ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck, ScenarioTest)
from ..storage_test_util import StorageScenarioMixin


class StorageFileShareScenarios(StorageScenarioMixin, ScenarioTest):

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_storage_file_upload_small_file_v2(self, resource_group, storage_account_info):
        account_info = storage_account_info
        share_name = self.create_share(account_info)

        curr_dir = os.path.dirname(os.path.realpath(__file__))
        local_file = os.path.join(curr_dir, 'upload_file').replace('\\', '\\\\')
        local_file_name = 'upload_file'

        self.storage_cmd('storage file upload -s {} --source "{}" '
                         '--content-cache-control no-cache '
                         '--content-disposition attachment '
                         '--content-encoding compress '
                         '--content-language en-US '
                         '--content-type "multipart/form-data;" '
                         '--metadata key=val ', account_info, share_name, local_file)

        self.storage_cmd('storage file show -s {} -p "{}"', account_info, share_name, local_file_name) \
            .assert_with_checks(JMESPathCheck('name', local_file_name),
                                JMESPathCheck('properties.contentSettings.cacheControl', 'no-cache'),
                                JMESPathCheck('properties.contentSettings.contentDisposition', 'attachment'),
                                JMESPathCheck('properties.contentSettings.contentEncoding', 'compress'),
                                JMESPathCheck('properties.contentSettings.contentLanguage', 'en-US'),
                                JMESPathCheck('properties.contentSettings.contentType', 'multipart/form-data;'),
                                JMESPathCheck('metadata', {'key': 'val'}))

        dest_dir = 'dest_dir'

        from azure.core.exceptions import ResourceNotFoundError
        with self.assertRaises(ResourceNotFoundError):
            self.storage_cmd('storage file upload -s {} --source "{}" -p {}',
                             account_info, share_name, local_file, dest_dir)

        self.storage_cmd('storage directory create -s {} -n {}', account_info, share_name, dest_dir)

        self.storage_cmd('storage file upload -s {} --source "{}" -p {}',
                         account_info, share_name, local_file, dest_dir)

        self.storage_cmd('storage file show -s {} -p "{}"', account_info, share_name, dest_dir + '/' + local_file_name) \
            .assert_with_checks(JMESPathCheck('name', local_file_name))

        dest_file = 'dest_file.json'

        self.storage_cmd('storage file upload -s {} --source "{}" -p {}',
                         account_info, share_name, local_file, dest_file)

        self.storage_cmd('storage file show -s {} -p "{}"', account_info, share_name, dest_file) \
            .assert_with_checks(JMESPathCheck('name', dest_file))

        dest_path = dest_dir + '/' + dest_file

        self.storage_cmd('storage file upload -s {} --source "{}" -p {}',
                         account_info, share_name, local_file, dest_path)

        self.storage_cmd('storage file show -s {} -p "{}"', account_info, share_name, dest_path) \
            .assert_with_checks(JMESPathCheck('name', dest_file))

        sub_deep_path = dest_dir + '/' + 'sub_dir'

        self.storage_cmd('storage directory create -s {} -n {}', account_info, share_name, sub_deep_path)

        self.storage_cmd('storage file upload -s {} --source "{}" -p {}',
                         account_info, share_name, local_file, sub_deep_path)

        self.storage_cmd('storage file show -s {} -p "{}"', account_info, share_name,
                         sub_deep_path + '/' + local_file_name). \
            assert_with_checks(JMESPathCheck('name', local_file_name))

        sub_deep_file = sub_deep_path + '/' + dest_file

        self.storage_cmd('storage file upload -s {} --source "{}" -p {}',
                         account_info, share_name, local_file, sub_deep_file)

        self.storage_cmd('storage file show -s {} -p "{}"', account_info, share_name,
                         sub_deep_file).assert_with_checks(JMESPathCheck('name', dest_file))
