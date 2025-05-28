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

#### Create a workspace with double encryption
Double Encryption is only enabled on Premium Databricks workspace.
You need to register the feature first:  
```
az feature register --namespace Microsoft.Storage --name AllowRequireInfrastructureEncryption
```  
Then get the change propagated:  
```
az provider register -n Microsoft.Storage
```  
Now you can create a workspace with double encryption enabled:
```
az databricks workspace create \
    -resource-group my-rg \
    --name my-workspace \
    --location eastus2euap \
    --sku premium \
    --prepare-encryption \
    --require-infrastructure-encryption
```

##### Update workspace tags
```
az databricks update \
    --name my-workspace \
    --tags key=value
```

##### Assign identity for managed storage account to prepare for CMK encryption
```
az databricks update \
    --name my-workspace \
    --resource-group my-rg \
    --prepare-encryption
```

##### Configure CMK encryption
```
az databricks update \
    --name my-workspace \
    --resource-group my-rg \
    --key-source Microsoft.Keyvault \
    --key-name my-key \
    --key-version 00000000000000000000000000000000 \
    --key-vault https://myKeyVault.vault.azure.net/
```

##### Revert encryption to Microsoft Managed Keys
```
az databricks update \
    --name my-workspace \
    --resource-group my-rg \
    --key-source Default
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
