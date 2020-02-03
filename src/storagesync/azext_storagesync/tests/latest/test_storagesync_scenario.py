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
                 '--name "SampleStorageSyncService_1" '
                 '--location "WestUS"',
                 checks=[])

        self.cmd('az storagesync sync-group create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--name "SampleSyncGroup_1"',
                 checks=[])

        self.cmd('az storagesync registered-server create '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1" '
                 '--server-id "\"080d4133-bdb5-40a0-96a0-71a6057bfe9a\"" '
                 '--server-certificate "\"MIIDFjCCAf6gAwIBAgIQQS+DS8uhc4VNzUkTw7wbRjANBgkqhkiG9w0BAQ0FADAzMTEwLwYDVQQDEyhhbmt1c2hiLXByb2QzLnJlZG1vbmQuY29ycC5taWNyb3NvZnQuY29tMB4XDTE3MDgwMzE3MDQyNFoXDTE4MDgwNDE3MDQyNFowMzExMC8GA1UEAxMoYW5rdXNoYi1wcm9kMy5yZWRtb25kLmNvcnAubWljcm9zb2Z0LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALDRvV4gmsIy6jGDPiHsXmvgVP749NNP7DopdlbHaNhjFmYINHl0uWylyaZmgJrROt2mnxN/zEyJtGnqYHlzUr4xvGq/qV5pqgdB9tag/sw9i22gfe9PRZ0FmSOZnXMbLYgLiDFqLtut5gHcOuWMj03YnkfoBEKlFBxWbagvW2yxz/Sxi9OVSJOKCaXra0RpcIHrO/KFl6ho2eE1/7Ykmfa8hZvSdoPd5gHdLiQcMB/pxq+mWp1fI6c8vFZoDu7Atn+NXTzYPKUxKzaisF12TsaKpohUsJpbB3Wocb0F5frn614D2pg14ERB5otjAMWw1m65csQWPI6dP8KIYe0+QPkCAwEAAaMmMCQwIgYDVR0lAQH/BBgwFgYIKwYBBQUHAwIGCisGAQQBgjcKAwwwDQYJKoZIhvcNAQENBQADggEBAA4RhVIBkw34M1RwakJgHvtjsOFxF1tVQA941NtLokx1l2Z8+GFQkcG4xpZSt+UN6wLerdCbnNhtkCErWUDeaT0jxk4g71Ofex7iM04crT4iHJr8mi96/XnhnkTUs+GDk12VgdeeNEczMZz+8Mxw9dJ5NCnYgTwO0SzGlclRsDvjzkLo8rh2ZG6n/jKrEyNXXo+hOqhupij0QbRP2Tvexdfw201kgN1jdZify8XzJ8Oi0bTS0KpJf2pNPOlooK2bjMUei9ANtEdXwwfVZGWvVh6tJjdv6k14wWWJ1L7zhA1IIVb1J+sQUzJji5iX0DrezjTz1Fg+gAzITaA/WsuujlM=\"" '
                 '--agent-version "1.0.277.0" '
                 '--server-osversion "10.0.14393.0" '
                 '--last-heart-beat "\"2017-08-08T18:29:06.470652Z\"" '
                 '--server-role "Standalone"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1" '
                 '--storage-account-resource-id "/subscriptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.Storage/storageAccounts/{{ storage_account_name }}" '
                 '--azure-file-share-name "cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4" '
                 '--storage-account-tenant-id "\"72f988bf-86f1-41af-91ab-2d7cd011db47\"" '
                 '--friendly-name "ankushbsubscriptionmgmtmab"',
                 checks=[])

        self.cmd('az storagesync server-endpoint create '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleServerEndpoint_1" '
                 '--cloud-tiering "off" '
                 '--volume-free-space-percent "100" '
                 '--tier-files-older-than-days "0" '
                 '--offline-data-transfer "on" '
                 '--offline-data-transfer-share-name "myfileshare"',
                 checks=[])

        self.cmd('az storagesync server-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleServerEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1"',
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

        self.cmd('az storagesync registered-server show '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1" '
                 '--server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a"',
                 checks=[])

        # EXAMPLE NOT FOUND: Workflows_Get
        self.cmd('az storagesync sync-group show '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--name "SampleSyncGroup_1"',
                 checks=[])

        # EXAMPLE NOT FOUND: Workflows_Get
        self.cmd('az storagesync registered-server list '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1"',
                 checks=[])

        self.cmd('az storagesync sync-group list '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1"',
                 checks=[])

        # EXAMPLE NOT FOUND: Workflows_ListByStorageSyncService
        self.cmd('az storagesync storage-sync-service show '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service list '
                 '--resource-group {rg}',
                 checks=[])

        self.cmd('az storagesync storage-sync-service list',
                 checks=[])

        # EXAMPLE NOT FOUND: Operations_List
        self.cmd('az storagesync cloud-endpoint trigger-change-detection '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1" '
                 '--directory-path "NewDirectory" '
                 '--change-detection-mode "Recursive"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint restoreheartbeat '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync server-endpoint recall-action '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleServerEndpoint_1" '
                 '--pattern "" '
                 '--recall-path ""',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint post-restore '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1" '
                 '--azure-file-share-uri "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare" '
                 '--status "Succeeded" '
                 '--source-azure-file-share-uri "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint pre-restore '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1" '
                 '--azure-file-share-uri "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint post-backup '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1" '
                 '--azure-file-share "https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint pre-backup '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1" '
                 '--azure-file-share "https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare"',
                 checks=[])

        self.cmd('az storagesync server-endpoint update '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleServerEndpoint_1" '
                 '--cloud-tiering "off" '
                 '--volume-free-space-percent "100" '
                 '--tier-files-older-than-days "0" '
                 '--offline-data-transfer "off"',
                 checks=[])

        self.cmd('az storagesync registered-server trigger-rollover '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1" '
                 '--server-id "d166ca76-dad2-49df-b409-12345642d730"',
                 checks=[])

        # EXAMPLE NOT FOUND: Workflows_Abort
        self.cmd('az storagesync storage-sync-service update '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service check-name-availability '
                 '--type "Microsoft.StorageSync/storageSyncServices"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service check-name-availability '
                 '--type "Microsoft.StorageSync/storageSyncServices"',
                 checks=[])

        self.cmd('az storagesync server-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleServerEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync cloud-endpoint delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--sync-group-name "SampleSyncGroup_1" '
                 '--name "SampleCloudEndpoint_1"',
                 checks=[])

        self.cmd('az storagesync registered-server delete '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1" '
                 '--server-id "41166691-ab03-43e9-ab3e-0330eda162ac"',
                 checks=[])

        self.cmd('az storagesync sync-group delete '
                 '--resource-group {rg} '
                 '--storage-sync-service-name "SampleStorageSyncService_1" '
                 '--name "SampleSyncGroup_1"',
                 checks=[])

        self.cmd('az storagesync storage-sync-service delete '
                 '--resource-group {rg} '
                 '--name "SampleStorageSyncService_1"',
                 checks=[])
