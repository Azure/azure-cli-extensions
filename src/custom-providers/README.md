# Azure CLI Custom Providers Extension
This is a extension for Custom Providers features.

### How to use
Install this extension using the below CLI command
```
az extension add --name custom-providers
```

### Included Features
#### Manage custom resource provider:


##### Create or update a custom resource provider

```
az custom-providers resource-provider create -n MyRP -g MyRG --action name=ping endpoint=https://test.azurewebsites.net/api routing_type=Proxy --resource-type name=users endpoint=https://test.azurewebsites.net/api routing_type="Proxy, Cache" --validation validation_type=swagger specification=https://raw.githubusercontent.com/test.json
```

##### Update the tags for a custom resource provider
```
az custom-providers resource-provider update -g MyRG -n MyRP --tags a=b
```

##### Get a custom resource provider
```
az custom-providers resource-provider show -g MyRG -n MyRP
```

##### Get all the custom resource providers within a resource group or in the current subscription
```
az custom-providers resource-provider list
```
```
az custom-providers resource-provider list -g MyRG
```

##### Delete a custom resource provider
```
az custom-providers resource-provider delete -g MyRG -n MyRP
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.