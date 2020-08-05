# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (JMESPathCheck, JMESPathCheckExists, ScenarioTest, ResourceGroupPreparer,
                               StorageAccountPreparer)
from ..storage_test_util import StorageScenarioMixin

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageBlobScenarioTest(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='version')
    def test_storage_blob_list_scenarios(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info, prefix="con")

        local_dir = self.create_temp_dir()
        local_file = self.create_temp_file(128)
        blob_name = self.create_random_name(prefix='blob', length=24)

        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} ', account_info,
                         container, local_file, blob_name)

        self.storage_cmd('storage blob list -c {} ', account_info, container).assert_with_checks(
            JMESPathCheck('length(@', 1)
        )

        result = self.storage_cmd('storage blob list -c {} --num-results 1 --show-next-marker',
                                  account_info, container).output
        next_marker = result['nextResult']

        self.storage_cmd('storage blob list -c {} --marker {}', account_info, container, next_marker) \
            .assert_with_checks(JMESPathCheck('length(@', 1))

        self.storage_cmd('storage blob list -c {} --prefix {}', account_info, container, 'prefix') \
            .assert_with_checks(JMESPathCheck('length(@', 1))

        self.storage_cmd('storage blob list -c {} --include {}', account_info, container, 'prefix') \
            .assert_with_checks(JMESPathCheck('length(@', 1))

        self.storage_cmd('storage blob list -c {} --delimiter "/"', account_info, container, 'prefix') \
            .assert_with_checks(JMESPathCheck('length(@', 1))

    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='version')
    def test_storage_blob_versioning(self, resource_group, storage_account):
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info, prefix="con")

        local_dir = self.create_temp_dir()
        local_file = self.create_temp_file(128)
        blob_name = self.create_random_name(prefix='blob', length=24)

        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} ', account_info,
                         container, local_file, blob_name)

        self.storage_cmd('storage blob list -c {}  --num-results 1', account_info, container)

