# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az datadog|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az datadog` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az datadog marketplace-agreement|MarketplaceAgreements|[commands](#CommandsInMarketplaceAgreements)|
|az datadog api-key|ApiKeys|[commands](#CommandsInApiKeys)|
|az datadog host|Hosts|[commands](#CommandsInHosts)|
|az datadog linked-resource|LinkedResources|[commands](#CommandsInLinkedResources)|
|az datadog monitored-resource|MonitoredResources|[commands](#CommandsInMonitoredResources)|
|az datadog monitor|Monitors|[commands](#CommandsInMonitors)|
|az datadog set-password-link|RefreshSetPassword|[commands](#CommandsInRefreshSetPassword)|
|az datadog tag-rule|TagRules|[commands](#CommandsInTagRules)|
|az datadog sso-config|SingleSignOnConfigurations|[commands](#CommandsInSingleSignOnConfigurations)|

## COMMANDS
### <a name="CommandsInApiKeys">Commands in `az datadog api-key` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog api-key list](#ApiKeysList)|List|[Parameters](#ParametersApiKeysList)|[Example](#ExamplesApiKeysList)|
|[az datadog api-key get-default-key](#ApiKeysGetDefaultKey)|GetDefaultKey|[Parameters](#ParametersApiKeysGetDefaultKey)|[Example](#ExamplesApiKeysGetDefaultKey)|
|[az datadog api-key set-default-key](#ApiKeysSetDefaultKey)|SetDefaultKey|[Parameters](#ParametersApiKeysSetDefaultKey)|[Example](#ExamplesApiKeysSetDefaultKey)|

### <a name="CommandsInHosts">Commands in `az datadog host` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog host list](#HostsList)|List|[Parameters](#ParametersHostsList)|[Example](#ExamplesHostsList)|

### <a name="CommandsInLinkedResources">Commands in `az datadog linked-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog linked-resource list](#LinkedResourcesList)|List|[Parameters](#ParametersLinkedResourcesList)|[Example](#ExamplesLinkedResourcesList)|

### <a name="CommandsInMarketplaceAgreements">Commands in `az datadog marketplace-agreement` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog marketplace-agreement list](#MarketplaceAgreementsList)|List|[Parameters](#ParametersMarketplaceAgreementsList)|[Example](#ExamplesMarketplaceAgreementsList)|
|[az datadog marketplace-agreement create](#MarketplaceAgreementsCreate)|Create|[Parameters](#ParametersMarketplaceAgreementsCreate)|[Example](#ExamplesMarketplaceAgreementsCreate)|

### <a name="CommandsInMonitors">Commands in `az datadog monitor` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog monitor list](#MonitorsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersMonitorsListByResourceGroup)|[Example](#ExamplesMonitorsListByResourceGroup)|
|[az datadog monitor list](#MonitorsList)|List|[Parameters](#ParametersMonitorsList)|[Example](#ExamplesMonitorsList)|
|[az datadog monitor show](#MonitorsGet)|Get|[Parameters](#ParametersMonitorsGet)|[Example](#ExamplesMonitorsGet)|
|[az datadog monitor create](#MonitorsCreate)|Create|[Parameters](#ParametersMonitorsCreate)|[Example](#ExamplesMonitorsCreate)|
|[az datadog monitor update](#MonitorsUpdate)|Update|[Parameters](#ParametersMonitorsUpdate)|[Example](#ExamplesMonitorsUpdate)|
|[az datadog monitor delete](#MonitorsDelete)|Delete|[Parameters](#ParametersMonitorsDelete)|[Example](#ExamplesMonitorsDelete)|

### <a name="CommandsInMonitoredResources">Commands in `az datadog monitored-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog monitored-resource list](#MonitoredResourcesList)|List|[Parameters](#ParametersMonitoredResourcesList)|[Example](#ExamplesMonitoredResourcesList)|

### <a name="CommandsInRefreshSetPassword">Commands in `az datadog set-password-link` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datadog set-password-link get](#RefreshSetPasswordGet)|Get|[Parameters](#ParametersRefreshSetPasswordGet)|[Example](#ExamplesRefreshSetPasswordGet)|

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


## COMMAND DETAILS

### group `az datadog api-key`
#### <a name="ApiKeysList">Command `az datadog api-key list`</a>

##### <a name="ExamplesApiKeysList">Example</a>
```
az datadog api-key list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersApiKeysList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="ApiKeysGetDefaultKey">Command `az datadog api-key get-default-key`</a>

##### <a name="ExamplesApiKeysGetDefaultKey">Example</a>
```
az datadog api-key get-default-key --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersApiKeysGetDefaultKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="ApiKeysSetDefaultKey">Command `az datadog api-key set-default-key`</a>

##### <a name="ExamplesApiKeysSetDefaultKey">Example</a>
```
az datadog api-key set-default-key --monitor-name "myMonitor" --key "1111111111111111aaaaaaaaaaaaaaaa" \
--resource-group "myResourceGroup"
```
##### <a name="ParametersApiKeysSetDefaultKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--created-by**|string|The user that created the API key.|created_by|createdBy|
|**--name**|string|The name of the API key.|name|name|
|**--key**|string|The value of the API key.|key|key|
|**--created**|string|The time of creation of the API key.|created|created|

### group `az datadog host`
#### <a name="HostsList">Command `az datadog host list`</a>

##### <a name="ExamplesHostsList">Example</a>
```
az datadog host list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersHostsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az datadog linked-resource`
#### <a name="LinkedResourcesList">Command `az datadog linked-resource list`</a>

##### <a name="ExamplesLinkedResourcesList">Example</a>
```
az datadog linked-resource list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersLinkedResourcesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az datadog marketplace-agreement`
#### <a name="MarketplaceAgreementsList">Command `az datadog marketplace-agreement list`</a>

##### <a name="ExamplesMarketplaceAgreementsList">Example</a>
```
az datadog marketplace-agreement list
```
##### <a name="ParametersMarketplaceAgreementsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="MarketplaceAgreementsCreate">Command `az datadog marketplace-agreement create`</a>

##### <a name="ExamplesMarketplaceAgreementsCreate">Example</a>
```
az datadog marketplace-agreement create --properties accepted=true
```
##### <a name="ParametersMarketplaceAgreementsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--properties**|object|Represents the properties of the resource.|properties|properties|

### group `az datadog monitor`
#### <a name="MonitorsListByResourceGroup">Command `az datadog monitor list`</a>

##### <a name="ExamplesMonitorsListByResourceGroup">Example</a>
```
az datadog monitor list --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|

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
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="MonitorsCreate">Command `az datadog monitor create`</a>

##### <a name="ExamplesMonitorsCreate">Example</a>
```
az datadog monitor create --name "myMonitor" --sku-name "myMonitor" --location "West US" \
--datadog-organization-properties name="myOrg" enterprise-app-id="00000000-0000-0000-0000-000000000000" \
linking-auth-code="someAuthCode" linking-client-id="00000000-0000-0000-0000-000000000000" subscription="pro" \
--user-info name="Alice" email-address="alice@microsoft.com" phone-number="123-456-7890" --sku-name "free_Monthly" \
--tags Environment="Dev" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|Dictionary of :code:`<string>`|tags|tags|
|**--location**|string||location|location|
|**--identity-type**|choice|Identity type|type|type|
|**--datadog-organization-properties**|object|Datadog organization properties|datadog_organization_properties|datadogOrganizationProperties|
|**--user-info**|object|User info|user_info|userInfo|
|**--sku-name**|string|Name of the SKU.|name|name|

#### <a name="MonitorsUpdate">Command `az datadog monitor update`</a>

##### <a name="ExamplesMonitorsUpdate">Example</a>
```
az datadog monitor update --name "myMonitor" --tags Environment="Dev" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|The new tags of the monitor resource.|tags|tags|

#### <a name="MonitorsDelete">Command `az datadog monitor delete`</a>

##### <a name="ExamplesMonitorsDelete">Example</a>
```
az datadog monitor delete --name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az datadog monitored-resource`
#### <a name="MonitoredResourcesList">Command `az datadog monitored-resource list`</a>

##### <a name="ExamplesMonitoredResourcesList">Example</a>
```
az datadog monitored-resource list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersMonitoredResourcesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az datadog set-password-link`
#### <a name="RefreshSetPasswordGet">Command `az datadog set-password-link get`</a>

##### <a name="ExamplesRefreshSetPasswordGet">Example</a>
```
az datadog set-password-link get --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersRefreshSetPasswordGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### group `az datadog sso-config`
#### <a name="SingleSignOnConfigurationsList">Command `az datadog sso-config list`</a>

##### <a name="ExamplesSingleSignOnConfigurationsList">Example</a>
```
az datadog sso-config list --monitor-name "myMonitor" --resource-group "myResourceGroup"
```
##### <a name="ParametersSingleSignOnConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
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
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
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
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string|Configuration name|configuration_name|configurationName|
|**--properties**|object||properties|properties|

#### <a name="SingleSignOnConfigurationsCreateOrUpdate#Update">Command `az datadog sso-config update`</a>

##### <a name="ParametersSingleSignOnConfigurationsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
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
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

#### <a name="TagRulesGet">Command `az datadog tag-rule show`</a>

##### <a name="ExamplesTagRulesGet">Example</a>
```
az datadog tag-rule show --monitor-name "myMonitor" --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Rule set name|rule_set_name|ruleSetName|

#### <a name="TagRulesCreateOrUpdate#Create">Command `az datadog tag-rule create`</a>

##### <a name="ExamplesTagRulesCreateOrUpdate#Create">Example</a>
```
az datadog tag-rule create --monitor-name "myMonitor" --log-rules-send-aad-logs false --log-rules-send-resource-logs \
true --log-rules-send-subscription-logs true --resource-group "myResourceGroup" --rule-set-name "default"
```
##### <a name="ParametersTagRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Rule set name|rule_set_name|ruleSetName|
|**--metric-rules-filtering-tags**|array|List of filtering tags to be used for capturing metrics. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|
|**--log-rules-send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--log-rules-send-subscription-logs**|boolean|Flag specifying if Azure subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--log-rules-send-resource-logs**|boolean|Flag specifying if Azure resource logs should be sent for the Monitor resource.|send_resource_logs|sendResourceLogs|

#### <a name="TagRulesCreateOrUpdate#Update">Command `az datadog tag-rule update`</a>

##### <a name="ParametersTagRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string|Rule set name|rule_set_name|ruleSetName|
|**--metric-rules-filtering-tags**|array|List of filtering tags to be used for capturing metrics. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|
|**--log-rules-send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--log-rules-send-subscription-logs**|boolean|Flag specifying if Azure subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--log-rules-send-resource-logs**|boolean|Flag specifying if Azure resource logs should be sent for the Monitor resource.|send_resource_logs|sendResourceLogs|
