# Azure CLI databricks Extension #
This package is for the 'databricks' extension, i.e. 'az databricks'. More info on what is [Databricks](https://docs.microsoft.com/en-us/azure/azure-databricks/what-is-azure-databricks).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name databricks
```

### Included Features
#### Databricks Workspace Management:
*Examples:*

##### Create a workspace
```
az databricks create \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-workspace \
    --location westus \
    --sku premium
```

##### Update workspace tags
```
az databricks update \
    --name my-workspace \
    --tags key=value
```

##### Show workspace
```
az databricks show \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-workspace \
```
or
```
az databricks show \
    --ids "/subscriptions/subscription_id/resourceGroups/my-rg/providers/Microsoft.Databricks/workspaces/my-workspace" \
```

##### List workspace in resource group
```
az databricks list \
    --resource-group my-rg
```

##### Delete workspace
```
az databricks delete \
    --subscription subscription_id \
    --resource-group my-rg \
    --name my-workspace \
```
or
```
az databricks delete \
    --ids "/subscriptions/subscription_id/resourceGroups/my-rg/providers/Microsoft.Databricks/workspaces/my-workspace" \
    -y
```
