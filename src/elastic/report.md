# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az elastic|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az elastic` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az elastic monitor|Monitors|[commands](#CommandsInMonitors)|
|az elastic monitor tag-rule|TagRules|[commands](#CommandsInTagRules)|

## COMMANDS
### <a name="CommandsInMonitors">Commands in `az elastic monitor` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic monitor list](#MonitorsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMonitorsListByResourceGroup)|[Example](#ExamplesMonitorsListByResourceGroup)|
|[az elastic monitor list](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az elastic monitor show](#MonitorsGet)|Get|[Parameters](#ParametersMonitorsGet)|[Example](#ExamplesMonitorsGet)|
|[az elastic monitor create](#MonitorsCreate)|Create|[Parameters](#ParametersMonitorsCreate)|[Example](#ExamplesMonitorsCreate)|
|[az elastic monitor update](#MonitorsUpdate)|Update|[Parameters](#ParametersMonitorsUpdate)|[Example](#ExamplesMonitorsUpdate)|
|[az elastic monitor delete](#MonitorsDelete)|Delete|[Parameters](#ParametersMonitorsDelete)|[Example](#ExamplesMonitorsDelete)|
|[az elastic monitor list-deployment-info](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az elastic monitor list-resource](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az elastic monitor list-vm-host](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az elastic monitor list-vm-ingestion-detail](#MonitorsDetails)|Details|[Parameters](#ParametersMonitorsDetails)|[Example](#ExamplesMonitorsDetails)|
|[az elastic monitor update-vm-collection](#MonitorsUpdate)|Update|[Parameters](#ParametersMonitorsUpdate)|[Example](#ExamplesMonitorsUpdate)|

### <a name="CommandsInTagRules">Commands in `az elastic monitor tag-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic monitor tag-rule list](#TagRulesList)|List|[Parameters](#ParametersTagRulesList)|[Example](#ExamplesTagRulesList)|
|[az elastic monitor tag-rule show](#TagRulesGet)|Get|[Parameters](#ParametersTagRulesGet)|[Example](#ExamplesTagRulesGet)|
|[az elastic monitor tag-rule create](#TagRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTagRulesCreateOrUpdate#Create)|[Example](#ExamplesTagRulesCreateOrUpdate#Create)|
|[az elastic monitor tag-rule update](#TagRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersTagRulesCreateOrUpdate#Update)|Not Found|
|[az elastic monitor tag-rule delete](#TagRulesDelete)|Delete|[Parameters](#ParametersTagRulesDelete)|[Example](#ExamplesTagRulesDelete)|


## COMMAND DETAILS
### group `az elastic monitor`
#### <a name="MonitorsListByResourceGroup">Command `az elastic monitor list`</a>

##### <a name="ExamplesMonitorsListByResourceGroup">Example</a>
```
az elastic monitor list --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|

#### <a name="MonitorsList">Command `az elastic monitor list`</a>

##### <a name="ExamplesMonitorsList">Example</a>
```
az elastic monitor list
```
##### <a name="ParametersMonitorsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="MonitorsGet">Command `az elastic monitor show`</a>

##### <a name="ExamplesMonitorsGet">Example</a>
```
az elastic monitor show --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsCreate">Command `az elastic monitor create`</a>

##### <a name="ExamplesMonitorsCreate">Example</a>
```
az elastic monitor create --name "myMonitor" --location "West US 2" --user-info "{\\"companyInfo\\":{\\"business\\":\\"\
Technology\\",\\"country\\":\\"US\\",\\"domain\\":\\"microsoft.com\\",\\"employeeNumber\\":\\"10000\\",\\"state\\":\\"W\
A\\"},\\"companyName\\":\\"Microsoft\\",\\"emailAddress\\":\\"alice@microsoft.com\\",\\"firstName\\":\\"Alice\\",\\"las\
tName\\":\\"Bob\\"}" --sku "free_Monthly" --tags Environment="Dev" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--location**|string|The location of the monitor resource|location|location|
|**--tags**|dictionary|The tags of the monitor resource.|tags|tags|
|**--provisioning-state**|choice|Provisioning state of the monitor resource.|provisioning_state|provisioningState|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|
|**--elastic-properties**|object|Elastic cloud properties.|elastic_properties|elasticProperties|
|**--user-info**|object|User information.|user_info|userInfo|
|**--sku**|string|Name of the SKU.|sku|name|

#### <a name="MonitorsUpdate">Command `az elastic monitor update`</a>

##### <a name="ExamplesMonitorsUpdate">Example</a>
```
az elastic monitor update --name "myMonitor" --tags Environment="Dev" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|elastic monitor resource tags.|tags|tags|

#### <a name="MonitorsDelete">Command `az elastic monitor delete`</a>

##### <a name="ExamplesMonitorsDelete">Example</a>
```
az elastic monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsList">Command `az elastic monitor list-deployment-info`</a>

##### <a name="ExamplesMonitorsList">Example</a>
```
az elastic monitor list-deployment-info --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsList">Command `az elastic monitor list-resource`</a>

##### <a name="ExamplesMonitorsList">Example</a>
```
az elastic monitor list-resource --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsList">Command `az elastic monitor list-vm-host`</a>

##### <a name="ExamplesMonitorsList">Example</a>
```
az elastic monitor list-vm-host --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsDetails">Command `az elastic monitor list-vm-ingestion-detail`</a>

##### <a name="ExamplesMonitorsDetails">Example</a>
```
az elastic monitor list-vm-ingestion-detail --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsUpdate">Command `az elastic monitor update-vm-collection`</a>

##### <a name="ExamplesMonitorsUpdate">Example</a>
```
az elastic monitor update-vm-collection --name "myMonitor" --operation-name "Add" --vm-resource-id \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtual\
machines/myVM" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--vm-resource-id**|string|ARM id of the VM resource.|vm_resource_id|vmResourceId|
|**--operation-name**|choice|Operation to be performed for given VM.|operation_name|operationName|

### group `az elastic monitor tag-rule`
#### <a name="TagRulesList">Command `az elastic monitor tag-rule list`</a>

##### <a name="ExamplesTagRulesList">Example</a>
```
az elastic monitor tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersTagRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="TagRulesGet">Command `az elastic monitor tag-rule show`</a>

##### <a name="ExamplesTagRulesGet">Example</a>
```
az elastic monitor tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name \
"default"
```
##### <a name="ParametersTagRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Tag Rule Set resource name|rule_set_name|ruleSetName|

#### <a name="TagRulesCreateOrUpdate#Create">Command `az elastic monitor tag-rule create`</a>

##### <a name="ExamplesTagRulesCreateOrUpdate#Create">Example</a>
```
az elastic monitor tag-rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" \
value="Prod" --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false \
--send-activity-logs true --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Tag Rule Set resource name|rule_set_name|ruleSetName|
|**--provisioning-state**|choice|Provisioning state of the monitoring tag rules.|provisioning_state|provisioningState|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-activity-logs**|boolean|Flag specifying if activity logs from Azure resources should be sent for the Monitor resource.|send_activity_logs|sendActivityLogs|
|**--filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendActivityLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|

#### <a name="TagRulesCreateOrUpdate#Update">Command `az elastic monitor tag-rule update`</a>


##### <a name="ParametersTagRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Tag Rule Set resource name|rule_set_name|ruleSetName|
|**--provisioning-state**|choice|Provisioning state of the monitoring tag rules.|provisioning_state|provisioningState|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-activity-logs**|boolean|Flag specifying if activity logs from Azure resources should be sent for the Monitor resource.|send_activity_logs|sendActivityLogs|
|**--filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendActivityLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|

#### <a name="TagRulesDelete">Command `az elastic monitor tag-rule delete`</a>

##### <a name="ExamplesTagRulesDelete">Example</a>
```
az elastic monitor tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name \
"default"
```
##### <a name="ParametersTagRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Tag Rule Set resource name|rule_set_name|ruleSetName|
