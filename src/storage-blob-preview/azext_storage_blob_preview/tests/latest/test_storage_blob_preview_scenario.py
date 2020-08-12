# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (JMESPathCheck, JMESPathCheckExists,
                               ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer)
from ..storage_test_util import StorageScenarioMixin


class StorageBlobScenarioTest(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='storage', kind='StorageV2', location='eastus2', sku='Standard_RAGZRS')
    def test_storage_blob_list_scenarios(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info, prefix="con")

        local_file = self.create_temp_file(128)
        blob_name1 = "/".join(["dir", self.create_random_name(prefix='blob', length=24)])
        blob_name2 = "/".join(["dir", self.create_random_name(prefix='blob', length=24)])

        # Prepare blob 1
        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} ', account_info,
                         container, local_file, blob_name1)

        # Test with include snapshot
        result = self.storage_cmd('storage blob snapshot -c {} -n {} ', account_info, container, blob_name1)\
            .get_output_in_json()
        self.assertIsNotNone(result['snapshot'])
        snapshot = result['snapshot']

        self.storage_cmd('storage blob list -c {} --include s', account_info, container) \
            .assert_with_checks(JMESPathCheck('[0].snapshot', snapshot))

        # Test with include metadata
        self.storage_cmd('storage blob metadata update -c {} -n {} --metadata test=1 ', account_info,
                         container, blob_name1)
        self.storage_cmd('storage blob metadata show -c {} -n {} ', account_info, container, blob_name1)\
            .assert_with_checks(JMESPathCheck('test', '1'))

        self.storage_cmd('storage blob list -c {} --include m', account_info, container) \
            .assert_with_checks(JMESPathCheck('[0].metadata.test', '1'))

        # Prepare blob 2
        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} ', account_info,
                         container, local_file, blob_name2)

        self.storage_cmd('storage blob list -c {} ', account_info, container).assert_with_checks(
            JMESPathCheck('length(@)', 2)
        )

        # Test num_results and next marker
        self.storage_cmd('storage blob list -c {} --num-results 1 ', account_info, container).assert_with_checks(
            JMESPathCheck('length(@)', 1))

        result = self.storage_cmd('storage blob list -c {} --num-results 1 --show-next-marker',
                                  account_info, container).get_output_in_json()
        self.assertIsNotNone(result[1]['nextMarker'])
        next_marker = result[1]['nextMarker']

        # Test with marker
        self.storage_cmd('storage blob list -c {} --marker {} ', account_info, container, next_marker) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        # Test with prefix
        self.storage_cmd('storage blob list -c {} --prefix {}', account_info, container, 'dir/') \
            .assert_with_checks(JMESPathCheck('length(@)', 2))

        # Test with include metadata, snapshot
        self.storage_cmd('storage blob list -c {} --include mscdv', account_info, container) \
            .assert_with_checks(JMESPathCheck('[0].metadata.test', '1'),
                                JMESPathCheck('[0].snapshot', snapshot))

        # Test with delimiter
        self.storage_cmd('storage blob list -c {} --delimiter "/"', account_info, container) \
            .assert_with_checks(JMESPathCheck('length(@)', 1),
                                JMESPathCheck('[0].name', 'dir/'))

        # Test secondary location
        account_name = account_info[0] + '-secondary'
        account_key = account_info[1]
        self.cmd('storage blob list -c {} --account-name {} --account-key {} '.format(
            container, account_name, account_key)).assert_with_checks(
            JMESPathCheck('length(@)', 2))

    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='version')
    def test_storage_blob_versioning(self, resource_group, storage_account):
        self.cmd('storage  account blob-service-properties update -n {} -g {} --enable-versioning '.format(
            storage_account, resource_group), checks=[
            JMESPathCheck('isVersioningEnabled', True)
        ])
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info, prefix="con")

        local_dir = self.create_temp_dir()
        local_file = self.create_temp_file(128)
        blob_name = self.create_random_name(prefix='blob', length=24)

        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} ', account_info,
                         container, local_file, blob_name)

        self.storage_cmd('storage blob show -c {} -n {} --version-id {}', account_info, container)

        self.storage_cmd('storage blob list -c {} --include v', account_info, container)

        self.storage_cmd('storage blob delete -c {} -n {} --version-id {}', account_info, container)




