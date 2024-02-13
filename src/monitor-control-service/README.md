# Azure CLI monitor-control-service Extension
This is the extension for monitor-control-service

### How to use
Install this extension using the below CLI command
```
az extension add --name monitor-control-service
```

### Included Features
#### data-collection rule
##### Create
```
az monitor data-collection rule create --resource-group "myResourceGroup" --location "eastus" --name "myCollectionRule" --data-flows destinations="centralWorkspace" streams="Microsoft-Perf" streams="Microsoft-Syslog" streams="Microsoft-WindowsEvent" --log-analytics name="centralWorkspace" resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/centralTeamWorkspace" --performance-counters name="cloudTeamCoreCounters" counter-specifiers="\\Processor(_Total)\\% Processor Time" counter-specifiers="\\Memory\\Committed Bytes" counter-specifiers="\\LogicalDisk(_Total)\\Free Megabytes" counter-specifiers="\\PhysicalDisk(_Total)\\Avg. Disk Queue Length" sampling-frequency=15 transfer-period="PT1M" streams="Microsoft-Perf" --performance-counters name="appTeamExtraCounters" counter-specifiers="\\Process(_Total)\\Thread Count" sampling-frequency=30 transfer-period="PT5M" streams="Microsoft-Perf" --syslog name="cronSyslog" facility-names="cron" log-levels="Debug" log-levels="Critical" log-levels="Emergency" streams="Microsoft-Syslog" --syslog name="syslogBase" facility-names="syslog" log-levels="Alert" log-levels="Critical" log-levels="Emergency" streams="Microsoft-Syslog" --windows-event-logs name="cloudSecurityTeamEvents" transfer-period="PT1M" streams="Microsoft-WindowsEvent" x-path-queries="Security!" --windows-event-logs name="appTeam1AppEvents" transfer-period="PT5M" streams="Microsoft-WindowsEvent" x-path-queries="System![System[(Level = 1 or Level = 2 or Level = 3)]]" x-path-queries="Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]"
```
##### Show
```
az monitor data-collection rule show --name "myCollectionRule" --resource-group "myResourceGroup"
```
##### List
List data collection rules by resource group
```
az monitor data-collection rule list --resource-group "myResourceGroup"
```
List data collection rules by subscription
```
az monitor data-collection rule list
```
##### Update
```
az monitor data-collection rule update --resource-group "myResourceGroup" --name "myCollectionRule" --data-flows destinations="centralWorkspace" streams="Microsoft-Perf" streams="Microsoft-Syslog" streams="Microsoft-WindowsEvent" --log-analytics name="centralWorkspace" resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/centralTeamWorkspace" --performance-counters name="appTeamExtraCounters" counter-specifiers="\\Process(_Total)\\Thread Count" sampling-frequency=30 transfer-period="PT5M" streams="Microsoft-Perf" --syslog name="cronSyslog" facility-names="cron" log-levels="Debug" log-levels="Critical" log-levels="Emergency" streams="Microsoft-Syslog" --windows-event-logs name="cloudSecurityTeamEvents" transfer-period="PT1M" streams="Microsoft-WindowsEvent" x-path-queries="Security!"
```
##### Delete
```
az monitor data-collection rule delete --name "myCollectionRule" --resource-group "myResourceGroup"
```

#### data-collection rule data-flow
##### List
```
az monitor data-collection rule data-flow list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### Add
```
az monitor data-collection rule data-flow add --rule-name "myCollectionRule" --resource-group "myResourceGroup" --destinations XX3 XX4 --streams "Microsoft-Perf" "Microsoft-WindowsEvent"
```

#### data-collection rule log-analytics
##### List
```
az monitor data-collection rule log-analytics list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### Show
```
az monitor data-collection rule log-analytics show --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "centralWorkspace"
```
##### Add
```
az monitor data-collection rule log-analytics add --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "workspace2" --resource-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/workspace2"
```
##### Delete
```
az monitor data-collection rule log-analytics delete --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "workspace2"
```
##### Update
```
az monitor data-collection rule log-analytics update --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "workspace2" --resource-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/anotherWorkspace"
```

#### data-collection rule performance-counter
##### List
```
az monitor data-collection rule performance-counter list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### Show
```
az monitor data-collection rule performance-counter show --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "appTeamExtraCounters"
```
##### Add
```
az monitor data-collection rule performance-counter add --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "team2ExtraCounters" --streams "Microsoft-Perf" --counter-specifiers "\\Process(_Total)\\Thread Count" "\\LogicalDisk(_Total)\\Free Megabytes" --sampling-frequency 30 --transfer-period PT15M
```
##### Delete
```
az monitor data-collection rule performance-counter delete --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "team2ExtraCounters"
```
##### Update
```
az monitor data-collection rule performance-counter update --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "team2ExtraCounters" --transfer-period PT1M
```

#### data-collection rule windows-event-log
##### List
```
az monitor data-collection rule windows-event-log list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### Show
```
az monitor data-collection rule windows-event-log show --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "appTeam1AppEvents"
```
##### Add
```
az monitor data-collection rule windows-event-log add --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "appTeam1AppEvents" --transfer-period "PT1M" --streams "Microsoft-WindowsEvent" --x-path-queries "Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]" "System![System[(Level = 1 or Level = 2 or Level = 3)]]"
```
##### Delete
```
az monitor data-collection rule windows-event-log delete --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "appTeam1AppEvents"
```
##### Update
```
az monitor data-collection rule windows-event-log update --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "appTeam1AppEvents" --x-path-queries "Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]"
```

#### data-collection rule syslog
##### List
```
az monitor data-collection rule syslog list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### Show
```
az monitor data-collection rule syslog show --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "syslogBase"
```
##### Add
```
az monitor data-collection rule syslog add --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "syslogBase" --facility-names "syslog" --log-levels "Alert" "Critical" --streams "Microsoft-Syslog"
```
##### Delete
```
az monitor data-collection rule syslog delete --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "syslogBase"
```
##### Update
```
az monitor data-collection rule syslog update --rule-name "myCollectionRule" --resource-group "myResourceGroup" --name "syslogBase" --facility-names "syslog" --log-levels "Emergency" "Critical"
```

#### data-collection rule association
##### Create
```
az monitor data-collection rule association create --name "myAssociation" --rule-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Insights/dataCollectionRules/myCollectionRule" --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### Show
```
az monitor data-collection rule association show --name "myAssociation" --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### Update
```
az monitor data-collection rule association update --name "myAssociation" --rule-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Insights/dataCollectionRules/myCollectionRule" --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### List
List associations for specified data collection rule
```
az monitor data-collection rule association list --rule-name "myCollectionRule" --resource-group "myResourceGroup" 
```
List associations for specified resource
```
az monitor data-collection rule association list --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### Delete
```
az monitor data-collection rule association delete --name "myAssociation" --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```

#### data-collection endpoint
##### Create
```
az monitor data-collection endpoint create --name "myEndpoint" -g "myResourceGroup" -l "eastus2euap" --public-network-access "enabled"
```
##### Show
```
az monitor data-collection endpoint show --name "myEndpoint" -g "myResourceGroup"
```
##### Update
```
az monitor data-collection endpoint update --name "myEndpoint" -g "myResourceGroup" --kind windows 
```
##### List
List endpoints for specified resource group
```
az monitor data-collection endpoint list -g "myResourceGroup"
```
List endpoints for subscription
```
az monitor data-collection endpoint list 
```
##### Delete
```
az monitor data-collection endpoint delete --name "myEndpoint" -g "myResourceGroup"
```
