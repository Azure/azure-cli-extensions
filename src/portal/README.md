Microsoft Azure CLI 'portal' Extension
==========================================

This package is for the 'portal' extension. i.e. 'az portal'
More info on what is [Azure portal](https://docs.microsoft.com/en-us/azure/azure-portal/azure-portal-overview).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name portal
```

### Included Features ###
Manage Azure portal dashboards: [more info](https://docs.microsoft.com/en-us/azure/azure-portal/azure-portal-dashboards-create-programmatically#fetch-the-json-representation-of-the-dashboard)


#### Import a portal dashboard ####
You should have a dashboard json template ready before using this operation, the file can be downloaded from Azure portal website.
More info can be found [here](https://docs.microsoft.com/en-us/azure/azure-portal/azure-portal-dashboards-create-programmatically#fetch-the-json-representation-of-the-dashboard)
Example:
```
az portal dashboard import \
--name dashboardName \
--resource-group groupName \
--input-path "/path/to/dashboard/template/file/directory"
```
An example dashboard JSON template may look like:
[dashboard.json](https://github.com/Azure/azure-cli-extensions/blob/master/src/portal/azext_portal/tests/latest/dashboard.json)

#### Create a portal dashboard ####
Example:
```
az portal dashboard create \
--location "eastus" \ 
--name dashboardName \
--resource-group groupName \
--input-path "/path/to/properties/file/directory"
--tags aKey=aValue anotherKey=anotherValue
```
An example propeties JSON file may look like:
[properties.json](https://github.com/Azure/azure-cli-extensions/blob/master/src/portal/azext_portal/tests/latest/properties.json)

#### List all portal dashboards ####
Example:
List all dashboards in a resourceGroup
```
az portal dashboard list \
--resource-group groupName
```
List all dashboards in a subscription
```
az portal dashboard list
```

#### Show a portal dashboard details ####
Example:
```
az portal dashboard show \
--name dashboardName \
--resource-group groupName
```

#### Update an existing dashboard ####
Example:
```
az portal dashboard update \
--name dashboardName \
--resource-group groupName \
--input-path "/src/json/properties.json"
```

#### Delete a dashboard ####
Example:
```
az portal dashboard delete \
--name dashboardName \
--resource-group groupName \
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.