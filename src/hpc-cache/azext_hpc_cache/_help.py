# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['hpc-cache skus'] = """
type: group
short-summary: Commands to manage hpc cache skus.
"""

helps['hpc-cache skus list'] = """
type: command
short-summary: Get the list of StorageCache.Cache SKUs available to this subscription.
examples:
  - name: Skus_List
    text: az hpc-cache skus list
"""

helps['hpc-cache usage-model'] = """
type: group
short-summary: Commands to manage hpc cache usage model.
"""

helps['hpc-cache usage-model list'] = """
type: command
short-summary: Get the list of Cache Usage Models available to this subscription.
examples:
  - name: UsageModels_List
    text: az hpc-cache usage-model list
"""

helps['hpc-cache'] = """
type: group
short-summary: Commands to manage hpc cache.
"""

helps['hpc-cache create'] = """
type: command
short-summary: Create or update a Cache.
examples:
  - name: Caches_CreateOrUpdate
    text: az hpc-cache create --resource-group "scgroup" --name "sc1" --location "eastus" --cache-size-gb "3072" --subnet "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/subnets/{subnet_name}" --sku-name "Standard_2G"
"""

helps['hpc-cache update'] = """
type: command
short-summary: Update a Cache.
examples:
  - name: Caches_Update
    text: az hpc-cache update --resource-group "scgroup" --name "sc1" --tags "key=val"
"""

helps['hpc-cache delete'] = """
type: command
short-summary: Schedule a Cache for deletion.
examples:
  - name: Caches_Delete
    text: az hpc-cache delete --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache show'] = """
type: command
short-summary: Return a Cache.
examples:
  - name: Caches_Get
    text: az hpc-cache show --resource-group "scgroup" --name "sc1"
"""

helps['hpc-cache list'] = """
type: command
short-summary: Return all Caches the user has access to under a resource group.
examples:
  - name: Caches_List
    text: az hpc-cache list
  - name: Caches_ListByResourceGroup
    text: az hpc-cache list --resource-group "scgroup"
"""

helps['hpc-cache start'] = """
type: command
short-summary: Tell a Stopped state Cache to transition to Active state.
examples:
  - name: Caches_Start
    text: az hpc-cache start --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache stop'] = """
type: command
short-summary: Tell an Active Cache to transition to Stopped state.
examples:
  - name: Caches_Stop
    text: az hpc-cache stop --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache flush'] = """
type: command
short-summary: Tell a Cache to write all dirty data to the Storage Target(s). During the flush, clients will see errors returned until the flush is complete.
examples:
  - name: Caches_Flush
    text: az hpc-cache flush --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache upgrade-firmware'] = """
type: command
short-summary: Upgrade a Cache's firmware if a new version is available. Otherwise, this operation has no effect.
examples:
  - name: Caches_UpgradeFirmware
    text: az hpc-cache upgrade-firmware --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache wait'] = """
type: command
short-summary: Wait a hpc Cache to specified state.
examples:
  - name: Caches_Wait
    text: az hpc-cache wait --resource-group "scgroup" --name "sc" --created
"""

helps['hpc-cache storage-target'] = """
type: group
short-summary: Commands to manage hpc cache storage target.
"""

helps['hpc-cache blob-storage-target'] = """
type: group
short-summary: Commands to create hpc cache blob storage target.
"""

helps['hpc-cache nfs-storage-target'] = """
type: group
short-summary: Commands to create hpc cache nfs storage target.
"""

helps['hpc-cache blob-storage-target add'] = """
type: command
short-summary: Create or update a blob Storage Target. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual creation/modification of the Storage Target may be delayed until the Cache is healthy again.
examples:
  - name: StorageTargets_CreateOrUpdate
    text: az hpc-cache blob-storage-target add --resource-group "scgroup" --cache-name "sc1" --name "st1" --storage-account "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{acount_name}" --container-name "cn" --virtual-namespace-path "/test"
"""

helps['hpc-cache blob-storage-target update'] = """
type: command
short-summary: Create or update a blob Storage Target. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual creation/modification of the Storage Target may be delayed until the Cache is healthy again.
"""

helps['hpc-cache nfs-storage-target add'] = """
type: command
short-summary: Create or update a nfs Storage Target. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual creation/modification of the Storage Target may be delayed until the Cache is healthy again.
examples:
  - name: StorageTargets_CreateOrUpdate
    text: az hpc-cache nfs-storage-target add --resource-group "scgroup" --cache-name "sc1" --name "st1" --nfs3-target 10.7.0.24 --nfs3-usage-model WRITE_AROUND --junction namespace-path="/nt2" nfs-export="/export/a" target-path="/1" --junction namespace-path="/nt3" nfs-export="/export/b"
"""

helps['hpc-cache nfs-storage-target update'] = """
type: command
short-summary: Create or update a nfs Storage Target. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual creation/modification of the Storage Target may be delayed until the Cache is healthy again.
"""

helps['hpc-cache storage-target remove'] = """
type: command
short-summary: Remove a Storage Target from a Cache. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual removal of the Storage Target may be delayed until the Cache is healthy again. Note that if the Cache has data to flush to the Storage Target, the data will be flushed before the Storage Target will be deleted.
examples:
  - name: StorageTargets_Delete
    text: az hpc-cache storage-target remove --resource-group "scgroup" --cache-name "sc1" --name "st1"
"""

helps['hpc-cache storage-target show'] = """
type: command
short-summary: Return a Storage Target from a Cache.
examples:
  - name: StorageTargets_Get
    text: az hpc-cache storage-target show --resource-group "scgroup" --cache-name "sc1" --name "st1"
"""

helps['hpc-cache storage-target list'] = """
type: command
short-summary: Return a list of Storage Targets for the specified Cache.
examples:
  - name: StorageTargets_List
    text: az hpc-cache storage-target list --resource-group "scgroup" --cache-name "sc1"
"""
