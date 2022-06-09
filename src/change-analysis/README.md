# Azure CLI ChangeAnalysis Extension #
This is an extension to Azure CLI to manage ChangeAnalysis resources.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name change-analysis
```
### Included Features
#### List changes for resources:

##### List the changes of a subscription within the specific time range.

```
az change-analysis list --start-time '05/24/2022 8:43:36' --end-time '05/25/2022 9:46:36'
```

##### List the changes of a resource group within the specific time range

```
az change-analysis list -g [ResourceGroup] --start-time '05/24/2022 8:43:36' --end-time '05/25/2022 9:46:36'
```

##### List the changes of a resource within the specified time range

```
az change-analysis list-by-resource -r [ResourceId] --start-time '05/24/2022 8:43:36' --end-time '05/25/2022 9:46:36'
```