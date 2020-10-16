# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (LiveScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, api_version_constraint,
                               JMESPathCheck, JMESPathCheckExists, NoneCheck, live_only)
from .storage_test_util import StorageScenarioMixin


class StorageSASScenario(StorageScenarioMixin, LiveScenarioTest):
    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='queuesas', kind='StorageV2', location='eastus2', sku='Standard_RAGRS')
    def test_storage_queue_sas_scenario(self, resource_group, storage_account):
        from datetime import datetime, timedelta
        expiry = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')
        account_info = self.get_account_info(resource_group, storage_account)
        queue = self.create_random_name('queue', 24)

        self.storage_cmd('storage queue create -n {} --fail-on-exist --metadata a=b c=d', account_info, queue) \
            .assert_with_checks(JMESPathCheck('created', True))

        sas = self.storage_cmd('storage queue generate-sas -n {} --permissions r --expiry {}',
                               account_info, queue, expiry).output
        self.assertIn('sig', sas, 'The sig segment is not in the sas {}'.format(sas))

        self.cmd('storage queue exists -n {} --account-name {} --sas-token {}'.format(queue, storage_account, sas),
                 checks=JMESPathCheck('exists', True))


if __name__ == '__main__':
    import unittest

    unittest.main()
