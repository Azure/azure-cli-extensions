# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az cloud-service|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az cloud-service` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az cloud-service role-instance|CloudServiceRoleInstances|[commands](#CommandsInCloudServiceRoleInstances)|
|az cloud-service role|CloudServiceRoles|[commands](#CommandsInCloudServiceRoles)|
|az cloud-service|CloudServices|[commands](#CommandsInCloudServices)|
|az cloud-service update-domain|CloudServicesUpdateDomain|[commands](#CommandsInCloudServicesUpdateDomain)|

## COMMANDS
### <a name="CommandsInCloudServices">Commands in `az cloud-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az cloud-service list](#CloudServicesList)|List|[Parameters](#ParametersCloudServicesList)|Not Found|
|[az cloud-service show](#CloudServicesGet)|Get|[Parameters](#ParametersCloudServicesGet)|Not Found|
|[az cloud-service create](#CloudServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersCloudServicesCreateOrUpdate#Create)|[Example](#ExamplesCloudServicesCreateOrUpdate#Create)|
|[az cloud-service update](#CloudServicesUpdate)|Update|[Parameters](#ParametersCloudServicesUpdate)|Not Found|
|[az cloud-service delete](#CloudServicesDelete)|Delete|[Parameters](#ParametersCloudServicesDelete)|Not Found|
|[az cloud-service delete-instance](#CloudServicesDeleteInstances)|DeleteInstances|[Parameters](#ParametersCloudServicesDeleteInstances)|Not Found|
|[az cloud-service list-all](#CloudServicesListAll)|ListAll|[Parameters](#ParametersCloudServicesListAll)|Not Found|
|[az cloud-service power-off](#CloudServicesPowerOff)|PowerOff|[Parameters](#ParametersCloudServicesPowerOff)|Not Found|
|[az cloud-service rebuild](#CloudServicesRebuild)|Rebuild|[Parameters](#ParametersCloudServicesRebuild)|Not Found|
|[az cloud-service reimage](#CloudServicesReimage)|Reimage|[Parameters](#ParametersCloudServicesReimage)|Not Found|
|[az cloud-service restart](#CloudServicesRestart)|Restart|[Parameters](#ParametersCloudServicesRestart)|Not Found|
|[az cloud-service show-instance-view](#CloudServicesGetInstanceView)|GetInstanceView|[Parameters](#ParametersCloudServicesGetInstanceView)|Not Found|
|[az cloud-service start](#CloudServicesStart)|Start|[Parameters](#ParametersCloudServicesStart)|Not Found|

### <a name="CommandsInCloudServiceRoles">Commands in `az cloud-service role` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az cloud-service role list](#CloudServiceRolesList)|List|[Parameters](#ParametersCloudServiceRolesList)|Not Found|
|[az cloud-service role show](#CloudServiceRolesGet)|Get|[Parameters](#ParametersCloudServiceRolesGet)|Not Found|

### <a name="CommandsInCloudServiceRoleInstances">Commands in `az cloud-service role-instance` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az cloud-service role-instance list](#CloudServiceRoleInstancesList)|List|[Parameters](#ParametersCloudServiceRoleInstancesList)|Not Found|
|[az cloud-service role-instance show](#CloudServiceRoleInstancesGet)|Get|[Parameters](#ParametersCloudServiceRoleInstancesGet)|Not Found|
|[az cloud-service role-instance delete](#CloudServiceRoleInstancesDelete)|Delete|[Parameters](#ParametersCloudServiceRoleInstancesDelete)|Not Found|
|[az cloud-service role-instance rebuild](#CloudServiceRoleInstancesRebuild)|Rebuild|[Parameters](#ParametersCloudServiceRoleInstancesRebuild)|Not Found|
|[az cloud-service role-instance reimage](#CloudServiceRoleInstancesReimage)|Reimage|[Parameters](#ParametersCloudServiceRoleInstancesReimage)|Not Found|
|[az cloud-service role-instance restart](#CloudServiceRoleInstancesRestart)|Restart|[Parameters](#ParametersCloudServiceRoleInstancesRestart)|Not Found|
|[az cloud-service role-instance show-instance-view](#CloudServiceRoleInstancesGetInstanceView)|GetInstanceView|[Parameters](#ParametersCloudServiceRoleInstancesGetInstanceView)|Not Found|
|[az cloud-service role-instance show-remote-desktop-file](#CloudServiceRoleInstancesGetRemoteDesktopFile)|GetRemoteDesktopFile|[Parameters](#ParametersCloudServiceRoleInstancesGetRemoteDesktopFile)|Not Found|

### <a name="CommandsInCloudServicesUpdateDomain">Commands in `az cloud-service update-domain` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az cloud-service update-domain list-update-domain](#CloudServicesUpdateDomainListUpdateDomains)|ListUpdateDomains|[Parameters](#ParametersCloudServicesUpdateDomainListUpdateDomains)|Not Found|
|[az cloud-service update-domain show-update-domain](#CloudServicesUpdateDomainGetUpdateDomain)|GetUpdateDomain|[Parameters](#ParametersCloudServicesUpdateDomainGetUpdateDomain)|Not Found|
|[az cloud-service update-domain walk-update-domain](#CloudServicesUpdateDomainWalkUpdateDomain)|WalkUpdateDomain|[Parameters](#ParametersCloudServicesUpdateDomainWalkUpdateDomain)|Not Found|


## COMMAND DETAILS

### group `az cloud-service`
#### <a name="CloudServicesList">Command `az cloud-service list`</a>

##### <a name="ParametersCloudServicesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|

#### <a name="CloudServicesGet">Command `az cloud-service show`</a>

##### <a name="ParametersCloudServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|

#### <a name="CloudServicesCreateOrUpdate#Create">Command `az cloud-service create`</a>

##### <a name="ExamplesCloudServicesCreateOrUpdate#Create">Example</a>
```
az cloud-service create --name "{cs-name}" --location "westus" --configuration "{ServiceConfiguration}" \
--load-balancer-configurations "[{\\"name\\":\\"contosolb\\",\\"properties\\":{\\"frontendIPConfigurations\\":[{\\"name\
\\":\\"contosofe\\",\\"properties\\":{\\"publicIPAddress\\":{\\"id\\":\\"/subscriptions/{subscription-id}/resourceGroup\
s/ConstosoRG/providers/Microsoft.Network/publicIPAddresses/contosopublicip\\"}}}]}}]" --package-url "{PackageUrl}" \
--roles "[{\\"name\\":\\"ContosoFrontend\\",\\"sku\\":{\\"name\\":\\"Standard_D1_v2\\",\\"capacity\\":1,\\"tier\\":\\"S\
tandard\\"}},{\\"name\\":\\"ContosoBackend\\",\\"sku\\":{\\"name\\":\\"Standard_D1_v2\\",\\"capacity\\":1,\\"tier\\":\\\
"Standard\\"}}]" --upgrade-mode "Auto" --resource-group "ConstosoRG"
```
##### <a name="ExamplesCloudServicesCreateOrUpdate#Create">Example</a>
```
az cloud-service create --name "{cs-name}" --location "westus" --configuration "{ServiceConfiguration}" \
--load-balancer-configurations "[{\\"name\\":\\"myLoadBalancer\\",\\"properties\\":{\\"frontendIPConfigurations\\":[{\\\
"name\\":\\"myfe\\",\\"properties\\":{\\"publicIPAddress\\":{\\"id\\":\\"/subscriptions/{subscription-id}/resourceGroup\
s/ConstosoRG/providers/Microsoft.Network/publicIPAddresses/myPublicIP\\"}}}]}}]" --package-url "{PackageUrl}" --roles \
"[{\\"name\\":\\"ContosoFrontend\\",\\"sku\\":{\\"name\\":\\"Standard_D1_v2\\",\\"capacity\\":1,\\"tier\\":\\"Standard\
\\"}}]" --upgrade-mode "Auto" --resource-group "ConstosoRG"
```
##### <a name="ExamplesCloudServicesCreateOrUpdate#Create">Example</a>
```
az cloud-service create --name "{cs-name}" --location "westus" --configuration "{ServiceConfiguration}" \
--load-balancer-configurations "[{\\"name\\":\\"contosolb\\",\\"properties\\":{\\"frontendIPConfigurations\\":[{\\"name\
\\":\\"contosofe\\",\\"properties\\":{\\"publicIPAddress\\":{\\"id\\":\\"/subscriptions/{subscription-id}/resourceGroup\
s/ConstosoRG/providers/Microsoft.Network/publicIPAddresses/contosopublicip\\"}}}]}}]" --secrets \
"[{\\"sourceVault\\":{\\"id\\":\\"/subscriptions/{subscription-id}/resourceGroups/ConstosoRG/providers/Microsoft.KeyVau\
lt/vaults/{keyvault-name}\\"},\\"vaultCertificates\\":[{\\"certificateUrl\\":\\"https://{keyvault-name}.vault.azure.net\
:443/secrets/ContosoCertificate/{secret-id}\\"}]}]" --package-url "{PackageUrl}" --roles \
"[{\\"name\\":\\"ContosoFrontend\\",\\"sku\\":{\\"name\\":\\"Standard_D1_v2\\",\\"capacity\\":1,\\"tier\\":\\"Standard\
\\"}}]" --upgrade-mode "Auto" --resource-group "ConstosoRG"
```
##### <a name="ExamplesCloudServicesCreateOrUpdate#Create">Example</a>
```
az cloud-service create --name "{cs-name}" --location "westus" --configuration "{ServiceConfiguration}" --extensions \
"[{\\"name\\":\\"RDPExtension\\",\\"properties\\":{\\"type\\":\\"RDP\\",\\"autoUpgradeMinorVersion\\":false,\\"protecte\
dSettings\\":\\"<PrivateConfig><Password>{password}</Password></PrivateConfig>\\",\\"publisher\\":\\"Microsoft.Windows.\
Azure.Extensions\\",\\"settings\\":\\"<PublicConfig><UserName>UserAzure</UserName><Expiration>10/22/2021 \
15:05:45</Expiration></PublicConfig>\\",\\"typeHandlerVersion\\":\\"1.2.1\\"}}]" --load-balancer-configurations \
"[{\\"name\\":\\"contosolb\\",\\"properties\\":{\\"frontendIPConfigurations\\":[{\\"name\\":\\"contosofe\\",\\"properti\
es\\":{\\"publicIPAddress\\":{\\"id\\":\\"/subscriptions/{subscription-id}/resourceGroups/ConstosoRG/providers/Microsof\
t.Network/publicIPAddresses/contosopublicip\\"}}}]}}]" --package-url "{PackageUrl}" --roles \
"[{\\"name\\":\\"ContosoFrontend\\",\\"sku\\":{\\"name\\":\\"Standard_D1_v2\\",\\"capacity\\":1,\\"tier\\":\\"Standard\
\\"}}]" --upgrade-mode "Auto" --resource-group "ConstosoRG"
```
##### <a name="ParametersCloudServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--location**|string|Resource location.|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--package-url**|string|Specifies a URL that refers to the location of the service package in the Blob service. The service package URL can be Shared Access Signature (SAS) URI from any storage account. This is a write-only property and is not returned in GET calls.|package_url|packageUrl|
|**--configuration**|string|Specifies the XML service configuration (.cscfg) for the cloud service.|configuration|configuration|
|**--configuration-url**|string|Specifies a URL that refers to the location of the service configuration in the Blob service. The service package URL  can be Shared Access Signature (SAS) URI from any storage account. This is a write-only property and is not returned in GET calls.|configuration_url|configurationUrl|
|**--start-cloud-service**|boolean|(Optional) Indicates whether to start the cloud service immediately after it is created. The default value is `true`. If false, the service model is still deployed, but the code is not run immediately. Instead, the service is PoweredOff until you call Start, at which time the service will be started. A deployed service still incurs charges, even if it is poweredoff.|start_cloud_service|startCloudService|
|**--upgrade-mode**|choice|Update mode for the cloud service. Role instances are allocated to update domains when the service is deployed. Updates can be initiated manually in each update domain or initiated automatically in all update domains. Possible Values are <br /><br />**Auto**<br /><br />**Manual** <br /><br />**Simultaneous**<br /><br /> If not specified, the default value is Auto. If set to Manual, PUT UpdateDomain must be called to apply the update. If set to Auto, the update is automatically applied to each update domain in sequence.|upgrade_mode|upgradeMode|
|**--extensions**|array|List of extensions for the cloud service.|extensions|extensions|
|**--load-balancer-configurations**|array|The list of load balancer configurations for the cloud service.|load_balancer_configurations|loadBalancerConfigurations|
|**--id**|string|Resource Id|id|id|
|**--secrets**|array|Specifies set of certificates that should be installed onto the role instances.|secrets|secrets|
|**--roles**|array|List of roles for the cloud service.|roles|roles|

#### <a name="CloudServicesUpdate">Command `az cloud-service update`</a>

##### <a name="ParametersCloudServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--tags**|dictionary|Resource tags|tags|tags|

#### <a name="CloudServicesDelete">Command `az cloud-service delete`</a>

##### <a name="ParametersCloudServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|

#### <a name="CloudServicesDeleteInstances">Command `az cloud-service delete-instance`</a>

##### <a name="ParametersCloudServicesDeleteInstances">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--role-instances**|array|List of cloud service role instance names. Value of '*' will signify all role instances of the cloud service.|role_instances|roleInstances|

#### <a name="CloudServicesListAll">Command `az cloud-service list-all`</a>

##### <a name="ParametersCloudServicesListAll">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="CloudServicesPowerOff">Command `az cloud-service power-off`</a>

##### <a name="ParametersCloudServicesPowerOff">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|

#### <a name="CloudServicesRebuild">Command `az cloud-service rebuild`</a>

##### <a name="ParametersCloudServicesRebuild">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--role-instances**|array|List of cloud service role instance names. Value of '*' will signify all role instances of the cloud service.|role_instances|roleInstances|

#### <a name="CloudServicesReimage">Command `az cloud-service reimage`</a>

##### <a name="ParametersCloudServicesReimage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--role-instances**|array|List of cloud service role instance names. Value of '*' will signify all role instances of the cloud service.|role_instances|roleInstances|

#### <a name="CloudServicesRestart">Command `az cloud-service restart`</a>

##### <a name="ParametersCloudServicesRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--role-instances**|array|List of cloud service role instance names. Value of '*' will signify all role instances of the cloud service.|role_instances|roleInstances|

#### <a name="CloudServicesGetInstanceView">Command `az cloud-service show-instance-view`</a>

##### <a name="ParametersCloudServicesGetInstanceView">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|

#### <a name="CloudServicesStart">Command `az cloud-service start`</a>

##### <a name="ParametersCloudServicesStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|

### group `az cloud-service role`
#### <a name="CloudServiceRolesList">Command `az cloud-service role list`</a>

##### <a name="ParametersCloudServiceRolesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRolesGet">Command `az cloud-service role show`</a>

##### <a name="ParametersCloudServiceRolesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-name**|string|Name of the role.|role_name|roleName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

### group `az cloud-service role-instance`
#### <a name="CloudServiceRoleInstancesList">Command `az cloud-service role-instance list`</a>

##### <a name="ParametersCloudServiceRoleInstancesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesGet">Command `az cloud-service role-instance show`</a>

##### <a name="ParametersCloudServiceRoleInstancesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesDelete">Command `az cloud-service role-instance delete`</a>

##### <a name="ParametersCloudServiceRoleInstancesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesRebuild">Command `az cloud-service role-instance rebuild`</a>

##### <a name="ParametersCloudServiceRoleInstancesRebuild">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesReimage">Command `az cloud-service role-instance reimage`</a>

##### <a name="ParametersCloudServiceRoleInstancesReimage">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesRestart">Command `az cloud-service role-instance restart`</a>

##### <a name="ParametersCloudServiceRoleInstancesRestart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesGetInstanceView">Command `az cloud-service role-instance show-instance-view`</a>

##### <a name="ParametersCloudServiceRoleInstancesGetInstanceView">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

#### <a name="CloudServiceRoleInstancesGetRemoteDesktopFile">Command `az cloud-service role-instance show-remote-desktop-file`</a>

##### <a name="ParametersCloudServiceRoleInstancesGetRemoteDesktopFile">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--role-instance-name**|string|Name of the role instance.|role_instance_name|roleInstanceName|
|**--resource-group-name**|string||resource_group_name|resourceGroupName|
|**--cloud-service-name**|string||cloud_service_name|cloudServiceName|

### group `az cloud-service update-domain`
#### <a name="CloudServicesUpdateDomainListUpdateDomains">Command `az cloud-service update-domain list-update-domain`</a>

##### <a name="ParametersCloudServicesUpdateDomainListUpdateDomains">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|

#### <a name="CloudServicesUpdateDomainGetUpdateDomain">Command `az cloud-service update-domain show-update-domain`</a>

##### <a name="ParametersCloudServicesUpdateDomainGetUpdateDomain">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--update-domain**|integer|Specifies an integer value that identifies the update domain. Update domains are identified with a zero-based index: the first update domain has an ID of 0, the second has an ID of 1, and so on.|update_domain|updateDomain|

#### <a name="CloudServicesUpdateDomainWalkUpdateDomain">Command `az cloud-service update-domain walk-update-domain`</a>

##### <a name="ParametersCloudServicesUpdateDomainWalkUpdateDomain">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group.|resource_group_name|resourceGroupName|
|**--cloud-service-name**|string|Name of the cloud service.|cloud_service_name|cloudServiceName|
|**--update-domain**|integer|Specifies an integer value that identifies the update domain. Update domains are identified with a zero-based index: the first update domain has an ID of 0, the second has an ID of 1, and so on.|update_domain|updateDomain|
