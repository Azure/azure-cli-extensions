# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az datadog|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az datadog` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az datadog terms|MarketplaceAgreements|[commands](#CommandsInMarketplaceAgreements)|
|az datadog monitor|Monitors|[commands](#CommandsInMonitors)|
|az datadog tag-rule|TagRules|[commands](#CommandsInTagRules)|
|az datadog sso-config|SingleSignOnConfigurations|[commands](#CommandsInSingleSignOnConfigurations)|

## COMMANDS
### <a name="CommandsInMonitors">Commands in `az datadog monitor` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog monitor list](#MonitorsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMonitorsListByResourceGroup)|[Example](#ExamplesMonitorsListByResourceGroup)|
|[az datadog monitor list](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az datadog monitor show](#MonitorsGet)|Get|[Parameters](#ParametersMonitorsGet)|[Example](#ExamplesMonitorsGet)|
|[az datadog monitor create](#MonitorsCreate)|Create|[Parameters](#ParametersMonitorsCreate)|[Example](#ExamplesMonitorsCreate)|
|[az datadog monitor update](#MonitorsUpdate)|Update|[Parameters](#ParametersMonitorsUpdate)|[Example](#ExamplesMonitorsUpdate)|
|[az datadog monitor delete](#MonitorsDelete)|Delete|[Parameters](#ParametersMonitorsDelete)|[Example](#ExamplesMonitorsDelete)|
|[az datadog monitor get-default-key](#MonitorsGetDefaultKey)|GetDefaultKey|[Parameters](#ParametersMonitorsGetDefaultKey)|[Example](#ExamplesMonitorsGetDefaultKey)|
|[az datadog monitor list-api-key](#MonitorsListApiKeys)|ListApiKeys|[Parameters](#ParametersMonitorsListApiKeys)|[Example](#ExamplesMonitorsListApiKeys)|
|[az datadog monitor list-host](#MonitorsListHosts)|ListHosts|[Parameters](#ParametersMonitorsListHosts)|[Example](#ExamplesMonitorsListHosts)|
|[az datadog monitor list-linked-resource](#MonitorsListLinkedResources)|ListLinkedResources|[Parameters](#ParametersMonitorsListLinkedResources)|[Example](#ExamplesMonitorsListLinkedResources)|
|[az datadog monitor list-monitored-resource](#MonitorsListMonitoredResources)|ListMonitoredResources|[Parameters](#ParametersMonitorsListMonitoredResources)|[Example](#ExamplesMonitorsListMonitoredResources)|
|[az datadog monitor refresh-set-password-link](#MonitorsRefreshSetPasswordLink)|RefreshSetPasswordLink|[Parameters](#ParametersMonitorsRefreshSetPasswordLink)|[Example](#ExamplesMonitorsRefreshSetPasswordLink)|
|[az datadog monitor set-default-key](#MonitorsSetDefaultKey)|SetDefaultKey|[Parameters](#ParametersMonitorsSetDefaultKey)|[Example](#ExamplesMonitorsSetDefaultKey)|

### <a name="CommandsInSingleSignOnConfigurations">Commands in `az datadog sso-config` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog sso-config list](#SingleSignOnConfigurationsList)|List|[Parameters](#ParametersSingleSignOnConfigurationsList)|[Example](#ExamplesSingleSignOnConfigurationsList)|
|[az datadog sso-config show](#SingleSignOnConfigurationsGet)|Get|[Parameters](#ParametersSingleSignOnConfigurationsGet)|[Example](#ExamplesSingleSignOnConfigurationsGet)|
|[az datadog sso-config create](#SingleSignOnConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSingleSignOnConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesSingleSignOnConfigurationsCreateOrUpdate#Create)|
|[az datadog sso-config update](#SingleSignOnConfigurationsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersSingleSignOnConfigurationsCreateOrUpdate#Update)|Not Found|

### <a name="CommandsInTagRules">Commands in `az datadog tag-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog tag-rule list](#TagRulesList)|List|[Parameters](#ParametersTagRulesList)|[Example](#ExamplesTagRulesList)|
|[az datadog tag-rule show](#TagRulesGet)|Get|[Parameters](#ParametersTagRulesGet)|[Example](#ExamplesTagRulesGet)|
|[az datadog tag-rule create](#TagRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTagRulesCreateOrUpdate#Create)|[Example](#ExamplesTagRulesCreateOrUpdate#Create)|
|[az datadog tag-rule update](#TagRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersTagRulesCreateOrUpdate#Update)|Not Found|

### <a name="CommandsInMarketplaceAgreements">Commands in `az datadog terms` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog terms list](#MarketplaceAgreementsList)|List|[Parameters](#ParametersMarketplaceAgreementsList)|[Example](#ExamplesMarketplaceAgreementsList)|
|[az datadog terms create](#MarketplaceAgreementsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMarketplaceAgreementsCreateOrUpdate#Create)|[Example](#ExamplesMarketplaceAgreementsCreateOrUpdate#Create)|
|[az datadog terms update](#MarketplaceAgreementsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersMarketplaceAgreementsCreateOrUpdate#Update)|Not Found|


## COMMAND DETAILS

### group `az datadog monitor`
#### <a name="MonitorsListByResourceGroup">Command `az datadog monitor list`</a>

##### <a name="ExamplesMonitorsListByResourceGroup">Example</a>
```
az datadog monitor list --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="MonitorsList">Command `az datadog monitor list`</a>

##### <a name="ExamplesMonitorsList">Example</a>
```
az datadog monitor list
```
##### <a name="ParametersMonitorsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="MonitorsGet">Command `az datadog monitor show`</a>

##### <a name="ExamplesMonitorsGet">Example</a>
```
az datadog monitor show --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsCreate">Command `az datadog monitor create`</a>

##### <a name="ExamplesMonitorsCreate">Example</a>
```
az datadog monitor create --monitor-name "myMonitor" --name "myMonitor" --location "West US" \
--datadog-organization-properties name="myOrg" enterprise-app-id="00000000-0000-0000-0000-000000000000" \
linking-auth-code="someAuthCode" linking-client-id="00000000-0000-0000-0000-000000000000" subscription="pro" \
--user-info name="Alice" email-address="alice@microsoft.com" phone-number="123-456-7890" --name "free_Monthly" --tags \
Environment="Dev" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|
|**--location**|string||location|location|
|**--type**|choice|Identity type|type|type|
|**--datadog-organization-properties**|object|Datadog organization properties|datadog_organization_properties|datadogOrganizationProperties|
|**--user-info**|object|User info|user_info|userInfo|
|**--name**|string|Name of the SKU.|name|name|

#### <a name="MonitorsUpdate">Command `az datadog monitor update`</a>

##### <a name="ExamplesMonitorsUpdate">Example</a>
```
az datadog monitor update --monitor-name "myMonitor" --tags Environment="Dev" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|The new tags of the monitor resource.|tags|tags|
|**--name**|string|Name of the SKU.|name|name|

#### <a name="MonitorsDelete">Command `az datadog monitor delete`</a>

##### <a name="ExamplesMonitorsDelete">Example</a>
```
az datadog monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsGetDefaultKey">Command `az datadog monitor get-default-key`</a>

##### <a name="ExamplesMonitorsGetDefaultKey">Example</a>
```
az datadog monitor get-default-key --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsGetDefaultKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsListApiKeys">Command `az datadog monitor list-api-key`</a>

##### <a name="ExamplesMonitorsListApiKeys">Example</a>
```
az datadog monitor list-api-key --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListApiKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsListHosts">Command `az datadog monitor list-host`</a>

##### <a name="ExamplesMonitorsListHosts">Example</a>
```
az datadog monitor list-host --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListHosts">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsListLinkedResources">Command `az datadog monitor list-linked-resource`</a>

##### <a name="ExamplesMonitorsListLinkedResources">Example</a>
```
az datadog monitor list-linked-resource --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListLinkedResources">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsListMonitoredResources">Command `az datadog monitor list-monitored-resource`</a>

##### <a name="ExamplesMonitorsListMonitoredResources">Example</a>
```
az datadog monitor list-monitored-resource --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListMonitoredResources">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsRefreshSetPasswordLink">Command `az datadog monitor refresh-set-password-link`</a>

##### <a name="ExamplesMonitorsRefreshSetPasswordLink">Example</a>
```
az datadog monitor refresh-set-password-link --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsRefreshSetPasswordLink">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsSetDefaultKey">Command `az datadog monitor set-default-key`</a>

##### <a name="ExamplesMonitorsSetDefaultKey">Example</a>
```
az datadog monitor set-default-key --monitor-name "myMonitor" --key "1111111111111111aaaaaaaaaaaaaaaa" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsSetDefaultKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--created-by**|string|The user that created the API key.|created_by|createdBy|
|**--name**|string|The name of the API key.|name|name|
|**--key**|string|The value of the API key.|key|key|
|**--created**|string|The time of creation of the API key.|created|created|

### group `az datadog sso-config`
#### <a name="SingleSignOnConfigurationsList">Command `az datadog sso-config list`</a>

##### <a name="ExamplesSingleSignOnConfigurationsList">Example</a>
```
az datadog sso-config list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersSingleSignOnConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="SingleSignOnConfigurationsGet">Command `az datadog sso-config show`</a>

##### <a name="ExamplesSingleSignOnConfigurationsGet">Example</a>
```
az datadog sso-config show --configuration-name "default" --monitor-name "myMonitor" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersSingleSignOnConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string|Configuration name|configuration_name|configurationName|

#### <a name="SingleSignOnConfigurationsCreateOrUpdate#Create">Command `az datadog sso-config create`</a>

##### <a name="ExamplesSingleSignOnConfigurationsCreateOrUpdate#Create">Example</a>
```
az datadog sso-config create --configuration-name "default" --monitor-name "myMonitor" --properties \
enterprise-app-id="00000000-0000-0000-0000-000000000000" single-sign-on-state="Enable" --resource-group \
"myResourceGroup"
```
##### <a name="ParametersSingleSignOnConfigurationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string|Configuration name|configuration_name|configurationName|
|**--properties**|object||properties|properties|

#### <a name="SingleSignOnConfigurationsCreateOrUpdate#Update">Command `az datadog sso-config update`</a>

##### <a name="ParametersSingleSignOnConfigurationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string|Configuration name|configuration_name|configurationName|
|**--properties**|object||properties|properties|

### group `az datadog tag-rule`
#### <a name="TagRulesList">Command `az datadog tag-rule list`</a>

##### <a name="ExamplesTagRulesList">Example</a>
```
az datadog tag-rule list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersTagRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="TagRulesGet">Command `az datadog tag-rule show`</a>

##### <a name="ExamplesTagRulesGet">Example</a>
```
az datadog tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Rule set name|rule_set_name|ruleSetName|

#### <a name="TagRulesCreateOrUpdate#Create">Command `az datadog tag-rule create`</a>

##### <a name="ExamplesTagRulesCreateOrUpdate#Create">Example</a>
```
az datadog tag-rule create --monitor-name "myMonitor" --log-rules-filtering-tags name="Environment" action="Include" \
value="Prod" --log-rules-filtering-tags name="Environment" action="Exclude" value="Dev" --send-aad-logs false \
--send-resource-logs true --send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Rule set name|rule_set_name|ruleSetName|
|**--filtering-tags**|array|List of filtering tags to be used for capturing metrics. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if Azure subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-resource-logs**|boolean|Flag specifying if Azure resource logs should be sent for the Monitor resource.|send_resource_logs|sendResourceLogs|
|**--log-rules-filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendResourceLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|log_rules_filtering_tags|filteringTags|

#### <a name="TagRulesCreateOrUpdate#Update">Command `az datadog tag-rule update`</a>

##### <a name="ParametersTagRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Rule set name|rule_set_name|ruleSetName|
|**--filtering-tags**|array|List of filtering tags to be used for capturing metrics. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|
|**--send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--send-subscription-logs**|boolean|Flag specifying if Azure subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--send-resource-logs**|boolean|Flag specifying if Azure resource logs should be sent for the Monitor resource.|send_resource_logs|sendResourceLogs|
|**--log-rules-filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendResourceLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|log_rules_filtering_tags|filteringTags|

### group `az datadog terms`
#### <a name="MarketplaceAgreementsList">Command `az datadog terms list`</a>

##### <a name="ExamplesMarketplaceAgreementsList">Example</a>
```
az datadog terms list
```
##### <a name="ParametersMarketplaceAgreementsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="MarketplaceAgreementsCreateOrUpdate#Create">Command `az datadog terms create`</a>

##### <a name="ExamplesMarketplaceAgreementsCreateOrUpdate#Create">Example</a>
```
az datadog terms create --properties accepted=true
```
##### <a name="ParametersMarketplaceAgreementsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--properties**|object|Represents the properties of the resource.|properties|properties|

#### <a name="MarketplaceAgreementsCreateOrUpdate#Update">Command `az datadog terms update`</a>

##### <a name="ParametersMarketplaceAgreementsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--properties**|object|Represents the properties of the resource.|properties|properties|
