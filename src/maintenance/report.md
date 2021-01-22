# Azure CLI Module Creation Report

### maintenance applyupdate create

create a maintenance applyupdate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance applyupdate|ApplyUpdates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdateParent|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

### maintenance applyupdate get-parent

get-parent a maintenance applyupdate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance applyupdate|ApplyUpdates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-parent|GetParent|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--apply-update-name**|string|applyUpdate Id|apply_update_name|applyUpdateName|

### maintenance applyupdate show

show a maintenance applyupdate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance applyupdate|ApplyUpdates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--apply-update-name**|string|applyUpdate Id|apply_update_name|applyUpdateName|

### maintenance applyupdate update

update a maintenance applyupdate.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance applyupdate|ApplyUpdates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

### maintenance assignment create

create a maintenance assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance assignment|ConfigurationAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdateParent|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Configuration assignment name|configuration_assignment_name|configurationAssignmentName|
|**--location**|string|Location of the resource|location|location|
|**--maintenance-configuration-id**|string|The maintenance configuration Id|maintenance_configuration_id|maintenanceConfigurationId|
|**--resource-id**|string|The unique resourceId|resource_id|resourceId|

### maintenance assignment delete

delete a maintenance assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance assignment|ConfigurationAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|DeleteParent|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Unique configuration assignment name|configuration_assignment_name|configurationAssignmentName|

### maintenance assignment list

list a maintenance assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance assignment|ConfigurationAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

### maintenance assignment list-parent

list-parent a maintenance assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance assignment|ConfigurationAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-parent|ListParent|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

### maintenance assignment update

update a maintenance assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance assignment|ConfigurationAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Configuration assignment name|configuration_assignment_name|configurationAssignmentName|
|**--location**|string|Location of the resource|location|location|
|**--maintenance-configuration-id**|string|The maintenance configuration Id|maintenance_configuration_id|maintenanceConfigurationId|
|**--resource-id**|string|The unique resourceId|resource_id|resourceId|

### maintenance configuration create

create a maintenance configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance configuration|MaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Resource Identifier|resource_name|resourceName|
|**--location**|string|Gets or sets location of the resource|location|location|
|**--tags**|dictionary|Gets or sets tags of the resource|tags|tags|
|**--namespace**|string|Gets or sets namespace of the resource|namespace|namespace|
|**--extension-properties**|dictionary|Gets or sets extensionProperties of the maintenanceConfiguration|extension_properties|extensionProperties|
|**--maintenance-scope**|choice|Gets or sets maintenanceScope of the configuration|maintenance_scope|maintenanceScope|
|**--visibility**|choice|Gets or sets the visibility of the configuration|visibility|visibility|
|**--maintenance-window-start-date-time**|string|Effective start date of the maintenance window in YYYY-MM-DD hh:mm format. The start date can be set to either the current date or future date. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone.|start_date_time|startDateTime|
|**--maintenance-window-expiration-date-time**|string|Effective expiration date of the maintenance window in YYYY-MM-DD hh:mm format. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone. Expiration date must be set to a future date. If not provided, it will be set to the maximum datetime 9999-12-31 23:59:59.|expiration_date_time|expirationDateTime|
|**--maintenance-window-duration**|string|Duration of the maintenance window in HH:mm format. If not provided, default value will be used based on maintenance scope provided. Example: 05:00.|duration|duration|
|**--maintenance-window-time-zone**|string|Name of the timezone. List of timezones can be obtained by executing [System.TimeZoneInfo]::GetSystemTimeZones() in PowerShell. Example: Pacific Standard Time, UTC, W. Europe Standard Time, Korea Standard Time, Cen. Australia Standard Time.|time_zone|timeZone|
|**--maintenance-window-recur-every**|string|Rate at which a Maintenance window is expected to recur. The rate can be expressed as daily, weekly, or monthly schedules. Daily schedule are formatted as recurEvery: [Frequency as integer]['Day(s)']. If no frequency is provided, the default frequency is 1. Daily schedule examples are recurEvery: Day, recurEvery: 3Days.  Weekly schedule are formatted as recurEvery: [Frequency as integer]['Week(s)'] [Optional comma separated list of weekdays Monday-Sunday]. Weekly schedule examples are recurEvery: 3Weeks, recurEvery: Week Saturday,Sunday. Monthly schedules are formatted as [Frequency as integer]['Month(s)'] [Comma separated list of month days] or [Frequency as integer]['Month(s)'] [Week of Month (First, Second, Third, Fourth, Last)] [Weekday Monday-Sunday]. Monthly schedule examples are recurEvery: Month, recurEvery: 2Months, recurEvery: Month day23,day24, recurEvery: Month Last Sunday, recurEvery: Month Fourth Monday.|recur_every|recurEvery|

### maintenance configuration delete

delete a maintenance configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance configuration|MaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Resource Identifier|resource_name|resourceName|

### maintenance configuration list

list a maintenance configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance configuration|MaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### maintenance configuration show

show a maintenance configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance configuration|MaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Resource Identifier|resource_name|resourceName|

### maintenance configuration update

update a maintenance configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance configuration|MaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Resource Identifier|resource_name|resourceName|
|**--location**|string|Gets or sets location of the resource|location|location|
|**--tags**|dictionary|Gets or sets tags of the resource|tags|tags|
|**--namespace**|string|Gets or sets namespace of the resource|namespace|namespace|
|**--extension-properties**|dictionary|Gets or sets extensionProperties of the maintenanceConfiguration|extension_properties|extensionProperties|
|**--maintenance-scope**|choice|Gets or sets maintenanceScope of the configuration|maintenance_scope|maintenanceScope|
|**--visibility**|choice|Gets or sets the visibility of the configuration|visibility|visibility|
|**--maintenance-window-start-date-time**|string|Effective start date of the maintenance window in YYYY-MM-DD hh:mm format. The start date can be set to either the current date or future date. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone.|start_date_time|startDateTime|
|**--maintenance-window-expiration-date-time**|string|Effective expiration date of the maintenance window in YYYY-MM-DD hh:mm format. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone. Expiration date must be set to a future date. If not provided, it will be set to the maximum datetime 9999-12-31 23:59:59.|expiration_date_time|expirationDateTime|
|**--maintenance-window-duration**|string|Duration of the maintenance window in HH:mm format. If not provided, default value will be used based on maintenance scope provided. Example: 05:00.|duration|duration|
|**--maintenance-window-time-zone**|string|Name of the timezone. List of timezones can be obtained by executing [System.TimeZoneInfo]::GetSystemTimeZones() in PowerShell. Example: Pacific Standard Time, UTC, W. Europe Standard Time, Korea Standard Time, Cen. Australia Standard Time.|time_zone|timeZone|
|**--maintenance-window-recur-every**|string|Rate at which a Maintenance window is expected to recur. The rate can be expressed as daily, weekly, or monthly schedules. Daily schedule are formatted as recurEvery: [Frequency as integer]['Day(s)']. If no frequency is provided, the default frequency is 1. Daily schedule examples are recurEvery: Day, recurEvery: 3Days.  Weekly schedule are formatted as recurEvery: [Frequency as integer]['Week(s)'] [Optional comma separated list of weekdays Monday-Sunday]. Weekly schedule examples are recurEvery: 3Weeks, recurEvery: Week Saturday,Sunday. Monthly schedules are formatted as [Frequency as integer]['Month(s)'] [Comma separated list of month days] or [Frequency as integer]['Month(s)'] [Week of Month (First, Second, Third, Fourth, Last)] [Weekday Monday-Sunday]. Monthly schedule examples are recurEvery: Month, recurEvery: 2Months, recurEvery: Month day23,day24, recurEvery: Month Last Sunday, recurEvery: Month Fourth Monday.|recur_every|recurEvery|

### maintenance public-configuration list

list a maintenance public-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance public-configuration|PublicMaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### maintenance public-configuration show

show a maintenance public-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance public-configuration|PublicMaintenanceConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Resource Identifier|resource_name|resourceName|

### maintenance update list

list a maintenance update.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance update|Updates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

### maintenance update list-parent

list-parent a maintenance update.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|maintenance update|Updates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-parent|ListParent|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
