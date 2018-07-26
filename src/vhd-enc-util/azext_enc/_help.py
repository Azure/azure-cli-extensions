# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['vm encryption encrypt-vhd'] = """
    type: command
    short-summary: encrypt VHD using XTS 256-bit cipher model
    examples:
        - name: encrype a VHD and upload to a storage account
          text: |
            az vm encryption encrypt-vhd --vhd-file ~/os_disk.vhd --storage-account myStorageAccount --container vhds --kv /subscriptions/xxxx/resourceGroups/myGroup/providers/Microsoft.KeyVault/vaults/myVault --kek myKey --storage-account myStorageAccount
        - name: encrypt a VHD at local (not uploading to storage)
          text: |
            az vm encryption encrypt-vhd --vhd-file ~/os_disk.vhd --vhd-file-enc ~/os_disk.encrypted.vhd --kv /subscriptions/xxxx/resourceGroups/myGroup/providers/Microsoft.KeyVault/vaults/myVault --kek myKey --storage-account myStorageAccount
"""
