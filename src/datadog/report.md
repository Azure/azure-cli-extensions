# Azure CLI Module Creation Report

### datadog api-key get-default-key

get-default-key a datadog api-key.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog api-key|ApiKeys|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-default-key|GetDefaultKey|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog api-key list

list a datadog api-key.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog api-key|ApiKeys|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog api-key set-default-key

set-default-key a datadog api-key.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog api-key|ApiKeys|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|set-default-key|SetDefaultKey|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--key**|string|The value of the API key.|key|key|
|**--created-by**|string|The user that created the API key.|created_by|createdBy|
|**--name**|string|The name of the API key.|name|name|
|**--created**|string|The time of creation of the API key.|created|created|

### datadog host list

list a datadog host.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog host|Hosts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog linked-resource list

list a datadog linked-resource.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog linked-resource|LinkedResources|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog monitor create

create a datadog monitor.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog monitor|Monitors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--location**|string||location|location|
|**--tags**|dictionary|Dictionary of :code:`<string>`|tags|tags|
|**--identity-type**|choice||type|type|
|**--provisioning-state**|choice||provisioning_state|provisioningState|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|
|**--marketplace-subscription-status**|choice|Flag specifying the Marketplace Subscription Status of the resource. If payment is not made in time, the resource will go in Suspended state.|marketplace_subscription_status|marketplaceSubscriptionStatus|
|**--datadog-organization-properties**|object||datadog_organization_properties|datadogOrganizationProperties|
|**--user-info**|object||user_info|userInfo|
|**--sku-name**|string|Name of the SKU.|name|name|

### datadog monitor delete

delete a datadog monitor.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog monitor|Monitors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog monitor list

list a datadog monitor.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog monitor|Monitors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|

### datadog monitor show

show a datadog monitor.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog monitor|Monitors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog monitor update

update a datadog monitor.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog monitor|Monitors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--tags**|dictionary|The new tags of the monitor resource.|tags|tags|
|**--monitoring-status**|choice|Flag specifying if the resource monitoring is enabled or disabled.|monitoring_status|monitoringStatus|

### datadog monitored-resource list

list a datadog monitored-resource.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog monitored-resource|MonitoredResources|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog refresh-set-password get

get a datadog refresh-set-password.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog refresh-set-password|RefreshSetPassword|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog single-sign-on-configuration create

create a datadog single-sign-on-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog single-sign-on-configuration|SingleSignOnConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string||configuration_name|configurationName|
|**--properties**|object||properties|properties|

### datadog single-sign-on-configuration list

list a datadog single-sign-on-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog single-sign-on-configuration|SingleSignOnConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog single-sign-on-configuration show

show a datadog single-sign-on-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog single-sign-on-configuration|SingleSignOnConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string||configuration_name|configurationName|

### datadog single-sign-on-configuration update

update a datadog single-sign-on-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog single-sign-on-configuration|SingleSignOnConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--configuration-name**|string||configuration_name|configurationName|
|**--properties**|object||properties|properties|

### datadog tag-rule create

create a datadog tag-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog tag-rule|TagRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
|**--metric-rules-filtering-tags**|array|List of filtering tags to be used for capturing metrics. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|
|**--log-rules-send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--log-rules-send-subscription-logs**|boolean|Flag specifying if Azure subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--log-rules-send-resource-logs**|boolean|Flag specifying if Azure resource logs should be sent for the Monitor resource.|send_resource_logs|sendResourceLogs|
|**--log-rules-filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendResourceLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|log_rules_filtering_tags|filteringTags|

### datadog tag-rule list

list a datadog tag-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog tag-rule|TagRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|

### datadog tag-rule show

show a datadog tag-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog tag-rule|TagRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|

### datadog tag-rule update

update a datadog tag-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datadog tag-rule|TagRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group to which the Datadog resource belongs.|resource_group_name|resourceGroupName|
|**--monitor-name**|string|Monitor resource name|monitor_name|monitorName|
|**--rule-set-name**|string||rule_set_name|ruleSetName|
|**--metric-rules-filtering-tags**|array|List of filtering tags to be used for capturing metrics. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|filtering_tags|filteringTags|
|**--log-rules-send-aad-logs**|boolean|Flag specifying if AAD logs should be sent for the Monitor resource.|send_aad_logs|sendAadLogs|
|**--log-rules-send-subscription-logs**|boolean|Flag specifying if Azure subscription logs should be sent for the Monitor resource.|send_subscription_logs|sendSubscriptionLogs|
|**--log-rules-send-resource-logs**|boolean|Flag specifying if Azure resource logs should be sent for the Monitor resource.|send_resource_logs|sendResourceLogs|
|**--log-rules-filtering-tags**|array|List of filtering tags to be used for capturing logs. This only takes effect if SendResourceLogs flag is enabled. If empty, all resources will be captured. If only Exclude action is specified, the rules will apply to the list of all available resources. If Include actions are specified, the rules will only include resources with the associated tags.|log_rules_filtering_tags|filteringTags|
