# Azure CLI Storage Preview Extension #
This is a extension for storage preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storage-preview
```

### Included Features
#### Management Policy:
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/azure/storage/common/storage-lifecycle-managment-concepts)\
*Examples:*
```
az storage account management-policy create \
    --account-name accountName \
    --resource-group groupName \
    --policy @{path}
```

#### Static Website:
Manage static website configurations: [more info](https://docs.microsoft.com/azure/storage/blobs/storage-blob-static-website)\
*Examples:*
```
az storage blob service-properties update \
    --account-name accountName \
    --static-website \
    --404-document error.html \
    --index-document index.html
```

#### Hierarchical Namespace:
Enable the blob service to exhibit filesystem semantics: [more info](https://docs.microsoft.com/azure/storage/data-lake-storage/namespace)\
*Examples:*
```
az storage account create \
    --name accountName \
    --resource-group groupName \
    --kind StorageV2 \
    --hierarchical-namespace
```

#### File AAD Integration:
Enable AAD integration for Azure files, which will support SMB access: [more info](https://docs.microsoft.com/azure/storage/files/storage-files-active-directory-enable)\
*Examples:*
```
az storage account create \
    --name accountName \
    --resource-group groupName \
    --kind StorageV2

az storage account update \
    --name accountName \
    --resource-group groupName
```

#### Premium Blobs/Files:
Create premium blob/file storage accounts.\
More info:[premium blobs](https://azure.microsoft.com/blog/introducing-azure-premium-blob-storage-limited-public-preview/) [premium files](https://docs.microsoft.com/azure/storage/files/storage-files-introduction)\
*Examples:*
```
az storage account create \
    --name accountName \
    --resource-group groupName \
    --sku Premium_LRS \
    --kind BlockBlobStorage

az storage account create \
    --name accountName \
    --resource-group groupName \
    --sku Premium_LRS \
    --kind FileStorage
```

#### Customer-Controlled Failover:
Failover GRS/RA-GRS storage accounts from the primary cluster to the secondary cluster: [more info](https://docs.microsoft.com/azure/storage/common/storage-disaster-recovery-guidance)\
*Examples:*
```
az storage account show \
    --name accountName \
    --expand geoReplicationStats

az storage account failover \
    --name accountName
```

#### AzCopy Integration:
[EXPERIMENTAL] Azure CLI is releasing new versions of the blob upload/download/delete commands that rely on the AzCopy tool. Users should see higher performance metrics: [more info](https://github.com/Azure/azure-storage-azcopy)\
*Examples:*
###### Delete a single blob and a virtual directory:
```
az storage azcopy blob delete \
    -c containerName \
    --account-name accountName \
    -t targetBlob

az storage azcopy blob delete \
    -c containerName \
    --account-name accountName \
    -t virtual_directory/path \
    --recursive
```
###### Upload a single blob and a directory:
```
az storage azcopy blob upload \
    -c containerName \
    --account-name accountName \
    -s "file/path" \
    -d blobName

az storage azcopy blob upload \
    -c containerName \
    --account-name accountName \
    -s directory/path \
    -d upload/path
    --recursive
```
###### Download a single blob and a directory:
```
az storage azcopy blob download \
    -c containerName \
    --account-name accountName \
    -s blobName \
    -d file/path

az storage azcopy blob download \
    -c containerName \
    --account-name accountName \
    -s virtual_directory/path \
    -d download/path \
    --recursive
```
###### Sync a single blob and a directory:
```
az storage azcopy blob sync \
    -c containerName \
    --account-name accountName \
    -s "file/path" \
    -d blobName

az storage azcopy blob sync \
    -c containerName \
    --account-name accountName \
    -s directory/path \
    -d sync/path
```

#### ADLS Gen2 Support:
This storage-preview extension ***2.0.9*** is published with ADLS Gen2 filesystem operations support. It can help you create and manage directories, files, and permissions in storage accounts that have a hierarchical namespace. To utilize features in ADLS Gen2, you have to use a storage account with kind `StorageV2` and enable hierarchical namespace to set ACL permissions. 

With new command group `az storage blob directory`, azure cli can provide support in storage blob directory level. In addition,existing storage blob command group will be extended with new features and you can use existing storage blob commands to manage your ADLS Gen2 account.

Note: Please make sure storage-preview version >= 2.0.9 with azure cli >= 2.0.67. If not, please install upgrade azure-cli version and use `az extension update -n storage-preview` to upgrade storage-preview extension. 

##### Mapping from ADLS Gen1 to ADLS Gen2
You can find the command mapping from ADLS Gen1 to ADLS Gen2 as follows:

|                      ADLS Gen1                 |                         ADLS Gen2                    |
|:----------------------------------------------:|:----------------------------------------------------:|
| az dls fs                                      | az storage blob directory                            |
| az dls fs access                               | az storage blob directory access                     |
| az dls fs access remove-all                    | NO                                                   |
| az dls fs access remove-entry                  | NO                                                   |
| az dls fs access set                           | az storage blob directory access set                 |
| az dls fs access set-entry                     | NO                                                   |  
| az dls fs access set-owner                     | az storage blob directory access update              |  
| az dls fs access set-permission                | az storage blob directory access update              |
| az dls fs access show                          | az storage blob directory access show                |
| az dls fs append                               | NO                                                   | 
| az dls fs create                               | az storage blob directory create                     |
| az dls fs delete                               | az storage blob directory delete                     |
| az dls fs download                             | az storage blob directory download                   | 
| az dls fs join                                 | NO                                                   |  
| az dls fs list                                 | az storage blob directory list                       | 
| az dls fs move                                 | az storage blob directory move                       |  
| az dls fs preview                              | NO                                                   |  
| az dls fs set-expiry                           | NO                                                   |       
| az dls fs show                                 | az storage blob directory show                       | 
| az dls fs test                                 | az storage blob directory exists                     | 
| az dls fs upload                               | az storage blob directory upload                     |
| NO                                             | az storage blob directory metadata show              |
| NO                                             | az storage blob directory metadata update            |


##### New commands for existing blob command group
* az storage blob move
* az storage blob access
* az storage blob access set
* az storage blob access update
* az storage blob access show


*Examples:*
###### Create a storage account with kind StorageV2 and enable hierarchical namespace
```
az storage account create -n mystorageaccount -g myresourcegroup --kind StorageV2 --hierarchical-namespace true
```
###### Create a file system in storage account
```
az storage container create -n my-file-system --account-name mystorageaccount
```
###### Create a directory
```
az storage blob directory create -c my-file-system -d my-directory --account-name mystorageaccount
```
###### Show directory properties
```
az storage blob directory show -c my-file-system -d my-directory --account-name mystorageaccount
```
###### Rename or move a directory 
This operation's behavior is different depending on whether *Hierarchical
Namespace* is enabled; if yes, the move operation is atomic and no marker is returned; if not, the operation is
performed in batches and a continuation token could be returned.

```
az storage blob directory move -c my-file-system -d my-new-directory -s my-directory --account-name mystorageaccount
```
###### Delete a directory
This operation's behavior is different depending on whether Hierarchical Namespace
is enabled; if yes, then the delete operation can be atomic and instantaneous;
if not, the operation is performed in batches and a continuation token could be returned.
```
 az storage blob directory delete -c my-file-system -d my-directory --account-name mystorageaccount 
```
###### Check if a directory exists
Determine if a specific directory exists in the file system
```
az storage blob directory exists -c my-file-system -d my-directory --account-name mystorageaccount
```
###### Upload to a directory
Upload files to a directory by using the `az storage blob directory upload` command.

- Upload a file named `upload.txt` to a directory named `my-directory`.
```
az storage blob directory upload -c my-file-system --account-name mystorageaccount -s "C:\mylocaldirectory\upload.txt" -d my-directory
```
- Upload an entire directory.
```
az storage blob directory upload -c my-file-system --account-name mystorageaccount -s "C:\mylocaldirectory\" -d my-directory --recursive
```
###### Download from a directory
Download files from a directory by using the `az storage blob directory download` command.

- Download a file named `upload.txt` from a directory named `my-directory`.
```
az storage blob directory download -c my-file-system --account-name mystorageaccount -s "my-directory/upload.txt" -d "C:\mylocalfolder\download.txt"
```
- Download an entire subdirectory named `sub-dir` from a directory named `my-directory`.
```
az storage blob directory download -c MyContainer --account-name MyStorageAccount -s "my-directory/sub-dir" -d "C:\mylocalfolder\" --recursive
```
- Download an entire directory.
```
az storage blob directory download -c my-file-system --account-name mystorageaccount -s "my-directory" -d "C:\mylocalfolder" --recursive
```
###### List directory contents
```
az storage blob directory list -c my-file-system -d my-directory --account-name mystorageaccount
```
###### Rename or Move a file
```
az storage blob move -c my-file-system -d my-file-renamed.txt -s my-file.txt --account-name mystorageaccount
```
###### Delete a file
```
az storage blob delete -c my-file-system -b my-file.txt --account-name mystorageaccount 
```
###### Show all user-defined metadata for the specified blob directory.
```
az storage blob directory metadata show -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
```
###### Set user-defined metadata for the specified blob directory as one or more name-value pairs.
```
az storage blob directory metadata update --metadata tag1=value1 -c MyContainer -d MyDirectoryPath --account-name MyStorageAccount
```
###### Manage permissions
- Get ACLs of a directory or file 
```
az storage blob access show -d my-directory -c my-file-system --account-name mystorageaccount

az storage blob access show -b my-directory/upload.txt -c my-file-system --account-name mystorageaccount
```
- Set ACLs of a directory or file
```
az storage blob directory access set -a "user::rw-,group::rw-,other::-wx" -d my-directory -c my-file-system --account-name mystorageaccount

az storage blob access set -a "user::rw-,group::rw-,other::-wx" -b my-directory/upload.txt -c my-file-system --account-name mystorageaccount
```
- Update directory or file permissions
```
az storage blob directory access update --permissions "rwxrwxrwx" -d my-directory -c my-file-system --account-name mystorageaccount

az storage blob access update --permissions "rwxrwxrwx" -b my-directory/upload.txt -c my-file-system --account-name mystorageaccount
```
- Update owning user of a directory or file
```
az storage blob directory access update --owner [entityId/UPN] -d my-directory -c my-file-system --account-name mystorageaccount

az storage blob access update --owner [entityId/UPN] -b my-directory/upload.txt -c my-file-system --account-name mystorageaccount
```
- Update owning group  of a directory or file
```
az storage blob access update --group [entityId/UPN] -d my-directory -c my-file-system --account-name mystorageaccount

az storage blob access update --group [entityId/UPN] -b my-directory/upload.txt -c my-file-system --account-name mystorageaccount
```