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
    short-summary: Manage Azure File Sync.
"""

helps['storagesync create'] = """
    type: command
    short-summary: Create a new storage sync service.
    examples:
      - name: Create a new storage sync service "SampleStorageSyncService" in resource group 'SampleResourceGroup'.
        text: |-
               az storagesync create --resource-group "SampleResourceGroup" \\
               --name "SampleStorageSyncService" --location "WestUS" --tags key1=value1
"""

helps['storagesync delete'] = """
    type: command
    short-summary: Delete a given storage sync service.
    examples:
      - name: Delete a storage sync service "SampleStorageSyncService" in resource group 'SampleResourceGroup'.
        text: |-
               az storagesync delete --resource-group "SampleResourceGroup" \\
               --name "SampleStorageSyncService"
"""

helps['storagesync show'] = """
    type: command
    short-summary: Show the properties for a given storage sync service.
    examples:
      - name: Show the properties for storage sync service "SampleStorageSyncService" in resource group 'SampleResourceGroup'.
        text: |-
               az storagesync show --resource-group "SampleResourceGroup" --name \\
               "SampleStorageSyncService"
"""

helps['storagesync list'] = """
    type: command
    short-summary: List all storage sync services in a resource group or a subscription.
    examples:
      - name: List all storage sync services in a resource group "SampleResourceGroup".
        text: |-
               az storagesync list --resource-group "SampleResourceGroup"
      - name: List all storage sync services in current subscription
        text: |-
               az storagesync list
"""

helps['storagesync sync-group'] = """
    type: group
    short-summary: Manage sync group.
"""

helps['storagesync sync-group create'] = """
    type: command
    short-summary: Create a new sync group.
    examples:
      - name: Create a new sync group "SampleSyncGroup" in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group create --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --name "SampleSyncGroup"
"""

helps['storagesync sync-group delete'] = """
    type: command
    short-summary: Delete a given sync group.
    examples:
      - name: Delete sync group "SampleSyncGroup" in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --name "SampleSyncGroup"
"""

helps['storagesync sync-group show'] = """
    type: command
    short-summary: Show the properties for a given sync group.
    examples:
      - name: Show the properties for sync group "SampleSyncGroup" in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group show --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --name "SampleSyncGroup"
"""

helps['storagesync sync-group list'] = """
    type: command
    short-summary: List all sync groups in a storage sync service.
    examples:
      - name: List all sync groups in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group list --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService"
"""

helps['storagesync sync-group cloud-endpoint'] = """
    type: group
    short-summary: Manage cloud endpoint.
"""

helps['storagesync sync-group cloud-endpoint create'] = """
    type: command
    short-summary: Create a new cloud endpoint.
    examples:
      - name: Create a new cloud endpoint "SampleCloudEndpoint" in sync group "SampleSyncGroup".
        text: |-
               az storagesync sync-group cloud-endpoint create --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleCloudEndpoint" --storage-account storageaccountnameorid --azure-file-share-name \\
               "cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4"
"""

helps['storagesync sync-group cloud-endpoint delete'] = """
    type: command
    short-summary: Delete a given cloud endpoint.
    examples:
      - name: Delete cloud endpoint "SampleCloudEndpoint".
        text: |-
               az storagesync sync-group cloud-endpoint delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleCloudEndpoint"
"""

helps['storagesync sync-group cloud-endpoint show'] = """
    type: command
    short-summary: Show the properties for a given cloud endpoint.
    examples:
      - name: Show the properties for cloud endpoint "SampleCloudEndpoint".
        text: |-
               az storagesync sync-group cloud-endpoint show --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleCloudEndpoint"
"""

helps['storagesync sync-group cloud-endpoint list'] = """
    type: command
    short-summary: List all cloud endpoints in a sync group.
    examples:
      - name: List all cloud endpoints in sync group "SampleSyncGroup".
        text: |-
               az storagesync sync-group cloud-endpoint list --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup"
"""

helps['storagesync sync-group cloud-endpoint wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of a cloud endpoint is met.
    examples:
      - name: Place the CLI in a waiting state until a condition of a cloud endpoint is created.
        text: |-
               az storagesync sync-group cloud-endpoint wait --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleCloudEndpoint" --created
"""

helps['storagesync sync-group server-endpoint'] = """
    type: group
    short-summary: Manage server endpoint.
"""

helps['storagesync sync-group server-endpoint create'] = """
    type: command
    short-summary: Create a new server endpoint.
    examples:
      - name: Create a new server endpoint "SampleServerEndpoint" in sync group "SampleSyncGroup".
        text: |-
               az storagesync sync-group server-endpoint create --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleServerEndpoint" --server-id 91beed22-7e9e-4bda-9313-fec96cf286e0 \\
               --server-local-path "d:\\abc" --cloud-tiering "off" --volume-free-space-percent 80 --tier-files-older-than-days 20 \\
               --offline-data-transfer "on" --offline-data-transfer-share-name "myfileshare"
"""

helps['storagesync sync-group server-endpoint update'] = """
    type: command
    short-summary: Update the properties for a given server endpoint.
    examples:
      - name: Update the properties for server endpoint "SampleServerEndpoint".
        text: |-
               az storagesync sync-group server-endpoint update --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleServerEndpoint" --cloud-tiering "off" \\
               --volume-free-space-percent "100" --tier-files-older-than-days "0" \\
               --offline-data-transfer "off"
"""

helps['storagesync sync-group server-endpoint delete'] = """
    type: command
    short-summary: Delete a given server endpoint.
    examples:
      - name: Delete a server endpoint "SampleServerEndpoint".
        text: |-
               az storagesync sync-group server-endpoint delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleServerEndpoint"
"""

helps['storagesync sync-group server-endpoint show'] = """
    type: command
    short-summary: Show the properties for a given server endpoint.
    examples:
      - name: Show the properties for server endpoint "SampleServerEndpoint".
        text: |-
               az storagesync sync-group server-endpoint show --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleServerEndpoint"
"""

helps['storagesync sync-group server-endpoint list'] = """
    type: command
    short-summary: List all server endpoints in a sync group.
    examples:
      - name: List all server endpoints in sync group "SampleSyncGroup".
        text: |-
               az storagesync sync-group server-endpoint list --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup"
"""

helps['storagesync sync-group server-endpoint wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of a server endpoint is met.
    examples:
      - name: Place the CLI in a waiting state until a condition of a server endpoint is created.
        text: |-
               az storagesync sync-group server-endpoint wait --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --name "SampleServerEndpoint" --created
"""

helps['storagesync registered-server'] = """
    type: group
    short-summary: Manage registered server.
"""

helps['storagesync registered-server delete'] = """
    type: command
    short-summary: Unregister an on-premises server from it's storage sync service.
    long-summary: Unregister an on-premises server from it's storage sync service which will result in cascading deletes of all server endpoints on this server.
    examples:
      - name: Unregister an on-premises server "41166691-ab03-43e9-ab3e-0330eda162ac" from it's storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync registered-server delete --resource-group "SampleResourceGroup" --storage-sync-service \\
               "SampleStorageSyncService" --server-id "41166691-ab03-43e9-ab3e-0330eda162ac"
"""

helps['storagesync registered-server show'] = """
    type: command
    short-summary: Show the properties for a given registered server.
    examples:
      - name: Show the properties for registered server "080d4133-bdb5-40a0-96a0-71a6057bfe9a".
        text: |-
               az storagesync registered-server show --resource-group "SampleResourceGroup" --storage-sync-service \\
               "SampleStorageSyncService" --server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a"
"""

helps['storagesync registered-server list'] = """
    type: command
    short-summary: List all registered servers for a given storage sync service.
    examples:
      - name: List all registered servers for storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync registered-server list --resource-group "SampleResourceGroup" --storage-sync-service \\
               "SampleStorageSyncService"
"""

helps['storagesync registered-server wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of a registered server is met.
    examples:
      - name: Place the CLI in a waiting state until a condition of a registered server is deleted.
        text: |-
               az storagesync registered-server wait --resource-group "SampleResourceGroup" \\
               --storage-sync-service "SampleStorageSyncService" \\
               --server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a" --deleted
"""
