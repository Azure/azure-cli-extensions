# Azure CLI ManagedCleanRoom Extension #
This is an extension to Azure CLI to manage Microsoft.CleanRoom resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name managedcleanroom
```

### Included Features
#### CleanRoom Management:
Manage CleanRoom: [more info](https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-clean-rooms)\
*Examples:*

##### Create a Consortium

```
az managedcleanroom consortium create \
    --resource-group groupName \
    --consortium-name consortiumName \
    --location westus
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.