# Azure CLI data-collection Extension #
This is the extension for data-collection

### How to use ###
Install this extension using the below CLI command
```
az extension add --name data-collection
```

### Included Features ###
#### data-collection data-collection-rule-association ####
##### Create #####
```
az data-collection data-collection-rule-association create --association-name "myAssociation" \
    --data-collection-rule-id "/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Insights/dataCollectionRules/myCollectionRule" \
    --resource-uri "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm" 
```
##### Show #####
```
az data-collection data-collection-rule-association show --association-name "myAssociation" \
    --resource-uri "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm" 
```
##### List #####
```
az data-collection data-collection-rule-association list --data-collection-rule-name "myCollectionRule" \
    --resource-group "myResourceGroup" 
```
##### Delete #####
```
az data-collection data-collection-rule-association delete --association-name "myAssociation" \
    --resource-uri "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm" 
```
#### data-collection data-collection-rule ####
##### Create #####
```
az data-collection data-collection-rule create --location "eastus" \
    --data-flows destinations="centralWorkspace" streams="Microsoft-Perf" streams="Microsoft-Syslog" streams="Microsoft-WindowsEvent" \
    --data-sources-performance-counters name="cloudTeamCoreCounters" counter-specifiers="\\\\Processor(_Total)\\\\% Processor Time" counter-specifiers="\\\\Memory\\\\Committed Bytes" counter-specifiers="\\\\LogicalDisk(_Total)\\\\Free Megabytes" counter-specifiers="\\\\PhysicalDisk(_Total)\\\\Avg. Disk Queue Length" sampling-frequency-in-seconds=15 scheduled-transfer-period="PT1M" streams="Microsoft-Perf" \
    --data-sources-performance-counters name="appTeamExtraCounters" counter-specifiers="\\\\Process(_Total)\\\\Thread Count" sampling-frequency-in-seconds=30 scheduled-transfer-period="PT5M" streams="Microsoft-Perf" \
    --data-sources-syslog name="cronSyslog" facility-names="cron" log-levels="Debug" log-levels="Critical" log-levels="Emergency" streams="Microsoft-Syslog" \
    --data-sources-syslog name="syslogBase" facility-names="syslog" log-levels="Alert" log-levels="Critical" log-levels="Emergency" streams="Microsoft-Syslog" \
    --data-sources-windows-event-logs name="cloudSecurityTeamEvents" scheduled-transfer-period="PT1M" streams="Microsoft-WindowsEvent" x-path-queries="Security!" \
    --data-sources-windows-event-logs name="appTeam1AppEvents" scheduled-transfer-period="PT5M" streams="Microsoft-WindowsEvent" x-path-queries="System![System[(Level = 1 or Level = 2 or Level = 3)]]" x-path-queries="Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]" \
    --destinations-log-analytics name="centralWorkspace" workspace-resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.OperationalInsights/workspaces/centralTeamWorkspace" \
    --name "myCollectionRule" --resource-group "myResourceGroup" 
```
##### Show #####
```
az data-collection data-collection-rule show --name "myCollectionRule" --resource-group "myResourceGroup"
```
##### List #####
```
az data-collection data-collection-rule list --resource-group "myResourceGroup"
```
##### Update #####
```
az data-collection data-collection-rule update --tags tag1="A" tag2="B" tag3="C" --name "myCollectionRule" \
    --resource-group "myResourceGroup" 
```
##### Delete #####
```
az data-collection data-collection-rule delete --name "myCollectionRule" --resource-group "myResourceGroup"
```