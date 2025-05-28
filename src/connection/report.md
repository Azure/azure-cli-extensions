# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az connection|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az connection` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az connection linker|Linker|[commands](#CommandsInLinker)|

## COMMANDS
### <a name="CommandsInLinker">Commands in `az connection linker` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az connection linker list](#LinkerList)|List|[Parameters](#ParametersLinkerList)|[Example](#ExamplesLinkerList)|
|[az connection linker show](#LinkerGet)|Get|[Parameters](#ParametersLinkerGet)|[Example](#ExamplesLinkerGet)|
|[az connection linker create](#LinkerCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersLinkerCreateOrUpdate#Create)|[Example](#ExamplesLinkerCreateOrUpdate#Create)|
|[az connection linker update](#LinkerUpdate)|Update|[Parameters](#ParametersLinkerUpdate)|[Example](#ExamplesLinkerUpdate)|
|[az connection linker delete](#LinkerDelete)|Delete|[Parameters](#ParametersLinkerDelete)|[Example](#ExamplesLinkerDelete)|
|[az connection linker list-configuration](#LinkerListConfigurations)|ListConfigurations|[Parameters](#ParametersLinkerListConfigurations)|[Example](#ExamplesLinkerListConfigurations)|
|[az connection linker validate-linker](#LinkerValidateLinker)|ValidateLinker|[Parameters](#ParametersLinkerValidateLinker)|[Example](#ExamplesLinkerValidateLinker)|


## COMMAND DETAILS

### group `az connection linker`
#### <a name="LinkerList">Command `az connection linker list`</a>

##### <a name="ExamplesLinkerList">Example</a>
```
az connection linker list --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/pro\
viders/Microsoft.Web/sites/test-app"
```
##### <a name="ParametersLinkerList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|

#### <a name="LinkerGet">Command `az connection linker show`</a>

##### <a name="ExamplesLinkerGet">Example</a>
```
az connection linker show --name "linkName" --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resource\
Groups/test-rg/providers/Microsoft.Web/sites/test-app"
```
##### <a name="ParametersLinkerGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|

#### <a name="LinkerCreateOrUpdate#Create">Command `az connection linker create`</a>

##### <a name="ExamplesLinkerCreateOrUpdate#Create">Example</a>
```
az connection linker create --name "linkName" --auth-info "{\\"name\\":\\"name\\",\\"authType\\":\\"secret\\",\\"secret\
\\":\\"secret\\"}" --target-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Mi\
crosoft.DocumentDb/databaseAccounts/test-acc/mongodbDatabases/test-db" --resource-uri "subscriptions/00000000-0000-0000\
-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.Web/sites/test-app"
```
##### <a name="ParametersLinkerCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
|**--target-id**|string|The resource Id of target service.|target_id|targetId|
|**--secret-auth-info**|object|The authentication info when authType is secret|secret_auth_info|SecretAuthInfo|
|**--user-assigned-identity-auth-info**|object|The authentication info when authType is userAssignedIdentity|user_assigned_identity_auth_info|UserAssignedIdentityAuthInfo|
|**--system-assigned-identity-auth-info**|object|The authentication info when authType is systemAssignedIdentity|system_assigned_identity_auth_info|SystemAssignedIdentityAuthInfo|
|**--service-principal-secret-auth-info**|object|The authentication info when authType is servicePrincipal secret|service_principal_secret_auth_info|ServicePrincipalSecretAuthInfo|
|**--service-principal-certificate-auth-info**|object|The authentication info when authType is servicePrincipal certificate|service_principal_certificate_auth_info|ServicePrincipalCertificateAuthInfo|
|**--client-type**|choice||client_type|clientType|

#### <a name="LinkerUpdate">Command `az connection linker update`</a>

##### <a name="ExamplesLinkerUpdate">Example</a>
```
az connection linker update --name "linkName" --auth-info "{\\"authType\\":\\"servicePrincipalSecret\\",\\"clientId\\":\
\\"name\\",\\"principalId\\":\\"id\\",\\"secret\\":\\"secret\\"}" --target-id "/subscriptions/00000000-0000-0000-0000-0\
00000000000/resourceGroups/test-rg/providers/Microsoft.DocumentDb/databaseAccounts/test-acc/mongodbDatabases/test-db" \
--resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Microsoft.Web/sites\
/test-app"
```
##### <a name="ParametersLinkerUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
|**--target-id**|string|The resource Id of target service.|target_id|targetId|
|**--secret-auth-info**|object|The authentication info when authType is secret|secret_auth_info|SecretAuthInfo|
|**--user-assigned-identity-auth-info**|object|The authentication info when authType is userAssignedIdentity|user_assigned_identity_auth_info|UserAssignedIdentityAuthInfo|
|**--system-assigned-identity-auth-info**|object|The authentication info when authType is systemAssignedIdentity|system_assigned_identity_auth_info|SystemAssignedIdentityAuthInfo|
|**--service-principal-secret-auth-info**|object|The authentication info when authType is servicePrincipal secret|service_principal_secret_auth_info|ServicePrincipalSecretAuthInfo|
|**--service-principal-certificate-auth-info**|object|The authentication info when authType is servicePrincipal certificate|service_principal_certificate_auth_info|ServicePrincipalCertificateAuthInfo|
|**--client-type**|choice||client_type|clientType|

#### <a name="LinkerDelete">Command `az connection linker delete`</a>

##### <a name="ExamplesLinkerDelete">Example</a>
```
az connection linker delete --name "linkName" --resource-uri "subscriptions/00000000-0000-0000-0000-000000000000/resour\
ceGroups/test-rg/providers/Microsoft.Web/sites/test-app"
```
##### <a name="ParametersLinkerDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|

#### <a name="LinkerListConfigurations">Command `az connection linker list-configuration`</a>

##### <a name="ExamplesLinkerListConfigurations">Example</a>
```
az connection linker list-configuration --name "linkName" --resource-uri "subscriptions/00000000-0000-0000-0000-0000000\
00000/resourceGroups/test-rg/providers/Microsoft.Web/sites/test-app"
```
##### <a name="ParametersLinkerListConfigurations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|

#### <a name="LinkerValidateLinker">Command `az connection linker validate-linker`</a>

##### <a name="ExamplesLinkerValidateLinker">Example</a>
```
az connection linker validate-linker --name "linkName" --resource-uri "subscriptions/00000000-0000-0000-0000-0000000000\
00/resourceGroups/test-rg/providers/Microsoft.Web/sites/test-app"
```
##### <a name="ExamplesLinkerValidateLinker">Example</a>
```
az connection linker validate-linker --name "linkName" --resource-uri "subscriptions/00000000-0000-0000-0000-0000000000\
00/resourceGroups/test-rg/providers/Microsoft.Web/sites/test-app"
```
##### <a name="ParametersLinkerValidateLinker">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-uri**|string|The fully qualified Azure Resource manager identifier of the resource to be connected.|resource_uri|resourceUri|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
