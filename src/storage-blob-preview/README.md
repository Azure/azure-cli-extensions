Microsoft Azure CLI 'storage-blob-preview' Extension
==========================================

This package is for the 'storage-blob-preview' extension.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storage-blob-preview
```

### Included Features
#### Management Policy:
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/azure/storage/common/storage-lifecycle-managment-concepts)\
```
Group
    az storage account management-policy : Manage storage account management policies.

Commands:
    create : Creates the data policy rules associated with the specified storage account.
    delete : Deletes the managementpolicy associated with the specified storage account.
    show   : Gets the managementpolicy associated with the specified storage account.
    update : Updates the data policy rules associated with the specified storage account.
```

*Examples:*
```
az storage account management-policy create \
    --account-name mystorageaccount \
    --resource-group groupName \
    --policy @{path}
```

```
az storage account management-policy show \
    --account-name mystorageaccount \
    --resource-group groupName
```

```
az storage account management-policy update \
    --account-name mystorageaccount \
    --resource-group groupName \
    --policy @{path}
```

```
az storage account management-policy delete \
    --account-name mystorageaccount \
    --resource-group groupName
```

#### Last Access Time Tracking

#### Container Soft Delete
