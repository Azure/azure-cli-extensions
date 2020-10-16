# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, api_version_constraint,
                               JMESPathCheck, JMESPathCheckExists, NoneCheck)
from .storage_test_util import StorageScenarioMixin


class StorageQueueScenarioTests(StorageScenarioMixin, ScenarioTest):
    @ResourceGroupPreparer(name_prefix='clitest')
    @StorageAccountPreparer(name_prefix='queue', kind='StorageV2', location='eastus2', sku='Standard_RAGRS')
    def test_storage_queue_general_scenario(self, resource_group, storage_account):
        from datetime import datetime, timedelta

        account_key = self.get_account_key(resource_group, storage_account)
        connection_string = self.get_connection_string(resource_group, storage_account)

        self.set_env('AZURE_STORAGE_ACCOUNT', storage_account)
        self.set_env('AZURE_STORAGE_KEY', account_key)

        queue = self.create_random_name('queue', 24)

        # Test create with metadata
        self.cmd('storage queue create -n {} --fail-on-exist --metadata a=b c=d'.format(queue),
                 checks=JMESPathCheck('created', True))
        # Test create with fail-on-exist
        from azure.core.exceptions import ResourceExistsError
        with self.assertRaisesRegexp(ResourceExistsError, 'The specified queue already exists.'):
            self.cmd(
                'storage queue create -n {} --fail-on-exist --connection-string {}'.format(queue, connection_string))

        # Test exists
        self.cmd('storage queue exists -n {}'.format(queue),
                 checks=JMESPathCheck('exists', True))

        # Test list
        res = self.cmd('storage queue list').get_output_in_json()
        self.assertIn(queue, [x['name'] for x in res], 'The newly created queue is not listed.')
        # Test list with connection-string
        res = self.cmd('storage queue list --connection-string {}'.format(connection_string)).get_output_in_json()
        self.assertIn(queue, [x['name'] for x in res], 'The newly created queue is not listed.')

        # Test generate-sas with start, expiry and permissions
        start = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%MZ')
        expiry = (datetime.utcnow() + timedelta(hours=2)).strftime('%Y-%m-%dT%H:%MZ')
        sas = self.cmd('storage queue generate-sas -n {} --permissions r --start {} --expiry {}'
                       .format(queue, start, expiry)).output
        self.assertIn('sig', sas, 'The sig segment is not in the sas {}'.format(sas))
        # Test generate-sas with ip and https-only
        sas2 = self.cmd('storage queue generate-sas -n {} --ip 172.20.34.0-172.20.34.255 --permissions r '
                        '--https-only --connection-string {}'.format(queue, connection_string)).output
        self.assertIn('sig', sas2, 'The sig segment is not in the sas {}'.format(sas2))

        # Test delete
        self.cmd('storage queue delete -n {} --connection-string {}'.format(queue, connection_string),
                 checks=JMESPathCheck('deleted', True))

        # Test exists with connection-string
        self.cmd('storage queue exists -n {} --connection-string {}'.format(queue, connection_string),
                 checks=JMESPathCheck('exists', False))

        # Test delete with fail-not-exist
        queue_not_exist = self.create_random_name('queue', 24)
        from azure.core.exceptions import ResourceNotFoundError
        with self.assertRaisesRegexp(ResourceNotFoundError, 'The specified queue does not exist.'):
            self.cmd('storage queue delete -n {} --fail-not-exist'.format(queue_not_exist))

        # check status of the queue
        queue_status = self.cmd('storage queue stats').get_output_in_json()
        self.assertIn(queue_status['geoReplication']['status'], ('live', 'unavailable'))

        # check status of the queue with connection string
        queue_status = self.cmd('storage queue stats --connection-string {}'.format(connection_string)) \
            .get_output_in_json()
        self.assertIn('lastSyncTime', queue_status['geoReplication'])

    def get_account_key(self, group, name):
        return self.cmd('storage account keys list -n {} -g {} --query "[0].value" -otsv'
                        .format(name, group)).output

    def get_connection_string(self, group, name):
        return self.cmd('storage account show-connection-string -n {} -g {} '
                        '--query connectionString -otsv'.format(name, group)).output.strip()


if __name__ == '__main__':
    import unittest

    unittest.main()
