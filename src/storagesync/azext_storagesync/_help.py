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

helps['storagesync storage-sync-service'] = """
    type: group
    short-summary: Manage storage sync service.
"""

helps['storagesync storage-sync-service create'] = """
    type: command
    short-summary: Create a new storage sync service.
    examples:
      - name: Create a new storage sync service "SampleStorageSyncService" in resource group 'SampleResourceGroup'.
        text: |-
               az storagesync storage-sync-service create --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --location "WestUS"
"""

helps['storagesync storage-sync-service delete'] = """
    type: command
    short-summary: Delete a given storage sync service.
    examples:
      - name: Delete a storage sync service "SampleStorageSyncService" in resource group 'SampleResourceGroup'.
        text: |-
               az storagesync storage-sync-service delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService"
"""

helps['storagesync storage-sync-service show'] = """
    type: command
    short-summary: Show the properties for a given storage sync service.
    examples:
      - name: Show the properties for storage sync service "SampleStorageSyncService" in resource group 'SampleResourceGroup'.
        text: |-
               az storagesync storage-sync-service show --resource-group "SampleResourceGroup" --storage-sync-service-name \\
               "SampleStorageSyncService"
"""

helps['storagesync storage-sync-service list'] = """
    type: command
    short-summary: List all storage sync services in a resource group or a subscription.
    examples:
      - name: List all storage sync services in a resource group "SampleResourceGroup".
        text: |-
               az storagesync storage-sync-service list --resource-group "SampleResourceGroup"
      - name: List all storage sync services in current subscription
        text: |-
               az storagesync storage-sync-service list
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
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name "SampleSyncGroup"
"""

helps['storagesync sync-group delete'] = """
    type: command
    short-summary: Delete a given sync group.
    examples:
      - name: Delete sync group "SampleSyncGroup" in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name "SampleSyncGroup"
"""

helps['storagesync sync-group show'] = """
    type: command
    short-summary: Show the properties for a given sync group.
    examples:
      - name: Show the properties for sync group "SampleSyncGroup" in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group show --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name "SampleSyncGroup"
"""

helps['storagesync sync-group list'] = """
    type: command
    short-summary: List all sync groups in a storage sync service.
    examples:
      - name: List all sync groups in storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync sync-group list --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService"
"""

helps['storagesync cloud-endpoint'] = """
    type: group
    short-summary: Manage cloud endpoint.
"""

helps['storagesync cloud-endpoint create'] = """
    type: command
    short-summary: Create a new cloud endpoint.
    examples:
      - name: Create a new cloud endpoint "SampleCloudEndpoint" in sync group "SampleSyncGroup".
        text: |-
               az storagesync cloud-endpoint create --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --cloud-endpoint-name "SampleCloudEndpoint" --storage-account "storage_account_name" --azure-file-share-name \\
               "cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4" --storage-account-tenant-id \\
               "72f988bf-86f1-41af-91ab-2d7cd011db47"
"""

helps['storagesync cloud-endpoint delete'] = """
    type: command
    short-summary: Delete a given cloud endpoint.
    examples:
      - name: Delete cloud endpoint "SampleCloudEndpoint".
        text: |-
               az storagesync cloud-endpoint delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --cloud-endpoint-name "SampleCloudEndpoint"
"""

helps['storagesync cloud-endpoint show'] = """
    type: command
    short-summary: Show the properties for a given cloud endpoint.
    examples:
      - name: Show the properties for cloud endpoint "SampleCloudEndpoint".
        text: |-
               az storagesync cloud-endpoint show --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --cloud-endpoint-name "SampleCloudEndpoint"
"""

helps['storagesync cloud-endpoint list'] = """
    type: command
    short-summary: List all cloud endpoints in a sync group.
    examples:
      - name: List all cloud endpoints in sync group "SampleSyncGroup".
        text: |-
               az storagesync cloud-endpoint list --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup"
"""

helps['storagesync server-endpoint'] = """
    type: group
    short-summary: Manage server endpoint.
"""

helps['storagesync server-endpoint create'] = """
    type: command
    short-summary: Create a new server endpoint.
    examples:
      - name: Create a new server endpoint "SampleServerEndpoint" in sync group "SampleSyncGroup".
        text: |-
               az storagesync server-endpoint create --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --server-endpoint-name "SampleServerEndpoint" --server-resource-id \\
               /subscriptions/sub/resourceGroups/rg/providers/microsoft.storagesync/storageSyncServices/ss/registeredServers/91beed22-7e9e-4bda-9313-fec96cf286e0 \\
               --server-local-path "d:\\abc"
"""

helps['storagesync server-endpoint update'] = """
    type: command
    short-summary: Update the properties for a given server endpoint.
    examples:
      - name: Update the properties for server endpoint "SampleServerEndpoint".
        text: |-
               az storagesync server-endpoint update --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --server-endpoint-name "SampleServerEndpoint" --cloud-tiering "off" \\
               --volume-free-space-percent "100" --tier-files-older-than-days "0" \\
               --offline-data-transfer "off"
"""

helps['storagesync server-endpoint delete'] = """
    type: command
    short-summary: Delete a given server endpoint.
    examples:
      - name: Delete a server endpoint "SampleServerEndpoint".
        text: |-
               az storagesync server-endpoint delete --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --server-endpoint-name "SampleServerEndpoint"
"""

helps['storagesync server-endpoint show'] = """
    type: command
    short-summary: Show the properties for a given server endpoint.
    examples:
      - name: Show the properties for server endpoint "SampleServerEndpoint".
        text: |-
               az storagesync server-endpoint show --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup" --server-endpoint-name "SampleServerEndpoint"
"""

helps['storagesync server-endpoint list'] = """
    type: command
    short-summary: List all server endpoints in a sync group.
    examples:
      - name: List all server endpoints in sync group "SampleSyncGroup".
        text: |-
               az storagesync server-endpoint list --resource-group "SampleResourceGroup" \\
               --storage-sync-service-name "SampleStorageSyncService" --sync-group-name \\
               "SampleSyncGroup"
"""

helps['storagesync registered-server'] = """
    type: group
    short-summary: Manage registered server.
"""

helps['storagesync registered-server create'] = """
    type: command
    short-summary: Register an on-premises server to a storage sync service which creates a trust relationship.
    examples:
      - name: Register an on-premises server to storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync registered-server create --resource-group "SampleResourceGroup" --storage-sync-service-name \\
               "SampleStorageSyncService"
"""

helps['storagesync registered-server delete'] = """
    type: command
    short-summary: Unregister an on-premises server from it's storage sync service.
    long-summary: Unregister an on-premises server from it's storage sync service which will result in cascading deletes of all server endpoints on this server.
    examples:
      - name: Unregister an on-premises server "41166691-ab03-43e9-ab3e-0330eda162ac" from it's storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync registered-server delete --resource-group "SampleResourceGroup" --storage-sync-service-name \\
               "SampleStorageSyncService" --server-id "41166691-ab03-43e9-ab3e-0330eda162ac"
"""

helps['storagesync registered-server show'] = """
    type: command
    short-summary: Show the properties for a given registered server.
    examples:
      - name: Show the properties for registered server "080d4133-bdb5-40a0-96a0-71a6057bfe9a".
        text: |-
               az storagesync registered-server show --resource-group "SampleResourceGroup" --storage-sync-service-name \\
               "SampleStorageSyncService" --server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a"
"""

helps['storagesync registered-server list'] = """
    type: command
    short-summary: List all registered servers for a given storage sync service.
    examples:
      - name: List all registered servers for storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync registered-server list --resource-group "SampleResourceGroup" --storage-sync-service-name \\
               "SampleStorageSyncService"
"""

helps['storagesync registered-server rollover-certificate'] = """
    type: command
    short-summary: Rollover the local server certificate used to describe the server identity to the storage sync service.
    long-summary: Rollover the local server certificate and inform the corresponding storage sync service of the server's new identity, in a secure way.
    examples:
      - name: Rollover local server certificate and inform storage sync service "SampleStorageSyncService".
        text: |-
               az storagesync registered-server rollover-certificate--resource-group \\
               "SampleResourceGroup" --storage-sync-service-name "SampleStorageSyncService"
"""