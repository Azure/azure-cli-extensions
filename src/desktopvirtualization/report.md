# Azure CLI Module Creation Report

### desktopvirtualization applicationgroup create

create a desktopvirtualization applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
|**--location**|string|The geo-location where the resource lives|location|
|**--host-pool-arm-path**|string|HostPool arm path of ApplicationGroup.|host_pool_arm_path|
|**--application-group-type**|choice|Resource Type of ApplicationGroup.|application_group_type|
|**--tags**|dictionary|Resource tags.|tags|
|**--description**|string|Description of ApplicationGroup.|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|
### desktopvirtualization applicationgroup delete

delete a desktopvirtualization applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
### desktopvirtualization applicationgroup list

list a desktopvirtualization applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--filter**|string|OData filter expression. Valid properties for filtering are applicationGroupType.|filter|
### desktopvirtualization applicationgroup show

show a desktopvirtualization applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
### desktopvirtualization applicationgroup update

update a desktopvirtualization applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
|**--tags**|dictionary|tags to be updated|tags|
|**--description**|string|Description of ApplicationGroup.|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|
### desktopvirtualization hostpool create

create a desktopvirtualization hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
|**--location**|string|The geo-location where the resource lives|location|
|**--host-pool-type**|choice|HostPool type for desktop.|host_pool_type|
|**--personal-desktop-assignment-type**|choice|PersonalDesktopAssignment type for HostPool.|personal_desktop_assignment_type|
|**--load-balancer-type**|choice|The type of the load balancer.|load_balancer_type|
|**--tags**|dictionary|Resource tags.|tags|
|**--friendly-name**|string|Friendly name of HostPool.|friendly_name|
|**--description**|string|Description of HostPool.|description|
|**--custom-rdp-property**|string|Custom rdp property of HostPool.|custom_rdp_property|
|**--max-session-limit**|integer|The max session limit of HostPool.|max_session_limit|
|**--ring**|integer|The ring number of HostPool.|ring|
|**--validation-environment**|boolean|Is validation environment.|validation_environment|
|**--registration-info**|object|The registration info of HostPool.|registration_info|
|**--vm-template**|string|VM template for sessionhosts configuration within hostpool.|vm_template|
|**--sso-context**|string|Path to keyvault containing ssoContext secret.|sso_context|
### desktopvirtualization hostpool delete

delete a desktopvirtualization hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
|**--force**|boolean|Force flag to delete sessionHost.|force|
### desktopvirtualization hostpool list

list a desktopvirtualization hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### desktopvirtualization hostpool show

show a desktopvirtualization hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
### desktopvirtualization hostpool update

update a desktopvirtualization hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
|**--tags**|dictionary|tags to be updated|tags|
|**--friendly-name**|string|Friendly name of HostPool.|friendly_name|
|**--description**|string|Description of HostPool.|description|
|**--custom-rdp-property**|string|Custom rdp property of HostPool.|custom_rdp_property|
|**--max-session-limit**|integer|The max session limit of HostPool.|max_session_limit|
|**--personal-desktop-assignment-type**|choice|PersonalDesktopAssignment type for HostPool.|personal_desktop_assignment_type|
|**--load-balancer-type**|choice|The type of the load balancer.|load_balancer_type|
|**--ring**|integer|The ring number of HostPool.|ring|
|**--validation-environment**|boolean|Is validation environment.|validation_environment|
|**--registration-info**|object|The registration info of HostPool.|registration_info|
|**--sso-context**|string|Path to keyvault containing ssoContext secret.|sso_context|
### desktopvirtualization workspace create

create a desktopvirtualization workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
|**--location**|string|The geo-location where the resource lives|location|
|**--tags**|dictionary|Resource tags.|tags|
|**--description**|string|Description of Workspace.|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|
|**--application-group-references**|array|List of applicationGroup resource Ids.|application_group_references|
### desktopvirtualization workspace delete

delete a desktopvirtualization workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
### desktopvirtualization workspace list

list a desktopvirtualization workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### desktopvirtualization workspace show

show a desktopvirtualization workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
### desktopvirtualization workspace update

update a desktopvirtualization workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
|**--tags**|dictionary|tags to be updated|tags|
|**--description**|string|Description of Workspace.|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|
|**--application-group-references**|array|List of applicationGroup links.|application_group_references|