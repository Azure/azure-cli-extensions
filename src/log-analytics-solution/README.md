# Azure CLI log-analytics-solution Extension #
This package is for the 'log-analytics-solution' extension, i.e. 'az monitor log-analytics solution'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name log-analytics-solution
```

### Included Features
#### Log Analytics Solution Management:
Manage Log Analytics Solution: [more info](https://docs.microsoft.com/en-us/azure/azure-monitor/insights/solutions) \
*Examples:*

##### Create a log-analytics solution for the plan product of OMSGallery/Containers
```
az monitor log-analytics solution create \
    --resource-group MyResourceGroup \
    --solution-type Containers \
    --workspace "/subscriptions/{SubID}/resourceGroups/{ResourceGroup}/providers/ \
    Microsoft.OperationalInsights/workspaces/{WorkspaceName}" \
    --tags key=value
```

##### Update a log-analytics solution
```
 az monitor log-analytics solution update \
    --resource-group MyResourceGroup \
    --name SolutionName \
    --tags key=value
```

##### Delete a log-analytics solution
```
az monitor log-analytics solution delete --resource-group MyResourceGroup --name SolutionName
```

##### Get details about the specified log-analytics solution
```
az monitor log-analytics solution show --resource-group MyResourceGroup --name SolutionName
```

##### List all of the log-analytics solutions in the specified subscription or resource group
```
az monitor log-analytics solution list
```
```
az monitor log-analytics solution list --subscription MySubscription
```
```
az monitor log-analytics solution list --resource-group MyResourceGroup
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
