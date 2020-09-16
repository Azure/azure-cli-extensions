# Azure CLI Module Creation Report

### costmanagement alert dismiss

dismiss a costmanagement alert.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement alert|Alerts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|dismiss|Dismiss|

#### Parameters
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

### costmanagement alert list

list a costmanagement alert.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement alert|Alerts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with alerts operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|

### costmanagement alert list-external

list-external a costmanagement alert.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement alert|Alerts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-external|ListExternal|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--external-cloud-provider-type**|choice|The external cloud provider type associated with dimension/query operations. This includes 'externalSubscriptions' for linked account and 'externalBillingAccounts' for consolidated account.|external_cloud_provider_type|externalCloudProviderType|
|**--external-cloud-provider-id**|string|This can be '{externalSubscriptionId}' for linked account or '{externalBillingAccountId}' for consolidated account used with dimension/query operations.|external_cloud_provider_id|externalCloudProviderId|

### costmanagement alert show

show a costmanagement alert.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement alert|Alerts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with alerts operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--alert-id**|string|Alert ID|alert_id|alertId|

### costmanagement dimension by-external-cloud-provider-type

by-external-cloud-provider-type a costmanagement dimension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement dimension|Dimensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|by-external-cloud-provider-type|ByExternalCloudProviderType|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--external-cloud-provider-type**|choice|The external cloud provider type associated with dimension/query operations. This includes 'externalSubscriptions' for linked account and 'externalBillingAccounts' for consolidated account.|external_cloud_provider_type|externalCloudProviderType|
|**--external-cloud-provider-id**|string|This can be '{externalSubscriptionId}' for linked account or '{externalBillingAccountId}' for consolidated account used with dimension/query operations.|external_cloud_provider_id|externalCloudProviderId|
|**--filter**|string|May be used to filter dimensions by properties/category, properties/usageStart, properties/usageEnd. Supported operators are 'eq','lt', 'gt', 'le', 'ge'.|filter|$filter|
|**--expand**|string|May be used to expand the properties/data within a dimension category. By default, data is not included when listing dimensions.|expand|$expand|
|**--skiptoken**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|
|**--top**|integer|May be used to limit the number of results to the most recent N dimension data.|top|$top|

### costmanagement dimension list

list a costmanagement dimension.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement dimension|Dimensions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with dimension operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--filter**|string|May be used to filter dimensions by properties/category, properties/usageStart, properties/usageEnd. Supported operators are 'eq','lt', 'gt', 'le', 'ge'.|filter|$filter|
|**--expand**|string|May be used to expand the properties/data within a dimension category. By default, data is not included when listing dimensions.|expand|$expand|
|**--skiptoken**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls.|skiptoken|$skiptoken|
|**--top**|integer|May be used to limit the number of results to the most recent N dimension data.|top|$top|

### costmanagement export create

create a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--definition-type**|choice|The type of the export. Note that 'Usage' is equivalent to 'ActualCost' and is applicable to exports that do not yet provide data for charges or amortization for service reservations.|type|type|
|**--definition-timeframe**|choice|The time frame for pulling data for the export. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--definition-time-period**|object|Has time period for pulling data for the export.|time_period|timePeriod|
|**--definition-data-set-configuration**|object|The export dataset configuration.|configuration|configuration|
|**--delivery-info-destination**|object|Has destination for the export being delivered.|destination|destination|
|**--schedule-status**|choice|The status of the export's schedule. If 'Inactive', the export's schedule is paused.|status|status|
|**--schedule-recurrence**|choice|The schedule recurrence.|recurrence|recurrence|
|**--schedule-recurrence-period**|object|Has start and end date of the recurrence. The start date must be in future. If present, the end date must be greater than start date.|recurrence_period|recurrencePeriod|

### costmanagement export delete

delete a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|

### costmanagement export execute

execute a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|execute|Execute|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|

### costmanagement export get-execution-history

get-execution-history a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-execution-history|GetExecutionHistory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|

### costmanagement export list

list a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--expand**|string|May be used to expand the properties within an export. Currently only 'runHistory' is supported and will return information for the last execution of each export.|expand|$expand|

### costmanagement export show

show a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|
|**--expand**|string|May be used to expand the properties within an export. Currently only 'runHistory' is supported and will return information for the last 10 executions of the export.|expand|$expand|

### costmanagement export update

update a costmanagement export.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement export|Exports|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with query and export operations. This includes '/subscriptions/{subscriptionId}/' for subscription scope, '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, '/providers/Microsoft.Management/managementGroups/{managementGroupId} for Management Group scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for billingProfile scope, '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}/invoiceSections/{invoiceSectionId}' for invoiceSection scope, and '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}/customers/{customerId}' specific for partners.|scope|scope|
|**--export-name**|string|Export Name.|export_name|exportName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--definition-type**|choice|The type of the export. Note that 'Usage' is equivalent to 'ActualCost' and is applicable to exports that do not yet provide data for charges or amortization for service reservations.|type|type|
|**--definition-timeframe**|choice|The time frame for pulling data for the export. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--definition-time-period**|object|Has time period for pulling data for the export.|time_period|timePeriod|
|**--definition-data-set-configuration**|object|The export dataset configuration.|configuration|configuration|
|**--delivery-info-destination**|object|Has destination for the export being delivered.|destination|destination|
|**--schedule-status**|choice|The status of the export's schedule. If 'Inactive', the export's schedule is paused.|status|status|
|**--schedule-recurrence**|choice|The schedule recurrence.|recurrence|recurrence|
|**--schedule-recurrence-period**|object|Has start and end date of the recurrence. The start date must be in future. If present, the end date must be greater than start date.|recurrence_period|recurrencePeriod|

### costmanagement forecast external-cloud-provider-usage

external-cloud-provider-usage a costmanagement forecast.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement forecast|Forecast|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|external-cloud-provider-usage|ExternalCloudProviderUsage|

#### Parameters
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
|**--dataset-filter**|object|Has filter expression to use in the forecast.|query_filter|filter|

### costmanagement forecast usage

usage a costmanagement forecast.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement forecast|Forecast|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|usage|Usage|

#### Parameters
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
|**--dataset-filter**|object|Has filter expression to use in the forecast.|query_filter|filter|

### costmanagement query usage

usage a costmanagement query.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement query|Query|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|usage|Usage|

#### Parameters
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

### costmanagement query usage-by-external-cloud-provider-type

usage-by-external-cloud-provider-type a costmanagement query.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement query|Query|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|usage-by-external-cloud-provider-type|UsageByExternalCloudProviderType|

#### Parameters
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

### costmanagement view create

create a costmanagement view.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement view|Views|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdateByScope|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|
|**--view-name**|string|View name|view_name|viewName|
|**--e-tag**|string|eTag of the resource. To handle concurrent update scenario, this field will be used to determine whether the user is updating the latest version or not.|e_tag|eTag|
|**--display-name**|string|User input name of the view. Required.|display_name|displayName|
|**--properties-scope**|string|Cost Management scope to save the view on. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for ExternalBillingAccount scope, and '/providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for ExternalSubscription scope.|view_properties_scope|scope|
|**--chart**|choice|Chart type of the main view in Cost Analysis. Required.|chart|chart|
|**--accumulated**|choice|Show costs accumulated over time.|accumulated|accumulated|
|**--metric**|choice|Metric to use when displaying costs.|metric|metric|
|**--kpis**|array|List of KPIs to show in Cost Analysis UI.|kpis|kpis|
|**--pivots**|array|Configuration of 3 sub-views in the Cost Analysis UI.|pivots|pivots|
|**--query-timeframe**|choice|The time frame for pulling data for the report. If custom, then a specific time period must be provided.|timeframe|timeframe|
|**--query-time-period**|object|Has time period for pulling data for the report.|time_period|timePeriod|
|**--query-dataset**|object|Has definition for data in this report config.|dataset|dataset|
|**--scope**|string|Cost Management scope to save the view on. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, '/providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for ExternalBillingAccount scope, and '/providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for ExternalSubscription scope.|scope|scope|

### costmanagement view delete

delete a costmanagement view.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement view|Views|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|DeleteByScope|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|
|**--view-name**|string|View name|view_name|viewName|

### costmanagement view get-by-scope

get-by-scope a costmanagement view.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement view|Views|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-by-scope|GetByScope|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|
|**--view-name**|string|View name|view_name|viewName|

### costmanagement view list

list a costmanagement view.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement view|Views|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByScope|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope**|string|The scope associated with view operations. This includes 'subscriptions/{subscriptionId}' for subscription scope, 'subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}' for resourceGroup scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for Billing Account scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/departments/{departmentId}' for Department scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/enrollmentAccounts/{enrollmentAccountId}' for EnrollmentAccount scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/billingProfiles/{billingProfileId}' for BillingProfile scope, 'providers/Microsoft.Billing/billingAccounts/{billingAccountId}/invoiceSections/{invoiceSectionId}' for InvoiceSection scope, 'providers/Microsoft.Management/managementGroups/{managementGroupId}' for Management Group scope, 'providers/Microsoft.CostManagement/externalBillingAccounts/{externalBillingAccountName}' for External Billing Account scope and 'providers/Microsoft.CostManagement/externalSubscriptions/{externalSubscriptionName}' for External Subscription scope.|scope|scope|

### costmanagement view show

show a costmanagement view.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement view|Views|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--view-name**|string|View name|view_name|viewName|

### costmanagement view update

update a costmanagement view.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|costmanagement view|Views|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
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
|**--query-dataset**|object|Has definition for data in this report config.|dataset|dataset|
