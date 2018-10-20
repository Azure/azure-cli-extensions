# Azure CLI Storage Preview Extension #
This is a extension for storage preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storage-preview
```

### Included Features
#### Management Policy:
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/en-us/azure/storage/common/storage-lifecycle-managment-concepts)\
*Examples:*
```
az storage account management-policy create \
    --account-name accountName \
    --resource-group groupName \
    --policy @{path}
```

#### Static Website:
Manage static website configurations: [more info](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website)\
*Examples:*
```
az storage blob service-properties update \
    --account-name accountName \
    --static-website \
    --404-document error.html \
    --index-document index.html
```

#### Hierarchical Namespace:
Enable the blob service to exhibit filesystem semantics: [more info](https://docs.microsoft.com/en-us/azure/storage/data-lake-storage/namespace)\
*Examples:*
```
az storage account create \
    --name accountName \
    --resource-group groupName \
    --kind StorageV2 \
    --hierarchical-namespace
```

#### File AAD Integration:
Enable AAD integration for Azure files, which will support SMB access: [more info](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-active-directory-enable)\
*Examples:*
```
az storage account create \
    --name accountName \
    --resource-group groupName \
    --kind StorageV2 \
    --file-aad

az storage account update \
    --name accountName \
    --resource-group groupName \
    --file-aad false
```

#### Premium Blobs/Files:
Create premium blob/file storage accounts. More info:[premium blobs](https://azure.microsoft.com/en-us/blog/introducing-azure-premium-blob-storage-limited-public-preview/) [premium files](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-introduction)\
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
