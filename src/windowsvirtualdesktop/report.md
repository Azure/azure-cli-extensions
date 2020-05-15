# Azure CLI Module Creation Report

### windows-virtual-desktop applicationgroup create

create a windows-virtual-desktop applicationgroup.

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
### windows-virtual-desktop applicationgroup delete

delete a windows-virtual-desktop applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
### windows-virtual-desktop applicationgroup list

list a windows-virtual-desktop applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--filter**|string|OData filter expression. Valid properties for filtering are applicationGroupType.|filter|
### windows-virtual-desktop applicationgroup show

show a windows-virtual-desktop applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
### windows-virtual-desktop applicationgroup update

update a windows-virtual-desktop applicationgroup.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--application-group-name**|string|The name of the application group|application_group_name|
|**--tags**|any|tags to be updated|tags|
|**--description**|string|Description of ApplicationGroup.|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|
### windows-virtual-desktop hostpool create

create a windows-virtual-desktop hostpool.

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
### windows-virtual-desktop hostpool delete

delete a windows-virtual-desktop hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
|**--force**|boolean|Force flag to delete sessionHost.|force|
### windows-virtual-desktop hostpool list

list a windows-virtual-desktop hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### windows-virtual-desktop hostpool show

show a windows-virtual-desktop hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
### windows-virtual-desktop hostpool update

update a windows-virtual-desktop hostpool.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|
|**--tags**|any|tags to be updated|tags|
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
### windows-virtual-desktop workspace create

create a windows-virtual-desktop workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
|**--location**|string|The geo-location where the resource lives|location|
|**--tags**|dictionary|Resource tags.|tags|
|**--description**|string|Description of Workspace.|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|
|**--application-group-references**|array|List of applicationGroup resource Ids.|application_group_references|
### windows-virtual-desktop workspace delete

delete a windows-virtual-desktop workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
### windows-virtual-desktop workspace list

list a windows-virtual-desktop workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### windows-virtual-desktop workspace show

show a windows-virtual-desktop workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
### windows-virtual-desktop workspace update

update a windows-virtual-desktop workspace.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace|workspace_name|
|**--tags**|any|tags to be updated|tags|
|**--description**|string|Description of Workspace.|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|
|**--application-group-references**|array|List of applicationGroup links.|application_group_references|