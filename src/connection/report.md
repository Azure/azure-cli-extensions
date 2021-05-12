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
az connection linker list --resource-group "test-rg" --source-provider "Microsoft.Web" --source-resource-name \
"test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|

#### <a name="LinkerGet">Command `az connection linker show`</a>

##### <a name="ExamplesLinkerGet">Example</a>
```
az connection linker show --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
--source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|

#### <a name="LinkerCreateOrUpdate#Create">Command `az connection linker create`</a>

##### <a name="ExamplesLinkerCreateOrUpdate#Create">Example</a>
```
az connection linker create --name "linkName" --auth-info "{\\"name\\":\\"name\\",\\"authType\\":\\"secret\\",\\"secret\
\\":\\"secret\\"}" --target-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/Mi\
crosoft.DocumentDb/databaseAccounts/test-acc/mongodbDatabases/test-db" --resource-group "test-rg" --source-provider \
"Microsoft.Web" --source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
|**--target-id**|string|The resource Id of target service.|target_id|targetId|
|**--secret-auth-info**|object|The authentication info when authType is secret|secret_auth_info|SecretAuthInfo|
|**--user-assigned-identity-auth-info**|object|The authentication info when authType is userAssignedIdentity|user_assigned_identity_auth_info|UserAssignedIdentityAuthInfo|
|**--system-assigned-identity-auth-info**|object|The authentication info when authType is systemAssignedIdentity|system_assigned_identity_auth_info|SystemAssignedIdentityAuthInfo|
|**--service-principal-auth-info**|object|The authentication info when authType is servicePrincipal|service_principal_auth_info|ServicePrincipalAuthInfo|

#### <a name="LinkerUpdate">Command `az connection linker update`</a>

##### <a name="ExamplesLinkerUpdate">Example</a>
```
az connection linker update --name "linkName" --auth-info "{\\"name\\":\\"name\\",\\"authType\\":\\"servicePrincipal\\"\
,\\"id\\":\\"id\\"}" --target-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test-rg/providers/\
Microsoft.DocumentDb/databaseAccounts/test-acc/mongodbDatabases/test-db" --resource-group "test-rg" --source-provider \
"Microsoft.Web" --source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
|**--target-id**|string|The resource Id of target service.|target_id|targetId|
|**--secret-auth-info**|object|The authentication info when authType is secret|secret_auth_info|SecretAuthInfo|
|**--user-assigned-identity-auth-info**|object|The authentication info when authType is userAssignedIdentity|user_assigned_identity_auth_info|UserAssignedIdentityAuthInfo|
|**--system-assigned-identity-auth-info**|object|The authentication info when authType is systemAssignedIdentity|system_assigned_identity_auth_info|SystemAssignedIdentityAuthInfo|
|**--service-principal-auth-info**|object|The authentication info when authType is servicePrincipal|service_principal_auth_info|ServicePrincipalAuthInfo|

#### <a name="LinkerDelete">Command `az connection linker delete`</a>

##### <a name="ExamplesLinkerDelete">Example</a>
```
az connection linker delete --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
--source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|

#### <a name="LinkerListConfigurations">Command `az connection linker list-configuration`</a>

##### <a name="ExamplesLinkerListConfigurations">Example</a>
```
az connection linker list-configuration --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
--source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerListConfigurations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|

#### <a name="LinkerValidateLinker">Command `az connection linker validate-linker`</a>

##### <a name="ExamplesLinkerValidateLinker">Example</a>
```
az connection linker validate-linker --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
--source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ExamplesLinkerValidateLinker">Example</a>
```
az connection linker validate-linker --name "linkName" --resource-group "test-rg" --source-provider "Microsoft.Web" \
--source-resource-name "test-app" --source-resource-type "sites"
```
##### <a name="ParametersLinkerValidateLinker">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--linker-name**|string|The name Linker resource.|linker_name|linkerName|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--source-provider**|string|The Azure resource provider of the source resource to be connected|source_provider|sourceProvider|
|**--source-resource-type**|string|The Azure resource type of source resource to be connected|source_resource_type|sourceResourceType|
|**--source-resource-name**|string|The Azure resource name of source resource to be connected|source_resource_name|sourceResourceName|
