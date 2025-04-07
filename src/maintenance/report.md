# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az maintenance|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az maintenance` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az maintenance applyupdate|ApplyUpdates|[commands](#CommandsInApplyUpdates)|
|az maintenance assignment|ConfigurationAssignments|[commands](#CommandsInConfigurationAssignments)|
|az maintenance configuration|MaintenanceConfigurations|[commands](#CommandsInMaintenanceConfigurations)|
|az maintenance public-configuration|PublicMaintenanceConfigurations|[commands](#CommandsInPublicMaintenanceConfigurations)|
|az maintenance update|Updates|[commands](#CommandsInUpdates)|

## COMMANDS
### <a name="CommandsInApplyUpdates">Commands in `az maintenance applyupdate` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az maintenance applyupdate list](#ApplyUpdatesList)|List|[Parameters](#ParametersApplyUpdatesList)|[Example](#ExamplesApplyUpdatesList)|
|[az maintenance applyupdate show](#ApplyUpdatesGet)|Get|[Parameters](#ParametersApplyUpdatesGet)|[Example](#ExamplesApplyUpdatesGet)|
|[az maintenance applyupdate create](#ApplyUpdatesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersApplyUpdatesCreateOrUpdate#Create)|[Example](#ExamplesApplyUpdatesCreateOrUpdate#Create)|
|[az maintenance applyupdate create-or-update-parent](#ApplyUpdatesCreateOrUpdateParent)|CreateOrUpdateParent|[Parameters](#ParametersApplyUpdatesCreateOrUpdateParent)|[Example](#ExamplesApplyUpdatesCreateOrUpdateParent)|
|[az maintenance applyupdate show-parent](#ApplyUpdatesGetParent)|GetParent|[Parameters](#ParametersApplyUpdatesGetParent)|[Example](#ExamplesApplyUpdatesGetParent)|

### <a name="CommandsInConfigurationAssignments">Commands in `az maintenance assignment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az maintenance assignment list](#ConfigurationAssignmentsList)|List|[Parameters](#ParametersConfigurationAssignmentsList)|[Example](#ExamplesConfigurationAssignmentsList)|
|[az maintenance assignment show](#ConfigurationAssignmentsGet)|Get|[Parameters](#ParametersConfigurationAssignmentsGet)|[Example](#ExamplesConfigurationAssignmentsGet)|
|[az maintenance assignment create](#ConfigurationAssignmentsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersConfigurationAssignmentsCreateOrUpdate#Create)|[Example](#ExamplesConfigurationAssignmentsCreateOrUpdate#Create)|
|[az maintenance assignment update](#ConfigurationAssignmentsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersConfigurationAssignmentsCreateOrUpdate#Update)|Not Found|
|[az maintenance assignment delete](#ConfigurationAssignmentsDelete)|Delete|[Parameters](#ParametersConfigurationAssignmentsDelete)|[Example](#ExamplesConfigurationAssignmentsDelete)|
|[az maintenance assignment create-or-update-parent](#ConfigurationAssignmentsCreateOrUpdateParent)|CreateOrUpdateParent|[Parameters](#ParametersConfigurationAssignmentsCreateOrUpdateParent)|[Example](#ExamplesConfigurationAssignmentsCreateOrUpdateParent)|
|[az maintenance assignment delete-parent](#ConfigurationAssignmentsDeleteParent)|DeleteParent|[Parameters](#ParametersConfigurationAssignmentsDeleteParent)|[Example](#ExamplesConfigurationAssignmentsDeleteParent)|
|[az maintenance assignment list-parent](#ConfigurationAssignmentsListParent)|ListParent|[Parameters](#ParametersConfigurationAssignmentsListParent)|[Example](#ExamplesConfigurationAssignmentsListParent)|
|[az maintenance assignment show-parent](#ConfigurationAssignmentsGetParent)|GetParent|[Parameters](#ParametersConfigurationAssignmentsGetParent)|[Example](#ExamplesConfigurationAssignmentsGetParent)|

### <a name="CommandsInMaintenanceConfigurations">Commands in `az maintenance configuration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az maintenance configuration list](#MaintenanceConfigurationsList)|List|[Parameters](#ParametersMaintenanceConfigurationsList)|[Example](#ExamplesMaintenanceConfigurationsList)|
|[az maintenance configuration show](#MaintenanceConfigurationsGet)|Get|[Parameters](#ParametersMaintenanceConfigurationsGet)|[Example](#ExamplesMaintenanceConfigurationsGet)|
|[az maintenance configuration create](#MaintenanceConfigurationsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMaintenanceConfigurationsCreateOrUpdate#Create)|[Example](#ExamplesMaintenanceConfigurationsCreateOrUpdate#Create)|
|[az maintenance configuration update](#MaintenanceConfigurationsUpdate)|Update|[Parameters](#ParametersMaintenanceConfigurationsUpdate)|[Example](#ExamplesMaintenanceConfigurationsUpdate)|
|[az maintenance configuration delete](#MaintenanceConfigurationsDelete)|Delete|[Parameters](#ParametersMaintenanceConfigurationsDelete)|[Example](#ExamplesMaintenanceConfigurationsDelete)|

### <a name="CommandsInPublicMaintenanceConfigurations">Commands in `az maintenance public-configuration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az maintenance public-configuration list](#PublicMaintenanceConfigurationsList)|List|[Parameters](#ParametersPublicMaintenanceConfigurationsList)|[Example](#ExamplesPublicMaintenanceConfigurationsList)|
|[az maintenance public-configuration show](#PublicMaintenanceConfigurationsGet)|Get|[Parameters](#ParametersPublicMaintenanceConfigurationsGet)|[Example](#ExamplesPublicMaintenanceConfigurationsGet)|

### <a name="CommandsInUpdates">Commands in `az maintenance update` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az maintenance update list](#UpdatesList)|List|[Parameters](#ParametersUpdatesList)|[Example](#ExamplesUpdatesList)|
|[az maintenance update list-parent](#UpdatesListParent)|ListParent|[Parameters](#ParametersUpdatesListParent)|[Example](#ExamplesUpdatesListParent)|


## COMMAND DETAILS
### group `az maintenance applyupdate`
#### <a name="ApplyUpdatesList">Command `az maintenance applyupdate list`</a>

##### <a name="ExamplesApplyUpdatesList">Example</a>
```
az maintenance applyupdate list
```
##### <a name="ParametersApplyUpdatesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="ApplyUpdatesGet">Command `az maintenance applyupdate show`</a>

##### <a name="ExamplesApplyUpdatesGet">Example</a>
```
az maintenance applyupdate show --name "e9b9685d-78e4-44c4-a81c-64a14f9b87b6" --provider-name "Microsoft.Compute" \
--resource-group "examplerg" --resource-name "smdtest1" --resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersApplyUpdatesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--apply-update-name**|string|applyUpdate Id|apply_update_name|applyUpdateName|

#### <a name="ApplyUpdatesCreateOrUpdate#Create">Command `az maintenance applyupdate create`</a>

##### <a name="ExamplesApplyUpdatesCreateOrUpdate#Create">Example</a>
```
az maintenance applyupdate create --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name \
"smdtest1" --resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersApplyUpdatesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

#### <a name="ApplyUpdatesCreateOrUpdateParent">Command `az maintenance applyupdate create-or-update-parent`</a>

##### <a name="ExamplesApplyUpdatesCreateOrUpdateParent">Example</a>
```
az maintenance applyupdate create-or-update-parent --provider-name "Microsoft.Compute" --resource-group "examplerg" \
--resource-name "smdvm1" --resource-parent-name "smdtest1" --resource-parent-type "virtualMachineScaleSets" \
--resource-type "virtualMachines"
```
##### <a name="ParametersApplyUpdatesCreateOrUpdateParent">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

#### <a name="ApplyUpdatesGetParent">Command `az maintenance applyupdate show-parent`</a>

##### <a name="ExamplesApplyUpdatesGetParent">Example</a>
```
az maintenance applyupdate show-parent --name "e9b9685d-78e4-44c4-a81c-64a14f9b87b6" --provider-name \
"Microsoft.Compute" --resource-group "examplerg" --resource-name "smdvm1" --resource-parent-name "smdtest1" \
--resource-parent-type "virtualMachineScaleSets" --resource-type "virtualMachines"
```
##### <a name="ParametersApplyUpdatesGetParent">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--apply-update-name**|string|applyUpdate Id|apply_update_name|applyUpdateName|

### group `az maintenance assignment`
#### <a name="ConfigurationAssignmentsList">Command `az maintenance assignment list`</a>

##### <a name="ExamplesConfigurationAssignmentsList">Example</a>
```
az maintenance assignment list --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name \
"smdtest1" --resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersConfigurationAssignmentsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

#### <a name="ConfigurationAssignmentsGet">Command `az maintenance assignment show`</a>

##### <a name="ExamplesConfigurationAssignmentsGet">Example</a>
```
az maintenance assignment show --name "workervmConfiguration" --provider-name "Microsoft.Compute" --resource-group \
"examplerg" --resource-name "smdtest1" --resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersConfigurationAssignmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Configuration assignment name|configuration_assignment_name|configurationAssignmentName|

#### <a name="ConfigurationAssignmentsCreateOrUpdate#Create">Command `az maintenance assignment create`</a>

##### <a name="ExamplesConfigurationAssignmentsCreateOrUpdate#Create">Example</a>
```
az maintenance assignment create --maintenance-configuration-id "/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/re\
sourcegroups/examplerg/providers/Microsoft.Maintenance/maintenanceConfigurations/configuration1" --name \
"workervmConfiguration" --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name "smdtest1" \
--resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersConfigurationAssignmentsCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="ConfigurationAssignmentsCreateOrUpdate#Update">Command `az maintenance assignment update`</a>


##### <a name="ParametersConfigurationAssignmentsCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="ConfigurationAssignmentsDelete">Command `az maintenance assignment delete`</a>

##### <a name="ExamplesConfigurationAssignmentsDelete">Example</a>
```
az maintenance assignment delete --name "workervmConfiguration" --provider-name "Microsoft.Compute" --resource-group \
"examplerg" --resource-name "smdtest1" --resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersConfigurationAssignmentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Unique configuration assignment name|configuration_assignment_name|configurationAssignmentName|

#### <a name="ConfigurationAssignmentsCreateOrUpdateParent">Command `az maintenance assignment create-or-update-parent`</a>

##### <a name="ExamplesConfigurationAssignmentsCreateOrUpdateParent">Example</a>
```
az maintenance assignment create-or-update-parent --maintenance-configuration-id "/subscriptions/5b4b650e-28b9-4790-b3a\
b-ddbd88d727c4/resourcegroups/examplerg/providers/Microsoft.Maintenance/maintenanceConfigurations/policy1" --name \
"workervmPolicy" --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name "smdvm1" \
--resource-parent-name "smdtest1" --resource-parent-type "virtualMachineScaleSets" --resource-type "virtualMachines"
```
##### <a name="ParametersConfigurationAssignmentsCreateOrUpdateParent">Parameters</a> 
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

#### <a name="ConfigurationAssignmentsDeleteParent">Command `az maintenance assignment delete-parent`</a>

##### <a name="ExamplesConfigurationAssignmentsDeleteParent">Example</a>
```
az maintenance assignment delete-parent --name "workervmConfiguration" --provider-name "Microsoft.Compute" \
--resource-group "examplerg" --resource-name "smdvm1" --resource-parent-name "smdtest1" --resource-parent-type \
"virtualMachineScaleSets" --resource-type "virtualMachines"
```
##### <a name="ParametersConfigurationAssignmentsDeleteParent">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Unique configuration assignment name|configuration_assignment_name|configurationAssignmentName|

#### <a name="ConfigurationAssignmentsListParent">Command `az maintenance assignment list-parent`</a>

##### <a name="ExamplesConfigurationAssignmentsListParent">Example</a>
```
az maintenance assignment list-parent --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name \
"smdtestvm1" --resource-parent-name "smdtest1" --resource-parent-type "virtualMachineScaleSets" --resource-type \
"virtualMachines"
```
##### <a name="ParametersConfigurationAssignmentsListParent">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

#### <a name="ConfigurationAssignmentsGetParent">Command `az maintenance assignment show-parent`</a>

##### <a name="ExamplesConfigurationAssignmentsGetParent">Example</a>
```
az maintenance assignment show-parent --name "workervmPolicy" --provider-name "Microsoft.Compute" --resource-group \
"examplerg" --resource-name "smdvm1" --resource-parent-name "smdtest1" --resource-parent-type \
"virtualMachineScaleSets" --resource-type "virtualMachines"
```
##### <a name="ParametersConfigurationAssignmentsGetParent">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
|**--configuration-assignment-name**|string|Configuration assignment name|configuration_assignment_name|configurationAssignmentName|

### group `az maintenance configuration`
#### <a name="MaintenanceConfigurationsList">Command `az maintenance configuration list`</a>

##### <a name="ExamplesMaintenanceConfigurationsList">Example</a>
```
az maintenance configuration list
```
##### <a name="ParametersMaintenanceConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="MaintenanceConfigurationsGet">Command `az maintenance configuration show`</a>

##### <a name="ExamplesMaintenanceConfigurationsGet">Example</a>
```
az maintenance configuration show --resource-group "examplerg" --resource-name "configuration1"
az maintenance configuration show --resource-group "examplerg" --resource-name "configuration1"
az maintenance configuration show --resource-group "examplerg" --resource-name "configuration1"
```
##### <a name="ParametersMaintenanceConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Maintenance Configuration Name|resource_name|resourceName|

#### <a name="MaintenanceConfigurationsCreateOrUpdate#Create">Command `az maintenance configuration create`</a>

##### <a name="ExamplesMaintenanceConfigurationsCreateOrUpdate#Create">Example</a>
```
az maintenance configuration create --location "westus2" --maintenance-scope "OSImage" --maintenance-window-duration \
"05:00" --maintenance-window-expiration-date-time "9999-12-31 00:00" --maintenance-window-recur-every "Day" \
--maintenance-window-start-date-time "2020-04-30 08:00" --maintenance-window-time-zone "Pacific Standard Time" \
--namespace "Microsoft.Maintenance" --visibility "Custom" --resource-group "examplerg" --resource-name \
"configuration1"
```
##### <a name="ParametersMaintenanceConfigurationsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Maintenance Configuration Name|resource_name|resourceName|
|**--location**|string|Gets or sets location of the resource|location|location|
|**--tags**|dictionary|Gets or sets tags of the resource|tags|tags|
|**--namespace**|string|Gets or sets namespace of the resource|namespace|namespace|
|**--extension-properties**|dictionary|Gets or sets extensionProperties of the maintenanceConfiguration|extension_properties|extensionProperties|
|**--maintenance-scope**|choice|Gets or sets maintenanceScope of the configuration|maintenance_scope|maintenanceScope|
|**--visibility**|choice|Gets or sets the visibility of the configuration. The default value is 'Custom'|visibility|visibility|
|**--start-date-time**|string|Effective start date of the maintenance window in YYYY-MM-DD hh:mm format. The start date can be set to either the current date or future date. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone.|start_date_time|startDateTime|
|**--expiration-date-time**|string|Effective expiration date of the maintenance window in YYYY-MM-DD hh:mm format. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone. Expiration date must be set to a future date. If not provided, it will be set to the maximum datetime 9999-12-31 23:59:59.|expiration_date_time|expirationDateTime|
|**--duration**|string|Duration of the maintenance window in HH:mm format. If not provided, default value will be used based on maintenance scope provided. Example: 05:00.|duration|duration|
|**--time-zone**|string|Name of the timezone. List of timezones can be obtained by executing [System.TimeZoneInfo]::GetSystemTimeZones() in PowerShell. Example: Pacific Standard Time, UTC, W. Europe Standard Time, Korea Standard Time, Cen. Australia Standard Time.|time_zone|timeZone|
|**--recur-every**|string|Rate at which a Maintenance window is expected to recur. The rate can be expressed as daily, weekly, or monthly schedules. Daily schedule are formatted as recurEvery: [Frequency as integer]['Day(s)']. If no frequency is provided, the default frequency is 1. Daily schedule examples are recurEvery: Day, recurEvery: 3Days.  Weekly schedule are formatted as recurEvery: [Frequency as integer]['Week(s)'] [Optional comma separated list of weekdays Monday-Sunday]. Weekly schedule examples are recurEvery: 3Weeks, recurEvery: Week Saturday,Sunday. Monthly schedules are formatted as [Frequency as integer]['Month(s)'] [Comma separated list of month days] or [Frequency as integer]['Month(s)'] [Week of Month (First, Second, Third, Fourth, Last)] [Weekday Monday-Sunday] [Optional Offset(No. of days)]. Offset value must be between -6 to 6 inclusive. Monthly schedule examples are recurEvery: Month, recurEvery: 2Months, recurEvery: Month day23,day24, recurEvery: Month Last Sunday, recurEvery: Month Fourth Monday, recurEvery: Month Last Sunday Offset-3, recurEvery: Month Third Sunday Offset6.|recur_every|recurEvery|
|**--reboot-setting**|choice|Possible reboot preference as defined by the user based on which it would be decided to reboot the machine or not after the patch operation is completed.|reboot_setting|rebootSetting|
|**--windows-parameters**|object|Input parameters specific to patching a Windows machine. For Linux machines, do not pass this property.|windows_parameters|windowsParameters|
|**--linux-parameters**|object|Input parameters specific to patching Linux machine. For Windows machines, do not pass this property.|linux_parameters|linuxParameters|
|**--pre-tasks**|array|List of pre tasks. e.g. [{'source' :'runbook', 'taskScope': 'Global', 'parameters': { 'arg1': 'value1'}}]|pre_tasks|preTasks|
|**--post-tasks**|array|List of post tasks. e.g. [{'source' :'runbook', 'taskScope': 'Resource', 'parameters': { 'arg1': 'value1'}}]|post_tasks|postTasks|

#### <a name="MaintenanceConfigurationsUpdate">Command `az maintenance configuration update`</a>

##### <a name="ExamplesMaintenanceConfigurationsUpdate">Example</a>
```
az maintenance configuration update --location "westus2" --maintenance-scope "OSImage" --maintenance-window-duration \
"05:00" --maintenance-window-expiration-date-time "9999-12-31 00:00" --maintenance-window-recur-every "Month Third \
Sunday" --maintenance-window-start-date-time "2020-04-30 08:00" --maintenance-window-time-zone "Pacific Standard Time" \
--namespace "Microsoft.Maintenance" --visibility "Custom" --resource-group "examplerg" --resource-name \
"configuration1"
```
##### <a name="ParametersMaintenanceConfigurationsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Maintenance Configuration Name|resource_name|resourceName|
|**--location**|string|Gets or sets location of the resource|location|location|
|**--tags**|dictionary|Gets or sets tags of the resource|tags|tags|
|**--namespace**|string|Gets or sets namespace of the resource|namespace|namespace|
|**--extension-properties**|dictionary|Gets or sets extensionProperties of the maintenanceConfiguration|extension_properties|extensionProperties|
|**--maintenance-scope**|choice|Gets or sets maintenanceScope of the configuration|maintenance_scope|maintenanceScope|
|**--visibility**|choice|Gets or sets the visibility of the configuration. The default value is 'Custom'|visibility|visibility|
|**--start-date-time**|string|Effective start date of the maintenance window in YYYY-MM-DD hh:mm format. The start date can be set to either the current date or future date. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone.|start_date_time|startDateTime|
|**--expiration-date-time**|string|Effective expiration date of the maintenance window in YYYY-MM-DD hh:mm format. The window will be created in the time zone provided and adjusted to daylight savings according to that time zone. Expiration date must be set to a future date. If not provided, it will be set to the maximum datetime 9999-12-31 23:59:59.|expiration_date_time|expirationDateTime|
|**--duration**|string|Duration of the maintenance window in HH:mm format. If not provided, default value will be used based on maintenance scope provided. Example: 05:00.|duration|duration|
|**--time-zone**|string|Name of the timezone. List of timezones can be obtained by executing [System.TimeZoneInfo]::GetSystemTimeZones() in PowerShell. Example: Pacific Standard Time, UTC, W. Europe Standard Time, Korea Standard Time, Cen. Australia Standard Time.|time_zone|timeZone|
|**--recur-every**|string|Rate at which a Maintenance window is expected to recur. The rate can be expressed as daily, weekly, or monthly schedules. Daily schedule are formatted as recurEvery: [Frequency as integer]['Day(s)']. If no frequency is provided, the default frequency is 1. Daily schedule examples are recurEvery: Day, recurEvery: 3Days.  Weekly schedule are formatted as recurEvery: [Frequency as integer]['Week(s)'] [Optional comma separated list of weekdays Monday-Sunday]. Weekly schedule examples are recurEvery: 3Weeks, recurEvery: Week Saturday,Sunday. Monthly schedules are formatted as [Frequency as integer]['Month(s)'] [Comma separated list of month days] or [Frequency as integer]['Month(s)'] [Week of Month (First, Second, Third, Fourth, Last)] [Weekday Monday-Sunday] [Optional Offset(No. of days)]. Offset value must be between -6 to 6 inclusive. Monthly schedule examples are recurEvery: Month, recurEvery: 2Months, recurEvery: Month day23,day24, recurEvery: Month Last Sunday, recurEvery: Month Fourth Monday, recurEvery: Month Last Sunday Offset-3, recurEvery: Month Third Sunday Offset6.|recur_every|recurEvery|
|**--reboot-setting**|choice|Possible reboot preference as defined by the user based on which it would be decided to reboot the machine or not after the patch operation is completed.|reboot_setting|rebootSetting|
|**--windows-parameters**|object|Input parameters specific to patching a Windows machine. For Linux machines, do not pass this property.|windows_parameters|windowsParameters|
|**--linux-parameters**|object|Input parameters specific to patching Linux machine. For Windows machines, do not pass this property.|linux_parameters|linuxParameters|
|**--pre-tasks**|array|List of pre tasks. e.g. [{'source' :'runbook', 'taskScope': 'Global', 'parameters': { 'arg1': 'value1'}}]|pre_tasks|preTasks|
|**--post-tasks**|array|List of post tasks. e.g. [{'source' :'runbook', 'taskScope': 'Resource', 'parameters': { 'arg1': 'value1'}}]|post_tasks|postTasks|

#### <a name="MaintenanceConfigurationsDelete">Command `az maintenance configuration delete`</a>

##### <a name="ExamplesMaintenanceConfigurationsDelete">Example</a>
```
az maintenance configuration delete --resource-group "examplerg" --resource-name "example1"
```
##### <a name="ParametersMaintenanceConfigurationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource Group Name|resource_group_name|resourceGroupName|
|**--resource-name**|string|Maintenance Configuration Name|resource_name|resourceName|

### group `az maintenance public-configuration`
#### <a name="PublicMaintenanceConfigurationsList">Command `az maintenance public-configuration list`</a>

##### <a name="ExamplesPublicMaintenanceConfigurationsList">Example</a>
```
az maintenance public-configuration list
```
##### <a name="ParametersPublicMaintenanceConfigurationsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="PublicMaintenanceConfigurationsGet">Command `az maintenance public-configuration show`</a>

##### <a name="ExamplesPublicMaintenanceConfigurationsGet">Example</a>
```
az maintenance public-configuration show --resource-name "configuration1"
```
##### <a name="ParametersPublicMaintenanceConfigurationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-name**|string|Maintenance Configuration Name|resource_name|resourceName|

### group `az maintenance update`
#### <a name="UpdatesList">Command `az maintenance update list`</a>

##### <a name="ExamplesUpdatesList">Example</a>
```
az maintenance update list --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name "smdtest1" \
--resource-type "virtualMachineScaleSets"
```
##### <a name="ParametersUpdatesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|

#### <a name="UpdatesListParent">Command `az maintenance update list-parent`</a>

##### <a name="ExamplesUpdatesListParent">Example</a>
```
az maintenance update list-parent --provider-name "Microsoft.Compute" --resource-group "examplerg" --resource-name "1" \
--resource-parent-name "smdtest1" --resource-parent-type "virtualMachineScaleSets" --resource-type "virtualMachines"
```
##### <a name="ParametersUpdatesListParent">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Resource group name|resource_group_name|resourceGroupName|
|**--provider-name**|string|Resource provider name|provider_name|providerName|
|**--resource-parent-type**|string|Resource parent type|resource_parent_type|resourceParentType|
|**--resource-parent-name**|string|Resource parent identifier|resource_parent_name|resourceParentName|
|**--resource-type**|string|Resource type|resource_type|resourceType|
|**--resource-name**|string|Resource identifier|resource_name|resourceName|
