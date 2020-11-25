# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az data-collection|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az data-collection` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az monitor data-collection rule association|DataCollectionRuleAssociations|[commands](#CommandsInDataCollectionRuleAssociations)|
|az monitor data-collection rule|DataCollectionRules|[commands](#CommandsInDataCollectionRules)|

## COMMANDS
### <a name="CommandsInDataCollectionRules">Commands in `az monitor data-collection rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az monitor data-collection rule list](#DataCollectionRulesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDataCollectionRulesListByResourceGroup)|[Example](#ExamplesDataCollectionRulesListByResourceGroup)|
|[az monitor data-collection rule list](#DataCollectionRulesListBySubscription)|ListBySubscription|[Parameters](#ParametersDataCollectionRulesListBySubscription)|[Example](#ExamplesDataCollectionRulesListBySubscription)|
|[az monitor data-collection rule show](#DataCollectionRulesGet)|Get|[Parameters](#ParametersDataCollectionRulesGet)|[Example](#ExamplesDataCollectionRulesGet)|
|[az monitor data-collection rule create](#DataCollectionRulesCreate)|Create|[Parameters](#ParametersDataCollectionRulesCreate)|[Example](#ExamplesDataCollectionRulesCreate)|
|[az monitor data-collection rule update](#DataCollectionRulesUpdate)|Update|[Parameters](#ParametersDataCollectionRulesUpdate)|[Example](#ExamplesDataCollectionRulesUpdate)|
|[az monitor data-collection rule delete](#DataCollectionRulesDelete)|Delete|[Parameters](#ParametersDataCollectionRulesDelete)|[Example](#ExamplesDataCollectionRulesDelete)|

### <a name="CommandsInDataCollectionRuleAssociations">Commands in `az monitor data-collection rule association` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az monitor data-collection rule association list](#DataCollectionRuleAssociationsListByRule)|ListByRule|[Parameters](#ParametersDataCollectionRuleAssociationsListByRule)|[Example](#ExamplesDataCollectionRuleAssociationsListByRule)|
|[az monitor data-collection rule association list](#DataCollectionRuleAssociationsListByResource)|ListByResource|[Parameters](#ParametersDataCollectionRuleAssociationsListByResource)|[Example](#ExamplesDataCollectionRuleAssociationsListByResource)|
|[az monitor data-collection rule association show](#DataCollectionRuleAssociationsGet)|Get|[Parameters](#ParametersDataCollectionRuleAssociationsGet)|[Example](#ExamplesDataCollectionRuleAssociationsGet)|
|[az monitor data-collection rule association create](#DataCollectionRuleAssociationsCreate)|Create|[Parameters](#ParametersDataCollectionRuleAssociationsCreate)|[Example](#ExamplesDataCollectionRuleAssociationsCreate)|
|[az monitor data-collection rule association delete](#DataCollectionRuleAssociationsDelete)|Delete|[Parameters](#ParametersDataCollectionRuleAssociationsDelete)|[Example](#ExamplesDataCollectionRuleAssociationsDelete)|


## COMMAND DETAILS

### group `az monitor data-collection rule`
#### <a name="DataCollectionRulesListByResourceGroup">Command `az monitor data-collection rule list`</a>

##### <a name="ExamplesDataCollectionRulesListByResourceGroup">Example</a>
```
az monitor data-collection rule list --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DataCollectionRulesListBySubscription">Command `az monitor data-collection rule list`</a>

##### <a name="ExamplesDataCollectionRulesListBySubscription">Example</a>
```
az monitor data-collection rule list
```
##### <a name="ParametersDataCollectionRulesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="DataCollectionRulesGet">Command `az monitor data-collection rule show`</a>

##### <a name="ExamplesDataCollectionRulesGet">Example</a>
```
az monitor data-collection rule show --name "myCollectionRule" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the data collection rule. The name is case insensitive.|name|dataCollectionRuleName|

#### <a name="DataCollectionRulesCreate">Command `az monitor data-collection rule create`</a>

##### <a name="ExamplesDataCollectionRulesCreate">Example</a>
```
az monitor data-collection rule create --location "eastus" --data-flows destinations="centralWorkspace" \
streams="Microsoft-Perf" streams="Microsoft-Syslog" streams="Microsoft-WindowsEvent" --data-sources-performance-counter\
s name="cloudTeamCoreCounters" counter-specifiers="\\\\Processor(_Total)\\\\% Processor Time" \
counter-specifiers="\\\\Memory\\\\Committed Bytes" counter-specifiers="\\\\LogicalDisk(_Total)\\\\Free Megabytes" \
counter-specifiers="\\\\PhysicalDisk(_Total)\\\\Avg. Disk Queue Length" sampling-frequency-in-seconds=15 \
scheduled-transfer-period="PT1M" streams="Microsoft-Perf" --data-sources-performance-counters \
name="appTeamExtraCounters" counter-specifiers="\\\\Process(_Total)\\\\Thread Count" sampling-frequency-in-seconds=30 \
scheduled-transfer-period="PT5M" streams="Microsoft-Perf" --data-sources-syslog name="cronSyslog" \
facility-names="cron" log-levels="Debug" log-levels="Critical" log-levels="Emergency" streams="Microsoft-Syslog" \
--data-sources-syslog name="syslogBase" facility-names="syslog" log-levels="Alert" log-levels="Critical" \
log-levels="Emergency" streams="Microsoft-Syslog" --data-sources-windows-event-logs name="cloudSecurityTeamEvents" \
scheduled-transfer-period="PT1M" streams="Microsoft-WindowsEvent" x-path-queries="Security!" \
--data-sources-windows-event-logs name="appTeam1AppEvents" scheduled-transfer-period="PT5M" \
streams="Microsoft-WindowsEvent" x-path-queries="System![System[(Level = 1 or Level = 2 or Level = 3)]]" \
x-path-queries="Application!*[System[(Level = 1 or Level = 2 or Level = 3)]]" --destinations-log-analytics \
name="centralWorkspace" workspace-resource-id="/subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myRes\
ourceGroup/providers/Microsoft.OperationalInsights/workspaces/centralTeamWorkspace" --name "myCollectionRule" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the data collection rule. The name is case insensitive.|name|dataCollectionRuleName|
|**--location**|string|The geo-location where the resource lives.|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of the data collection rule.|description|description|
|**--data-flows**|array|The specification of data flows.|data_flows|dataFlows|
|**--destinations-log-analytics**|array|List of Log Analytics destinations.|log_analytics|logAnalytics|
|**--destinations-azure-monitor-metrics**|object|Azure Monitor Metrics destination.|azure_monitor_metrics|azureMonitorMetrics|
|**--data-sources-performance-counters**|array|The list of performance counter data source configurations.|performance_counters|performanceCounters|
|**--data-sources-windows-event-logs**|array|The list of Windows Event Log data source configurations.|windows_event_logs|windowsEventLogs|
|**--data-sources-syslog**|array|The list of Syslog data source configurations.|syslog|syslog|
|**--data-sources-extensions**|array|The list of Azure VM extension data source configurations.|extensions|extensions|

#### <a name="DataCollectionRulesUpdate">Command `az monitor data-collection rule update`</a>

##### <a name="ExamplesDataCollectionRulesUpdate">Example</a>
```
az monitor data-collection rule update --tags tag1="A" tag2="B" tag3="C" --name "myCollectionRule" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the data collection rule. The name is case insensitive.|name|dataCollectionRuleName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="DataCollectionRulesDelete">Command `az monitor data-collection rule delete`</a>

##### <a name="ExamplesDataCollectionRulesDelete">Example</a>
```
az monitor data-collection rule delete --name "myCollectionRule" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--name**|string|The name of the data collection rule. The name is case insensitive.|name|dataCollectionRuleName|

### group `az monitor data-collection rule association`
#### <a name="DataCollectionRuleAssociationsListByRule">Command `az monitor data-collection rule association list`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsListByRule">Example</a>
```
az monitor data-collection rule association list --rule-name "myCollectionRule" --resource-group "myResourceGroup"
```
##### <a name="ParametersDataCollectionRuleAssociationsListByRule">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--rule-name**|string|The name of the data collection rule. The name is case insensitive.|rule_name|dataCollectionRuleName|

#### <a name="DataCollectionRuleAssociationsListByResource">Command `az monitor data-collection rule association list`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsListByResource">Example</a>
```
az monitor data-collection rule association list --resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourc\
eGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsListByResource">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource**|string|The identifier of the resource.|resource|resourceUri|

#### <a name="DataCollectionRuleAssociationsGet">Command `az monitor data-collection rule association show`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsGet">Example</a>
```
az monitor data-collection rule association show --name "myAssociation" --resource "subscriptions/703362b3-f278-4e4b-91\
79-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource**|string|The identifier of the resource.|resource|resourceUri|
|**--name**|string|The name of the association.|name|associationName|

#### <a name="DataCollectionRuleAssociationsCreate">Command `az monitor data-collection rule association create`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsCreate">Example</a>
```
az monitor data-collection rule association create --name "myAssociation" --rule-id "/subscriptions/703362b3-f278-4e4b-\
9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Insights/dataCollectionRules/myCollectionRule" \
--resource "subscriptions/703362b3-f278-4e4b-9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compu\
te/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource**|string|The identifier of the resource.|resource|resourceUri|
|**--name**|string|The name of the association.|name|associationName|
|**--description**|string|Description of the association.|description|description|
|**--rule-id**|string|The resource ID of the data collection rule that is to be associated.|rule_id|dataCollectionRuleId|

#### <a name="DataCollectionRuleAssociationsDelete">Command `az monitor data-collection rule association delete`</a>

##### <a name="ExamplesDataCollectionRuleAssociationsDelete">Example</a>
```
az monitor data-collection rule association delete --name "myAssociation" --resource "subscriptions/703362b3-f278-4e4b-\
9179-c76eaf41ffc2/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtualMachines/myVm"
```
##### <a name="ParametersDataCollectionRuleAssociationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource**|string|The identifier of the resource.|resource|resourceUri|
|**--name**|string|The name of the association.|name|associationName|
