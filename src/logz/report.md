# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az logz|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az logz` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az logz monitor|Monitors|[commands](#CommandsInMonitors)|
|az logz tag-rule|TagRules|[commands](#CommandsInTagRules)|
|az logz single-sign-on|SingleSignOn|[commands](#CommandsInSingleSignOn)|
|az logz sub-account|SubAccount|[commands](#CommandsInSubAccount)|
|az logz sub-account-tag-rule|SubAccountTagRules|[commands](#CommandsInSubAccountTagRules)|

## COMMANDS
### <a name="CommandsInMonitors">Commands in `az logz monitor` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logz monitor list](#MonitorsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMonitorsListByResourceGroup)|[Example](#ExamplesMonitorsListByResourceGroup)|
|[az logz monitor list](#MonitorsListBySubscription)|ListBySubscription|[Parameters](#ParametersMonitorsListBySubscription)|[Example](#ExamplesMonitorsListBySubscription)|
|[az logz monitor show](#MonitorsGet)|Get|[Parameters](#ParametersMonitorsGet)|[Example](#ExamplesMonitorsGet)|
|[az logz monitor create](#MonitorsCreate)|Create|[Parameters](#ParametersMonitorsCreate)|[Example](#ExamplesMonitorsCreate)|
|[az logz monitor update](#MonitorsUpdate)|Update|[Parameters](#ParametersMonitorsUpdate)|[Example](#ExamplesMonitorsUpdate)|
|[az logz monitor delete](#MonitorsDelete)|Delete|[Parameters](#ParametersMonitorsDelete)|[Example](#ExamplesMonitorsDelete)|
|[az logz monitor list-monitored-resource](#MonitorsListMonitoredResources)|ListMonitoredResources|[Parameters](#ParametersMonitorsListMonitoredResources)|[Example](#ExamplesMonitorsListMonitoredResources)|

### <a name="CommandsInSingleSignOn">Commands in `az logz single-sign-on` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logz single-sign-on list](#SingleSignOnList)|List|[Parameters](#ParametersSingleSignOnList)|[Example](#ExamplesSingleSignOnList)|
|[az logz single-sign-on show](#SingleSignOnGet)|Get|[Parameters](#ParametersSingleSignOnGet)|[Example](#ExamplesSingleSignOnGet)|
|[az logz single-sign-on create](#SingleSignOnCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSingleSignOnCreateOrUpdate#Create)|[Example](#ExamplesSingleSignOnCreateOrUpdate#Create)|
|[az logz single-sign-on update](#SingleSignOnCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersSingleSignOnCreateOrUpdate#Update)|Not Found|

### <a name="CommandsInSubAccount">Commands in `az logz sub-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logz sub-account list](#SubAccountList)|List|[Parameters](#ParametersSubAccountList)|[Example](#ExamplesSubAccountList)|
|[az logz sub-account show](#SubAccountGet)|Get|[Parameters](#ParametersSubAccountGet)|[Example](#ExamplesSubAccountGet)|
|[az logz sub-account create](#SubAccountCreate)|Create|[Parameters](#ParametersSubAccountCreate)|[Example](#ExamplesSubAccountCreate)|
|[az logz sub-account update](#SubAccountUpdate)|Update|[Parameters](#ParametersSubAccountUpdate)|[Example](#ExamplesSubAccountUpdate)|
|[az logz sub-account delete](#SubAccountDelete)|Delete|[Parameters](#ParametersSubAccountDelete)|[Example](#ExamplesSubAccountDelete)|
|[az logz sub-account list-monitored-resource](#SubAccountListMonitoredResources)|ListMonitoredResources|[Parameters](#ParametersSubAccountListMonitoredResources)|[Example](#ExamplesSubAccountListMonitoredResources)|

### <a name="CommandsInSubAccountTagRules">Commands in `az logz sub-account-tag-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logz sub-account-tag-rule list](#SubAccountTagRulesList)|List|[Parameters](#ParametersSubAccountTagRulesList)|[Example](#ExamplesSubAccountTagRulesList)|
|[az logz sub-account-tag-rule show](#SubAccountTagRulesGet)|Get|[Parameters](#ParametersSubAccountTagRulesGet)|[Example](#ExamplesSubAccountTagRulesGet)|
|[az logz sub-account-tag-rule create](#SubAccountTagRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSubAccountTagRulesCreateOrUpdate#Create)|[Example](#ExamplesSubAccountTagRulesCreateOrUpdate#Create)|
|[az logz sub-account-tag-rule update](#SubAccountTagRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersSubAccountTagRulesCreateOrUpdate#Update)|Not Found|
|[az logz sub-account-tag-rule delete](#SubAccountTagRulesDelete)|Delete|[Parameters](#ParametersSubAccountTagRulesDelete)|[Example](#ExamplesSubAccountTagRulesDelete)|

### <a name="CommandsInTagRules">Commands in `az logz tag-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az logz tag-rule list](#TagRulesList)|List|[Parameters](#ParametersTagRulesList)|[Example](#ExamplesTagRulesList)|
|[az logz tag-rule show](#TagRulesGet)|Get|[Parameters](#ParametersTagRulesGet)|[Example](#ExamplesTagRulesGet)|
|[az logz tag-rule create](#TagRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTagRulesCreateOrUpdate#Create)|[Example](#ExamplesTagRulesCreateOrUpdate#Create)|
|[az logz tag-rule update](#TagRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersTagRulesCreateOrUpdate#Update)|Not Found|
|[az logz tag-rule delete](#TagRulesDelete)|Delete|[Parameters](#ParametersTagRulesDelete)|[Example](#ExamplesTagRulesDelete)|


## COMMAND DETAILS

### group `az logz monitor`
#### <a name="MonitorsListByResourceGroup">Command `az logz monitor list`</a>

##### <a name="ExamplesMonitorsListByResourceGroup">Example</a>
```
az logz monitor list --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="MonitorsListBySubscription">Command `az logz monitor list`</a>

##### <a name="ExamplesMonitorsListBySubscription">Example</a>
```
az logz monitor list
```
##### <a name="ParametersMonitorsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="MonitorsGet">Command `az logz monitor show`</a>

##### <a name="ExamplesMonitorsGet">Example</a>
```
az logz monitor show --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsCreate">Command `az logz monitor create`</a>

##### <a name="ExamplesMonitorsCreate">Example</a>
```
az logz monitor create --name "myMonitor" --location "West US" --plan-data billing-cycle="Monthly" \
effective-date="2019-08-30T15:14:33+02:00" plan-details="logzapitestplan" usage-type="Committed" --user-info \
email-address="alice@microsoft.com" first-name="Alice" last-name="Bob" phone-number="123456" --tags Environment="Dev" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|
|**--location**|string||location|location|
|**--type**|choice||type|type|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|
|**--marketplace-subscription-status**|choice|Flag specifying the Marketplace Subscription Status of the resource. If payment is not made in time, the resource will go in Suspended state.|marketplace_subscription_status|marketplaceSubscriptionStatus|
|**--logz-organization-properties**|object||logz_organization_properties|logzOrganizationProperties|
|**--user-info**|object||user_info|userInfo|
|**--plan-data**|object||plan_data|planData|

#### <a name="MonitorsUpdate">Command `az logz monitor update`</a>

##### <a name="ExamplesMonitorsUpdate">Example</a>
```
az logz monitor update --name "myMonitor" --monitoring-status "Enabled" --tags Environment="Dev" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersMonitorsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|The new tags of the monitor resource.|tags|tags|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|

#### <a name="MonitorsDelete">Command `az logz monitor delete`</a>

##### <a name="ExamplesMonitorsDelete">Example</a>
```
az logz monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsListMonitoredResources">Command `az logz monitor list-monitored-resource`</a>

##### <a name="ExamplesMonitorsListMonitoredResources">Example</a>
```
az logz monitor list-monitored-resource --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListMonitoredResources">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az logz single-sign-on`
#### <a name="SingleSignOnList">Command `az logz single-sign-on list`</a>

##### <a name="ExamplesSingleSignOnList">Example</a>
```
az logz single-sign-on list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersSingleSignOnList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="SingleSignOnGet">Command `az logz single-sign-on show`</a>

##### <a name="ExamplesSingleSignOnGet">Example</a>
```
az logz single-sign-on show --configuration-name "default" --monitor-name "myMonitor" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersSingleSignOnGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string||configuration_name|configurationName|

#### <a name="SingleSignOnCreateOrUpdate#Create">Command `az logz single-sign-on create`</a>

##### <a name="ExamplesSingleSignOnCreateOrUpdate#Create">Example</a>
```
az logz single-sign-on create --configuration-name "default" --monitor-name "myMonitor" --properties \
enterprise-app-id="00000000-0000-0000-0000-000000000000" single-sign-on-state="Enable" single-sign-on-url=null \
--resource-group "myResourceGroup"
```
##### <a name="ParametersSingleSignOnCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string||configuration_name|configurationName|
|**--properties**|object||properties|properties|

#### <a name="SingleSignOnCreateOrUpdate#Update">Command `az logz single-sign-on update`</a>

##### <a name="ParametersSingleSignOnCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string||configuration_name|configurationName|
|**--properties**|object||properties|properties|

### group `az logz sub-account`
#### <a name="SubAccountList">Command `az logz sub-account list`</a>

##### <a name="ExamplesSubAccountList">Example</a>
```
az logz sub-account list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersSubAccountList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="SubAccountGet">Command `az logz sub-account show`</a>

##### <a name="ExamplesSubAccountGet">Example</a>
```
az logz sub-account show --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "SubAccount1"
```
##### <a name="ParametersSubAccountGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|

#### <a name="SubAccountCreate">Command `az logz sub-account create`</a>

##### <a name="ExamplesSubAccountCreate">Example</a>
```
az logz sub-account create --monitor-name "myMonitor" --type "Microsoft.Logz/monitors" --location "West US" \
--monitoring-status "Enabled" --tags Environment="Dev" --resource-group "myResourceGroup" --name "SubAccount1"
```
##### <a name="ParametersSubAccountCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|
|**--location**|string||location|location|
|**--type**|choice||type|type|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|
|**--marketplace-subscription-status**|choice|Flag specifying the Marketplace Subscription Status of the resource. If payment is not made in time, the resource will go in Suspended state.|marketplace_subscription_status|marketplaceSubscriptionStatus|
|**--logz-organization-properties**|object||logz_organization_properties|logzOrganizationProperties|
|**--user-info**|object||user_info|userInfo|
|**--plan-data**|object||plan_data|planData|

#### <a name="SubAccountUpdate">Command `az logz sub-account update`</a>

##### <a name="ExamplesSubAccountUpdate">Example</a>
```
az logz sub-account update --monitor-name "myMonitor" --monitoring-status "Enabled" --tags Environment="Dev" \
--resource-group "myResourceGroup" --name "SubAccount1"
```
##### <a name="ParametersSubAccountUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|
|**--tags**|dictionary|The new tags of the monitor resource.|tags|tags|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|

#### <a name="SubAccountDelete">Command `az logz sub-account delete`</a>

##### <a name="ExamplesSubAccountDelete">Example</a>
```
az logz sub-account delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --name "someName"
```
##### <a name="ParametersSubAccountDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|

#### <a name="SubAccountListMonitoredResources">Command `az logz sub-account list-monitored-resource`</a>

##### <a name="ExamplesSubAccountListMonitoredResources">Example</a>
```
az logz sub-account list-monitored-resource --monitor-name "myMonitor" --resource-group "myResourceGroup" --name \
"SubAccount1"
```
##### <a name="ParametersSubAccountListMonitoredResources">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|

### group `az logz sub-account-tag-rule`
#### <a name="SubAccountTagRulesList">Command `az logz sub-account-tag-rule list`</a>

##### <a name="ExamplesSubAccountTagRulesList">Example</a>
```
az logz sub-account-tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup" --sub-account-name \
"SubAccount1"
```
##### <a name="ParametersSubAccountTagRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|

#### <a name="SubAccountTagRulesGet">Command `az logz sub-account-tag-rule show`</a>

##### <a name="ExamplesSubAccountTagRulesGet">Example</a>
```
az logz sub-account-tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name \
"default" --sub-account-name "SubAccount1"
```
##### <a name="ParametersSubAccountTagRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|

#### <a name="SubAccountTagRulesCreateOrUpdate#Create">Command `az logz sub-account-tag-rule create`</a>

##### <a name="ExamplesSubAccountTagRulesCreateOrUpdate#Create">Example</a>
```
az logz sub-account-tag-rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" \
value="Prod" --filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false \
--send-activity-logs true --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default" \
--sub-account-name "SubAccount1"
```
##### <a name="ParametersSubAccountTagRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-activity-logs**|boolean|Flag specifying if activity logs from Azure resources should be sent for the Monitor resource.|send_activity_logs|sendActivityLogs|
|**--filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendActivityLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|

#### <a name="SubAccountTagRulesCreateOrUpdate#Update">Command `az logz sub-account-tag-rule update`</a>

##### <a name="ParametersSubAccountTagRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-activity-logs**|boolean|Flag specifying if activity logs from Azure resources should be sent for the Monitor resource.|send_activity_logs|sendActivityLogs|
|**--filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendActivityLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|

#### <a name="SubAccountTagRulesDelete">Command `az logz sub-account-tag-rule delete`</a>

##### <a name="ExamplesSubAccountTagRulesDelete">Example</a>
```
az logz sub-account-tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name \
"default" --sub-account-name "SubAccount1"
```
##### <a name="ParametersSubAccountTagRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--sub-account-name**|string|Sub Account resource name|sub_account_name|subAccountName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|

### group `az logz tag-rule`
#### <a name="TagRulesList">Command `az logz tag-rule list`</a>

##### <a name="ExamplesTagRulesList">Example</a>
```
az logz tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersTagRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="TagRulesGet">Command `az logz tag-rule show`</a>

##### <a name="ExamplesTagRulesGet">Example</a>
```
az logz tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|

#### <a name="TagRulesCreateOrUpdate#Create">Command `az logz tag-rule create`</a>

##### <a name="ExamplesTagRulesCreateOrUpdate#Create">Example</a>
```
az logz tag-rule create --monitor-name "myMonitor" --filtering-tags name="Environment" action="Include" value="Prod" \
--filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false --send-activity-logs true \
--send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-activity-logs**|boolean|Flag specifying if activity logs from Azure resources should be sent for the Monitor resource.|send_activity_logs|sendActivityLogs|
|**--filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendActivityLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|

#### <a name="TagRulesCreateOrUpdate#Update">Command `az logz tag-rule update`</a>

##### <a name="ParametersTagRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-activity-logs**|boolean|Flag specifying if activity logs from Azure resources should be sent for the Monitor resource.|send_activity_logs|sendActivityLogs|
|**--filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendActivityLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|

#### <a name="TagRulesDelete">Command `az logz tag-rule delete`</a>

##### <a name="ExamplesTagRulesDelete">Example</a>
```
az logz tag-rule delete --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
