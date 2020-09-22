# Azure CLI Module Creation Report

### desktopvirtualization applicationgroup create

create a desktopvirtualization applicationgroup.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization applicationgroup|ApplicationGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--host-pool-arm-path**|string|HostPool arm path of ApplicationGroup.|host_pool_arm_path|hostPoolArmPath|
|**--application-group-type**|choice|Resource Type of ApplicationGroup.|application_group_type|applicationGroupType|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of ApplicationGroup.|description|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|friendlyName|

### desktopvirtualization applicationgroup delete

delete a desktopvirtualization applicationgroup.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization applicationgroup|ApplicationGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|

### desktopvirtualization applicationgroup list

list a desktopvirtualization applicationgroup.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization applicationgroup|ApplicationGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--filter**|string|OData filter expression. Valid properties for filtering are applicationGroupType.|filter|$filter|

### desktopvirtualization applicationgroup show

show a desktopvirtualization applicationgroup.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization applicationgroup|ApplicationGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|

### desktopvirtualization applicationgroup update

update a desktopvirtualization applicationgroup.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization applicationgroup|ApplicationGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|
|**--tags**|dictionary|tags to be updated|tags|tags|
|**--description**|string|Description of ApplicationGroup.|description|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|friendlyName|

### desktopvirtualization hostpool create

create a desktopvirtualization hostpool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization hostpool|HostPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--host-pool-type**|choice|HostPool type for desktop.|host_pool_type|hostPoolType|
|**--load-balancer-type**|choice|The type of the load balancer.|load_balancer_type|loadBalancerType|
|**--preferred-app-group-type**|choice|The type of preferred application group type, default to Desktop Application Group|preferred_app_group_type|preferredAppGroupType|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--friendly-name**|string|Friendly name of HostPool.|friendly_name|friendlyName|
|**--description**|string|Description of HostPool.|description|description|
|**--personal-desktop-assignment-type**|choice|PersonalDesktopAssignment type for HostPool.|personal_desktop_assignment_type|personalDesktopAssignmentType|
|**--custom-rdp-property**|string|Custom rdp property of HostPool.|custom_rdp_property|customRdpProperty|
|**--max-session-limit**|integer|The max session limit of HostPool.|max_session_limit|maxSessionLimit|
|**--ring**|integer|The ring number of HostPool.|ring|ring|
|**--validation-environment**|boolean|Is validation environment.|validation_environment|validationEnvironment|
|**--registration-info**|object|The registration info of HostPool.|registration_info|registrationInfo|
|**--vm-template**|string|VM template for sessionhosts configuration within hostpool.|vm_template|vmTemplate|
|**--sso-context**|string|Path to keyvault containing ssoContext secret.|sso_context|ssoContext|

### desktopvirtualization hostpool delete

delete a desktopvirtualization hostpool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization hostpool|HostPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--force**|boolean|Force flag to delete sessionHost.|force|force|

### desktopvirtualization hostpool list

list a desktopvirtualization hostpool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization hostpool|HostPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

### desktopvirtualization hostpool show

show a desktopvirtualization hostpool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization hostpool|HostPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|

### desktopvirtualization hostpool update

update a desktopvirtualization hostpool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization hostpool|HostPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--tags**|dictionary|tags to be updated|tags|tags|
|**--friendly-name**|string|Friendly name of HostPool.|friendly_name|friendlyName|
|**--description**|string|Description of HostPool.|description|description|
|**--custom-rdp-property**|string|Custom rdp property of HostPool.|custom_rdp_property|customRdpProperty|
|**--max-session-limit**|integer|The max session limit of HostPool.|max_session_limit|maxSessionLimit|
|**--personal-desktop-assignment-type**|choice|PersonalDesktopAssignment type for HostPool.|personal_desktop_assignment_type|personalDesktopAssignmentType|
|**--load-balancer-type**|choice|The type of the load balancer.|load_balancer_type|loadBalancerType|
|**--ring**|integer|The ring number of HostPool.|ring|ring|
|**--validation-environment**|boolean|Is validation environment.|validation_environment|validationEnvironment|
|**--registration-info**|object|The registration info of HostPool.|registration_info|registrationInfo|
|**--sso-context**|string|Path to keyvault containing ssoContext secret.|sso_context|ssoContext|
|**--preferred-app-group-type**|choice|The type of preferred application group type, default to Desktop Application Group|preferred_app_group_type|preferredAppGroupType|

### desktopvirtualization workspace create

create a desktopvirtualization workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of Workspace.|description|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|friendlyName|
|**--application-group-references**|array|List of applicationGroup resource Ids.|application_group_references|applicationGroupReferences|

### desktopvirtualization workspace delete

delete a desktopvirtualization workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|

### desktopvirtualization workspace list

list a desktopvirtualization workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

### desktopvirtualization workspace show

show a desktopvirtualization workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|

### desktopvirtualization workspace update

update a desktopvirtualization workspace.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|desktopvirtualization workspace|Workspaces|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|
|**--tags**|dictionary|tags to be updated|tags|tags|
|**--description**|string|Description of Workspace.|description|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|friendlyName|
|**--application-group-references**|array|List of applicationGroup links.|application_group_references|applicationGroupReferences|
