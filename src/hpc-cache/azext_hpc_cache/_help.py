# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['hpc-cache operation'] = """
    type: group
    short-summary: Commands to manage hpc cache operation.
"""

helps['hpc-cache operation list'] = """
    type: command
    short-summary: Lists all of the available Resource Provider operations.
    examples:
      - name: StorageTargets_List
        text: |-
               az hpc-cache operation list
"""

helps['hpc-cache skus'] = """
    type: group
    short-summary: Commands to manage hpc cache skus.
"""

helps['hpc-cache skus list'] = """
    type: command
    short-summary: Get the list of StorageCache.Cache SKUs available to this subscription.
    examples:
      - name: Skus_List
        text: |-
               az hpc-cache skus list
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
        text: |-
               az hpc-cache usage-model list
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
        text: |-
               az hpc-cache create --resource-group "scgroup" --name "sc1" --location "eastus" \\
               --cache-size-gb "3072" --subnet "/subscriptions/{{ subscription_id }}/resourceGroups/{{ re
               source_group }}/providers/Microsoft.Network/virtualNetworks/{{ virtual_network_name }}/sub
               nets/{{ subnet_name }}" --sku-name "Standard_2G"
"""

helps['hpc-cache update'] = """
    type: command
    short-summary: Create or update a Cache.
    examples:
      - name: Caches_Update
        text: |-
               az hpc-cache update --resource-group "scgroup" --name "sc1" --location "eastus" \\
               --cache-size-gb "3072" --subnet "/subscriptions/{{ subscription_id }}/resourceGroups/{{ re
               source_group }}/providers/Microsoft.Network/virtualNetworks/{{ virtual_network_name }}/sub
               nets/{{ subnet_name }}" --sku-name "Standard_2G"
"""

helps['hpc-cache delete'] = """
    type: command
    short-summary: Schedules a Cache for deletion.
    examples:
      - name: Caches_Delete
        text: |-
               az hpc-cache delete --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache show'] = """
    type: command
    short-summary: Returns a Cache.
    examples:
      - name: Caches_Get
        text: |-
               az hpc-cache show --resource-group "scgroup" --name "sc1"
"""

helps['hpc-cache list'] = """
    type: command
    short-summary: Returns all Caches the user has access to under a resource group.
    examples:
      - name: Caches_List
        text: |-
               az hpc-cache list
      - name: Caches_ListByResourceGroup
        text: |-
               az hpc-cache list --resource-group "scgroup"
"""

helps['hpc-cache flush'] = """
    type: command
    short-summary: Tells a Cache to write all dirty data to the Storage Target(s). During the flush, clients will see errors returned until the flush is complete.
    examples:
      - name: Caches_Flush
        text: |-
               az hpc-cache flush --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache start'] = """
    type: command
    short-summary: Tells a Stopped state Cache to transition to Active state.
    examples:
      - name: Caches_Start
        text: |-
               az hpc-cache start --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache stop'] = """
    type: command
    short-summary: Tells an Active Cache to transition to Stopped state.
    examples:
      - name: Caches_Stop
        text: |-
               az hpc-cache stop --resource-group "scgroup" --name "sc"
"""

helps['hpc-cache upgrade-firmware'] = """
    type: command
    short-summary: Upgrade a Cache's firmware if a new version is available. Otherwise, this operation has no effect.
    examples:
      - name: Caches_UpgradeFirmware
        text: |-
               az hpc-cache upgrade-firmware --resource-group "scgroup" --name "sc1"
"""

helps['hpc-cache storage-target'] = """
    type: group
    short-summary: Commands to manage hpc cache storage target.
"""

helps['hpc-cache storage-target create'] = """
    type: command
    short-summary: Create or update a Storage Target. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual creation/modification of the Storage Target may be delayed until the Cache is healthy again.
    examples:
      - name: StorageTargets_CreateOrUpdate
        text: |-
               az hpc-cache storage-target create --resource-group "scgroup" --cache-name "sc1" --name \\
               "st1" --target-type "nfs3" --nfs3-target "10.0.44.44" --nfs3-usage-model \\
               "READ_HEAVY_INFREQ"
"""

helps['hpc-cache storage-target update'] = """
    type: command
    short-summary: Create or update a Storage Target. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual creation/modification of the Storage Target may be delayed until the Cache is healthy again.
"""

helps['hpc-cache storage-target delete'] = """
    type: command
    short-summary: Removes a Storage Target from a Cache. This operation is allowed at any time, but if the Cache is down or unhealthy, the actual removal of the Storage Target may be delayed until the Cache is healthy again. Note that if the Cache has data to flush to the Storage Target, the data will be flushed before the Storage Target will be deleted.
    examples:
      - name: StorageTargets_Delete
        text: |-
               az hpc-cache storage-target delete --resource-group "scgroup" --cache-name "sc1" --name \\
               "st1"
"""

helps['hpc-cache storage-target show'] = """
    type: command
    short-summary: Returns a Storage Target from a Cache.
    examples:
      - name: StorageTargets_Get
        text: |-
               az hpc-cache storage-target show --resource-group "scgroup" --cache-name "sc1" --name \\
               "st1"
"""

helps['hpc-cache storage-target list'] = """
    type: command
    short-summary: Returns a list of Storage Targets for the specified Cache.
    examples:
      - name: StorageTargets_List
        text: |-
               az hpc-cache storage-target list --resource-group "scgroup" --cache-name "sc1"
"""
