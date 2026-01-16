# Azure CLI StorageDiscovery Extension #
This is an extension to Azure CLI to manage StorageDiscovery resources.

## How to use ##
### az storage-discovery workspace create ###
```commandline
az storage-discovery workspace create \
  --resource-group myRG \
  --name myWorkspace \
  --location francecentral \
  --workspace-roots "/subscriptions/mySubId/resourceGroups/myRG" \
  --scopes '[{"displayName":"basic","resourceTypes":["Microsoft.Storage/storageAccounts"]}]'
```

### az storage-discovery workspace create (with full configuration) ###
```commandline
az storage-discovery workspace create \
  --resource-group myRG \
  --name myWorkspace \
  --location francecentral \
  --description "My workspace for storage discovery" \
  --sku Standard \
  --workspace-roots "/subscriptions/mySubId/resourceGroups/myRG" \
  --scopes '[{"displayName":"production","resourceTypes":["Microsoft.Storage/storageAccounts"],"tagKeysOnly":["environment"],"tags":{"project":"demo","tier":"prod"}}]'
```

### az storage-discovery workspace show ###
```commandline
az storage-discovery workspace show --resource-group myRG --name myWorkspace
```

### az storage-discovery workspace update ###
```commandline
az storage-discovery workspace update \
  --resource-group myRG \
  --name myWorkspace \
  --description "Updated description" \
  --sku Free \
  --scopes '[{"displayName":"updated","resourceTypes":["Microsoft.Storage/storageAccounts"],"tags":{"environment":"test"}}]' \
  --tags environment=production team=storage
```

### az storage-discovery workspace list ###
```commandline
az storage-discovery workspace list --resource-group myRG
```

### az storage-discovery workspace list (subscription level) ###
```commandline
az storage-discovery workspace list
```

### az storage-discovery workspace delete ###
```commandline
az storage-discovery workspace delete --resource-group myRG --name myWorkspace
```