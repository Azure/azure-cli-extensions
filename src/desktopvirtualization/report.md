# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az desktopvirtualization|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az desktopvirtualization` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az desktopvirtualization applicationgroup|ApplicationGroups|[commands](#CommandsInApplicationGroups)|
|az desktopvirtualization hostpool|HostPools|[commands](#CommandsInHostPools)|
|az desktopvirtualization workspace|Workspaces|[commands](#CommandsInWorkspaces)|

## COMMANDS
### <a name="CommandsInApplicationGroups">Commands in `az desktopvirtualization applicationgroup` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az desktopvirtualization applicationgroup list](#ApplicationGroupsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersApplicationGroupsListByResourceGroup)|[Example](#ExamplesApplicationGroupsListByResourceGroup)|
|[az desktopvirtualization applicationgroup list](#ApplicationGroupsListBySubscription)|ListBySubscription|[Parameters](#ParametersApplicationGroupsListBySubscription)|[Example](#ExamplesApplicationGroupsListBySubscription)|
|[az desktopvirtualization applicationgroup show](#ApplicationGroupsGet)|Get|[Parameters](#ParametersApplicationGroupsGet)|[Example](#ExamplesApplicationGroupsGet)|
|[az desktopvirtualization applicationgroup create](#ApplicationGroupsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersApplicationGroupsCreateOrUpdate#Create)|[Example](#ExamplesApplicationGroupsCreateOrUpdate#Create)|
|[az desktopvirtualization applicationgroup update](#ApplicationGroupsUpdate)|Update|[Parameters](#ParametersApplicationGroupsUpdate)|[Example](#ExamplesApplicationGroupsUpdate)|
|[az desktopvirtualization applicationgroup delete](#ApplicationGroupsDelete)|Delete|[Parameters](#ParametersApplicationGroupsDelete)|[Example](#ExamplesApplicationGroupsDelete)|

### <a name="CommandsInHostPools">Commands in `az desktopvirtualization hostpool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az desktopvirtualization hostpool list](#HostPoolsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersHostPoolsListByResourceGroup)|[Example](#ExamplesHostPoolsListByResourceGroup)|
|[az desktopvirtualization hostpool list](#HostPoolsList)|List|[Parameters](#ParametersHostPoolsList)|[Example](#ExamplesHostPoolsList)|
|[az desktopvirtualization hostpool show](#HostPoolsGet)|Get|[Parameters](#ParametersHostPoolsGet)|[Example](#ExamplesHostPoolsGet)|
|[az desktopvirtualization hostpool create](#HostPoolsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersHostPoolsCreateOrUpdate#Create)|[Example](#ExamplesHostPoolsCreateOrUpdate#Create)|
|[az desktopvirtualization hostpool update](#HostPoolsUpdate)|Update|[Parameters](#ParametersHostPoolsUpdate)|[Example](#ExamplesHostPoolsUpdate)|
|[az desktopvirtualization hostpool delete](#HostPoolsDelete)|Delete|[Parameters](#ParametersHostPoolsDelete)|[Example](#ExamplesHostPoolsDelete)|
|[az desktopvirtualization hostpool retrieve-registration-token](#HostPoolsRetrieveRegistrationToken)|RetrieveRegistrationToken|[Parameters](#ParametersHostPoolsRetrieveRegistrationToken)|[Example](#ExamplesHostPoolsRetrieveRegistrationToken)|

### <a name="CommandsInWorkspaces">Commands in `az desktopvirtualization workspace` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az desktopvirtualization workspace list](#WorkspacesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersWorkspacesListByResourceGroup)|[Example](#ExamplesWorkspacesListByResourceGroup)|
|[az desktopvirtualization workspace list](#WorkspacesListBySubscription)|ListBySubscription|[Parameters](#ParametersWorkspacesListBySubscription)|[Example](#ExamplesWorkspacesListBySubscription)|
|[az desktopvirtualization workspace show](#WorkspacesGet)|Get|[Parameters](#ParametersWorkspacesGet)|[Example](#ExamplesWorkspacesGet)|
|[az desktopvirtualization workspace create](#WorkspacesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersWorkspacesCreateOrUpdate#Create)|[Example](#ExamplesWorkspacesCreateOrUpdate#Create)|
|[az desktopvirtualization workspace update](#WorkspacesUpdate)|Update|[Parameters](#ParametersWorkspacesUpdate)|[Example](#ExamplesWorkspacesUpdate)|
|[az desktopvirtualization workspace delete](#WorkspacesDelete)|Delete|[Parameters](#ParametersWorkspacesDelete)|[Example](#ExamplesWorkspacesDelete)|


## COMMAND DETAILS
### group `az desktopvirtualization applicationgroup`
#### <a name="ApplicationGroupsListByResourceGroup">Command `az desktopvirtualization applicationgroup list`</a>

##### <a name="ExamplesApplicationGroupsListByResourceGroup">Example</a>
```
az desktopvirtualization applicationgroup list --filter "applicationGroupType eq \'RailApplication\'" --resource-group \
"resourceGroup1"
```
##### <a name="ParametersApplicationGroupsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--filter**|string|OData filter expression. Valid properties for filtering are applicationGroupType.|filter|$filter|

#### <a name="ApplicationGroupsListBySubscription">Command `az desktopvirtualization applicationgroup list`</a>

##### <a name="ExamplesApplicationGroupsListBySubscription">Example</a>
```
az desktopvirtualization applicationgroup list --filter "applicationGroupType eq \'RailApplication\'"
```
##### <a name="ParametersApplicationGroupsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|OData filter expression. Valid properties for filtering are applicationGroupType.|filter|$filter|

#### <a name="ApplicationGroupsGet">Command `az desktopvirtualization applicationgroup show`</a>

##### <a name="ExamplesApplicationGroupsGet">Example</a>
```
az desktopvirtualization applicationgroup show --name "applicationGroup1" --resource-group "resourceGroup1"
```
##### <a name="ParametersApplicationGroupsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|

#### <a name="ApplicationGroupsCreateOrUpdate#Create">Command `az desktopvirtualization applicationgroup create`</a>

##### <a name="ExamplesApplicationGroupsCreateOrUpdate#Create">Example</a>
```
az desktopvirtualization applicationgroup create --location "centralus" --description "des1" --application-group-type \
"RemoteApp" --friendly-name "friendly" --host-pool-arm-path "/subscriptions/daefabc0-95b4-48b3-b645-8a753a63c4fa/resour\
ceGroups/resourceGroup1/providers/Microsoft.DesktopVirtualization/hostPools/hostPool1" --tags tag1="value1" tag2="value2" --name "applicationGroup1" --resource-group "resourceGroup1"
```
##### <a name="ParametersApplicationGroupsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--host-pool-arm-path**|string|HostPool arm path of ApplicationGroup.|host_pool_arm_path|hostPoolArmPath|
|**--application-group-type**|choice|Resource Type of ApplicationGroup.|application_group_type|applicationGroupType|
|**--description**|string|Description of ApplicationGroup.|description|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|friendlyName|

#### <a name="ApplicationGroupsUpdate">Command `az desktopvirtualization applicationgroup update`</a>

##### <a name="ExamplesApplicationGroupsUpdate">Example</a>
```
az desktopvirtualization applicationgroup update --description "des1" --friendly-name "friendly" --tags tag1="value1" \
tag2="value2" --name "applicationGroup1" --resource-group "resourceGroup1"
```
##### <a name="ParametersApplicationGroupsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|
|**--tags**|dictionary|tags to be updated|tags|tags|
|**--description**|string|Description of ApplicationGroup.|description|description|
|**--friendly-name**|string|Friendly name of ApplicationGroup.|friendly_name|friendlyName|

#### <a name="ApplicationGroupsDelete">Command `az desktopvirtualization applicationgroup delete`</a>

##### <a name="ExamplesApplicationGroupsDelete">Example</a>
```
az desktopvirtualization applicationgroup delete --name "applicationGroup1" --resource-group "resourceGroup1"
```
##### <a name="ParametersApplicationGroupsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--application-group-name**|string|The name of the application group|application_group_name|applicationGroupName|

### group `az desktopvirtualization hostpool`
#### <a name="HostPoolsListByResourceGroup">Command `az desktopvirtualization hostpool list`</a>

##### <a name="ExamplesHostPoolsListByResourceGroup">Example</a>
```
az desktopvirtualization hostpool list --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="HostPoolsList">Command `az desktopvirtualization hostpool list`</a>

##### <a name="ExamplesHostPoolsList">Example</a>
```
az desktopvirtualization hostpool list
```
##### <a name="ParametersHostPoolsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="HostPoolsGet">Command `az desktopvirtualization hostpool show`</a>

##### <a name="ExamplesHostPoolsGet">Example</a>
```
az desktopvirtualization hostpool show --name "hostPool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|

#### <a name="HostPoolsCreateOrUpdate#Create">Command `az desktopvirtualization hostpool create`</a>

##### <a name="ExamplesHostPoolsCreateOrUpdate#Create">Example</a>
```
az desktopvirtualization hostpool create --location "centralus" --description "des1" --friendly-name "friendly" \
--host-pool-type "Pooled" --load-balancer-type "BreadthFirst" --max-session-limit 999999 \
--personal-desktop-assignment-type "Automatic" --preferred-app-group-type "Desktop" \
--registration-info expiration-time="2020-10-01T14:01:54.9571247Z" registration-token-operation="Update" \
--sso-client-id "client" --sso-client-secret-key-vault-path "https://keyvault/secret" --sso-secret-type "SharedKey" \
--ssoadfs-authority "https://adfs" --start-vm-on-connect false --vm-template "{json:json}" --tags tag1="value1" \
tag2="value2" --name "hostPool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--host-pool-type**|choice|HostPool type for desktop.|host_pool_type|hostPoolType|
|**--load-balancer-type**|choice|The type of the load balancer.|load_balancer_type|loadBalancerType|
|**--preferred-app-group-type**|choice|The type of preferred application group type, default to Desktop Application Group|preferred_app_group_type|preferredAppGroupType|
|**--friendly-name**|string|Friendly name of HostPool.|friendly_name|friendlyName|
|**--description**|string|Description of HostPool.|description|description|
|**--personal-desktop-assignment-type**|choice|PersonalDesktopAssignment type for HostPool.|personal_desktop_assignment_type|personalDesktopAssignmentType|
|**--custom-rdp-property**|string|Custom rdp property of HostPool.|custom_rdp_property|customRdpProperty|
|**--max-session-limit**|integer|The max session limit of HostPool.|max_session_limit|maxSessionLimit|
|**--ring**|integer|The ring number of HostPool.|ring|ring|
|**--validation-environment**|boolean|Is validation environment.|validation_environment|validationEnvironment|
|**--registration-info**|object|The registration info of HostPool.|registration_info|registrationInfo|
|**--vm-template**|string|VM template for sessionhosts configuration within hostpool.|vm_template|vmTemplate|
|**--ssoadfs-authority**|string|URL to customer ADFS server for signing WVD SSO certificates.|ssoadfs_authority|ssoadfsAuthority|
|**--sso-client-id**|string|ClientId for the registered Relying Party used to issue WVD SSO certificates.|sso_client_id|ssoClientId|
|**--sso-client-secret-key-vault-path**|string|Path to Azure KeyVault storing the secret used for communication to ADFS.|sso_client_secret_key_vault_path|ssoClientSecretKeyVaultPath|
|**--sso-secret-type**|choice|The type of single sign on Secret Type.|sso_secret_type|ssoSecretType|
|**--start-vm-on-connect**|boolean|The flag to turn on/off StartVMOnConnect feature.|start_vm_on_connect|startVMOnConnect|

#### <a name="HostPoolsUpdate">Command `az desktopvirtualization hostpool update`</a>

##### <a name="ExamplesHostPoolsUpdate">Example</a>
```
az desktopvirtualization hostpool update --description "des1" --friendly-name "friendly" --load-balancer-type \
"BreadthFirst" --max-session-limit 999999 --personal-desktop-assignment-type "Automatic" --registration-info \
expiration-time="2020-10-01T15:01:54.9571247Z" registration-token-operation="Update" --sso-client-id "client" \
--sso-client-secret-key-vault-path "https://keyvault/secret" --sso-secret-type "SharedKey" --ssoadfs-authority \
"https://adfs" --start-vm-on-connect false --vm-template "{json:json}" --tags tag1="value1" tag2="value2" --name \
"hostPool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsUpdate">Parameters</a> 
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
|**--vm-template**|string|VM template for sessionhosts configuration within hostpool.|vm_template|vmTemplate|
|**--ssoadfs-authority**|string|URL to customer ADFS server for signing WVD SSO certificates.|ssoadfs_authority|ssoadfsAuthority|
|**--sso-client-id**|string|ClientId for the registered Relying Party used to issue WVD SSO certificates.|sso_client_id|ssoClientId|
|**--sso-client-secret-key-vault-path**|string|Path to Azure KeyVault storing the secret used for communication to ADFS.|sso_client_secret_key_vault_path|ssoClientSecretKeyVaultPath|
|**--sso-secret-type**|choice|The type of single sign on Secret Type.|sso_secret_type|ssoSecretType|
|**--preferred-app-group-type**|choice|The type of preferred application group type, default to Desktop Application Group|preferred_app_group_type|preferredAppGroupType|
|**--start-vm-on-connect**|boolean|The flag to turn on/off StartVMOnConnect feature.|start_vm_on_connect|startVMOnConnect|

#### <a name="HostPoolsDelete">Command `az desktopvirtualization hostpool delete`</a>

##### <a name="ExamplesHostPoolsDelete">Example</a>
```
az desktopvirtualization hostpool delete --force true --name "hostPool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--force**|boolean|Force flag to delete sessionHost.|force|force|

#### <a name="HostPoolsRetrieveRegistrationToken">Command `az desktopvirtualization hostpool retrieve-registration-token`</a>

##### <a name="ExamplesHostPoolsRetrieveRegistrationToken">Example</a>
```
az desktopvirtualization hostpool retrieve-registration-token --name "hostPool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsRetrieveRegistrationToken">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|

### group `az desktopvirtualization workspace`
#### <a name="WorkspacesListByResourceGroup">Command `az desktopvirtualization workspace list`</a>

##### <a name="ExamplesWorkspacesListByResourceGroup">Example</a>
```
az desktopvirtualization workspace list --resource-group "resourceGroup1"
```
##### <a name="ParametersWorkspacesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="WorkspacesListBySubscription">Command `az desktopvirtualization workspace list`</a>

##### <a name="ExamplesWorkspacesListBySubscription">Example</a>
```
az desktopvirtualization workspace list
```
##### <a name="ParametersWorkspacesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="WorkspacesGet">Command `az desktopvirtualization workspace show`</a>

##### <a name="ExamplesWorkspacesGet">Example</a>
```
az desktopvirtualization workspace show --resource-group "resourceGroup1" --name "workspace1"
```
##### <a name="ParametersWorkspacesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|

#### <a name="WorkspacesCreateOrUpdate#Create">Command `az desktopvirtualization workspace create`</a>

##### <a name="ExamplesWorkspacesCreateOrUpdate#Create">Example</a>
```
az desktopvirtualization workspace create --resource-group "resourceGroup1" --location "centralus" --description \
"des1" --friendly-name "friendly" --tags tag1="value1" tag2="value2" --name "workspace1"
```
##### <a name="ParametersWorkspacesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--description**|string|Description of Workspace.|description|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|friendlyName|
|**--application-group-references**|array|List of applicationGroup resource Ids.|application_group_references|applicationGroupReferences|

#### <a name="WorkspacesUpdate">Command `az desktopvirtualization workspace update`</a>

##### <a name="ExamplesWorkspacesUpdate">Example</a>
```
az desktopvirtualization workspace update --resource-group "resourceGroup1" --description "des1" --friendly-name \
"friendly" --tags tag1="value1" tag2="value2" --name "workspace1"
```
##### <a name="ParametersWorkspacesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|
|**--tags**|dictionary|tags to be updated|tags|tags|
|**--description**|string|Description of Workspace.|description|description|
|**--friendly-name**|string|Friendly name of Workspace.|friendly_name|friendlyName|
|**--application-group-references**|array|List of applicationGroup links.|application_group_references|applicationGroupReferences|

#### <a name="WorkspacesDelete">Command `az desktopvirtualization workspace delete`</a>

##### <a name="ExamplesWorkspacesDelete">Example</a>
```
az desktopvirtualization workspace delete --resource-group "resourceGroup1" --name "workspace1"
```
##### <a name="ParametersWorkspacesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace|workspace_name|workspaceName|
