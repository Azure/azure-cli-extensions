# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az desktopvirtualization|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az desktopvirtualization` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az desktopvirtualization workspace|Workspaces|[commands](#CommandsInWorkspaces)|
|az desktopvirtualization applicationgroup|ApplicationGroups|[commands](#CommandsInApplicationGroups)|
|az desktopvirtualization hostpool|HostPools|[commands](#CommandsInHostPools)|
|az desktopvirtualization msix-package|MSIXPackages|[commands](#CommandsInMSIXPackages)|
|az desktopvirtualization msix-image|MsixImages|[commands](#CommandsInMsixImages)|

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

### <a name="CommandsInMsixImages">Commands in `az desktopvirtualization msix-image` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az desktopvirtualization msix-image expand](#MsixImagesExpand)|Expand|[Parameters](#ParametersMsixImagesExpand)|[Example](#ExamplesMsixImagesExpand)|

### <a name="CommandsInMSIXPackages">Commands in `az desktopvirtualization msix-package` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az desktopvirtualization msix-package list](#MSIXPackagesList)|List|[Parameters](#ParametersMSIXPackagesList)|[Example](#ExamplesMSIXPackagesList)|
|[az desktopvirtualization msix-package show](#MSIXPackagesGet)|Get|[Parameters](#ParametersMSIXPackagesGet)|[Example](#ExamplesMSIXPackagesGet)|
|[az desktopvirtualization msix-package create](#MSIXPackagesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersMSIXPackagesCreateOrUpdate#Create)|[Example](#ExamplesMSIXPackagesCreateOrUpdate#Create)|
|[az desktopvirtualization msix-package update](#MSIXPackagesUpdate)|Update|[Parameters](#ParametersMSIXPackagesUpdate)|[Example](#ExamplesMSIXPackagesUpdate)|
|[az desktopvirtualization msix-package delete](#MSIXPackagesDelete)|Delete|[Parameters](#ParametersMSIXPackagesDelete)|[Example](#ExamplesMSIXPackagesDelete)|

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
ceGroups/resourceGroup1/providers/Microsoft.DesktopVirtualization/hostPools/hostPool1" --tags tag1="value1" \
tag2="value2" --name "applicationGroup1" --resource-group "resourceGroup1"
```
##### <a name="ParametersApplicationGroupsCreateOrUpdate#Create">Parameters</a> 
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
--personal-desktop-assignment-type "Automatic" --preferred-app-group-type "Desktop" --registration-info \
expiration-time="2020-10-01T14:01:54.9571247Z" registration-token-operation="Update" --sso-client-id "client" \
--sso-client-secret-key-vault-path "https://keyvault/secret" --sso-context "KeyVaultPath" --sso-secret-type \
"SharedKey" --ssoadfs-authority "https://adfs" --start-vm-on-connect false --vm-template "{json:json}" --tags \
tag1="value1" tag2="value2" --name "hostPool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersHostPoolsCreateOrUpdate#Create">Parameters</a> 
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
--sso-client-secret-key-vault-path "https://keyvault/secret" --sso-context "KeyVaultPath" --sso-secret-type \
"SharedKey" --ssoadfs-authority "https://adfs" --start-vm-on-connect false --vm-template "{json:json}" --tags \
tag1="value1" tag2="value2" --name "hostPool1" --resource-group "resourceGroup1"
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
|**--sso-context**|string|Path to keyvault containing ssoContext secret.|sso_context|ssoContext|
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

### group `az desktopvirtualization msix-image`
#### <a name="MsixImagesExpand">Command `az desktopvirtualization msix-image expand`</a>

##### <a name="ExamplesMsixImagesExpand">Example</a>
```
az desktopvirtualization msix-image expand --host-pool-name "hostpool1" --uri "imagepath" --resource-group \
"resourceGroup1"
```
##### <a name="ParametersMsixImagesExpand">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--uri**|string|URI to Image|uri|uri|

### group `az desktopvirtualization msix-package`
#### <a name="MSIXPackagesList">Command `az desktopvirtualization msix-package list`</a>

##### <a name="ExamplesMSIXPackagesList">Example</a>
```
az desktopvirtualization msix-package list --host-pool-name "hostpool1" --resource-group "resourceGroup1"
```
##### <a name="ParametersMSIXPackagesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|

#### <a name="MSIXPackagesGet">Command `az desktopvirtualization msix-package show`</a>

##### <a name="ExamplesMSIXPackagesGet">Example</a>
```
az desktopvirtualization msix-package show --host-pool-name "hostpool1" --msix-package-full-name "packagefullname" \
--resource-group "resourceGroup1"
```
##### <a name="ParametersMSIXPackagesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--msix-package-full-name**|string|The version specific package full name of the MSIX package within specified hostpool|msix_package_full_name|msixPackageFullName|

#### <a name="MSIXPackagesCreateOrUpdate#Create">Command `az desktopvirtualization msix-package create`</a>

##### <a name="ExamplesMSIXPackagesCreateOrUpdate#Create">Example</a>
```
az desktopvirtualization msix-package create --host-pool-name "hostpool1" --display-name "displayname" --image-path \
"imagepath" --is-active false --is-regular-registration false --last-updated "2008-09-22T14:01:54.9571247Z" \
--package-applications description="application-desc" app-id="ApplicationId" app-user-model-id="AppUserModelId" \
friendly-name="friendlyname" icon-image-name="Apptile" raw-icon="VGhpcyBpcyBhIHN0cmluZyB0byBoYXNo" \
raw-png="VGhpcyBpcyBhIHN0cmluZyB0byBoYXNo" --package-dependencies dependency-name="MsixTest_Dependency_Name" \
min-version="version" publisher="PublishedName" --package-family-name "MsixPackage_FamilyName" --package-name \
"MsixPackage_name" --package-relative-path "packagerelativepath" --version "version" --msix-package-full-name \
"msixpackagefullname" --resource-group "resourceGroup1"
```
##### <a name="ParametersMSIXPackagesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--msix-package-full-name**|string|The version specific package full name of the MSIX package within specified hostpool|msix_package_full_name|msixPackageFullName|
|**--image-path**|string|VHD/CIM image path on Network Share.|image_path|imagePath|
|**--package-name**|string|Package Name from appxmanifest.xml.|package_name|packageName|
|**--package-family-name**|string|Package Family Name from appxmanifest.xml. Contains Package Name and Publisher name.|package_family_name|packageFamilyName|
|**--display-name**|string|User friendly Name to be displayed in the portal.|display_name|displayName|
|**--package-relative-path**|string|Relative Path to the package inside the image.|package_relative_path|packageRelativePath|
|**--is-regular-registration**|boolean|Specifies how to register Package in feed.|is_regular_registration|isRegularRegistration|
|**--is-active**|boolean|Make this version of the package the active one across the hostpool.|is_active|isActive|
|**--package-dependencies**|array|List of package dependencies.|package_dependencies|packageDependencies|
|**--version**|string|Package Version found in the appxmanifest.xml.|version|version|
|**--last-updated**|date-time|Date Package was last updated, found in the appxmanifest.xml.|last_updated|lastUpdated|
|**--package-applications**|array|List of package applications.|package_applications|packageApplications|

#### <a name="MSIXPackagesUpdate">Command `az desktopvirtualization msix-package update`</a>

##### <a name="ExamplesMSIXPackagesUpdate">Example</a>
```
az desktopvirtualization msix-package update --host-pool-name "hostpool1" --display-name "displayname" --is-active \
true --is-regular-registration false --msix-package-full-name "msixpackagefullname" --resource-group "resourceGroup1"
```
##### <a name="ParametersMSIXPackagesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--msix-package-full-name**|string|The version specific package full name of the MSIX package within specified hostpool|msix_package_full_name|msixPackageFullName|
|**--is-active**|boolean|Set a version of the package to be active across hostpool.|is_active|isActive|
|**--is-regular-registration**|boolean|Set Registration mode. Regular or Delayed.|is_regular_registration|isRegularRegistration|
|**--display-name**|string|Display name for MSIX Package.|display_name|displayName|

#### <a name="MSIXPackagesDelete">Command `az desktopvirtualization msix-package delete`</a>

##### <a name="ExamplesMSIXPackagesDelete">Example</a>
```
az desktopvirtualization msix-package delete --host-pool-name "hostpool1" --msix-package-full-name "packagefullname" \
--resource-group "resourceGroup1"
```
##### <a name="ParametersMSIXPackagesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--host-pool-name**|string|The name of the host pool within the specified resource group|host_pool_name|hostPoolName|
|**--msix-package-full-name**|string|The version specific package full name of the MSIX package within specified hostpool|msix_package_full_name|msixPackageFullName|

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
