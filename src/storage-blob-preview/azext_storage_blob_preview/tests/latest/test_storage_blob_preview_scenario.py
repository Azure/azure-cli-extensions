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
    @StorageAccountPreparer(name_prefix='version', kind='StorageV2', location='eastus2euap')
    def test_storage_blob_versioning(self, resource_group, storage_account):
        import time
        from datetime import datetime, timedelta
        self.cmd('storage account blob-service-properties update -n {} -g {} --enable-versioning '.format(
            storage_account, resource_group), checks=[
            JMESPathCheck('isVersioningEnabled', True)
        ])
        account_info = self.get_account_info(resource_group, storage_account)
        container = self.create_container(account_info, prefix="con")

        temp_dir = self.create_temp_dir()
        local_file = self.create_temp_file(1)
        blob_name = self.create_random_name(prefix='blob', length=24)

        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} ', account_info,
                         container, local_file, blob_name)
        count = 1
        while True:
            # get previous version
            result = self.storage_cmd('storage blob list -c {} --include v', account_info,
                                      container).get_output_in_json()
            version_id = result[0]['versionId']
            if version_id:
                break
            time.sleep(10)
            self.storage_cmd('storage blob upload -c {} -f "{}" -n {} --overwrite ', account_info,
                             container, local_file, blob_name)
            count += 1

        local_file2 = self.create_temp_file(2)
        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} --overwrite ', account_info,
                         container, local_file2, blob_name)
        count += 1
        # show with version id
        self.storage_cmd('storage blob show -c {} -n {} --version-id {} ', account_info, container, blob_name,
                         version_id).assert_with_checks(JMESPathCheck('versionId', version_id),
                                                        JMESPathCheck('name', blob_name),
                                                        JMESPathCheck('properties.blobTier', 'Hot'),
                                                        JMESPathCheck('properties.contentLength', 1024))

        # download with version id
        self.storage_cmd('storage blob download -c {} -n {} --version-id {} -f "{}" ', account_info, container,
                         blob_name, version_id, os.path.join(temp_dir, local_file))

        # set-tier with version id, not for page blob
        self.storage_cmd('storage blob set-tier -c {} -n {} --version-id {} --tier Cool ', account_info, container,
                         blob_name, version_id)
        self.storage_cmd('storage blob show -c {} -n {} --version-id {} ', account_info, container, blob_name,
                         version_id).assert_with_checks(JMESPathCheck('versionId', version_id),
                                                        JMESPathCheck('name', blob_name),
                                                        JMESPathCheck('properties.blobTier', 'Cool'))

        # generate sas with version id
        expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')
        sas_token = self.storage_cmd(
            'storage blob generate-sas -c {} -n {} --version-id {} --permissions dx --expiry {} ', account_info,
            container, blob_name, version_id, expiry).output.strip('\n')
        self.assertIn('sig=', sas_token)

        # delete with version id
        self.storage_cmd('storage blob list -c {} --include v', account_info, container)\
            .assert_with_checks(JMESPathCheck('length(@)', count))
        self.storage_cmd('storage blob delete -c {} -n {} --version-id {} --account-name {}  ', account_info,
                         container, blob_name, version_id, storage_account, sas_token)

        self.storage_cmd('storage blob list -c {} --include v', account_info, container)\
            .assert_with_checks(JMESPathCheck('length(@)', count - 1))

    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='blobtag', kind='StorageV2', location='eastus2euap')
    def test_storage_blob_tags_scenario(self, resource_group, storage_account):
        import time
        account_info = self.get_account_info(resource_group, storage_account)
        container1 = self.create_container(account_info, prefix="cont1")
        container2 = self.create_container(account_info, prefix="cont2")

        local_file = self.create_temp_file(128)
        blob_name1 = self.create_random_name(prefix='blob', length=24)
        blob_name2 = self.create_random_name(prefix='blob', length=24)

        # upload with tags
        tags = 'date=2020-01-01 category=test'
        self.storage_cmd('storage blob upload -c {} -f "{}" -n {} --tags {} ', account_info,
                         container1, local_file, blob_name1, tags)

        # May several seconds to take effect
        time.sleep(30)
        self.storage_cmd('storage blob list -c {} --include t', account_info, container1) \
            .assert_with_checks(JMESPathCheck('[0].tags.date', '2020-01-01'),
                                JMESPathCheck('[0].tags.category', 'test'))
        self.storage_cmd('storage blob tag list -n {} -c {} ', account_info, blob_name1, container1)\
            .assert_with_checks(JMESPathCheck('date', '2020-01-01'),
                                JMESPathCheck('category', 'test'))

        # copy with tags
        tag = 'number=1'
        self.storage_cmd('storage blob copy start --source-blob {} --source-container {} -c {} -b {} --tags {}',
                         account_info, blob_name1, container1, container2, blob_name2, tag)
        # May several seconds to take effect
        self.storage_cmd('storage blob tag list -n {} -c {} ', account_info, blob_name2, container2)\
            .assert_with_checks(JMESPathCheck('number', '1'))
        self.storage_cmd('storage blob list -c {} --include t ', account_info, container2)\
            .assert_with_checks(JMESPathCheck('[0].tags.number', '1'))

        # set tags
        self.storage_cmd('storage blob tag set -n {} -c {} --tags {}', account_info, blob_name1, container1,
                         'test=tag').assert_with_checks(JMESPathCheck('test', 'tag'))

        # list tags
        self.storage_cmd('storage blob tag list -n {} -c {} ', account_info, blob_name1, container1)\
            .assert_with_checks(JMESPathCheck('test', 'tag'))

        # generate sas with tag permission
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')
        sas = self.storage_cmd('storage blob generate-sas -n {} -c {} --permissions t --expiry {} --https-only -o tsv',
                               account_info, blob_name1, container1, expiry).output.strip('\n')
        self.assertTrue(sas)
        self.assertIn('sig=', sas)

        # find blobs cross containers with index tags
        self.storage_cmd("storage blob filter --tag-filter \"test='tag'\" ", account_info).\
            assert_with_checks(JMESPathCheck('length(@)', 1),
                               JMESPathCheck('[0].containerName', container1),
                               JMESPathCheck('[0].name', blob_name1))

        # tag condition
        tag_condition = "test=\'tag\'"
        self.storage_cmd('storage blob copy start --source-blob {} --source-container {} -c {} -b {} '
                         '--source-tags-condition "{}" ', account_info, blob_name1, container1, container2,
                         blob_name2, tag_condition)

        self.storage_cmd('storage blob upload -n {} -c {} --tags-condition "{}" -f "{}" --tags {} --overwrite ', account_info,
                         blob_name1, container1, tag_condition, local_file, tags)

        # metadata
        tag_condition = "category=\'test\'"
        self.storage_cmd('storage blob metadata update -n {} -c {} --tags-condition "{}" --metadata a=b ', account_info,
                         blob_name1, container1, tag_condition)
        self.storage_cmd('storage blob metadata show -n {} -c {} --tags-condition "{}" ', account_info,
                         blob_name1, container1, tag_condition)\
            .assert_with_checks(JMESPathCheck('a', 'b'))

        # lease
        proposed_lease_id = 'abcdabcd-abcd-abcd-abcd-abcdabcdabcd'
        new_lease_id = 'dcbadcba-dcba-dcba-dcba-dcbadcbadcba'
        self.storage_cmd('storage blob lease acquire --lease-duration 60 -b {} -c {} --proposed-lease-id {} '
                         '--tags-condition "{}" ', account_info, blob_name1, container1, proposed_lease_id, tag_condition)
        self.storage_cmd('storage blob show -n {} -c {}', account_info, blob_name1, container1) \
            .assert_with_checks(JMESPathCheck('properties.lease.duration', 'fixed'),
                                JMESPathCheck('properties.lease.state', 'leased'),
                                JMESPathCheck('properties.lease.status', 'locked'))
        self.storage_cmd('storage blob lease change -b {} -c {} --lease-id {} --proposed-lease-id {} '
                         '--tags-condition "{}" ', account_info, blob_name1, container1, proposed_lease_id,
                         new_lease_id, tag_condition)
        self.storage_cmd('storage blob lease renew -b {} -c {} --lease-id {} --tags-condition "{}" ', account_info,
                         blob_name1, container1, new_lease_id, tag_condition)
        self.storage_cmd('storage blob show -n {} -c {}', account_info, blob_name1, container1) \
            .assert_with_checks(JMESPathCheck('properties.lease.duration', 'fixed'),
                                JMESPathCheck('properties.lease.state', 'leased'),
                                JMESPathCheck('properties.lease.status', 'locked'))
        self.storage_cmd('storage blob lease break -b {} -c {} --lease-break-period 30 --tags-condition "{}" ',
                         account_info, blob_name1, container1, tag_condition)
        self.storage_cmd('storage blob show -n {} -c {}', account_info, blob_name1, container1) \
            .assert_with_checks(JMESPathCheck('properties.lease.duration', None),
                                JMESPathCheck('properties.lease.state', 'breaking'),
                                JMESPathCheck('properties.lease.status', 'locked'))
        self.storage_cmd('storage blob lease release -b {} -c {} --lease-id {} --tags-condition "{}" ', account_info,
                         blob_name1, container1, new_lease_id, tag_condition)
        self.storage_cmd('storage blob show -n {} -c {}', account_info, blob_name1, container1) \
            .assert_with_checks(JMESPathCheck('properties.lease.duration', None),
                                JMESPathCheck('properties.lease.state', 'available'),
                                JMESPathCheck('properties.lease.status', 'unlocked'))

        self.storage_cmd('storage blob set-tier -n {} -c {} --tier Hot --tags-condition "{}" ', account_info,
                         blob_name1, container1, tag_condition)

        result = self.storage_cmd('storage blob snapshot -n {} -c {} --tags-condition "{}" ', account_info,
                                  blob_name1, container1, tag_condition).get_output_in_json()
        snapshot = result['snapshot']

        self.storage_cmd('storage blob tag set -n {} -c {} --tags-condition "{}" --tags {} ', account_info,
                         blob_name1, container1, tag_condition, tags) \
            .assert_with_checks(JMESPathCheck('category', 'test'))
        self.storage_cmd('storage blob tag list -n {} -c {} --tags-condition "{}" ', account_info,
                         blob_name1, container1, tag_condition) \
            .assert_with_checks(JMESPathCheck('category', 'test'))

        self.storage_cmd("storage blob list -c {} ", account_info, container1)\
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.storage_cmd("storage blob list -c {} --include s ", account_info, container1)\
            .assert_with_checks(JMESPathCheck('length(@)', 2))
        self.storage_cmd('storage blob delete -n {} -c {} --tags-condition "{}" --snapshot {} ', account_info,
                         blob_name1, container1, tag_condition, snapshot)
        self.storage_cmd('storage blob delete -n {} -c {} --tags-condition "{}" ', account_info,
                         blob_name1, container1, tag_condition)
        self.storage_cmd("storage blob list -c {} ", account_info, container1)\
            .assert_with_checks(JMESPathCheck('length(@)', 0))
