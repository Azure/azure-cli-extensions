# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long, too-many-lines

helps['storage account create'] = """
    type: command
    short-summary: Create a storage account.
    long-summary: >
        The SKU of the storage account defaults to 'Standard_RAGRS'.
    examples:
        - name: Create a storage account 'MyStorageAccount' in resource group 'MyResourceGroup' in the West US region with locally redundant storage.
          text: az storage account create -n MyStorageAccount -g MyResourceGroup -l westus --sku Standard_LRS
          min_profile: latest
        - name: Create a storage account 'MyStorageAccount' in resource group 'MyResourceGroup' in the West US region with locally redundant storage.
          text: az storage account create -n MyStorageAccount -g MyResourceGroup -l westus --account-type Standard_LRS
          max_profile: 2017-03-09-profile
"""

helps['storage account update'] = """
    type: command
    short-summary: Update the properties of a storage account.
"""

helps['storage blob service-properties'] = """
    type: group
    short-summary: Manage storage blob service properties.
"""

helps['storage blob service-properties update'] = """
    type: command
    short-summary: Update storage blob service properties.
"""

helps['storage account management-policy'] = """
    type: group
    short-summary: Manage storage account management policies.
"""

helps['storage account management-policy create'] = """
    type: command
    short-summary: Creates the data policy rules associated with the specified storage account.
"""

helps['storage account management-policy update'] = """
    type: command
    short-summary: Updates the data policy rules associated with the specified storage account.
"""

helps['storage azcopy'] = """
    type: group
    short-summary: |
        [EXPERIMENTAL] Manage storage operations utilizing AzCopy.
    long-summary: |
        Open issues here: https://github.com/Azure/azure-storage-azcopy
"""

helps['storage azcopy blob'] = """
    type: group
    short-summary: Manage object storage for unstructured data (blobs) using AzCopy.
"""

helps['storage azcopy blob upload'] = """
    type: command
    short-summary: Upload blobs to a storage blob container using AzCopy.
"""

helps['storage azcopy blob download'] = """
    type: command
    short-summary: Download blobs from a storage blob container using AzCopy.
"""

helps['storage azcopy blob delete'] = """
    type: command
    short-summary: Delete blobs from a storage blob container using AzCopy.
"""

helps['storage azcopy run-command'] = """
    type: command
    short-summary: Run a command directly using the AzCopy CLI. Please use SAS tokens for authentication.
"""
