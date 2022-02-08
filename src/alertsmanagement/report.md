# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az alertsmanagement|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az alertsmanagement` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az alertsmanagement alert|Alerts|[commands](#CommandsInAlerts)|
|az alertsmanagement alert-processing-rule|AlertProcessingRules|[commands](#CommandsInAlertProcessingRules)|
|az alertsmanagement smart-group|SmartGroups|[commands](#CommandsInSmartGroups)|

## COMMANDS
### <a name="CommandsInAlerts">Commands in `az alertsmanagement alert` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az alertsmanagement alert show](#AlertsGetById)|GetById|[Parameters](#ParametersAlertsGetById)|[Example](#ExamplesAlertsGetById)|
|[az alertsmanagement alert change-state](#AlertsChangeState)|ChangeState|[Parameters](#ParametersAlertsChangeState)|[Example](#ExamplesAlertsChangeState)|
|[az alertsmanagement alert meta-data](#AlertsMetaData)|MetaData|[Parameters](#ParametersAlertsMetaData)|[Example](#ExamplesAlertsMetaData)|
|[az alertsmanagement alert show-all](#AlertsGetAll)|GetAll|[Parameters](#ParametersAlertsGetAll)|[Example](#ExamplesAlertsGetAll)|
|[az alertsmanagement alert show-history](#AlertsGetHistory)|GetHistory|[Parameters](#ParametersAlertsGetHistory)|[Example](#ExamplesAlertsGetHistory)|
|[az alertsmanagement alert show-summary](#AlertsGetSummary)|GetSummary|[Parameters](#ParametersAlertsGetSummary)|[Example](#ExamplesAlertsGetSummary)|

### <a name="CommandsInAlertProcessingRules">Commands in `az alertsmanagement alert-processing-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az alertsmanagement alert-processing-rule list](#AlertProcessingRulesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersAlertProcessingRulesListByResourceGroup)|[Example](#ExamplesAlertProcessingRulesListByResourceGroup)|
|[az alertsmanagement alert-processing-rule list](#AlertProcessingRulesListBySubscription)|ListBySubscription|[Parameters](#ParametersAlertProcessingRulesListBySubscription)|[Example](#ExamplesAlertProcessingRulesListBySubscription)|
|[az alertsmanagement alert-processing-rule show](#AlertProcessingRulesGetByName)|GetByName|[Parameters](#ParametersAlertProcessingRulesGetByName)|[Example](#ExamplesAlertProcessingRulesGetByName)|
|[az alertsmanagement alert-processing-rule create](#AlertProcessingRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAlertProcessingRulesCreateOrUpdate#Create)|[Example](#ExamplesAlertProcessingRulesCreateOrUpdate#Create)|
|[az alertsmanagement alert-processing-rule update](#AlertProcessingRulesUpdate)|Update|[Parameters](#ParametersAlertProcessingRulesUpdate)|[Example](#ExamplesAlertProcessingRulesUpdate)|
|[az alertsmanagement alert-processing-rule delete](#AlertProcessingRulesDelete)|Delete|[Parameters](#ParametersAlertProcessingRulesDelete)|[Example](#ExamplesAlertProcessingRulesDelete)|

### <a name="CommandsInSmartGroups">Commands in `az alertsmanagement smart-group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az alertsmanagement smart-group show](#SmartGroupsGetById)|GetById|[Parameters](#ParametersSmartGroupsGetById)|[Example](#ExamplesSmartGroupsGetById)|
|[az alertsmanagement smart-group change-state](#SmartGroupsChangeState)|ChangeState|[Parameters](#ParametersSmartGroupsChangeState)|[Example](#ExamplesSmartGroupsChangeState)|
|[az alertsmanagement smart-group show-all](#SmartGroupsGetAll)|GetAll|[Parameters](#ParametersSmartGroupsGetAll)|[Example](#ExamplesSmartGroupsGetAll)|
|[az alertsmanagement smart-group show-history](#SmartGroupsGetHistory)|GetHistory|[Parameters](#ParametersSmartGroupsGetHistory)|[Example](#ExamplesSmartGroupsGetHistory)|


## COMMAND DETAILS
### group `az alertsmanagement alert`
#### <a name="AlertsGetById">Command `az alertsmanagement alert show`</a>

##### <a name="ExamplesAlertsGetById">Example</a>
```
az alertsmanagement alert show --alert-id "66114d64-d9d9-478b-95c9-b789d6502100"
```
##### <a name="ParametersAlertsGetById">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--alert-id**|string|Unique ID of an alert instance.|alert_id|alertId|

#### <a name="AlertsChangeState">Command `az alertsmanagement alert change-state`</a>

##### <a name="ExamplesAlertsChangeState">Example</a>
```
az alertsmanagement alert change-state --alert-id "66114d64-d9d9-478b-95c9-b789d6502100" --new-state "Acknowledged"
```
##### <a name="ParametersAlertsChangeState">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--alert-id**|string|Unique ID of an alert instance.|alert_id|alertId|
|**--new-state**|choice|New state of the alert.|new_state|newState|

#### <a name="AlertsMetaData">Command `az alertsmanagement alert meta-data`</a>

##### <a name="ExamplesAlertsMetaData">Example</a>
```
az alertsmanagement alert meta-data
```
##### <a name="ParametersAlertsMetaData">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="AlertsGetAll">Command `az alertsmanagement alert show-all`</a>

##### <a name="ExamplesAlertsGetAll">Example</a>
```
az alertsmanagement alert show-all
```
##### <a name="ParametersAlertsGetAll">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--target-resource**|string|Filter by target resource( which is full ARM ID) Default value is select all.|target_resource|targetResource|
|**--target-resource-type**|string|Filter by target resource type. Default value is select all.|target_resource_type|targetResourceType|
|**--target-resource-group**|string|Filter by target resource group name. Default value is select all.|target_resource_group|targetResourceGroup|
|**--monitor-service**|choice|Filter by monitor service which generates the alert instance. Default value is select all.|monitor_service|monitorService|
|**--monitor-condition**|choice|Filter by monitor condition which is either 'Fired' or 'Resolved'. Default value is to select all.|monitor_condition|monitorCondition|
|**--severity**|choice|Filter by severity.  Default value is select all.|severity|severity|
|**--alert-state**|choice|Filter by state of the alert instance. Default value is to select all.|alert_state|alertState|
|**--alert-rule**|string|Filter by specific alert rule.  Default value is to select all.|alert_rule|alertRule|
|**--smart-group-id**|string|Filter the alerts list by the Smart Group Id. Default value is none.|smart_group_id|smartGroupId|
|**--include-context**|boolean|Include context which has contextual data specific to the monitor service. Default value is false'|include_context|includeContext|
|**--include-egress-config**|boolean|Include egress config which would be used for displaying the content in portal.  Default value is 'false'.|include_egress_config|includeEgressConfig|
|**--page-count**|integer|Determines number of alerts returned per page in response. Permissible value is between 1 to 250. When the "includeContent"  filter is selected, maximum value allowed is 25. Default value is 25.|page_count|pageCount|
|**--sort-by**|choice|Sort the query results by input field,  Default value is 'lastModifiedDateTime'.|sort_by|sortBy|
|**--sort-order**|choice|Sort the query results order in either ascending or descending.  Default value is 'desc' for time fields and 'asc' for others.|sort_order|SortOrder|
|**--select**|string|This filter allows to selection of the fields(comma separated) which would  be part of the essential section. This would allow to project only the  required fields rather than getting entire content.  Default is to fetch all the fields in the essentials section.|select|select|
|**--time-range**|choice|Filter by time range by below listed values. Default value is 1 day.|time_range|timeRange|
|**--custom-time-range**|string|Filter by custom time range in the format <start-time>/<end-time>  where time is in (ISO-8601 format)'. Permissible values is within 30 days from  query time. Either timeRange or customTimeRange could be used but not both. Default is none.|custom_time_range|customTimeRange|

#### <a name="AlertsGetHistory">Command `az alertsmanagement alert show-history`</a>

##### <a name="ExamplesAlertsGetHistory">Example</a>
```
az alertsmanagement alert show-history --alert-id "66114d64-d9d9-478b-95c9-b789d6502100"
```
##### <a name="ParametersAlertsGetHistory">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--alert-id**|string|Unique ID of an alert instance.|alert_id|alertId|

#### <a name="AlertsGetSummary">Command `az alertsmanagement alert show-summary`</a>

##### <a name="ExamplesAlertsGetSummary">Example</a>
```
az alertsmanagement alert show-summary --groupby "severity,alertState"
```
##### <a name="ParametersAlertsGetSummary">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--groupby**|choice|This parameter allows the result set to be grouped by input fields (Maximum 2 comma separated fields supported). For example, groupby=severity or groupby=severity,alertstate.|groupby|groupby|
|**--include-smart-groups-count**|boolean|Include count of the SmartGroups as part of the summary. Default value is 'false'.|include_smart_groups_count|includeSmartGroupsCount|
|**--target-resource**|string|Filter by target resource( which is full ARM ID) Default value is select all.|target_resource|targetResource|
|**--target-resource-type**|string|Filter by target resource type. Default value is select all.|target_resource_type|targetResourceType|
|**--target-resource-group**|string|Filter by target resource group name. Default value is select all.|target_resource_group|targetResourceGroup|
|**--monitor-service**|choice|Filter by monitor service which generates the alert instance. Default value is select all.|monitor_service|monitorService|
|**--monitor-condition**|choice|Filter by monitor condition which is either 'Fired' or 'Resolved'. Default value is to select all.|monitor_condition|monitorCondition|
|**--severity**|choice|Filter by severity.  Default value is select all.|severity|severity|
|**--alert-state**|choice|Filter by state of the alert instance. Default value is to select all.|alert_state|alertState|
|**--alert-rule**|string|Filter by specific alert rule.  Default value is to select all.|alert_rule|alertRule|
|**--time-range**|choice|Filter by time range by below listed values. Default value is 1 day.|time_range|timeRange|
|**--custom-time-range**|string|Filter by custom time range in the format <start-time>/<end-time>  where time is in (ISO-8601 format)'. Permissible values is within 30 days from  query time. Either timeRange or customTimeRange could be used but not both. Default is none.|custom_time_range|customTimeRange|

### group `az alertsmanagement alert-processing-rule`
#### <a name="AlertProcessingRulesListByResourceGroup">Command `az alertsmanagement alert-processing-rule list`</a>

##### <a name="ExamplesAlertProcessingRulesListByResourceGroup">Example</a>
```
az alertsmanagement alert-processing-rule list --resource-group "alertscorrelationrg"
```
##### <a name="ParametersAlertProcessingRulesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name where the resource is created.|resource_group_name|resourceGroupName|

#### <a name="AlertProcessingRulesListBySubscription">Command `az alertsmanagement alert-processing-rule list`</a>

##### <a name="ExamplesAlertProcessingRulesListBySubscription">Example</a>
```
az alertsmanagement alert-processing-rule list
```
##### <a name="ParametersAlertProcessingRulesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="AlertProcessingRulesGetByName">Command `az alertsmanagement alert-processing-rule show`</a>

##### <a name="ExamplesAlertProcessingRulesGetByName">Example</a>
```
az alertsmanagement alert-processing-rule show --name "DailySuppression" --resource-group "alertscorrelationrg"
```
##### <a name="ParametersAlertProcessingRulesGetByName">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name where the resource is created.|resource_group_name|resourceGroupName|
|**--alert-processing-rule-name**|string|The name of the alert processing rule that needs to be fetched.|alert_processing_rule_name|alertProcessingRuleName|

#### <a name="AlertProcessingRulesCreateOrUpdate#Create">Command `az alertsmanagement alert-processing-rule create`</a>

##### <a name="ExamplesAlertProcessingRulesCreateOrUpdate#Create">Example</a>
```
az alertsmanagement alert-processing-rule create --location "Global" --description "Add ActionGroup1 to all alerts in \
the subscription" --actions actionGroupIds="/subscriptions/subId1/resourcegroups/RGId1/providers/microsoft.insights/act\
iongroups/ActionGroup1" action-type="AddActionGroups" --enabled true --scopes "/subscriptions/subId1" --name \
"AddActionGroupToSubscription" --resource-group "alertscorrelationrg"
az alertsmanagement alert-processing-rule create --location "Global" --description "Add AGId1 and AGId2 to all Sev0 \
and Sev1 alerts in these resourceGroups" --actions actionGroupIds="/subscriptions/subId1/resourcegroups/RGId1/providers\
/microsoft.insights/actiongroups/AGId1" actionGroupIds="/subscriptions/subId1/resourcegroups/RGId1/providers/microsoft.\
insights/actiongroups/AGId2" action-type="AddActionGroups" --conditions field="Severity" operator="Equals" \
values="sev0" values="sev1" --enabled true --scopes "/subscriptions/subId1/resourceGroups/RGId1" \
"/subscriptions/subId1/resourceGroups/RGId2" --name "AddActionGroupsBySeverity" --resource-group "alertscorrelationrg"
az alertsmanagement alert-processing-rule create --location "Global" --description "Removes all ActionGroups from all \
Alerts on VMName during the maintenance window" --actions action-type="RemoveAllActionGroups" --enabled true \
--effective-from "2021-04-15T18:00:00" --effective-until "2021-04-15T20:00:00" --time-zone "Pacific Standard Time" \
--scopes "/subscriptions/subId1/resourceGroups/RGId1/providers/Microsoft.Compute/virtualMachines/VMName" --name \
"RemoveActionGroupsMaintenanceWindow" --resource-group "alertscorrelationrg"
az alertsmanagement alert-processing-rule create --location "Global" --description "Removes all ActionGroups from all \
Alerts that fire on above AlertRule" --actions action-type="RemoveAllActionGroups" --conditions field="AlertRuleId" \
operator="Equals" values="/subscriptions/suubId1/resourceGroups/Rgid2/providers/microsoft.insights/activityLogAlerts/Ru\
leName" --enabled true --scopes "/subscriptions/subId1" --name "RemoveActionGroupsSpecificAlertRule" --resource-group \
"alertscorrelationrg"
az alertsmanagement alert-processing-rule create --location "Global" --description "Remove all ActionGroups from all \
Vitual machine Alerts during the recurring maintenance" --actions action-type="RemoveAllActionGroups" --conditions \
field="TargetResourceType" operator="Equals" values="microsoft.compute/virtualmachines" --enabled true --recurrences \
daysOfWeek="Saturday" daysOfWeek="Sunday" end-time="04:00:00" recurrence-type="Weekly" start-time="22:00:00" \
--time-zone "India Standard Time" --scopes "/subscriptions/subId1/resourceGroups/RGId1" "/subscriptions/subId1/resource\
Groups/RGId2" --name "RemoveActionGroupsRecurringMaintenance" --resource-group "alertscorrelationrg"
az alertsmanagement alert-processing-rule create --location "Global" --description "Remove all ActionGroups outside \
business hours" --actions action-type="RemoveAllActionGroups" --enabled true --recurrences end-time="09:00:00" \
recurrence-type="Daily" start-time="17:00:00" --recurrences daysOfWeek="Saturday" daysOfWeek="Sunday" \
recurrence-type="Weekly" --time-zone "Eastern Standard Time" --scopes "/subscriptions/subId1" --name \
"RemoveActionGroupsOutsideBusinessHours" --resource-group "alertscorrelationrg"
```
##### <a name="ParametersAlertProcessingRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name where the resource is created.|resource_group_name|resourceGroupName|
|**--alert-processing-rule-name**|string|The name of the alert processing rule that needs to be created/updated.|alert_processing_rule_name|alertProcessingRuleName|
|**--location**|string|Resource location|location|location|
|**--tags**|dictionary|Resource tags|tags|tags|
|**--scopes**|array|Scopes on which alert processing rule will apply.|scopes|scopes|
|**--conditions**|array|Conditions on which alerts will be filtered.|conditions|conditions|
|**--actions**|array|Actions to be applied.|actions|actions|
|**--description**|string|Description of alert processing rule.|description|description|
|**--enabled**|boolean|Indicates if the given alert processing rule is enabled or disabled.|enabled|enabled|
|**--effective-from**|string|Scheduling effective from time. Date-Time in ISO-8601 format without timezone suffix.|effective_from|effectiveFrom|
|**--effective-until**|string|Scheduling effective until time. Date-Time in ISO-8601 format without timezone suffix.|effective_until|effectiveUntil|
|**--time-zone**|string|Scheduling time zone.|time_zone|timeZone|
|**--recurrences**|array|List of recurrences.|recurrences|recurrences|

#### <a name="AlertProcessingRulesUpdate">Command `az alertsmanagement alert-processing-rule update`</a>

##### <a name="ExamplesAlertProcessingRulesUpdate">Example</a>
```
az alertsmanagement alert-processing-rule update --name "WeeklySuppression" --enabled false --tags key1="value1" \
key2="value2" --resource-group "alertscorrelationrg"
```
##### <a name="ParametersAlertProcessingRulesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name where the resource is created.|resource_group_name|resourceGroupName|
|**--alert-processing-rule-name**|string|The name that needs to be updated.|alert_processing_rule_name|alertProcessingRuleName|
|**--tags**|dictionary|Tags to be updated.|tags|tags|
|**--enabled**|boolean|Indicates if the given alert processing rule is enabled or disabled.|enabled|enabled|

#### <a name="AlertProcessingRulesDelete">Command `az alertsmanagement alert-processing-rule delete`</a>

##### <a name="ExamplesAlertProcessingRulesDelete">Example</a>
```
az alertsmanagement alert-processing-rule delete --name "DailySuppression" --resource-group "alertscorrelationrg"
```
##### <a name="ParametersAlertProcessingRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name where the resource is created.|resource_group_name|resourceGroupName|
|**--alert-processing-rule-name**|string|The name of the alert processing rule that needs to be deleted.|alert_processing_rule_name|alertProcessingRuleName|

### group `az alertsmanagement smart-group`
#### <a name="SmartGroupsGetById">Command `az alertsmanagement smart-group show`</a>

##### <a name="ExamplesSmartGroupsGetById">Example</a>
```
az alertsmanagement smart-group show --smart-group-id "603675da-9851-4b26-854a-49fc53d32715"
```
##### <a name="ParametersSmartGroupsGetById">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--smart-group-id**|string|Smart group unique id. |smart_group_id|smartGroupId|

#### <a name="SmartGroupsChangeState">Command `az alertsmanagement smart-group change-state`</a>

##### <a name="ExamplesSmartGroupsChangeState">Example</a>
```
az alertsmanagement smart-group change-state --new-state "Acknowledged" --smart-group-id \
"a808445e-bb38-4751-85c2-1b109ccc1059"
```
##### <a name="ParametersSmartGroupsChangeState">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--smart-group-id**|string|Smart group unique id. |smart_group_id|smartGroupId|
|**--new-state**|choice|New state of the alert.|new_state|newState|

#### <a name="SmartGroupsGetAll">Command `az alertsmanagement smart-group show-all`</a>

##### <a name="ExamplesSmartGroupsGetAll">Example</a>
```
az alertsmanagement smart-group show-all
```
##### <a name="ParametersSmartGroupsGetAll">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--target-resource**|string|Filter by target resource( which is full ARM ID) Default value is select all.|target_resource|targetResource|
|**--target-resource-group**|string|Filter by target resource group name. Default value is select all.|target_resource_group|targetResourceGroup|
|**--target-resource-type**|string|Filter by target resource type. Default value is select all.|target_resource_type|targetResourceType|
|**--monitor-service**|choice|Filter by monitor service which generates the alert instance. Default value is select all.|monitor_service|monitorService|
|**--monitor-condition**|choice|Filter by monitor condition which is either 'Fired' or 'Resolved'. Default value is to select all.|monitor_condition|monitorCondition|
|**--severity**|choice|Filter by severity.  Default value is select all.|severity|severity|
|**--smart-group-state**|choice|Filter by state of the smart group. Default value is to select all.|smart_group_state|smartGroupState|
|**--time-range**|choice|Filter by time range by below listed values. Default value is 1 day.|time_range|timeRange|
|**--page-count**|integer|Determines number of alerts returned per page in response. Permissible value is between 1 to 250. When the "includeContent"  filter is selected, maximum value allowed is 25. Default value is 25.|page_count|pageCount|
|**--sort-by**|choice|Sort the query results by input field. Default value is sort by 'lastModifiedDateTime'.|sort_by|sortBy|
|**--sort-order**|choice|Sort the query results order in either ascending or descending.  Default value is 'desc' for time fields and 'asc' for others.|sort_order|SortOrder|

#### <a name="SmartGroupsGetHistory">Command `az alertsmanagement smart-group show-history`</a>

##### <a name="ExamplesSmartGroupsGetHistory">Example</a>
```
az alertsmanagement smart-group show-history --smart-group-id "a808445e-bb38-4751-85c2-1b109ccc1059"
```
##### <a name="ParametersSmartGroupsGetHistory">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--smart-group-id**|string|Smart group unique id. |smart_group_id|smartGroupId|
