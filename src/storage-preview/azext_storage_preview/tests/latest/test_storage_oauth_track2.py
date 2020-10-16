# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from datetime import datetime, timedelta
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer, StorageAccountPreparer)
from .storage_test_util import StorageScenarioMixin


class StorageOauthTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='storage', kind='StorageV2', location='eastus2', sku='Standard_RAGRS')
    def test_storage_queue_oauth(self, resource_group, storage_account):
        self.kwargs.update({
            'rg': resource_group,
            'account': storage_account,
            'queue_name': self.create_random_name(prefix='queue', length=24),
        })

        # Test create oauth
        self.oauth_cmd('storage queue create -n {queue_name} --metadata key1=value1 --account-name {account} ')\
            .assert_with_checks(JMESPathCheck('created', True))

        # Test exists oauth
        self.oauth_cmd('storage queue exists -n {queue_name} --account-name {account} ')\
            .assert_with_checks(JMESPathCheck('exists', True))

        # Test list oauth
        self.oauth_cmd('storage queue list --include-metadata --account-name {account} ') \
            .assert_with_checks(JMESPathCheck('length(@)', 1), JMESPathCheck('[0].metadata.key1', 'value1'))

        # Test stats oauth
        queue_status = self.oauth_cmd('storage queue stats --account-name {account} ').get_output_in_json()
        self.assertIn(queue_status['geoReplication']['status'], ('live', 'unavailable'))

        # Test delete oauth
        self.oauth_cmd('storage queue delete -n {queue_name} --account-name {account} ')\
            .assert_with_checks(JMESPathCheck('deleted', True))


if __name__ == '__main__':
    import unittest

    unittest.main()
