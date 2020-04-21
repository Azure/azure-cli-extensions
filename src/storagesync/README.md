==========================================
# Azure CLI Storage Sync Extension #
This is a extension for StorageSync features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storagesync
```

### Included Features
#### Manage storage sync service:

##### Create a new storage sync service.

```
az storagesync create \
    --resource-group rg \
    --name storage_sync_service_name \ 
    --location westus \
    --tags key1=value1
```

##### Delete a given storage sync service.
```
az storagesync delete \
    --resource-group rg \
    --name storage_sync_service_name
```

##### Show the properties for a given storage sync service.
```
az storagesync show \
    --resource-group rg \
    --name storage_sync_service_name
```

##### List all storage sync services in a resource group or a subscription.
```
az storagesync list
```
```
az storagesync list \
    --resource-group rg
```

#### Manage sync group:

##### Create a new sync group.
```
az storagesync sync-group create \
    --resource-group rg \
    --name sync_group_name \
    --storage-sync-service storage-sync-service-name
```

##### Delete a given sync group.
```
az storagesync sync-group delete \
    --resource-group rg \
    --name sync_group_name \
    --storage-sync-service storage-sync-service-name
```

##### Show the properties for a given sync group.
```
az storagesync sync-group show \
    --resource-group rg \
    --name sync_group_name \
    --storage-sync-service storage-sync-service-name
```

##### List all sync groups in a storage sync service.
```
az storagesync sync-group list \
    --resource-group rg \
    --storage-sync-service storage-sync-service-name
```

#### Manage cloud endpoint.

##### Create a new cloud endpoint.
```
az storagesync sync-group cloud-endpoint create \
    --resource-group rg \
    --name cloud-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name \
    --storage-account storageaccountnameorid \
    --azure-file-share-name file-share-name
```

##### Delete a given cloud endpoint.
```
az storagesync sync-group cloud-endpoint delete \
    --resource-group rg \
    --name cloud-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name 
```

##### Show the properties for a given cloud endpoint.
```
az storagesync sync-group cloud-endpoint show \
    --resource-group rg \
    --name cloud-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name 
```

##### List all cloud endpoints in a sync group.
```
az storagesync sync-group cloud-endpoint list \
    --resource-group rg \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name 
```

#### Manage cloud endpoint.

##### Create a new server endpoint.
```
az storagesync sync-group server-endpoint create \
    --resource-group rg \
    --name server-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name \
    --server-id server-id \
    --server-local-path "d:\\abc"
```

##### Update the properties for a given server endpoint.
```
az storagesync sync-group server-endpoint create \
    --resource-group rg \
    --name server-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name \
    --server-id server-id \
    --server-local-path "d:\\abc"
```

##### Delete a given server endpoint.
```
az storagesync sync-group server-endpoint delete \
    --resource-group rg \
    --name server-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name
```

##### Show the properties for a given server endpoint.
```
az storagesync sync-group server-endpoint show \
    --resource-group rg \
    --name server-endpoint-name \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name
```

##### List all server endpoints in a sync group.
```
az storagesync sync-group server-endpoint list \
    --resource-group rg \
    --storage-sync-service storage-sync-service-name \
    --sync-group-name sync-group-name
```

#### Manage registered server.

##### Register an on-premises server to a storage sync service.

*This command is not supported in CLI yet. You can use Azure PowerShell command [Register-AzStorageSyncServer](https://docs.microsoft.com/en-us/powershell/module/az.storagesync/register-azstoragesyncserver?view=azps-3.6.1) or [Azure File Sync Agent](https://docs.microsoft.com/en-us/azure/storage/files/storage-sync-files-deployment-guide?tabs=azure-portal#register-windows-server-with-storage-sync-service) instead.*

##### Unregister an on-premises server from it's storage sync service.
```
az storagesync registered-server delete \
    --resource-group rg \
    --storage-sync-service storage-sync-service-name \
    --server-id server-id 
```

##### Show the properties for a given registered server.
```
az storagesync registered-server show \
    --resource-group rg \
    --storage-sync-service storage-sync-service-name \
    --server-id server-id 
```

##### List all registered servers for a given storage sync service.
```
az storagesync registered-server list \
    --resource-group rg \
    --storage-sync-service storage-sync-service-name
```

##### Roll the storage sync server certificate used to describe the server identity to the storage sync service.

*This command is not supported in CLI yet. You can use Azure PowerShell command [Reset-AzStorageSyncServerCertificate](https://docs.microsoft.com/en-us/powershell/module/az.storagesync/reset-azstoragesyncservercertificate?view=azps-3.6.1) instead.*

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
