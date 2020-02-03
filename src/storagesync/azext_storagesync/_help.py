# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['storagesync'] = """
    type: group
    short-summary: Commands to manage .
"""

helps['storagesync storage-sync-service'] = """
    type: group
    short-summary: Commands to manage storagesync storage sync service.
"""

helps['storagesync storage-sync-service create'] = """
    type: command
    short-summary: Create a new StorageSyncService.
    examples:
      - name: StorageSyncServices_Create
        text: |-
               az storagesync storage-sync-service create --resource-group "SampleResourceGroup_1" \\
               --name "SampleStorageSyncService_1" --location "WestUS"
"""

helps['storagesync storage-sync-service update'] = """
    type: command
    short-summary: Create a new StorageSyncService.
    examples:
      - name: StorageSyncServices_Update
        text: |-
               az storagesync storage-sync-service update --resource-group "SampleResourceGroup_1" \\
               --name "SampleStorageSyncService_1"
"""

helps['storagesync storage-sync-service delete'] = """
    type: command
    short-summary: Delete a given StorageSyncService.
    examples:
      - name: StorageSyncServices_Delete
        text: |-
               az storagesync storage-sync-service delete --resource-group "SampleResourceGroup_1" \\
               --name "SampleStorageSyncService_1"
"""

helps['storagesync storage-sync-service show'] = """
    type: command
    short-summary: Get a given StorageSyncService.
    examples:
      - name: StorageSyncServices_Get
        text: |-
               az storagesync storage-sync-service show --resource-group "SampleResourceGroup_1" --name \\
               "SampleStorageSyncService_1"
"""

helps['storagesync storage-sync-service list'] = """
    type: command
    short-summary: Get a StorageSyncService list by Resource group name.
    examples:
      - name: StorageSyncServices_ListByResourceGroup
        text: |-
               az storagesync storage-sync-service list --resource-group "SampleResourceGroup_1"
      - name: StorageSyncServices_ListBySubscription
        text: |-
               az storagesync storage-sync-service list
"""

helps['storagesync storage-sync-service check-name-availability'] = """
    type: command
    short-summary: Check the give namespace name availability.
    examples:
      - name: StorageSyncServiceCheckNameAvailability_AlreadyExists
        text: |-
               az storagesync storage-sync-service check-name-availability --location-name "westus" \\
               --name "newstoragesyncservicename" --type "Microsoft.StorageSync/storageSyncServices"
      - name: StorageSyncServiceCheckNameAvailability_Available
        text: |-
               az storagesync storage-sync-service check-name-availability --location-name "westus" \\
               --name "newstoragesyncservicename" --type "Microsoft.StorageSync/storageSyncServices"
"""

helps['storagesync sync-group'] = """
    type: group
    short-summary: Commands to manage storagesync sync group.
"""

helps['storagesync sync-group create'] = """
    type: command
    short-summary: Create a new SyncGroup.
    examples:
      - name: SyncGroups_Create
        text: |-
               az storagesync sync-group create --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --name "SampleSyncGroup_1"
"""

helps['storagesync sync-group update'] = """
    type: command
    short-summary: Create a new SyncGroup.
"""

helps['storagesync sync-group delete'] = """
    type: command
    short-summary: Delete a given SyncGroup.
    examples:
      - name: SyncGroups_Delete
        text: |-
               az storagesync sync-group delete --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --name "SampleSyncGroup_1"
"""

helps['storagesync sync-group show'] = """
    type: command
    short-summary: Get a given SyncGroup.
    examples:
      - name: SyncGroups_Get
        text: |-
               az storagesync sync-group show --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --name "SampleSyncGroup_1"
"""

helps['storagesync sync-group list'] = """
    type: command
    short-summary: Get a SyncGroup List.
    examples:
      - name: SyncGroups_ListByStorageSyncService
        text: |-
               az storagesync sync-group list --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1"
"""

helps['storagesync cloud-endpoint'] = """
    type: group
    short-summary: Commands to manage storagesync cloud endpoint.
"""

helps['storagesync cloud-endpoint create'] = """
    type: command
    short-summary: Create a new CloudEndpoint.
    examples:
      - name: CloudEndpoints_Create
        text: |-
               az storagesync cloud-endpoint create --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1" --storage-account-resource-id "/subscri
               ptions/{{ subscription_id }}/resourceGroups/{{ resource_group }}/providers/Microsoft.Stora
               ge/storageAccounts/{{ storage_account_name }}" --azure-file-share-name \\
               "cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4" --storage-account-tenant-id \\
               "\\"72f988bf-86f1-41af-91ab-2d7cd011db47\\"" --friendly-name "ankushbsubscriptionmgmtmab"
"""

helps['storagesync cloud-endpoint update'] = """
    type: command
    short-summary: Create a new CloudEndpoint.
"""

helps['storagesync cloud-endpoint delete'] = """
    type: command
    short-summary: Delete a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_Delete
        text: |-
               az storagesync cloud-endpoint delete --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1"
"""

helps['storagesync cloud-endpoint show'] = """
    type: command
    short-summary: Get a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_Get
        text: |-
               az storagesync cloud-endpoint show --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1"
"""

helps['storagesync cloud-endpoint list'] = """
    type: command
    short-summary: Get a CloudEndpoint List.
    examples:
      - name: CloudEndpoints_ListBySyncGroup
        text: |-
               az storagesync cloud-endpoint list --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1"
"""

helps['storagesync cloud-endpoint pre-backup'] = """
    type: command
    short-summary: Pre Backup a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_PreBackup
        text: |-
               az storagesync cloud-endpoint pre-backup --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1" --azure-file-share \\
               "https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare"
"""

helps['storagesync cloud-endpoint post-backup'] = """
    type: command
    short-summary: Post Backup a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_PostBackup
        text: |-
               az storagesync cloud-endpoint post-backup --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1" --azure-file-share \\
               "https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare"
"""

helps['storagesync cloud-endpoint pre-restore'] = """
    type: command
    short-summary: Pre Restore a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_PreRestore
        text: |-
               az storagesync cloud-endpoint pre-restore --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1" --azure-file-share-uri \\
               "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare"
"""

helps['storagesync cloud-endpoint restoreheartbeat'] = """
    type: command
    short-summary: Restore Heartbeat a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_restoreheartbeat
        text: |-
               az storagesync cloud-endpoint restoreheartbeat --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1"
"""

helps['storagesync cloud-endpoint post-restore'] = """
    type: command
    short-summary: Post Restore a given CloudEndpoint.
    examples:
      - name: CloudEndpoints_PostRestore
        text: |-
               az storagesync cloud-endpoint post-restore --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleCloudEndpoint_1" --azure-file-share-uri \\
               "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare" \\
               --status "Succeeded" --source-azure-file-share-uri \\
               "https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare"
"""

helps['storagesync cloud-endpoint trigger-change-detection'] = """
    type: command
    short-summary: Triggers detection of changes performed on Azure File share connected to the specified Azure File Sync Cloud Endpoint.
    examples:
      - name: CloudEndpoints_TriggerChangeDetection
        text: |-
               az storagesync cloud-endpoint trigger-change-detection --resource-group \\
               "SampleResourceGroup_1" --storage-sync-service-name "SampleStorageSyncService_1" \\
               --sync-group-name "SampleSyncGroup_1" --name "SampleCloudEndpoint_1" --directory-path \\
               "NewDirectory" --change-detection-mode "Recursive"
"""

helps['storagesync server-endpoint'] = """
    type: group
    short-summary: Commands to manage storagesync server endpoint.
"""

helps['storagesync server-endpoint create'] = """
    type: command
    short-summary: Create a new ServerEndpoint.
    examples:
      - name: ServerEndpoints_Create
        text: |-
               az storagesync server-endpoint create --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleServerEndpoint_1" --cloud-tiering "off" \\
               --volume-free-space-percent "100" --tier-files-older-than-days "0" \\
               --offline-data-transfer "on" --offline-data-transfer-share-name "myfileshare"
"""

helps['storagesync server-endpoint update'] = """
    type: command
    short-summary: Create a new ServerEndpoint.
    examples:
      - name: ServerEndpoints_Update
        text: |-
               az storagesync server-endpoint update --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleServerEndpoint_1" --cloud-tiering "off" \\
               --volume-free-space-percent "100" --tier-files-older-than-days "0" \\
               --offline-data-transfer "off"
"""

helps['storagesync server-endpoint delete'] = """
    type: command
    short-summary: Delete a given ServerEndpoint.
    examples:
      - name: ServerEndpoints_Delete
        text: |-
               az storagesync server-endpoint delete --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleServerEndpoint_1"
"""

helps['storagesync server-endpoint show'] = """
    type: command
    short-summary: Get a ServerEndpoint.
    examples:
      - name: ServerEndpoints_Get
        text: |-
               az storagesync server-endpoint show --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleServerEndpoint_1"
"""

helps['storagesync server-endpoint list'] = """
    type: command
    short-summary: Get a ServerEndpoint list.
    examples:
      - name: ServerEndpoints_ListBySyncGroup
        text: |-
               az storagesync server-endpoint list --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1"
"""

helps['storagesync server-endpoint recall-action'] = """
    type: command
    short-summary: Recall a server endpoint.
    examples:
      - name: ServerEndpoints_recallAction
        text: |-
               az storagesync server-endpoint recall-action --resource-group "SampleResourceGroup_1" \\
               --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \\
               "SampleSyncGroup_1" --name "SampleServerEndpoint_1" --pattern "" --recall-path ""
"""

helps['storagesync registered-server'] = """
    type: group
    short-summary: Commands to manage storagesync registered server.
"""

helps['storagesync registered-server create'] = """
    type: command
    short-summary: Add a new registered server.
    examples:
      - name: RegisteredServers_Create
        text: |-
               az storagesync registered-server create --resource-group "SampleResourceGroup_1" --name \\
               "SampleStorageSyncService_1" --server-id "\\"080d4133-bdb5-40a0-96a0-71a6057bfe9a\\"" \\
               --server-certificate "\\"MIIDFjCCAf6gAwIBAgIQQS+DS8uhc4VNzUkTw7wbRjANBgkqhkiG9w0BAQ0FADAzMT
               EwLwYDVQQDEyhhbmt1c2hiLXByb2QzLnJlZG1vbmQuY29ycC5taWNyb3NvZnQuY29tMB4XDTE3MDgwMzE3MDQyNFoX
               DTE4MDgwNDE3MDQyNFowMzExMC8GA1UEAxMoYW5rdXNoYi1wcm9kMy5yZWRtb25kLmNvcnAubWljcm9zb2Z0LmNvbT
               CCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALDRvV4gmsIy6jGDPiHsXmvgVP749NNP7DopdlbHaNhjFmYI
               NHl0uWylyaZmgJrROt2mnxN/zEyJtGnqYHlzUr4xvGq/qV5pqgdB9tag/sw9i22gfe9PRZ0FmSOZnXMbLYgLiDFqLt
               ut5gHcOuWMj03YnkfoBEKlFBxWbagvW2yxz/Sxi9OVSJOKCaXra0RpcIHrO/KFl6ho2eE1/7Ykmfa8hZvSdoPd5gHd
               LiQcMB/pxq+mWp1fI6c8vFZoDu7Atn+NXTzYPKUxKzaisF12TsaKpohUsJpbB3Wocb0F5frn614D2pg14ERB5otjAM
               Ww1m65csQWPI6dP8KIYe0+QPkCAwEAAaMmMCQwIgYDVR0lAQH/BBgwFgYIKwYBBQUHAwIGCisGAQQBgjcKAwwwDQYJ
               KoZIhvcNAQENBQADggEBAA4RhVIBkw34M1RwakJgHvtjsOFxF1tVQA941NtLokx1l2Z8+GFQkcG4xpZSt+UN6wLerd
               CbnNhtkCErWUDeaT0jxk4g71Ofex7iM04crT4iHJr8mi96/XnhnkTUs+GDk12VgdeeNEczMZz+8Mxw9dJ5NCnYgTwO
               0SzGlclRsDvjzkLo8rh2ZG6n/jKrEyNXXo+hOqhupij0QbRP2Tvexdfw201kgN1jdZify8XzJ8Oi0bTS0KpJf2pNPO
               looK2bjMUei9ANtEdXwwfVZGWvVh6tJjdv6k14wWWJ1L7zhA1IIVb1J+sQUzJji5iX0DrezjTz1Fg+gAzITaA/Wsuu
               jlM=\\"" --agent-version "1.0.277.0" --server-osversion "10.0.14393.0" --last-heart-beat \\
               "\\"2017-08-08T18:29:06.470652Z\\"" --server-role "Standalone"
"""

helps['storagesync registered-server update'] = """
    type: command
    short-summary: Add a new registered server.
"""

helps['storagesync registered-server delete'] = """
    type: command
    short-summary: Delete the given registered server.
    examples:
      - name: RegisteredServers_Delete
        text: |-
               az storagesync registered-server delete --resource-group "SampleResourceGroup_1" --name \\
               "SampleStorageSyncService_1" --server-id "41166691-ab03-43e9-ab3e-0330eda162ac"
"""

helps['storagesync registered-server show'] = """
    type: command
    short-summary: Get a given registered server.
    examples:
      - name: RegisteredServers_Get
        text: |-
               az storagesync registered-server show --resource-group "SampleResourceGroup_1" --name \\
               "SampleStorageSyncService_1" --server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a"
"""

helps['storagesync registered-server list'] = """
    type: command
    short-summary: Get a given registered server list.
    examples:
      - name: RegisteredServers_ListByStorageSyncService
        text: |-
               az storagesync registered-server list --resource-group "SampleResourceGroup_1" --name \\
               "SampleStorageSyncService_1"
"""

helps['storagesync registered-server trigger-rollover'] = """
    type: command
    short-summary: Triggers Server certificate rollover.
    examples:
      - name: RegisteredServers_triggerRollover
        text: |-
               az storagesync registered-server trigger-rollover --resource-group \\
               "SampleResourceGroup_1" --name "SampleStorageSyncService_1" --server-id \\
               "d166ca76-dad2-49df-b409-12345642d730"
"""

helps['-'] = """
    type: group
    short-summary: Commands to manage .
"""

helps['-'] = """
    type: group
    short-summary: Commands to manage .
"""
