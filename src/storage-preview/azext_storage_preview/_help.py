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
        - name: Create a storage account 'mystorageaccount' in resource group 'MyResourceGroup' in the West US region with locally redundant storage.
          text: az storage account create -n mystorageaccount -g MyResourceGroup -l westus --sku Standard_LRS
"""

helps['storage account blob-inventory-policy'] = """
type: group
short-summary: Manage storage account Blob Inventory Policy.
"""

helps['storage account blob-inventory-policy create'] = """
type: command
short-summary: Create Blob Inventory Policy for storage account.
examples:
  - name: Create Blob Inventory Policy trough json file for storage account.
    text: az storage account blob-inventory-policy create -g ResourceGroupName --account-name storageAccountName --policy @policy.json
"""

helps['storage account blob-inventory-policy show'] = """
type: command
short-summary: Show Blob Inventory Policy properties associated with the specified storage account.
examples:
  - name: Show Blob Inventory Policy properties associated with the specified storage account without prompt.
    text: az storage account blob-inventory-policy show -g ResourceGroupName --account-name storageAccountName
"""

helps['storage account blob-inventory-policy update'] = """
type: command
short-summary: Update Blob Inventory Policy associated with the specified storage account.
examples:
  - name: Update Blob Inventory Policy associated with the specified storage account.
    text: az storage account blob-inventory-policy update -g ResourceGroupName --account-name storageAccountName --set "policy.rules[0].name=newname"
"""

helps['storage account blob-inventory-policy delete'] = """
type: command
short-summary: Delete Blob Inventory Policy associated with the specified storage account.
examples:
  - name: Delete Blob Inventory Policy associated with the specified storage account without prompt.
    text: az storage account blob-inventory-policy delete -g ResourceGroupName --account-name storageAccountName -y
"""

helps['storage account file-service-properties'] = """
type: group
short-summary: Manage the properties of file service in storage account.
"""

helps['storage account file-service-properties show'] = """
type: command
short-summary: Show the properties of file service in storage account.
long-summary: >
    Show the properties of file service in storage account.
examples:
  - name: Show the properties of file service in storage account.
    text: az storage account file-service-properties show -n mystorageaccount -g MyResourceGroup
"""

helps['storage account file-service-properties update'] = """
type: command
short-summary: Update the properties of file service in storage account.
long-summary: >
    Update the properties of file service in storage account.
examples:
  - name: Enable soft delete policy and set delete retention days to 100 for file service in storage account.
    text: az storage account file-service-properties update --enable-delete-retention true --delete-retention-days 100 -n mystorageaccount -g MyResourceGroup
  - name: Disable soft delete policy for file service.
    text: az storage account file-service-properties update --enable-delete-retention false -n mystorageaccount -g MyResourceGroup
  - name: Enable SMB Multichannel setting for file service.
    text: az storage account file-service-properties update --enable-smb-multichannel -n mystorageaccount -g MyResourceGroup
  - name: Disable SMB Multichannel setting for file service.
    text: az storage account file-service-properties update --enable-smb-multichannel false -n mystorageaccount -g MyResourceGroup
  - name: Set secured SMB setting for file service.
    text: >
        az storage account file-service-properties update --versions SMB2.1;SMB3.0;SMB3.1.1
        --auth-methods NTLMv2;Kerberos --kerb-ticket-encryption RC4-HMAC;AES-256
        --channel-encryption AES-CCM-128;AES-GCM-128;AES-GCM-256 -n mystorageaccount -g MyResourceGroup
"""

helps['storage account keys list'] = """
type: command
short-summary: List the access keys or Kerberos keys (if active directory enabled) for a storage account.
examples:
  - name: List the access keys for a storage account.
    text: az storage account keys list -g MyResourceGroup -n MyStorageAccount
"""

helps['storage account keys renew'] = """
type: command
short-summary: Regenerate one of the access keys or Kerberos keys (if active directory enabled) for a storage account.
long-summary: >
    Kerberos key is generated per storage account for Azure Files identity based authentication either with
    Azure Active Directory Domain Service (Azure AD DS) or Active Directory Domain Service (AD DS). It is used as the
    password of the identity registered in the domain service that represents the storage account. Kerberos key does not
    provide access permission to perform any control or data plane read or write operations against the storage account.
examples:
  - name: Regenerate one of the access keys for a storage account.
    text: az storage account keys renew -g MyResourceGroup -n MyStorageAccount --key primary
  - name: Regenerate one of the Kerberos keys for a storage account.
    text: az storage account keys renew -g MyResourceGroup -n MyStorageAccount --key secondary
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
    examples:
        - name: Upload a single blob to a container.
          text: az storage azcopy blob upload -c MyContainer --account-name MyStorageAccount -s "path/to/file" -d NewBlob
        - name: Upload a directory to a container.
          text: az storage azcopy blob upload -c MyContainer --account-name MyStorageAccount -s "path/to/directory" --recursive
        - name: Upload the contents of a directory to a container.
          text: az storage azcopy blob upload -c MyContainer --account-name MyStorageAccount -s "path/to/directory/*" --recursive
"""

helps['storage azcopy blob download'] = """
    type: command
    short-summary: Download blobs from a storage blob container using AzCopy.
    examples:
        - name: Download a single blob from a container.
          text: az storage azcopy blob download -c MyContainer --account-name MyStorageAccount -s "path/to/blob" -d "path/to/file"
        - name: Download a virtual directory from a container.
          text: az storage azcopy blob download -c MyContainer --account-name MyStorageAccount -s "path/to/virtual_directory" -d "download/path" --recursive
        - name: Download the contents of a container onto a local file system.
          text: az storage azcopy blob download -c MyContainer --account-name MyStorageAccount -s * -d "download/path" --recursive
"""

helps['storage azcopy blob delete'] = """
    type: command
    short-summary: Delete blobs from a storage blob container using AzCopy.
    examples:
        - name: Delete a single blob from a container.
          text: az storage azcopy blob delete -c MyContainer --account-name MyStorageAccount -t TargetBlob
        - name: Delete all blobs from a container.
          text: az storage azcopy blob delete -c MyContainer --account-name MyStorageAccount --recursive
        - name: Delete all blobs in a virtual directory.
          text: az storage azcopy blob delete -c MyContainer --account-name MyStorageAccount -t "path/to/virtual_directory" --recursive
"""

helps['storage azcopy blob sync'] = """
    type: command
    short-summary: Sync blobs recursively to a storage blob container using AzCopy.
    examples:
        - name: Sync a single blob to a container.
          text: az storage azcopy blob sync -c MyContainer --account-name MyStorageAccount -s "path/to/file" -d NewBlob
        - name: Sync a directory to a container.
          text: az storage azcopy blob sync -c MyContainer --account-name MyStorageAccount -s "path/to/directory"
"""

helps['storage azcopy run-command'] = """
    type: command
    short-summary: Run a command directly using the AzCopy CLI. Please use SAS tokens for authentication.
"""

helps['storage blob access'] = """
    type: group
    short-summary: Manage the access control properties of a blob when Hierarchical Namespace is enabled
"""

helps['storage blob access set'] = """
    type: command
    short-summary: Set the access control properties of a blob.
    examples:
        - name: Set the access control properties of a blob.
          text: az storage blob access set -a "user::rwx,group::r--,other::---" -b MyBlob -c MyContainer --account-name MyStorageAccount
"""

helps['storage blob access show'] = """
    type: command
    short-summary: Show the access control properties of a blob.
    examples:
        - name: Show the access control properties of a blob.
          text: az storage blob access show -b MyBlob -c MyContainer --account-name MyStorageAccount
"""

helps['storage blob access update'] = """
    type: command
    short-summary: Update the access control properties of a blob.
    examples:
        - name: Update the access permissions of a blob.
          text: az storage blob access update --permissions "rwxrwxrwx" -b MyBlob -c MyContainer --account-name MyStorageAccount
        - name: Update the owning user of a blob.
          text: az storage blob access update --owner [entityId/UPN] -b MyBlob -c MyContainer --account-name MyStorageAccount
        - name: Update the owning group of a blob.
          text: az storage blob access update --group [entityId/UPN] -b MyBlob -c MyContainer --account-name MyStorageAccount
"""

helps['storage blob move'] = """
    type: command
    short-summary: Move a blob in a storage container.
    examples:
        - name: Move a blob in a storage container.
          text: az storage blob move -c MyContainer -d DestinationBlobPath -s SourceBlobPath --account-name MyStorageAccount
"""

helps['storage blob directory'] = """
    type: group
    short-summary: Manage blob directories in storage account container.
    long-summary: To use the directory commands, please make sure your storage account type is StorageV2.
"""

helps['storage blob directory access'] = """
    type: group
    short-summary: Manage the access control properties of a directory when Hierarchical Namespace is enabled
"""

helps['storage blob directory access set'] = """
    type: command
    short-summary: Set the access control properties of a directory.
    examples:
        - name: Set the access control properties of a directory.
          text: az storage blob directory access set -a "user::rwx,group::r--,other::---" -d MyDirectoryPath -c MyContainer --account-name MyStorageAccount
"""

helps['storage blob directory access show'] = """
    type: command
    short-summary: Show the access control properties of a directory.
    examples:
        - name: Show the access control properties of a directory.
          text: az storage blob directory access show -d MyDirectoryPath -c MyContainer --account-name MyStorageAccount
"""

helps['storage blob directory access update'] = """
    type: command
    short-summary: Update the access control properties of a directory.
    examples:
        - name: Update the access permissions of a directory.
          text: az storage blob directory access update --permissions "rwxrwxrwx" -d MyDirectoryPath -c MyContainer --account-name MyStorageAccount
        - name: Update the owning user of a directory.
          text: az storage blob directory access update --owner [entityId/UPN] -d MyDirectoryPath -c MyContainer --account-name MyStorageAccount
        - name: Update the owning group of a directory.
          text: az storage blob directory access update --group [entityId/UPN] -d MyDirectoryPath -c MyContainer --account-name MyStorageAccount
"""

helps['storage blob directory create'] = """
    type: command
    short-summary: Create a storage blob directory in a storage container.
    long-summary: Create a storage blob directory which can contain other directories or blobs in a storage container.
    examples:
        - name: Create a storage blob directory in a storage container.
          text: az storage blob directory create -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
        - name: Create a storage blob directory with permissions and umask.
          text: az storage blob directory create -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount --permissions rwxrwxrwx --umask 0000
"""

helps['storage blob directory delete'] = """
    type: command
    short-summary: Delete a storage blob directory in a storage container.
    long-summary: >
        This operation's behavior is different depending on whether Hierarchical Namespace
        is enabled; if yes, then the delete operation can be atomic and instantaneous;
        if not, the operation is performed in batches and a continuation token could be returned.
    examples:
        - name: Delete a storage blob directory in a storage container.
          text: az storage blob directory delete -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
"""

helps['storage blob directory download'] = """
    type: command
    short-summary: Download blobs to a local file path.
    examples:
        - name: Download a single blob in a storage blob directory.
          text: az storage blob directory download -c MyContainer --account-name MyStorageAccount -s "path/to/blob" -d "<local-path>"
        - name: Download the entire directory in a storage container.
          text: az storage blob directory download -c MyContainer --account-name MyStorageAccount -s SourceDirectoryPath -d "<local-path>" --recursive
        - name: Download an entire subdirectory of a storage blob directory.
          text: az storage blob directory download -c MyContainer --account-name MyStorageAccount -s "path/to/subdirectory" -d "<local-path>" --recursive
"""

helps['storage blob directory exists'] = """
    type: command
    short-summary: Check for the existence of a blob directory in a storage container.
    examples:
        - name: Check for the existence of a blob directory in a storage container.
          text: az storage blob directory exists -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
"""

helps['storage blob directory list'] = """
    type: command
    short-summary: List blobs and blob subdirectories in a storage directory.
    examples:
        - name: List blobs and blob subdirectories in a storage directory.
          text: az storage blob directory list -c MyContainer -d DestinationDirectoryPath --account-name MyStorageAccount
"""

helps['storage blob directory metadata'] = """
    type: group
    short-summary: Manage directory metadata.
"""

helps['storage blob directory metadata show'] = """
    type: command
    short-summary: Show all user-defined metadata for the specified blob directory.
    examples:
        - name: Show all user-defined metadata for the specified blob directory.
          text: az storage blob directory metadata show -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
"""

helps['storage blob directory metadata update'] = """
    type: command
    short-summary: Set user-defined metadata for the specified blob directory as one or more name-value pairs.
    examples:
        - name: Set user-defined metadata for the specified blob directory as one or more name-value pairs.
          text: az storage blob directory metadata update --metadata tag1=value1 -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
"""

helps['storage blob directory move'] = """
    type: command
    short-summary: Move a storage directory to another storage blob directory in a storage container.
    long-summary: >
        Move a storage directory and all its content (which can contain other directories or blobs) to another storage
        blob directory in a storage container. This operation's behavior is different depending on whether Hierarchical
        Namespace is enabled; if yes, the move operation is atomic and no marker is returned; if not, the operation is
        performed in batches and a continuation token could be returned.
    examples:
        - name: Move a storage directory to another storage blob directory in a storage container.
          text: az storage blob directory move -c MyContainer -d my-new-directory -s dir --account-name MyStorageAccount
        - name: Move a storage subdirectory to another storage blob directory in a storage container.
          text: az storage blob directory move -c MyContainer -d my-new-directory -s dir/subdirectory --account-name MyStorageAccount
"""

helps['storage blob directory show'] = """
    type: command
    short-summary: Show a storage blob directory properties in a storage container.
    examples:
        - name: Show a storage blob directory properties in a storage container.
          text: az storage blob directory show -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
"""

helps['storage blob directory upload'] = """
    type: command
    short-summary: Upload blobs or subdirectories to a storage blob directory.
    examples:
        - name: Upload a single blob to a storage blob directory.
          text: az storage blob directory upload -c MyContainer --account-name MyStorageAccount -s "path/to/file" -d directory
        - name: Upload a local directory to a storage blob directory.
          text: az storage blob directory upload -c MyContainer --account-name MyStorageAccount -s "path/to/directory" -d directory --recursive
        - name: Upload a set of files in a local directory to a storage blob directory.
          text: az storage blob directory upload -c MyContainer --account-name MyStorageAccount -s "path/to/file*" -d directory --recursive
"""

helps['storage fs list-deleted-path'] = """
type: command
short-summary: List the deleted (file or directory) paths under the specified file system.
examples:
  - name: List the deleted (file or directory) paths under the specified file system..
    text: |
        az storage fs list-deleted-path -f myfilesystem --account-name mystorageccount --account-key 00000000
"""

helps['storage fs service-properties'] = """
type: group
short-summary: Manage storage datalake service properties.
"""

helps['storage fs service-properties show'] = """
type: command
short-summary: Show the properties of a storage account's datalake service, including Azure Storage Analytics.
examples:
  - name: Show the properties of a storage account's datalake service
    text: |
        az storage fs service-properties show --account-name mystorageccount --account-key 00000000
"""

helps['storage fs service-properties update'] = """
type: command
short-summary: Update the properties of a storage account's datalake service, including Azure Storage Analytics.
examples:
  - name: Update the properties of a storage account's datalake service
    text: |
        az storage fs service-properties update --delete-retention --delete-retention-period 7 --account-name mystorageccount --account-key 00000000
"""

helps['storage fs undelete-path'] = """
type: command
short-summary: Restore soft-deleted path.
long-summary: Operation will only be successful if used within the specified number of days set in the delete retention policy.
examples:
  - name: Restore soft-deleted path.
    text: |
        az storage fs undelete-path -f myfilesystem --deleted-path-name dir --deletion-id 0000 --account-name mystorageccount --account-key 00000000
"""
