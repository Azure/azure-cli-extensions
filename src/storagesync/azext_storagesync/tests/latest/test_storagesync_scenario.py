# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class MicrosoftStorageSyncScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_storagesync')
    def test_storagesync(self, resource_group):

        self.cmd('az storagesync storage-sync-service create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--location "WestUS"',
                 checks=[])

        self.cmd('az storagesync sync-group create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1"',
                 checks=[])

        # test in windows server
        self.cmd('az storagesync registered-server create '
                 '--resource-group {rg} '
                 '--storage_sync_service_name "SampleStorageSyncService_1" ',
                 checks=[])

        # Create file share

        self.cmd('az storagesync cloud-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--cloud-endpoint-name "SampleCloudEndpoint_1" '
                 '--storage-account {storage_account_name} '
                 '--azure-file-share-name "cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4" '
                 '--storage-account-tenant-id "\"72f988bf-86f1-41af-91ab-2d7cd011db47\"" ',
                 checks=[])

        self.cmd('az storagesync server-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--server-endpoint-name "SampleServerEndpoint_1" ',
                 checks=[])

        # Get server resource id and server id
        self.cmd('az storagesync registered-server list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1"',
                 checks=[])

        self.cmd('az storagesync registered-server show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a"',
                 checks=[])

        self.cmd('az storagesync server-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--server-endpoint-name "SampleServerEndpoint_1" '
                 '--server-resource-id "xxx" '
                 '--server-local-path "xxx"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--cloud-endpoint-name "SampleCloudEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync sync-group show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name  "SampleSyncGroup_1"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1"',
                 checks=[])

        self.cmd('az storagesync server-endpoint list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1"',
                 checks=[])

        self.cmd('az storagesync sync-group list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az storagesync storage-sync-service list',
                 checks=[])

        # test in windows server
        self.cmd('az storagesync registered-server rollover-certificate '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" ',
                 checks=[])

        self.cmd('az storagesync server-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--server-endpoint-name "SampleServerEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--cloud-endpoint-name "SampleCloudEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync registered-server delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--server-id "41166691-ab03-43e9-ab3e-0330eda162ac"',
                 checks=[])

        self.cmd('az storagesync sync-group delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1"',
                 checks=[])
