# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az costmanagement|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az costmanagement` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az costmanagement view|Views|[commands](#CommandsInViews)|
|az costmanagement alert|Alerts|[commands](#CommandsInAlerts)|
|az costmanagement forecast|Forecast|[commands](#CommandsInForecast)|
|az costmanagement dimension|Dimensions|[commands](#CommandsInDimensions)|
|az costmanagement query|Query|[commands](#CommandsInQuery)|
|az costmanagement export|Exports|[commands](#CommandsInExports)|

## COMMANDS
### <a name="CommandsInAlerts">Commands in `az costmanagement alert` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az costmanagement alert list](#AlertsList)|List|[Parameters](#ParametersAlertsList)|[Example](#ExamplesAlertsList)|
|[az costmanagement alert show](#AlertsGet)|Get|[Parameters](#ParametersAlertsGet)|[Example](#ExamplesAlertsGet)|
|[az costmanagement alert dismiss](#AlertsDismiss)|Dismiss|[Parameters](#ParametersAlertsDismiss)|[Example](#ExamplesAlertsDismiss)|
|[az costmanagement alert list-external](#AlertsListExternal)|ListExternal|[Parameters](#ParametersAlertsListExternal)|[Example](#ExamplesAlertsListExternal)|

### <a name="CommandsInDimensions">Commands in `az costmanagement dimension` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az costmanagement dimension list](#DimensionsList)|List|[Parameters](#ParametersDimensionsList)|[Example](#ExamplesDimensionsList)|
|[az costmanagement dimension by-external-cloud-provider-type](#DimensionsByExternalCloudProviderType)|ByExternalCloudProviderType|[Parameters](#ParametersDimensionsByExternalCloudProviderType)|[Example](#ExamplesDimensionsByExternalCloudProviderType)|

### <a name="CommandsInExports">Commands in `az costmanagement export` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az costmanagement export list](#ExportsList)|List|[Parameters](#ParametersExportsList)|[Example](#ExamplesExportsList)|
|[az costmanagement export show](#ExportsGet)|Get|[Parameters](#ParametersExportsGet)|[Example](#ExamplesExportsGet)|
|[az costmanagement export create](#ExportsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersExportsCreateOrUpdate#Create)|[Example](#ExamplesExportsCreateOrUpdate#Create)|
|[az costmanagement export update](#ExportsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersExportsCreateOrUpdate#Update)|Not Found|
|[az costmanagement export delete](#ExportsDelete)|Delete|[Parameters](#ParametersExportsDelete)|[Example](#ExamplesExportsDelete)|
|[az costmanagement export execute](#ExportsExecute)|Execute|[Parameters](#ParametersExportsExecute)|[Example](#ExamplesExportsExecute)|
|[az costmanagement export get-execution-history](#ExportsGetExecutionHistory)|GetExecutionHistory|[Parameters](#ParametersExportsGetExecutionHistory)|[Example](#ExamplesExportsGetExecutionHistory)|

### <a name="CommandsInForecast">Commands in `az costmanagement forecast` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az costmanagement forecast external-cloud-provider-usage](#ForecastExternalCloudProviderUsage)|ExternalCloudProviderUsage|[Parameters](#ParametersForecastExternalCloudProviderUsage)|[Example](#ExamplesForecastExternalCloudProviderUsage)|
|[az costmanagement forecast usage](#ForecastUsage)|Usage|[Parameters](#ParametersForecastUsage)|[Example](#ExamplesForecastUsage)|

### <a name="CommandsInQuery">Commands in `az costmanagement query` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az costmanagement query usage](#QueryUsage)|Usage|[Parameters](#ParametersQueryUsage)|[Example](#ExamplesQueryUsage)|
|[az costmanagement query usage-by-external-cloud-provider-type](#QueryUsageByExternalCloudProviderType)|UsageByExternalCloudProviderType|[Parameters](#ParametersQueryUsageByExternalCloudProviderType)|[Example](#ExamplesQueryUsageByExternalCloudProviderType)|

### <a name="CommandsInViews">Commands in `az costmanagement view` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az costmanagement view list](#ViewsListByScope)|ListByScope|[Parameters](#ParametersViewsListByScope)|[Example](#ExamplesViewsListByScope)|
|[az costmanagement view list](#ViewsList)|List|[Parameters](#ParametersViewsList)|[Example](#ExamplesViewsList)|
|[az costmanagement view show](#ViewsGet)|Get|[Parameters](#ParametersViewsGet)|[Example](#ExamplesViewsGet)|
|[az costmanagement view create](#ViewsCreateOrUpdateByScope)|CreateOrUpdateByScope|[Parameters](#ParametersViewsCreateOrUpdateByScope)|[Example](#ExamplesViewsCreateOrUpdateByScope)|
|[az costmanagement view create](#ViewsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersViewsCreateOrUpdate#Create)|[Example](#ExamplesViewsCreateOrUpdate#Create)|
|[az costmanagement view update](#ViewsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersViewsCreateOrUpdate#Update)|Not Found|
|[az costmanagement view delete](#ViewsDeleteByScope)|DeleteByScope|[Parameters](#ParametersViewsDeleteByScope)|[Example](#ExamplesViewsDeleteByScope)|
|[az costmanagement view delete](#ViewsDelete)|Delete|[Parameters](#ParametersViewsDelete)|[Example](#ExamplesViewsDelete)|
|[az costmanagement view get-by-scope](#ViewsGetByScope)|GetByScope|[Parameters](#ParametersViewsGetByScope)|[Example](#ExamplesViewsGetByScope)|


## COMMAND DETAILS

### group `az costmanagement alert`
#### <a name="AlertsList">Command `az costmanagement alert list`</a>

##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789"
```
##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579"
```
##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/departments/123"
```
##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/enrollmentAccounts/456"
```
##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579/invo\
iceSections/9876"
```
##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ScreenSharingTe\
st-peer"
```
##### <a name="ExamplesAlertsList">Example</a>
```
az costmanagement alert list --scope "subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersAlertsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with alerts operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|

#### <a name="AlertsGet">Command `az costmanagement alert show`</a>

##### <a name="ExamplesAlertsGet">Example</a>
```
az costmanagement alert show --alert-id "22222222-2222-2222-2222-222222222222" --scope "subscriptions/00000000-0000-000\
0-0000-000000000000/resourceGroups/ScreenSharingTest-peer"
```
##### <a name="ExamplesAlertsGet">Example</a>
```
az costmanagement alert show --alert-id "22222222-2222-2222-2222-222222222222" --scope "subscriptions/00000000-0000-000\
0-0000-000000000000"
```
##### <a name="ParametersAlertsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with alerts operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--alert-id**|string|Alert ID|alert_id|alertId|

#### <a name="AlertsDismiss">Command `az costmanagement alert dismiss`</a>

##### <a name="ExamplesAlertsDismiss">Example</a>
```
az costmanagement alert dismiss --alert-id "22222222-2222-2222-2222-222222222222" --status "Dismissed" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ScreenSharingTest-peer"
```
##### <a name="ExamplesAlertsDismiss">Example</a>
```
az costmanagement alert dismiss --alert-id "22222222-2222-2222-2222-222222222222" --status "Dismissed" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersAlertsDismiss">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with alerts operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--alert-id**|string|Alert ID|alert_id|alertId|
|**--definition**|object|defines the type of alert|definition|definition|
|**--description**|string|Alert description|description|description|
|**--source**|choice|Source of alert|source|source|
|**--cost-entity-id**|string|related budget|cost_entity_id|costEntityId|
|**--status**|choice|alert status|status|status|
|**--creation-time**|string|dateTime in which alert was created|creation_time|creationTime|
|**--close-time**|string|dateTime in which alert was closed|close_time|closeTime|
|**--modification-time**|string|dateTime in which alert was last modified|modification_time|modificationTime|
|**--status-modification-user-name**|string||status_modification_user_name|statusModificationUserName|
|**--status-modification-time**|string|dateTime in which the alert status was last modified|status_modification_time|statusModificationTime|
|**--details-time-grain-type**|choice|Type of timegrain cadence|time_grain_type|timeGrainType|
|**--details-period-start-date**|string|datetime of periodStartDate|period_start_date|periodStartDate|
|**--details-triggered-by**|string|notificationId that triggered this alert|triggered_by|triggeredBy|
|**--details-resource-group-filter**|array|array of resourceGroups to filter by|resource_group_filter|resourceGroupFilter|
|**--details-resource-filter**|array|array of resources to filter by|resource_filter|resourceFilter|
|**--details-meter-filter**|array|array of meters to filter by|meter_filter|meterFilter|
|**--details-tag-filter**|any|tags to filter by|tag_filter|tagFilter|
|**--details-threshold**|number|notification threshold percentage as a decimal which activated this alert|threshold|threshold|
|**--details-operator**|choice|operator used to compare currentSpend with amount|operator|operator|
|**--details-amount**|number|budget threshold amount|amount|amount|
|**--details-unit**|string|unit of currency being used|unit|unit|
|**--details-current-spend**|number|current spend|current_spend|currentSpend|
|**--details-contact-emails**|array|list of emails to contact|contact_emails|contactEmails|
|**--details-contact-groups**|array|list of action groups to broadcast to|contact_groups|contactGroups|
|**--details-contact-roles**|array|list of contact roles|contact_roles|contactRoles|
|**--details-overriding-alert**|string|overriding alert|overriding_alert|overridingAlert|

#### <a name="AlertsListExternal">Command `az costmanagement alert list-external`</a>

##### <a name="ExamplesAlertsListExternal">Example</a>
```
az costmanagement alert list-external --external-cloud-provider-id "100" --external-cloud-provider-type \
"externalBillingAccounts"
```
##### <a name="ExamplesAlertsListExternal">Example</a>
```
az costmanagement alert list-external --external-cloud-provider-id "100" --external-cloud-provider-type \
"externalSubscriptions"
```
##### <a name="ParametersAlertsListExternal">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--external-cloud-provider-type**|choice|The external cloud provider type associated with dimension/query operations. This includes 'externalSubscriptions' for linked account and 'externalBillingAccounts' for consolidated account.|external_cloud_provider_type|externalCloudProviderType|
|**--external-cloud-provider-id**|string|This can be '{externalSubscriptionId}' for linked account or '{externalBillingAccountId}' for consolidated account used with dimension/query operations.|external_cloud_provider_id|externalCloudProviderId|

### group `az costmanagement dimension`
#### <a name="DimensionsList">Command `az costmanagement dimension list`</a>

##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/100"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/100"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/12345:6789"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/100"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/12345:6789"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/12345:6789/billingProfiles/13579"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/customers/5678"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/12345:6789/customers/5678"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/12345:6789/customers/5678"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/100/departments/123"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/100/departments/123"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/100/departments/123"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/100/enrollmentAccounts/456"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/100/enrollmentAccounts/456"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/100/enrollmentAccounts/456"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579/\
invoiceSections/9876"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Billing/billingAccount\
s/12345:6789/billingProfiles/13579/invoiceSections/9876"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579/invoiceSections/9876"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --scope "providers/Microsoft.Management/managementGroups/MyMgId"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "providers/Microsoft.Management/managementG\
roups/MyMgId"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --filter "properties/category eq \'resourceId\'" --top 5 \
--scope "providers/Microsoft.Management/managementGroups/MyMgId"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "subscriptions/00000000-0000-0000-0000-0000\
00000000/resourceGroups/system.orlando"
```
##### <a name="ExamplesDimensionsList">Example</a>
```
az costmanagement dimension list --expand "properties/data" --top 5 --scope "subscriptions/00000000-0000-0000-0000-0000\
00000000"
```
##### <a name="ParametersDimensionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with dimension operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--filter**|string|May be used to filter dimensions by properties/category, properties/usageStart, properties/usageEnd. Supported operators are 'eq','lt', 'gt', 'le', 'ge'.|filter|$filter|
|**--expand**|string|May be used to expand the properties/data within a dimension category. By default, data is not included when listing dimensions.|expand|$expand|
|**--skiptoken**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|
|**--top**|integer|May be used to limit the number of results to the most recent N dimension data.|top|$top|

#### <a name="DimensionsByExternalCloudProviderType">Command `az costmanagement dimension by-external-cloud-provider-type`</a>

##### <a name="ExamplesDimensionsByExternalCloudProviderType">Example</a>
```
az costmanagement dimension by-external-cloud-provider-type --external-cloud-provider-id "100" \
--external-cloud-provider-type "externalBillingAccounts"
```
##### <a name="ExamplesDimensionsByExternalCloudProviderType">Example</a>
```
az costmanagement dimension by-external-cloud-provider-type --external-cloud-provider-id "100" \
--external-cloud-provider-type "externalSubscriptions"
```
##### <a name="ParametersDimensionsByExternalCloudProviderType">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--external-cloud-provider-type**|choice|The external cloud provider type associated with dimension/query operations. This includes 'externalSubscriptions' for linked account and 'externalBillingAccounts' for consolidated account.|external_cloud_provider_type|externalCloudProviderType|
|**--external-cloud-provider-id**|string|This can be '{externalSubscriptionId}' for linked account or '{externalBillingAccountId}' for consolidated account used with dimension/query operations.|external_cloud_provider_id|externalCloudProviderId|
|**--filter**|string|May be used to filter dimensions by properties/category, properties/usageStart, properties/usageEnd. Supported operators are 'eq','lt', 'gt', 'le', 'ge'.|filter|$filter|
|**--expand**|string|May be used to expand the properties/data within a dimension category. By default, data is not included when listing dimensions.|expand|$expand|
|**--skiptoken**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|
|**--top**|integer|May be used to limit the number of results to the most recent N dimension data.|top|$top|

### group `az costmanagement export`
#### <a name="ExportsList">Command `az costmanagement export list`</a>

##### <a name="ExamplesExportsList">Example</a>
```
az costmanagement export list --scope "providers/Microsoft.Billing/billingAccounts/123456"
```
##### <a name="ExamplesExportsList">Example</a>
```
az costmanagement export list --scope "providers/Microsoft.Billing/billingAccounts/12/departments/123"
```
##### <a name="ExamplesExportsList">Example</a>
```
az costmanagement export list --scope "providers/Microsoft.Billing/billingAccounts/100/enrollmentAccounts/456"
```
##### <a name="ExamplesExportsList">Example</a>
```
az costmanagement export list --scope "providers/Microsoft.Management/managementGroups/TestMG"
```
##### <a name="ExamplesExportsList">Example</a>
```
az costmanagement export list --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG"
```
##### <a name="ExamplesExportsList">Example</a>
```
az costmanagement export list --scope "subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersExportsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--expand**|string|May be used to expand the properties within an export. Currently only 'runHistory' is supported and will return information for the last execution of each export.|expand|$expand|

#### <a name="ExportsGet">Command `az costmanagement export show`</a>

##### <a name="ExamplesExportsGet">Example</a>
```
az costmanagement export show --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/123456"
```
##### <a name="ExamplesExportsGet">Example</a>
```
az costmanagement export show --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/12/departments/1\
234"
```
##### <a name="ExamplesExportsGet">Example</a>
```
az costmanagement export show --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/100/enrollmentAc\
counts/456"
```
##### <a name="ExamplesExportsGet">Example</a>
```
az costmanagement export show --name "TestExport" --scope "providers/Microsoft.Management/managementGroups/TestMG"
```
##### <a name="ExamplesExportsGet">Example</a>
```
az costmanagement export show --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceG\
roups/MYDEVTESTRG"
```
##### <a name="ExamplesExportsGet">Example</a>
```
az costmanagement export show --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersExportsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|
|**--expand**|string|May be used to expand the properties within an export. Currently only 'runHistory' is supported and will return information for the last 10 executions of the export.|expand|$expand|

#### <a name="ExportsCreateOrUpdate#Create">Command `az costmanagement export create`</a>

##### <a name="ExamplesExportsCreateOrUpdate#Create">Example</a>
```
az costmanagement export create --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/123456"
```
##### <a name="ExamplesExportsCreateOrUpdate#Create">Example</a>
```
az costmanagement export create --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/12/departments\
/1234"
```
##### <a name="ExamplesExportsCreateOrUpdate#Create">Example</a>
```
az costmanagement export create --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/100/enrollment\
Accounts/456"
```
##### <a name="ExamplesExportsCreateOrUpdate#Create">Example</a>
```
az costmanagement export create --name "TestExport" --scope "providers/Microsoft.Management/managementGroups/TestMG"
```
##### <a name="ExamplesExportsCreateOrUpdate#Create">Example</a>
```
az costmanagement export create --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourc\
eGroups/MYDEVTESTRG"
```
##### <a name="ExamplesExportsCreateOrUpdate#Create">Example</a>
```
az costmanagement export create --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersExportsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--schedule-status**|choice|The status of the export's schedule. If 'Inactive', the export's schedule is paused.|status|status|
|**--schedule-recurrence**|choice|The schedule recurrence.|recurrence|recurrence|
|**--schedule-recurrence-period**|object|Has start and end date of the recurrence. The start date must be in future. If present, the end date must be greater than start date.|recurrence_period|recurrencePeriod|
|**--definition-type**|choice|The type of the export. Note that 'Usage' is equivalent to 'ActualCost' and is applicable to exports that do not yet provide data for charges or amortization for service reservations.|type|type|
|**--definition-timeframe**|choice|The time frame for pulling data for the export. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--definition-time-period**|object|Has time period for pulling data for the export.|time_period|timePeriod|
|**--definition-data-set-configuration**|object|The export dataset configuration.|configuration|configuration|
|**--delivery-info-destination**|object|Has destination for the export being delivered.|destination|destination|

#### <a name="ExportsCreateOrUpdate#Update">Command `az costmanagement export update`</a>

##### <a name="ParametersExportsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--schedule-status**|choice|The status of the export's schedule. If 'Inactive', the export's schedule is paused.|status|status|
|**--schedule-recurrence**|choice|The schedule recurrence.|recurrence|recurrence|
|**--schedule-recurrence-period**|object|Has start and end date of the recurrence. The start date must be in future. If present, the end date must be greater than start date.|recurrence_period|recurrencePeriod|
|**--definition-type**|choice|The type of the export. Note that 'Usage' is equivalent to 'ActualCost' and is applicable to exports that do not yet provide data for charges or amortization for service reservations.|type|type|
|**--definition-timeframe**|choice|The time frame for pulling data for the export. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--definition-time-period**|object|Has time period for pulling data for the export.|time_period|timePeriod|
|**--definition-data-set-configuration**|object|The export dataset configuration.|configuration|configuration|
|**--delivery-info-destination**|object|Has destination for the export being delivered.|destination|destination|

#### <a name="ExportsDelete">Command `az costmanagement export delete`</a>

##### <a name="ExamplesExportsDelete">Example</a>
```
az costmanagement export delete --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/123456"
```
##### <a name="ExamplesExportsDelete">Example</a>
```
az costmanagement export delete --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/12/departments\
/1234"
```
##### <a name="ExamplesExportsDelete">Example</a>
```
az costmanagement export delete --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/100/enrollment\
Accounts/456"
```
##### <a name="ExamplesExportsDelete">Example</a>
```
az costmanagement export delete --name "TestExport" --scope "providers/Microsoft.Management/managementGroups/TestMG"
```
##### <a name="ExamplesExportsDelete">Example</a>
```
az costmanagement export delete --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourc\
eGroups/MYDEVTESTRG"
```
##### <a name="ExamplesExportsDelete">Example</a>
```
az costmanagement export delete --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersExportsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|

#### <a name="ExportsExecute">Command `az costmanagement export execute`</a>

##### <a name="ExamplesExportsExecute">Example</a>
```
az costmanagement export execute --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/123456"
```
##### <a name="ExamplesExportsExecute">Example</a>
```
az costmanagement export execute --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/12/department\
s/1234"
```
##### <a name="ExamplesExportsExecute">Example</a>
```
az costmanagement export execute --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts/100/enrollmen\
tAccounts/456"
```
##### <a name="ExamplesExportsExecute">Example</a>
```
az costmanagement export execute --name "TestExport" --scope "providers/Microsoft.Management/managementGroups/TestMG"
```
##### <a name="ExamplesExportsExecute">Example</a>
```
az costmanagement export execute --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000/resour\
ceGroups/MYDEVTESTRG"
```
##### <a name="ExamplesExportsExecute">Example</a>
```
az costmanagement export execute --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersExportsExecute">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|

#### <a name="ExportsGetExecutionHistory">Command `az costmanagement export get-execution-history`</a>

##### <a name="ExamplesExportsGetExecutionHistory">Example</a>
```
az costmanagement export get-execution-history --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts\
/123456"
```
##### <a name="ExamplesExportsGetExecutionHistory">Example</a>
```
az costmanagement export get-execution-history --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts\
/12/departments/1234"
```
##### <a name="ExamplesExportsGetExecutionHistory">Example</a>
```
az costmanagement export get-execution-history --name "TestExport" --scope "providers/Microsoft.Billing/billingAccounts\
/100/enrollmentAccounts/456"
```
##### <a name="ExamplesExportsGetExecutionHistory">Example</a>
```
az costmanagement export get-execution-history --name "TestExport" --scope "providers/Microsoft.Management/managementGr\
oups/TestMG"
```
##### <a name="ExamplesExportsGetExecutionHistory">Example</a>
```
az costmanagement export get-execution-history --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-00000\
0000000/resourceGroups/MYDEVTESTRG"
```
##### <a name="ExamplesExportsGetExecutionHistory">Example</a>
```
az costmanagement export get-execution-history --name "TestExport" --scope "subscriptions/00000000-0000-0000-0000-00000\
0000000"
```
##### <a name="ParametersExportsGetExecutionHistory">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|

### group `az costmanagement forecast`
#### <a name="ForecastExternalCloudProviderUsage">Command `az costmanagement forecast external-cloud-provider-usage`</a>

##### <a name="ExamplesForecastExternalCloudProviderUsage">Example</a>
```
az costmanagement forecast external-cloud-provider-usage --external-cloud-provider-id "100" \
--external-cloud-provider-type "externalBillingAccounts" --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dime\
nsion\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West \
Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\
\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe \
"MonthToDate"
```
##### <a name="ExamplesForecastExternalCloudProviderUsage">Example</a>
```
az costmanagement forecast external-cloud-provider-usage --external-cloud-provider-id "100" \
--external-cloud-provider-type "externalSubscriptions" --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimens\
ion\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West \
Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\
\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe \
"MonthToDate"
```
##### <a name="ParametersForecastExternalCloudProviderUsage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--external-cloud-provider-type**|choice|The external cloud provider type associated with dimension/query operations. This includes 'externalSubscriptions' for linked account and 'externalBillingAccounts' for consolidated account.|external_cloud_provider_type|externalCloudProviderType|
|**--external-cloud-provider-id**|string|This can be '{externalSubscriptionId}' for linked account or '{externalBillingAccountId}' for consolidated account used with dimension/query operations.|external_cloud_provider_id|externalCloudProviderId|
|**--type**|choice|The type of the forecast.|type|type|
|**--timeframe**|choice|The time frame for pulling data for the forecast. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--filter**|string|May be used to filter forecasts by properties/usageDate (Utc time), properties/chargeType or properties/grain. The filter supports 'eq', 'lt', 'gt', 'le', 'ge', and 'and'. It does not currently support 'ne', 'or', or 'not'.|filter|$filter|
|**--time-period**|object|Has time period for pulling data for the forecast.|time_period|timePeriod|
|**--include-actual-cost**|boolean|a boolean determining if actualCost will be included|include_actual_cost|includeActualCost|
|**--include-fresh-partial-cost**|boolean|a boolean determining if FreshPartialCost will be included|include_fresh_partial_cost|includeFreshPartialCost|
|**--dataset-configuration**|object|Has configuration information for the data in the export. The configuration will be ignored if aggregation and grouping are provided.|configuration|configuration|
|**--dataset-aggregation**|dictionary|Dictionary of aggregation expression to use in the forecast. The key of each item in the dictionary is the alias for the aggregated column. forecast can have up to 2 aggregation clauses.|aggregation|aggregation|
|**--query-filter**|object|Has filter expression to use in the forecast.|query_filter|filter|

#### <a name="ForecastUsage">Command `az costmanagement forecast usage`</a>

##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "providers/Microsoft.Billing/billingAccounts/12345\
:6789"
```
##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "providers/Microsoft.Billing/billingAccounts/12345\
:6789/billingProfiles/13579"
```
##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "providers/Microsoft.Billing/billingAccounts/12345\
:6789/departments/123"
```
##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "providers/Microsoft.Billing/billingAccounts/12345\
:6789/enrollmentAccounts/456"
```
##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "providers/Microsoft.Billing/billingAccounts/12345\
:6789/billingProfiles/13579/invoiceSections/9876"
```
##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "subscriptions/00000000-0000-0000-0000-00000000000\
0/resourceGroups/ScreenSharingTest-peer"
```
##### <a name="ExamplesForecastUsage">Example</a>
```
az costmanagement forecast usage --type "Usage" --query-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"\
ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"\
Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"Resource\
Group\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --include-actual-cost false \
--include-fresh-partial-cost false --timeframe "MonthToDate" --scope "subscriptions/00000000-0000-0000-0000-00000000000\
0"
```
##### <a name="ParametersForecastUsage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with forecast operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--type**|choice|The type of the forecast.|type|type|
|**--timeframe**|choice|The time frame for pulling data for the forecast. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--filter**|string|May be used to filter forecasts by properties/usageDate (Utc time), properties/chargeType or properties/grain. The filter supports 'eq', 'lt', 'gt', 'le', 'ge', and 'and'. It does not currently support 'ne', 'or', or 'not'.|filter|$filter|
|**--time-period**|object|Has time period for pulling data for the forecast.|time_period|timePeriod|
|**--include-actual-cost**|boolean|a boolean determining if actualCost will be included|include_actual_cost|includeActualCost|
|**--include-fresh-partial-cost**|boolean|a boolean determining if FreshPartialCost will be included|include_fresh_partial_cost|includeFreshPartialCost|
|**--dataset-configuration**|object|Has configuration information for the data in the export. The configuration will be ignored if aggregation and grouping are provided.|configuration|configuration|
|**--dataset-aggregation**|dictionary|Dictionary of aggregation expression to use in the forecast. The key of each item in the dictionary is the alias for the aggregated column. forecast can have up to 2 aggregation clauses.|aggregation|aggregation|
|**--query-filter**|object|Has filter expression to use in the forecast.|query_filter|filter|

### group `az costmanagement query`
#### <a name="QueryUsage">Command `az costmanagement query usage`</a>

##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/70664866"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/70664866"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789/customers/5678"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789/customers/5678"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/100/departments/123"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/100/departments/123"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/100/enrollmentAccounts/456"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/100/enrollmentAccounts/456"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579/invoiceSections/9876"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Billing/billingAccounts/12345:6789/billingProfiles/13579/invoiceSections/9876"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"providers/Microsoft.Management/managementGroups/MyMgId"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"providers/Microsoft.Management/managementGroups/MyMgId"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ScreenSharingTest-peer"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceType" type="Dimension" --timeframe "TheLastMonth" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ScreenSharingTest-peer"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"R\
esourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"E\
nvironment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceG\
roup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe "MonthToDate" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ExamplesQueryUsage">Example</a>
```
az costmanagement query usage --type "Usage" --dataset-aggregation "{\\"totalCost\\":{\\"name\\":\\"PreTaxCost\\",\\"fu\
nction\\":\\"Sum\\"}}" --dataset-grouping name="ResourceGroup" type="Dimension" --timeframe "TheLastMonth" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersQueryUsage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--type**|choice|The type of the query.|type|type|
|**--timeframe**|choice|The time frame for pulling data for the query. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--time-period**|object|Has time period for pulling data for the query.|time_period|timePeriod|
|**--dataset-configuration**|object|Has configuration information for the data in the export. The configuration will be ignored if aggregation and grouping are provided.|configuration|configuration|
|**--dataset-aggregation**|dictionary|Dictionary of aggregation expression to use in the query. The key of each item in the dictionary is the alias for the aggregated column. Query can have up to 2 aggregation clauses.|aggregation|aggregation|
|**--dataset-grouping**|array|Array of group by expression to use in the query. Query can have up to 2 group by clauses.|grouping|grouping|
|**--dataset-filter**|object|Has filter expression to use in the query.|filter|filter|

#### <a name="QueryUsageByExternalCloudProviderType">Command `az costmanagement query usage-by-external-cloud-provider-type`</a>

##### <a name="ExamplesQueryUsageByExternalCloudProviderType">Example</a>
```
az costmanagement query usage-by-external-cloud-provider-type --external-cloud-provider-id "100" \
--external-cloud-provider-type "externalBillingAccounts" --type "Usage" --dataset-filter \
"{\\"and\\":[{\\"or\\":[{\\"dimension\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"Ea\
st US\\",\\"West Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\
\\"Prod\\"]}}]},{\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" \
--timeframe "MonthToDate"
```
##### <a name="ExamplesQueryUsageByExternalCloudProviderType">Example</a>
```
az costmanagement query usage-by-external-cloud-provider-type --external-cloud-provider-id "100" \
--external-cloud-provider-type "externalSubscriptions" --type "Usage" --dataset-filter "{\\"and\\":[{\\"or\\":[{\\"dime\
nsion\\":{\\"name\\":\\"ResourceLocation\\",\\"operator\\":\\"In\\",\\"values\\":[\\"East US\\",\\"West \
Europe\\"]}},{\\"tag\\":{\\"name\\":\\"Environment\\",\\"operator\\":\\"In\\",\\"values\\":[\\"UAT\\",\\"Prod\\"]}}]},{\
\\"dimension\\":{\\"name\\":\\"ResourceGroup\\",\\"operator\\":\\"In\\",\\"values\\":[\\"API\\"]}}]}" --timeframe \
"MonthToDate"
```
##### <a name="ParametersQueryUsageByExternalCloudProviderType">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--external-cloud-provider-type**|choice|The external cloud provider type associated with dimension/query operations. This includes 'externalSubscriptions' for linked account and 'externalBillingAccounts' for consolidated account.|external_cloud_provider_type|externalCloudProviderType|
|**--external-cloud-provider-id**|string|This can be '{externalSubscriptionId}' for linked account or '{externalBillingAccountId}' for consolidated account used with dimension/query operations.|external_cloud_provider_id|externalCloudProviderId|
|**--type**|choice|The type of the query.|type|type|
|**--timeframe**|choice|The time frame for pulling data for the query. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--time-period**|object|Has time period for pulling data for the query.|time_period|timePeriod|
|**--dataset-configuration**|object|Has configuration information for the data in the export. The configuration will be ignored if aggregation and grouping are provided.|configuration|configuration|
|**--dataset-aggregation**|dictionary|Dictionary of aggregation expression to use in the query. The key of each item in the dictionary is the alias for the aggregated column. Query can have up to 2 aggregation clauses.|aggregation|aggregation|
|**--dataset-grouping**|array|Array of group by expression to use in the query. Query can have up to 2 group by clauses.|grouping|grouping|
|**--dataset-filter**|object|Has filter expression to use in the query.|filter|filter|

### group `az costmanagement view`
#### <a name="ViewsListByScope">Command `az costmanagement view list`</a>

##### <a name="ExamplesViewsListByScope">Example</a>
```
az costmanagement view list --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG"
```
##### <a name="ParametersViewsListByScope">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|

#### <a name="ViewsList">Command `az costmanagement view list`</a>

##### <a name="ExamplesViewsList">Example</a>
```
az costmanagement view list
```
##### <a name="ParametersViewsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ViewsGet">Command `az costmanagement view show`</a>

##### <a name="ExamplesViewsGet">Example</a>
```
az costmanagement view show --name "swaggerExample"
```
##### <a name="ParametersViewsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--view-name**|string|View name|view_name|viewName|

#### <a name="ViewsCreateOrUpdateByScope">Command `az costmanagement view create`</a>

##### <a name="ExamplesViewsCreateOrUpdateByScope">Example</a>
```
az costmanagement view create --e-tag "\\"1d4ff9fe66f1d10\\"" --accumulated "true" --chart "Table" --display-name \
"swagger Example" --kpis type="Forecast" enabled=true id=null --kpis type="Budget" enabled=true \
id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Consumption/budg\
ets/swaggerDemo" --metric "ActualCost" --pivots name="ServiceName" type="Dimension" --pivots name="MeterCategory" \
type="Dimension" --pivots name="swaggerTagKey" type="TagKey" --query-timeframe "MonthToDate" --scope \
"subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG" --name "swaggerExample"
```
##### <a name="ParametersViewsCreateOrUpdateByScope">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|
|**--view-name**|string|View name|view_name|viewName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--display-name**|string|User input name of the view. Required.|display_name|displayName|
|**--view-properties-scope**|string|Cost Management scope to save the view on. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for ExternalBillingAccount scope, and '/providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for ExternalSubscription scope.|view_properties_scope|scope|
|**--chart**|choice|Chart type of the main view in Cost Analysis. Required.|chart|chart|
|**--accumulated**|choice|Show costs accumulated over time.|accumulated|accumulated|
|**--metric**|choice|Metric to use when displaying costs.|metric|metric|
|**--kpis**|array|List of KPIs to show in Cost Analysis UI.|kpis|kpis|
|**--pivots**|array|Configuration of 3 sub-views in the Cost Analysis UI.|pivots|pivots|
|**--query-timeframe**|choice|The time frame for pulling data for the report. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--query-time-period**|object|Has time period for pulling data for the report.|time_period|timePeriod|
|**--dataset-granularity**|choice|The granularity of rows in the report.|granularity|granularity|
|**--dataset-configuration**|object|Has configuration information for the data in the report. The configuration will be ignored if aggregation and grouping are provided.|configuration|configuration|
|**--dataset-aggregation**|dictionary|Dictionary of aggregation expression to use in the report. The key of each item in the dictionary is the alias for the aggregated column. Report can have up to 2 aggregation clauses.|aggregation|aggregation|
|**--dataset-grouping**|array|Array of group by expression to use in the report. Report can have up to 2 group by clauses.|grouping|grouping|
|**--dataset-sorting**|array|Array of order by expression to use in the report.|sorting|sorting|
|**--dataset-filter**|object|Has filter expression to use in the report.|filter|filter|

#### <a name="ViewsCreateOrUpdate#Create">Command `az costmanagement view create`</a>

##### <a name="ExamplesViewsCreateOrUpdate#Create">Example</a>
```
az costmanagement view create --e-tag "\\"1d4ff9fe66f1d10\\"" --accumulated "true" --chart "Table" --display-name \
"swagger Example" --kpis type="Forecast" enabled=true id=null --kpis type="Budget" enabled=true \
id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG/providers/Microsoft.Consumption/budg\
ets/swaggerDemo" --metric "ActualCost" --pivots name="ServiceName" type="Dimension" --pivots name="MeterCategory" \
type="Dimension" --pivots name="swaggerTagKey" type="TagKey" --query-timeframe "MonthToDate" --name "swaggerExample"
```
##### <a name="ParametersViewsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|Cost Management scope to save the view on. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for ExternalBillingAccount scope, and '/providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for ExternalSubscription scope.|scope|scope|

#### <a name="ViewsCreateOrUpdate#Update">Command `az costmanagement view update`</a>

##### <a name="ParametersViewsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--view-name**|string|View name|view_name|viewName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--display-name**|string|User input name of the view. Required.|display_name|displayName|
|**--scope**|string|Cost Management scope to save the view on. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for ExternalBillingAccount scope, and '/providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for ExternalSubscription scope.|scope|scope|
|**--chart**|choice|Chart type of the main view in Cost Analysis. Required.|chart|chart|
|**--accumulated**|choice|Show costs accumulated over time.|accumulated|accumulated|
|**--metric**|choice|Metric to use when displaying costs.|metric|metric|
|**--kpis**|array|List of KPIs to show in Cost Analysis UI.|kpis|kpis|
|**--pivots**|array|Configuration of 3 sub-views in the Cost Analysis UI.|pivots|pivots|
|**--query-timeframe**|choice|The time frame for pulling data for the report. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--query-time-period**|object|Has time period for pulling data for the report.|time_period|timePeriod|
|**--dataset-granularity**|choice|The granularity of rows in the report.|granularity|granularity|
|**--dataset-configuration**|object|Has configuration information for the data in the report. The configuration will be ignored if aggregation and grouping are provided.|configuration|configuration|
|**--dataset-aggregation**|dictionary|Dictionary of aggregation expression to use in the report. The key of each item in the dictionary is the alias for the aggregated column. Report can have up to 2 aggregation clauses.|aggregation|aggregation|
|**--dataset-grouping**|array|Array of group by expression to use in the report. Report can have up to 2 group by clauses.|grouping|grouping|
|**--dataset-sorting**|array|Array of order by expression to use in the report.|sorting|sorting|
|**--dataset-filter**|object|Has filter expression to use in the report.|filter|filter|

#### <a name="ViewsDeleteByScope">Command `az costmanagement view delete`</a>

##### <a name="ExamplesViewsDeleteByScope">Example</a>
```
az costmanagement view delete --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTESTRG" \
--name "TestView"
```
##### <a name="ParametersViewsDeleteByScope">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|
|**--view-name**|string|View name|view_name|viewName|

#### <a name="ViewsDelete">Command `az costmanagement view delete`</a>

##### <a name="ExamplesViewsDelete">Example</a>
```
az costmanagement view delete --name "TestView"
```
##### <a name="ParametersViewsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ViewsGetByScope">Command `az costmanagement view get-by-scope`</a>

##### <a name="ExamplesViewsGetByScope">Example</a>
```
az costmanagement view get-by-scope --scope "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MYDEVTES\
TRG" --name "swaggerExample"
```
##### <a name="ParametersViewsGetByScope">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|
|**--view-name**|string|View name|view_name|viewName|
