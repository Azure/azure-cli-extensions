Microsoft Azure CLI 'scheduled-query' Extension
==========================================

This package is for the 'scheduled-query' extension.
i.e. 'az scheduled-query'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name scheduled-query
```

### Sample Commands ###
Create a scheduled query for a vm
```
az monitor scheduled-query create -g {rg} -n {name1} --scopes {vm_id} --condition "count \'union Event, Syslog | where TimeGenerated > ago(1h)\' > 360" --description "Test rule" --target-resource-type Microsoft.Compute/virtualMachines
```
Update the scheduled query for a vm
```
az monitor scheduled-query update -g {rg} -n {name1} --condition "count \'union Event, Syslog | where TimeGenerated > ago(1h)\' > 360" --description "Test rule"
```
Show the detail of a scheduled query
```
az monitor scheduled-query show -g {rg} -n {name1}
```
List all scheduled queries in a resource group
```
az monitor scheduled-query list -g {rg}
```
Delete the scheduled query
```
az monitor scheduled-query delete -g {rg} -n {name1}
```