# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az videoanalyzer|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az videoanalyzer` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az videoanalyzer video-analyzer|VideoAnalyzers|[commands](#CommandsInVideoAnalyzers)|
|az videoanalyzer edge-module|EdgeModules|[commands](#CommandsInEdgeModules)|
|az videoanalyzer video|Videos|[commands](#CommandsInVideos)|
|az videoanalyzer access-policy|AccessPolicies|[commands](#CommandsInAccessPolicies)|

## COMMANDS
### <a name="CommandsInAccessPolicies">Commands in `az videoanalyzer access-policy` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az videoanalyzer access-policy list](#AccessPoliciesList)|List|[Parameters](#ParametersAccessPoliciesList)|[Example](#ExamplesAccessPoliciesList)|
|[az videoanalyzer access-policy show](#AccessPoliciesGet)|Get|[Parameters](#ParametersAccessPoliciesGet)|[Example](#ExamplesAccessPoliciesGet)|
|[az videoanalyzer access-policy create](#AccessPoliciesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAccessPoliciesCreateOrUpdate#Create)|[Example](#ExamplesAccessPoliciesCreateOrUpdate#Create)|
|[az videoanalyzer access-policy update](#AccessPoliciesUpdate)|Update|[Parameters](#ParametersAccessPoliciesUpdate)|[Example](#ExamplesAccessPoliciesUpdate)|
|[az videoanalyzer access-policy delete](#AccessPoliciesDelete)|Delete|[Parameters](#ParametersAccessPoliciesDelete)|[Example](#ExamplesAccessPoliciesDelete)|

### <a name="CommandsInEdgeModules">Commands in `az videoanalyzer edge-module` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az videoanalyzer edge-module list](#EdgeModulesList)|List|[Parameters](#ParametersEdgeModulesList)|[Example](#ExamplesEdgeModulesList)|
|[az videoanalyzer edge-module show](#EdgeModulesGet)|Get|[Parameters](#ParametersEdgeModulesGet)|[Example](#ExamplesEdgeModulesGet)|
|[az videoanalyzer edge-module create](#EdgeModulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersEdgeModulesCreateOrUpdate#Create)|[Example](#ExamplesEdgeModulesCreateOrUpdate#Create)|
|[az videoanalyzer edge-module update](#EdgeModulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersEdgeModulesCreateOrUpdate#Update)|Not Found|
|[az videoanalyzer edge-module delete](#EdgeModulesDelete)|Delete|[Parameters](#ParametersEdgeModulesDelete)|[Example](#ExamplesEdgeModulesDelete)|
|[az videoanalyzer edge-module list-provisioning-token](#EdgeModulesListProvisioningToken)|ListProvisioningToken|[Parameters](#ParametersEdgeModulesListProvisioningToken)|[Example](#ExamplesEdgeModulesListProvisioningToken)|

### <a name="CommandsInVideos">Commands in `az videoanalyzer video` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az videoanalyzer video list](#VideosList)|List|[Parameters](#ParametersVideosList)|[Example](#ExamplesVideosList)|
|[az videoanalyzer video show](#VideosGet)|Get|[Parameters](#ParametersVideosGet)|[Example](#ExamplesVideosGet)|
|[az videoanalyzer video create](#VideosCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVideosCreateOrUpdate#Create)|[Example](#ExamplesVideosCreateOrUpdate#Create)|
|[az videoanalyzer video update](#VideosUpdate)|Update|[Parameters](#ParametersVideosUpdate)|[Example](#ExamplesVideosUpdate)|
|[az videoanalyzer video delete](#VideosDelete)|Delete|[Parameters](#ParametersVideosDelete)|[Example](#ExamplesVideosDelete)|
|[az videoanalyzer video list-streaming-token](#VideosListStreamingToken)|ListStreamingToken|[Parameters](#ParametersVideosListStreamingToken)|[Example](#ExamplesVideosListStreamingToken)|

### <a name="CommandsInVideoAnalyzers">Commands in `az videoanalyzer video-analyzer` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az videoanalyzer video-analyzer list](#VideoAnalyzersList)|List|[Parameters](#ParametersVideoAnalyzersList)|[Example](#ExamplesVideoAnalyzersList)|
|[az videoanalyzer video-analyzer list](#VideoAnalyzersListBySubscription)|ListBySubscription|[Parameters](#ParametersVideoAnalyzersListBySubscription)|[Example](#ExamplesVideoAnalyzersListBySubscription)|
|[az videoanalyzer video-analyzer show](#VideoAnalyzersGet)|Get|[Parameters](#ParametersVideoAnalyzersGet)|[Example](#ExamplesVideoAnalyzersGet)|
|[az videoanalyzer video-analyzer create](#VideoAnalyzersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersVideoAnalyzersCreateOrUpdate#Create)|[Example](#ExamplesVideoAnalyzersCreateOrUpdate#Create)|
|[az videoanalyzer video-analyzer update](#VideoAnalyzersUpdate)|Update|[Parameters](#ParametersVideoAnalyzersUpdate)|[Example](#ExamplesVideoAnalyzersUpdate)|
|[az videoanalyzer video-analyzer delete](#VideoAnalyzersDelete)|Delete|[Parameters](#ParametersVideoAnalyzersDelete)|[Example](#ExamplesVideoAnalyzersDelete)|
|[az videoanalyzer video-analyzer sync-storage-key](#VideoAnalyzersSyncStorageKeys)|SyncStorageKeys|[Parameters](#ParametersVideoAnalyzersSyncStorageKeys)|[Example](#ExamplesVideoAnalyzersSyncStorageKeys)|


## COMMAND DETAILS

### group `az videoanalyzer access-policy`
#### <a name="AccessPoliciesList">Command `az videoanalyzer access-policy list`</a>

##### <a name="ExamplesAccessPoliciesList">Example</a>
```
az videoanalyzer access-policy list --top "2" --account-name "testaccount2" --resource-group "testrg"
```
##### <a name="ParametersAccessPoliciesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--top**|integer|Specifies a non-negative integer n that limits the number of items returned from a collection. The service returns the number of available items up to but not greater than the specified value n.|top|$top|

#### <a name="AccessPoliciesGet">Command `az videoanalyzer access-policy show`</a>

##### <a name="ExamplesAccessPoliciesGet">Example</a>
```
az videoanalyzer access-policy show --name "accessPolicyName1" --account-name "testaccount2" --resource-group "testrg"
```
##### <a name="ParametersAccessPoliciesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--access-policy-name**|string|The name of the access policy to retrieve.|access_policy_name|accessPolicyName|

#### <a name="AccessPoliciesCreateOrUpdate#Create">Command `az videoanalyzer access-policy create`</a>

##### <a name="ExamplesAccessPoliciesCreateOrUpdate#Create">Example</a>
```
az videoanalyzer access-policy create --name "accessPolicyName1" --account-name "testaccount2" --authentication \
"{\\"@type\\":\\"#Microsoft.VideoAnalyzer.JwtAuthentication\\",\\"audiences\\":[\\"audience1\\"],\\"claims\\":[{\\"name\
\\":\\"claimname1\\",\\"value\\":\\"claimvalue1\\"},{\\"name\\":\\"claimname2\\",\\"value\\":\\"claimvalue2\\"}],\\"iss\
uers\\":[\\"issuer1\\",\\"issuer2\\"],\\"keys\\":[{\\"@type\\":\\"#Microsoft.VideoAnalyzer.RsaTokenKey\\",\\"alg\\":\\"\
RS256\\",\\"e\\":\\"ZLFzZTY0IQ==\\",\\"kid\\":\\"123\\",\\"n\\":\\"YmFzZTY0IQ==\\"},{\\"@type\\":\\"#Microsoft.VideoAna\
lyzer.EccTokenKey\\",\\"alg\\":\\"ES256\\",\\"kid\\":\\"124\\",\\"x\\":\\"XX==\\",\\"y\\":\\"YY==\\"}]}" \
--resource-group "testrg"
```
##### <a name="ParametersAccessPoliciesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--access-policy-name**|string|The name of the access policy to create or update.|access_policy_name|accessPolicyName|
|**--jwt-authentication**|object|Properties for access validation based on JSON Web Tokens (JWT).|jwt_authentication|JwtAuthentication|

#### <a name="AccessPoliciesUpdate">Command `az videoanalyzer access-policy update`</a>

##### <a name="ExamplesAccessPoliciesUpdate">Example</a>
```
az videoanalyzer access-policy update --name "accessPolicyName1" --account-name "testaccount2" --authentication \
"{\\"@type\\":\\"#Microsoft.VideoAnalyzer.JwtAuthentication\\",\\"keys\\":[{\\"@type\\":\\"#Microsoft.VideoAnalyzer.Rsa\
TokenKey\\",\\"alg\\":\\"RS256\\",\\"e\\":\\"ZLFzZTY0IQ==\\",\\"kid\\":\\"123\\",\\"n\\":\\"YmFzZTY0IQ==\\"},{\\"@type\
\\":\\"#Microsoft.VideoAnalyzer.EccTokenKey\\",\\"alg\\":\\"Updated\\",\\"kid\\":\\"124\\",\\"x\\":\\"XX==\\",\\"y\\":\
\\"YY==\\"}]}" --resource-group "testrg"
```
##### <a name="ParametersAccessPoliciesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--access-policy-name**|string|The name of the access policy to update.|access_policy_name|accessPolicyName|
|**--jwt-authentication**|object|Properties for access validation based on JSON Web Tokens (JWT).|jwt_authentication|JwtAuthentication|

#### <a name="AccessPoliciesDelete">Command `az videoanalyzer access-policy delete`</a>

##### <a name="ExamplesAccessPoliciesDelete">Example</a>
```
az videoanalyzer access-policy delete --name "accessPolicyName1" --account-name "testaccount2" --resource-group \
"testrg"
```
##### <a name="ParametersAccessPoliciesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--access-policy-name**|string|The name of the access policy to delete.|access_policy_name|accessPolicyName|

### group `az videoanalyzer edge-module`
#### <a name="EdgeModulesList">Command `az videoanalyzer edge-module list`</a>

##### <a name="ExamplesEdgeModulesList">Example</a>
```
az videoanalyzer edge-module list --account-name "testaccount2" --resource-group "testrg"
```
##### <a name="ParametersEdgeModulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--filter**|string|Restricts the set of items returned.|filter|$filter|
|**--top**|integer|Specifies a non-negative integer n that limits the number of items returned from a collection. The service returns the number of available items up to but not greater than the specified value n.|top|$top|
|**--orderby**|string|Specifies the key by which the result collection should be ordered.|orderby|$orderby|

#### <a name="EdgeModulesGet">Command `az videoanalyzer edge-module show`</a>

##### <a name="ExamplesEdgeModulesGet">Example</a>
```
az videoanalyzer edge-module show --account-name "testaccount2" --name "edgeModule1" --resource-group "testrg"
```
##### <a name="ParametersEdgeModulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--edge-module-name**|string|The name of the edge module to retrieve.|edge_module_name|edgeModuleName|

#### <a name="EdgeModulesCreateOrUpdate#Create">Command `az videoanalyzer edge-module create`</a>

##### <a name="ExamplesEdgeModulesCreateOrUpdate#Create">Example</a>
```
az videoanalyzer edge-module create --account-name "testaccount2" --name "edgeModule1" --resource-group "testrg"
```
##### <a name="ParametersEdgeModulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--edge-module-name**|string|The name of the edge module to create or update.|edge_module_name|edgeModuleName|

#### <a name="EdgeModulesCreateOrUpdate#Update">Command `az videoanalyzer edge-module update`</a>

##### <a name="ParametersEdgeModulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--edge-module-name**|string|The name of the edge module to create or update.|edge_module_name|edgeModuleName|

#### <a name="EdgeModulesDelete">Command `az videoanalyzer edge-module delete`</a>

##### <a name="ExamplesEdgeModulesDelete">Example</a>
```
az videoanalyzer edge-module delete --account-name "testaccount2" --name "edgeModule1" --resource-group "testrg"
```
##### <a name="ParametersEdgeModulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--edge-module-name**|string|The name of the edge module to be deleted.|edge_module_name|edgeModuleName|

#### <a name="EdgeModulesListProvisioningToken">Command `az videoanalyzer edge-module list-provisioning-token`</a>

##### <a name="ExamplesEdgeModulesListProvisioningToken">Example</a>
```
az videoanalyzer edge-module list-provisioning-token --account-name "testaccount2" --name "edgeModule1" \
--expiration-date "3021-01-23T11:04:49.0526841-08:00" --resource-group "testrg"
```
##### <a name="ParametersEdgeModulesListProvisioningToken">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--edge-module-name**|string|The name of the edge module used to create a new provisioning token.|edge_module_name|edgeModuleName|
|**--expiration-date**|date-time|The desired expiration date of the registration token. The Azure Video Analyzer IoT edge module must be initialized and connected to the Internet prior to the token expiration date.|expiration_date|expirationDate|

### group `az videoanalyzer video`
#### <a name="VideosList">Command `az videoanalyzer video list`</a>

##### <a name="ExamplesVideosList">Example</a>
```
az videoanalyzer video list --top "2" --account-name "testaccount2" --resource-group "testrg"
```
##### <a name="ParametersVideosList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--top**|integer|Specifies a non-negative integer n that limits the number of items returned from a collection. The service returns the number of available items up to but not greater than the specified value n.|top|$top|

#### <a name="VideosGet">Command `az videoanalyzer video show`</a>

##### <a name="ExamplesVideosGet">Example</a>
```
az videoanalyzer video show --account-name "testaccount2" --resource-group "testrg" --name "video1"
```
##### <a name="ParametersVideosGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--video-name**|string|The name of the video to retrieve.|video_name|videoName|

#### <a name="VideosCreateOrUpdate#Create">Command `az videoanalyzer video create`</a>

##### <a name="ExamplesVideosCreateOrUpdate#Create">Example</a>
```
az videoanalyzer video create --account-name "testaccount2" --description "Sample Description 1" --title "Sample Title \
1" --resource-group "testrg" --name "video1"
```
##### <a name="ParametersVideosCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--video-name**|string|The name of the video to create or update.|video_name|videoName|
|**--title**|string|Optional video title provided by the user. Value can be up to 256 characters long.|title|title|
|**--description**|string|Optional video description provided by the user. Value can be up to 2048 characters long.|description|description|

#### <a name="VideosUpdate">Command `az videoanalyzer video update`</a>

##### <a name="ExamplesVideosUpdate">Example</a>
```
az videoanalyzer video update --account-name "testaccount2" --description "Parking Lot East Entrance" --resource-group \
"testrg" --name "video1"
```
##### <a name="ParametersVideosUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--video-name**|string|The name of the video to update.|video_name|videoName|
|**--title**|string|Optional video title provided by the user. Value can be up to 256 characters long.|title|title|
|**--description**|string|Optional video description provided by the user. Value can be up to 2048 characters long.|description|description|

#### <a name="VideosDelete">Command `az videoanalyzer video delete`</a>

##### <a name="ExamplesVideosDelete">Example</a>
```
az videoanalyzer video delete --account-name "testaccount2" --resource-group "testrg" --name "video1"
```
##### <a name="ParametersVideosDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--video-name**|string|The name of the video to delete.|video_name|videoName|

#### <a name="VideosListStreamingToken">Command `az videoanalyzer video list-streaming-token`</a>

##### <a name="ExamplesVideosListStreamingToken">Example</a>
```
az videoanalyzer video list-streaming-token --account-name "testaccount2" --resource-group "testrg" --name "video3"
```
##### <a name="ParametersVideosListStreamingToken">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Azure Video Analyzer account name.|account_name|accountName|
|**--video-name**|string|The name of the video to generate a token for playback.|video_name|videoName|

### group `az videoanalyzer video-analyzer`
#### <a name="VideoAnalyzersList">Command `az videoanalyzer video-analyzer list`</a>

##### <a name="ExamplesVideoAnalyzersList">Example</a>
```
az videoanalyzer video-analyzer list --resource-group "contoso"
```
##### <a name="ParametersVideoAnalyzersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="VideoAnalyzersListBySubscription">Command `az videoanalyzer video-analyzer list`</a>

##### <a name="ExamplesVideoAnalyzersListBySubscription">Example</a>
```
az videoanalyzer video-analyzer list
```
##### <a name="ParametersVideoAnalyzersListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="VideoAnalyzersGet">Command `az videoanalyzer video-analyzer show`</a>

##### <a name="ExamplesVideoAnalyzersGet">Example</a>
```
az videoanalyzer video-analyzer show --account-name "contosotv" --resource-group "contoso"
```
##### <a name="ParametersVideoAnalyzersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Video Analyzer account name.|account_name|accountName|

#### <a name="VideoAnalyzersCreateOrUpdate#Create">Command `az videoanalyzer video-analyzer create`</a>

##### <a name="ExamplesVideoAnalyzersCreateOrUpdate#Create">Example</a>
```
az videoanalyzer video-analyzer create --account-name "contosotv" --video-analyzer-identity-type "UserAssigned" \
--user-assigned-identities "{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microso\
ft.ManagedIdentity/userAssignedIdentities/id1\\":{},\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGrou\
ps/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id2\\":{},\\"/subscriptions/00000000-0000-0000-0000-00\
0000000000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id3\\":{}}" --location "South \
Central US" --type "SystemKey" --storage-accounts id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroup\
s/rg/providers/Microsoft.Storage/storageAccounts/storage1" user-assigned-identity="/subscriptions/00000000-0000-0000-00\
00-000000000000/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id2" --tags tag1="value1" \
tag2="value2" --resource-group "contoso"
```
##### <a name="ParametersVideoAnalyzersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Video Analyzer account name.|account_name|accountName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--storage-accounts**|array|The storage accounts for this resource.|storage_accounts|storageAccounts|
|**--type**|choice|The type of key used to encrypt the Account Key.|type|type|
|**--user-assigned-identity**|string|The user assigned managed identity's resource identifier to use when accessing a resource.|user_assigned_identity|userAssignedIdentity|
|**--key-identifier**|string|The URL of the Key Vault key used to encrypt the account. The key may either be versioned (for example https://vault/keys/mykey/version1) or reference a key without a version (for example https://vault/keys/mykey).|key_identifier|keyIdentifier|
|**--video-analyzer-identity-type**|string|The identity type.|video_analyzer_identity_type|type|
|**--user-assigned-identities**|dictionary|The User Assigned Managed Identities.|user_assigned_identities|userAssignedIdentities|

#### <a name="VideoAnalyzersUpdate">Command `az videoanalyzer video-analyzer update`</a>

##### <a name="ExamplesVideoAnalyzersUpdate">Example</a>
```
az videoanalyzer video-analyzer update --account-name "contosotv" --tags key1="value3" --resource-group "contoso"
```
##### <a name="ParametersVideoAnalyzersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Video Analyzer account name.|account_name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--storage-accounts**|array|The storage accounts for this resource.|storage_accounts|storageAccounts|
|**--type**|choice|The type of key used to encrypt the Account Key.|type|type|
|**--user-assigned-identity**|string|The user assigned managed identity's resource identifier to use when accessing a resource.|user_assigned_identity|userAssignedIdentity|
|**--key-identifier**|string|The URL of the Key Vault key used to encrypt the account. The key may either be versioned (for example https://vault/keys/mykey/version1) or reference a key without a version (for example https://vault/keys/mykey).|key_identifier|keyIdentifier|
|**--video-analyzer-identity-type**|string|The identity type.|video_analyzer_identity_type|type|
|**--user-assigned-identities**|dictionary|The User Assigned Managed Identities.|user_assigned_identities|userAssignedIdentities|

#### <a name="VideoAnalyzersDelete">Command `az videoanalyzer video-analyzer delete`</a>

##### <a name="ExamplesVideoAnalyzersDelete">Example</a>
```
az videoanalyzer video-analyzer delete --account-name "contosotv" --resource-group "contoso"
```
##### <a name="ParametersVideoAnalyzersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Video Analyzer account name.|account_name|accountName|

#### <a name="VideoAnalyzersSyncStorageKeys">Command `az videoanalyzer video-analyzer sync-storage-key`</a>

##### <a name="ExamplesVideoAnalyzersSyncStorageKeys">Example</a>
```
az videoanalyzer video-analyzer sync-storage-key --account-name "contosotv" --id "/subscriptions/00000000-0000-0000-000\
0-000000000000/resourceGroups/contoso/providers/Microsoft.Storage/storageAccounts/contosotvstore" --resource-group \
"contoso"
```
##### <a name="ParametersVideoAnalyzersSyncStorageKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The Video Analyzer account name.|account_name|accountName|
|**--id**|string|The ID of the storage account resource.|id|id|
