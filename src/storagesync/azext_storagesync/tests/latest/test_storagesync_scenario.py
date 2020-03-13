# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, JMESPathCheck, StorageAccountPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class MicrosoftStorageSyncScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_storagesync')
    @StorageAccountPreparer()
    def test_storagesync(self):
        # setup
        sync_service_name = self.create_random_name('sync-service', 24)
        sync_group_name = self.create_random_name('sync-group', 24)
        cloud_endpoint_name = self.create_random_name('cloud-endpoint', 24)
        server_endpoint_name = self.create_random_name('server-endpoint', 24)
        file_share_name = self.create_random_name('file-share', 24)

        self.kwargs.update({
            'sync_service_name': sync_service_name,
            'sync_group_name': sync_group_name,
            'cloud_endpoint_name': cloud_endpoint_name,
            'server_endpoint_name': server_endpoint_name,
            'file_share_name': file_share_name
        })

        self.cmd('az storage share create '
                 '--name {file_share_name} '
                 '--quota 1 '
                 '--account-name {sa}')

        # run
        self.cmd('az storagesync storage-sync-service create '
                 '--resource-group {rg} '
                 '--name {sync_service_name} '
                 '--tags key1=value1',
                 checks=[JMESPathCheck('name', sync_service_name)])

        self.cmd('az storagesync storage-sync-service show '
                 '--resource-group {rg} '
                 '--name {sync_service_name}',
                 checks=[JMESPathCheck('storageSyncServiceStatus', 0)])

        self.cmd('az storagesync storage-sync-service list '
                 '--resource-group {rg}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('az storagesync sync-group create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--name {sync_group_name}',
                 checks=[JMESPathCheck('name', sync_group_name),
                         JMESPathCheck('syncGroupStatus', 0)])

        self.cmd('az storagesync sync-group show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--name {sync_group_name}',
                 checks=[JMESPathCheck('name', sync_group_name),
                         JMESPathCheck('syncGroupStatus', 0)])

        self.cmd('az storagesync sync-group list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('az storagesync cloud-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name} '
                 '--storage-account {sa} '
                 '--azure-file-share-name {file_share_name}',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded')])

        self.cmd('az storagesync cloud-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name}',
                 checks=[JMESPathCheck('name', cloud_endpoint_name)])

        self.cmd('az storagesync cloud-endpoint list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name}',
                 checks=[JMESPathCheck('length(@)', 1)])

        server_list = self.cmd('az storagesync registered-server list '
                               '--resource-group {rg} '
                               '--storage-sync-service-name {sync_service_name}').get_output_in_json()
        self.assertEqual(1, len(server_list))

        server_id = server_list[0]['serverId']
        self.kwargs.update({
            'server_id': server_id
        })

        self.cmd('az storagesync registered-server show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--server-id {server_id}',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('serverId', server_id)])

        self.cmd('az storagesync server-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} '
                 '--server-id {server_id} '
                 '--server-local-path "c:\\users\\syncfolder"',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('name', server_endpoint_name)])

        self.cmd('az storagesync server-endpoint update '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} '
                 '--tier-files-older-than-days 10',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('tierFilesOlderThanDays', 10)])

        self.cmd('az storagesync server-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} ',
                 checks=[JMESPathCheck('provisioningState', 'Succeeded'),
                         JMESPathCheck('name', server_endpoint_name)])

        self.cmd('az storagesync server-endpoint list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('az storagesync registered-server delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--server-id {server_id} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync server-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {server_endpoint_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--sync-group-name {sync_group_name} '
                 '--name {cloud_endpoint_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync sync-group delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name {sync_service_name} '
                 '--name {sync_group_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync storage-sync-service delete '
                 '--resource-group {rg} '
                 '--name {sync_service_name} '
                 '-y',
                 checks=[])

        self.cmd('az storagesync storage-sync-service show '
                 '--resource-group {rg} '
                 '--name {sync_service_name}',
                 expect_failure=True)

        # tear down
        self.cmd('az storage share delete '
                 '--name {file_share_name} '
                 '--account-name {sa}')
