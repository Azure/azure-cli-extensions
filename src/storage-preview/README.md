# Azure CLI Storage Preview Extension #
This is a extension for storage preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storage-preview
```

### Included Features
**OAuth:**
Allow use of login credentials for authorization of storage operations: [more info](https://docs.microsoft.com/en-us/rest/api/storageservices/authenticate-with-azure-active-directory)
*Examples:*
```
az storage container list \
    --account-name wilxstoragev2 \
    --auth-mode login
```

**Immutable Storage-WORM(Write-Once-Read-Many):**
Manage immutability storage with Azure blobs: [more info](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-immutable-storage)
*Examples:*
```
az storage container immutability-policy create \
    --account-name accountName \
    --resource-group groupName \
    --container-name containerName \
    --period 2

az storage container immutability-policy lock \
    --account-name accountName \
    --resource-group groupName \
    --if-match "\"12345678abcdefg\""

az storage container legal-hold set \
    --account-name accountName \
    --resource-group groupName \
    --tags tag1 tag2
```

**Management Policy:**
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/en-us/azure/storage/common/storage-lifecycle-managment-concepts)
*Examples:*
```
az storage account management-policy create \
    --account-name accountName \
    --resource-group groupName \
    --policy @{path}
```

**Static Website:**
Manage static website configurations.
*Examples:*
```
az storage blob service-properties update \
    --account-name accountName \
    --static-website \
    --404-document error.html \
    --index-document index.html
```

**Hierarchical Namespace:**
Enable the blob service to exhibit filesystem semantics.
*Examples:*
```
az storage account create \
    --name accountName \
    --resource-group groupName \
    --hierarchical-namespace
```