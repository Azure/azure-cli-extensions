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
    long-summary: |
        To learn more about azcopy sync,see https://docs.microsoft.com/azure/storage/common/storage-ref-azcopy-sync.
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

helps['storage file'] = """
type: group
short-summary: Manage file shares that use the SMB 3.0 protocol.
"""

helps['storage file copy'] = """
type: group
short-summary: Manage file copy operations.
"""

helps['storage file copy start'] = """
type: command
short-summary: Copy a file asynchronously.
parameters:
  - name: --source-uri -u
    type: string
    short-summary: >
        A URL of up to 2 KB in length that specifies an Azure file or blob.
        The value should be URL-encoded as it would appear in a request URI.
        If the source is in another account, the source must either be public
        or must be authenticated via a shared access signature. If the source
        is public, no authentication is required.
        Examples:
        https://myaccount.file.core.windows.net/myshare/mydir/myfile
        https://otheraccount.file.core.windows.net/myshare/mydir/myfile?sastoken.
examples:
    - name: Copy a file asynchronously.
      text: |
        az storage file copy start --source-account-name srcaccount --source-account-key 00000000 --source-path <srcpath-to-file> --source-share srcshare --destination-path <destpath-to-file> --destination-share destshare --account-name destaccount --account-key 00000000
    - name: Copy a file asynchronously from source uri to destination storage account with sas token.
      text: |
        az storage file copy start --source-uri "https://srcaccount.file.core.windows.net/myshare/mydir/myfile?<sastoken>" --destination-path <destpath-to-file> --destination-share destshare --account-name destaccount --sas-token <destination-sas>
    - name: Copy a file asynchronously from file snapshot to destination storage account with sas token.
      text: |
        az storage file copy start --source-account-name srcaccount --source-account-key 00000000 --source-path <srcpath-to-file> --source-share srcshare --file-snapshot "2020-03-02T13:51:54.0000000Z" --destination-path <destpath-to-file> --destination-share destshare --account-name destaccount --sas-token <destination-sas>
"""

helps['storage file copy start-batch'] = """
type: command
short-summary: Copy multiple files or blobs to a file share.
parameters:
  - name: --destination-share
    type: string
    short-summary: The file share where the source data is copied to.
  - name: --destination-path
    type: string
    short-summary: The directory where the source data is copied to. If omitted, data is copied to the root directory.
  - name: --pattern
    type: string
    short-summary: The pattern used for globbing files and blobs. The supported patterns are '*', '?', '[seq]', and '[!seq]'. For more information, please refer to https://docs.python.org/3.7/library/fnmatch.html.
    long-summary: When you use '*' in --pattern, it will match any character including the the directory separator '/'.
  - name: --dryrun
    type: bool
    short-summary: List the files and blobs to be copied. No actual data transfer will occur.
  - name: --source-account-name
    type: string
    short-summary: The source storage account to copy the data from. If omitted, the destination account is used.
  - name: --source-account-key
    type: string
    short-summary: The account key for the source storage account. If omitted, the active login is used to determine the account key.
  - name: --source-container
    type: string
    short-summary: The source container blobs are copied from.
  - name: --source-share
    type: string
    short-summary: The source share files are copied from.
  - name: --source-uri
    type: string
    short-summary: A URI that specifies a the source file share or blob container.
    long-summary: If the source is in another account, the source must either be public or authenticated via a shared access signature.
  - name: --source-sas
    type: string
    short-summary: The shared access signature for the source storage account.
examples:
  - name: Copy all files in a file share to another storage account.
    text: |
        az storage file copy start-batch --source-account-name srcaccount --source-account-key 00000000 --source-share srcshare --destination-path <destpath-to-directory> --destination-share destshare --account-name destaccount --account-key 00000000
  - name: Copy all files in a file share to another storage account. with sas token.
    text: |
        az storage file copy start-batch --source-uri "https://srcaccount.file.core.windows.net/myshare?<sastoken>" --destination-path <destpath-to-directory> --destination-share destshare --account-name destaccount --sas-token <destination-sas>
"""

helps['storage file delete-batch'] = """
type: command
short-summary: Delete files from an Azure Storage File Share.
parameters:
  - name: --source -s
    type: string
    short-summary: The source of the file delete operation. The source can be the file share URL or the share name.
  - name: --pattern
    type: string
    short-summary: The pattern used for file globbing. The supported patterns are '*', '?', '[seq]', and '[!seq]'. For more information, please refer to https://docs.python.org/3.7/library/fnmatch.html.
    long-summary: When you use '*' in --pattern, it will match any character including the the directory separator '/'.
  - name: --dryrun
    type: bool
    short-summary: List the files and blobs to be deleted. No actual data deletion will occur.
examples:
  - name: Delete files from an Azure Storage File Share. (autogenerated)
    text: |
        az storage file delete-batch --account-key 00000000 --account-name MyAccount --source /path/to/file
    crafted: true
  - name: Delete files from an Azure Storage File Share. (autogenerated)
    text: |
        az storage file delete-batch --account-key 00000000 --account-name MyAccount --pattern *.py --source /path/to/file
    crafted: true
"""

helps['storage file download'] = """
type: command
short-summary: Download a file to a file path, with automatic chunking and progress notifications.
long-summary: Return an instance of File with properties and metadata.
"""

helps['storage file download-batch'] = """
type: command
short-summary: Download files from an Azure Storage File Share to a local directory in a batch operation.
parameters:
  - name: --source -s
    type: string
    short-summary: The source of the file download operation. The source can be the file share URL or the share name.
  - name: --destination -d
    type: string
    short-summary: The local directory where the files are downloaded to. This directory must already exist.
  - name: --pattern
    type: string
    short-summary: The pattern used for file globbing. The supported patterns are '*', '?', '[seq]', and '[!seq]'. For more information, please refer to https://docs.python.org/3.7/library/fnmatch.html.
    long-summary: When you use '*' in --pattern, it will match any character including the the directory separator '/'.
  - name: --dryrun
    type: bool
    short-summary: List the files and blobs to be downloaded. No actual data transfer will occur.
  - name: --max-connections
    type: integer
    short-summary: The maximum number of parallel connections to use. Default value is 1.
  - name: --snapshot
    type: string
    short-summary: A string that represents the snapshot version, if applicable.
  - name: --validate-content
    type: bool
    short-summary: If set, calculates an MD5 hash for each range of the file for validation.
    long-summary: >
        The storage service checks the hash of the content that has arrived is identical to the hash that was sent.
        This is mostly valuable for detecting bitflips during transfer if using HTTP instead of HTTPS. This hash is not stored.
examples:
  - name: Download files from an Azure Storage File Share to a local directory in a batch operation. (autogenerated)
    text: |
        az storage file download-batch --account-key 00000000 --account-name MyAccount --destination . --no-progress --source /path/to/file
    crafted: true
"""

helps['storage file exists'] = """
type: command
short-summary: Check for the existence of a file.
examples:
  - name: Check for the existence of a file. (autogenerated)
    text: |
        az storage file exists --account-key 00000000 --account-name MyAccount --path path/file.txt --share-name MyShare
    crafted: true
  - name: Check for the existence of a file. (autogenerated)
    text: |
        az storage file exists --connection-string $connectionString --path path/file.txt --share-name MyShare
    crafted: true
"""

helps['storage file generate-sas'] = """
type: command
short-summary: Generate a shared access signature for the file.
examples:
  - name: Generate a sas token for a file.
    text: |
        end=`date -u -d "30 minutes" '+%Y-%m-%dT%H:%MZ'`
        az storage file generate-sas -p path/file.txt -s MyShare --account-name MyStorageAccount --permissions rcdw --https-only --expiry $end
  - name: Generate a shared access signature for the file. (autogenerated)
    text: |
        az storage file generate-sas --account-name MyStorageAccount --expiry 2037-12-31T23:59:00Z --path path/file.txt --permissions rcdw --share-name MyShare --start 2019-01-01T12:20Z
    crafted: true
  - name: Generate a shared access signature for the file. (autogenerated)
    text: |
        az storage file generate-sas --account-key 00000000 --account-name mystorageaccount --expiry 2037-12-31T23:59:00Z --https-only --path path/file.txt --permissions rcdw --share-name myshare
    crafted: true
"""

helps['storage file show'] = """
type: command
short-summary: Return all user-defined metadata, standard HTTP properties, and system properties for the file.
examples:
  - name:  Show properties of file in file share.
    text: |
        az storage file show -p dir/a.txt -s sharename --account-name myadlsaccount --account-key 0000-0000
"""

helps['storage file list'] = """
type: command
short-summary: List files and directories in a share.
parameters:
  - name: --exclude-dir
    type: bool
    short-summary: List only files in the given share.
examples:
  - name: List files and directories in a share. (autogenerated)
    text: |
        az storage file list --share-name MyShare
    crafted: true
"""

helps['storage file delete'] = """
type: command
short-summary: Mark the specified file for deletion.
long-summary: The file is later deleted during garbage collection.
"""

helps['storage file resize'] = """
type: command
short-summary: Resize a file to the specified size.
long-summary: If the specified byte value is less than the current size of the file, then all ranges above
        the specified byte value are cleared.
parameters:
    - name: --size
      short-summary: Size to resize file to (in bytes).
"""

helps['storage file metadata'] = """
type: group
short-summary: Manage file metadata.
"""

helps['storage file metadata show'] = """
type: command
short-summary:  Return all user-defined metadata for the file.
examples:
  - name: Show metadata for the file
    text: az storage file metadata show -s MyShare --path /path/to/file
"""

helps['storage file metadata update'] = """
type: command
short-summary:  Update file metadata.
examples:
  - name: Update metadata for the file
    text: az storage file metadata update -s MyShare --path /path/to/file --metadata key1=value1
"""

helps['storage file update'] = """
type: command
short-summary: Set system properties on the file.
long-summary: If one property is set for the content_settings, all properties will be overriden.
examples:
  - name:  Set system properties on the file.
    text: |
        az storage file update -p dir/a.txt -s sharename --account-name myadlsaccount --account-key 0000-0000 --content-type test/type
"""

helps['storage file upload'] = """
type: command
short-summary: Upload a file to a share that uses the SMB 3.0 protocol.
long-summary: Creates or updates an Azure file from a source path with automatic chunking and progress notifications.
examples:
  - name: Upload to a local file to a share.
    text: az storage file upload -s MyShare --source /path/to/file
  - name: Upload a file to a share that uses the SMB 3.0 protocol. (autogenerated)
    text: |
        az storage file upload --account-key 00000000 --account-name MyStorageAccount --path path/file.txt --share-name MyShare --source /path/to/file
    crafted: true
"""

helps['storage file upload-batch'] = """
type: command
short-summary: Upload files from a local directory to an Azure Storage File Share in a batch operation.
parameters:
  - name: --source -s
    type: string
    short-summary: The directory to upload files from.
  - name: --destination -d
    type: string
    short-summary: The destination of the upload operation.
    long-summary: The destination can be the file share URL or the share name. When the destination is the share URL, the storage account name is parsed from the URL.
  - name: --destination-path
    type: string
    short-summary: The directory where the source data is copied to. If omitted, data is copied to the root directory.
  - name: --pattern
    type: string
    short-summary: The pattern used for file globbing. The supported patterns are '*', '?', '[seq]', and '[!seq]'. For more information, please refer to https://docs.python.org/3.7/library/fnmatch.html.
    long-summary: When you use '*' in --pattern, it will match any character including the the directory separator '/'.
  - name: --dryrun
    type: bool
    short-summary: List the files and blobs to be uploaded. No actual data transfer will occur.
  - name: --max-connections
    type: integer
    short-summary: The maximum number of parallel connections to use. Default value is 1.
  - name: --validate-content
    type: bool
    short-summary: If set, calculates an MD5 hash for each range of the file for validation.
    long-summary: >
        The storage service checks the hash of the content that has arrived is identical to the hash that was sent.
        This is mostly valuable for detecting bitflips during transfer if using HTTP instead of HTTPS. This hash is not stored.
examples:
  - name: Upload files from a local directory to an Azure Storage File Share in a batch operation.
    text: |
        az storage file upload-batch --destination myshare --source . --account-name myaccount --account-key 00000000
  - name: Upload files from a local directory to an Azure Storage File Share with url in a batch operation.
    text: |
        az storage file upload-batch --destination https://myaccount.file.core.windows.net/myshare --source . --account-key 00000000
"""

helps['storage file url'] = """
type: command
short-summary: Create the url to access a file.
examples:
  - name: Create the url to access a file. (autogenerated)
    text: |
        az storage file url --account-key 00000000 --account-name mystorageaccount --path path/file.txt --share-name myshare
    crafted: true
"""

helps['storage directory'] = """
type: group
short-summary: Manage file storage directories.
"""

helps['storage directory create'] = """
type: command
short-summary: Create a new directory under the specified share or parent directory.
"""

helps['storage directory delete'] = """
type: command
short-summary: Delete the specified empty directory.
"""

helps['storage directory show'] = """
type: command
short-summary: Get all user-defined metadata and system properties for the specified directory
"""

helps['storage directory exists'] = """
type: command
short-summary: Check for the existence of a storage directory.
examples:
  - name: Check for the existence of a storage directory. (autogenerated)
    text: |
        az storage directory exists --account-key 00000000 --account-name MyAccount --name MyDirectory --share-name MyShare
    crafted: true
"""

helps['storage directory list'] = """
type: command
short-summary: List directories in a share.
examples:
  - name: List directories in a share. (autogenerated)
    text: |
        az storage directory list --account-key 00000000 --account-name MyAccount --share-name MyShare
    crafted: true
"""

helps['storage directory metadata'] = """
type: group
short-summary: Manage file storage directory metadata.
"""

helps['storage directory metadata show'] = """
type: command
short-summary: Get all user-defined metadata for the specified directory.
"""

helps['storage directory metadata update'] = """
type: command
short-summary: Set one or more user-defined name-value pairs for the specified directory.
"""

helps['storage share list-handle'] = """
type: command
short-summary: List file handles of a file share.
examples:
  - name: List all file handles of a file share recursively.
    text: |
        az storage share list-handle --account-name MyAccount --name MyFileShare --recursive
  - name: List all file handles of a file directory recursively.
    text: |
        az storage share list-handle --account-name MyAccount --name MyFileShare --path 'dir1' --recursive
  - name: List all file handles of a file.
    text: |
        az storage share list-handle --account-name MyAccount --name MyFileShare --path 'dir1/test.txt'
"""

helps['storage share close-handle'] = """
type: command
short-summary: Close file handles of a file share.
examples:
  - name: Close all file handles of a file share recursively.
    text: |
        az storage share close-handle --account-name MyAccount --name MyFileShare --close-all --recursive
        az storage share close-handle --account-name MyAccount --name MyFileShare --handle-id "*" --recursive
  - name: Close all file handles of a file directory recursively.
    text: |
        az storage share close-handle --account-name MyAccount --name MyFileShare --path 'dir1' --close-all --recursive
  - name: Close all file handles of a file.
    text: |
        az storage share close-handle --account-name MyAccount --name MyFileShare --path 'dir1/test.txt' --close-all
  - name: Close file handle with a specific handle-id of a file.
    text: |
        az storage share close-handle --account-name MyAccount --name MyFileShare --path 'dir1/test.txt' --handle-id "id"
"""
