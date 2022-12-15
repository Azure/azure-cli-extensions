# Azure CLI Adp Extension #
This is an extension to Azure CLI to manage Adp resources.

## How to use ##

## manage workspaces ## 
Create a workspace with 3 storage accounts with LRS sku.
```
az adp workspace create \
    --name sample-ws
    --location westus3 \
    --storage-account-count 3 \
    --storage-sku name=Standard_LRS \
    --resource-group sample-rg
```

delete a workspace.
```
az adp workspace delete \
    --location westus3 \
    --subscription sample-subscription \
    --resource-group sample-rg \
    --name sample-ws 
```

list workspaces.
```
az adp workspace list \
    --subscription sample-subscription \
    --resource-group sample-rg \
```


update workspace to have 3 storage account
```
az adp workspace update \
    --location westus3 \
    --subscription sample-subscription \
    --resource-group sample-rg \
    --name sample-ws \
    --set properties.StorageAccountCount=3
```