# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az elastic|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az elastic` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az elastic deployment-info|DeploymentInfo|[commands](#CommandsInDeploymentInfo)|
|az elastic monitor|Monitors|[commands](#CommandsInMonitors)|
|az elastic monitored-resource|MonitoredResources|[commands](#CommandsInMonitoredResources)|
|az elastic tag-rule|TagRules|[commands](#CommandsInTagRules)|
|az elastic vm-collection|VMCollection|[commands](#CommandsInVMCollection)|
|az elastic vm-host|VMHost|[commands](#CommandsInVMHost)|
|az elastic vm-ingestion|VMIngestion|[commands](#CommandsInVMIngestion)|

## COMMANDS
### <a name="CommandsInDeploymentInfo">Commands in `az elastic deployment-info` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic deployment-info list](#DeploymentInfoList)|List|[Parameters](#ParametersDeploymentInfoList)|[Example](#ExamplesDeploymentInfoList)|

### <a name="CommandsInMonitors">Commands in `az elastic monitor` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic monitor list](#MonitorsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMonitorsListByResourceGroup)|[Example](#ExamplesMonitorsListByResourceGroup)|
|[az elastic monitor list](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az elastic monitor show](#MonitorsGet)|Get|[Parameters](#ParametersMonitorsGet)|[Example](#ExamplesMonitorsGet)|
|[az elastic monitor create](#MonitorsCreate)|Create|[Parameters](#ParametersMonitorsCreate)|[Example](#ExamplesMonitorsCreate)|
|[az elastic monitor update](#MonitorsUpdate)|Update|[Parameters](#ParametersMonitorsUpdate)|[Example](#ExamplesMonitorsUpdate)|
|[az elastic monitor delete](#MonitorsDelete)|Delete|[Parameters](#ParametersMonitorsDelete)|[Example](#ExamplesMonitorsDelete)|

### <a name="CommandsInMonitoredResources">Commands in `az elastic monitored-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic monitored-resource list](#MonitoredResourcesList)|List|[Parameters](#ParametersMonitoredResourcesList)|[Example](#ExamplesMonitoredResourcesList)|

### <a name="CommandsInTagRules">Commands in `az elastic tag-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic tag-rule list](#TagRulesList)|List|[Parameters](#ParametersTagRulesList)|[Example](#ExamplesTagRulesList)|
|[az elastic tag-rule show](#TagRulesGet)|Get|[Parameters](#ParametersTagRulesGet)|[Example](#ExamplesTagRulesGet)|
|[az elastic tag-rule create](#TagRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTagRulesCreateOrUpdate#Create)|[Example](#ExamplesTagRulesCreateOrUpdate#Create)|
|[az elastic tag-rule update](#TagRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersTagRulesCreateOrUpdate#Update)|Not Found|
|[az elastic tag-rule delete](#TagRulesDelete)|Delete|[Parameters](#ParametersTagRulesDelete)|[Example](#ExamplesTagRulesDelete)|

### <a name="CommandsInVMCollection">Commands in `az elastic vm-collection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic vm-collection update](#VMCollectionUpdate)|Update|[Parameters](#ParametersVMCollectionUpdate)|[Example](#ExamplesVMCollectionUpdate)|

### <a name="CommandsInVMHost">Commands in `az elastic vm-host` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic vm-host list](#VMHostList)|List|[Parameters](#ParametersVMHostList)|[Example](#ExamplesVMHostList)|

### <a name="CommandsInVMIngestion">Commands in `az elastic vm-ingestion` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az elastic vm-ingestion detail](#VMIngestionDetails)|Details|[Parameters](#ParametersVMIngestionDetails)|[Example](#ExamplesVMIngestionDetails)|


## COMMAND DETAILS
### group `az elastic deployment-info`
#### <a name="DeploymentInfoList">Command `az elastic deployment-info list`</a>

##### <a name="ExamplesDeploymentInfoList">Example</a>
```
az elastic deployment-info list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersDeploymentInfoList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

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
az elastic monitor create --monitor-name "myMonitor" --location "West US 2" --user-info "{\\"companyInfo\\":{\\"busines\
s\\":\\"Technology\\",\\"country\\":\\"US\\",\\"domain\\":\\"microsoft.com\\",\\"employeeNumber\\":\\"10000\\",\\"state\
\\":\\"WA\\"},\\"companyName\\":\\"Microsoft\\",\\"emailAddress\\":\\"alice@microsoft.com\\",\\"firstName\\":\\"Alice\\\
",\\"lastName\\":\\"Bob\\"}" --name "free_Monthly" --tags Environment="Dev" --resource-group "myResourceGroup"
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
|**--name**|string|Name of the SKU.|name|name|

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

### group `az elastic monitored-resource`
#### <a name="MonitoredResourcesList">Command `az elastic monitored-resource list`</a>

##### <a name="ExamplesMonitoredResourcesList">Example</a>
```
az elastic monitored-resource list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitoredResourcesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az elastic tag-rule`
#### <a name="TagRulesList">Command `az elastic tag-rule list`</a>

##### <a name="ExamplesTagRulesList">Example</a>
```
az elastic tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersTagRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="TagRulesGet">Command `az elastic tag-rule show`</a>

##### <a name="ExamplesTagRulesGet">Example</a>
```
az elastic tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Tag Rule Set resource name|rule_set_name|ruleSetName|

#### <a name="TagRulesCreateOrUpdate#Create">Command `az elastic tag-rule create`</a>

##### <a name="ExamplesTagRulesCreateOrUpdate#Create">Example</a>
```
az elastic tag-rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" \
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

#### <a name="TagRulesCreateOrUpdate#Update">Command `az elastic tag-rule update`</a>


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

#### <a name="TagRulesDelete">Command `az elastic tag-rule delete`</a>

##### <a name="ExamplesTagRulesDelete">Example</a>
```
az elastic tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Tag Rule Set resource name|rule_set_name|ruleSetName|

### group `az elastic vm-collection`
#### <a name="VMCollectionUpdate">Command `az elastic vm-collection update`</a>

##### <a name="ExamplesVMCollectionUpdate">Example</a>
```
az elastic vm-collection update --monitor-name "myMonitor" --operation-name "Add" --vm-resource-id \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myResourceGroup/providers/Microsoft.Compute/virtual\
machines/myVM" --resource-group "myResourceGroup"
```
##### <a name="ParametersVMCollectionUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--vm-resource-id**|string|ARM id of the VM resource.|vm_resource_id|vmResourceId|
|**--operation-name**|choice|Operation to be performed for given VM.|operation_name|operationName|

### group `az elastic vm-host`
#### <a name="VMHostList">Command `az elastic vm-host list`</a>

##### <a name="ExamplesVMHostList">Example</a>
```
az elastic vm-host list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersVMHostList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az elastic vm-ingestion`
#### <a name="VMIngestionDetails">Command `az elastic vm-ingestion detail`</a>

##### <a name="ExamplesVMIngestionDetails">Example</a>
```
az elastic vm-ingestion detail --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersVMIngestionDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Elastic resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
