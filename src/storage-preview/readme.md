# Azure CLI Storage Preview Extension #
This is a extension for storage preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storage-preview
```

### Included Features
**OAuth**
Allow use of login credentials for authorization of storage operations: [more info](https://docs.microsoft.com/en-us/rest/api/storageservices/authenticate-with-azure-active-directory)

**WORM(Write-Once-Read-Many)**
Manage immutability storage with Azure blobs: [more info](https://azure.microsoft.com/en-us/blog/azure-immutable-blob-storage-now-in-public-preview/)

**Management Policy**
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/en-us/azure/storage/common/storage-lifecycle-managment-concepts)