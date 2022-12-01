# Azure CLI alertsmanagement Extension

This extension can manage alert related resources. Currently, it supports
alert processing rule management.

### How to use
Install this extension using the below CLI command
```
az extension add --name alertsmanagement
```

### Alert Processing Rule
Alert processing rule documentation: https://docs.microsoft.com/en-us/azure/azure-monitor/platform/alerts-action-rules.

Create or update a rule that removes all action groups from alerts on a specific VM during a one-off maintenance window (1800-2000 at a specific date, Pacific Standard Time)
```
az monitor alert-processing-rule create --name 'RemoveActionGroupsMaintenanceWindow' --rule-type RemoveAllActionGroups --scopes "/subscriptions/MySubscriptionId1/resourceGroups/MyResourceGroup1/providers/Microsoft.Compute/virtualMachines/VMName" --resource-group alertscorrelationrg --schedule-start-datetime '2022-01-02 18:00:00' --schedule-end-datetime '2022-01-02 20:00:00' --schedule-time-zone 'Pacific Standard Time' --description "Removes all ActionGroups from all Alerts on VMName during the maintenance window"
```
Create or update a rule that removes all action groups from all alerts in a subscription coming from a specific alert rule
```
az monitor alert-processing-rule create --name 'RemoveActionGroupsSpecificAlertRule' --rule-type RemoveAllActionGroups --scopes "/subscriptions/MySubscriptionId1" --resource-group alertscorrelationrg --filter-alert-rule-id Equals "/subscriptions/MySubscriptionId1/resourceGroups/MyResourceGroup1/providers/microsoft.insights/activityLogAlerts/RuleName"  --description "Removes all ActionGroups from all Alerts that fire on above AlertRule"
```
Create or update a rule that adds two action groups to all Sev0 and Sev1 alerts in two resource groups
```
az monitor alert-processing-rule create --name 'AddActionGroupsBySeverity'--rule-type AddActionGroups --action-groups "/subscriptions/MySubscriptionId/resourcegroups/MyResourceGroup1/providers/microsoft.insights/actiongroups/MyActionGroupId1" "/subscriptions/MySubscriptionId/resourceGroups/MyResourceGroup2/providers/microsoft.insights/actionGroups/MyActionGroup2" --scopes "/subscriptions/MySubscriptionId" --resource-group alertscorrelationrg --filter-severity Equals Sev0 Sev1 --description "Add AGId1 and AGId2 to all Sev0 and Sev1 alerts in these resourceGroups"
```
Update an action rule
```
az monitor alert-processing-rule update --resource-group myResourceGroup --name myRuleName --enabled False
```
Delete an action rule
```
az monitor alert-processing-rule delete --resource-group myResourceGroup --name myRuleName
```
Get an action rule
```
az monitor alert-processing-rule show --name myRuleName --resource-group myRuleNameResourceGroup
```
List action rules of the subscription
```
az monitor alert-processing-rule list
```
List action rules of the resource group
```
az monitor alert-processing-rule show --resource-group myResourceGroup
```