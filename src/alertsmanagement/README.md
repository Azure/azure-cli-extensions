# Azure CLI alertsmanagement Extension

This extension can manage alert related resources. Currently, it supports
action rule management.

### How to use
Install this extension using the below CLI command
```
az extension add --name alertsmanagement
```

### Action rule
Action rule documentation: https://docs.microsoft.com/en-us/azure/azure-monitor/platform/alerts-action-rules.

Create an action rule to suppress notifications for all Sev4 alerts on all VMs within the subscription every weekend.
```
az monitor action-rule create --resource-group rg --name rule --location Global --status Enabled --rule-type Suppression --severity Equals Sev4 --target-resource-type Equals Microsoft.Compute/VirtualMachines --suppression-recurrence-type Weekly --suppression-recurrence 0 6 --suppression-start-date 12/09/2018 --suppression-end-date 12/18/2018 --suppression-start-time 06:00:00 --suppression-end-time 14:00:00
```
Create an action rule to suppress notifications for all log alerts generated for Computer-01 in subscription indefinitely as it's going through maintenance.
```
az monitor action-rule create --resource-group rg --name rule --location Global --status Enabled --rule-type Suppression --suppression-recurrence-type Always --alert-context Contains Computer-01 --monitor-service Equals "Log Analytics"
```
Create an action rule to suppress notifications in a resource group
```
az monitor action-rule create --resource-group rg --name rule --location Global --status Enabled --rule-type Suppression --scope-type ResourceGroup --scope /subscriptions/0b1f6471-1bf0-4dda-aec3-cb9272f09590/resourceGroups/rg --suppression-recurrence-type Always --alert-context Contains Computer-01 --monitor-service Equals "Log Analytics"
```
Update an action rule
```
az monitor action-rule update --resource-group rg --name rule --status Disabled
```
Delete an action rule
```
az monitor action-rule delete --resource-group rg --name rule
```
Get an action rule
```
az monitor action-rule show --resource-group rg --name rule
```
List action rules of the subscription
```
az monitor action-rule list
```
List action rules of the resource group
```
az monitor action-rule list --resource-group rg
```