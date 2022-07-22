# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az devcenter|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az devcenter` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az devcenter artifact|Artifacts|[commands](#CommandsInArtifacts)|
|az devcenter catalog-item|CatalogItem|[commands](#CommandsInCatalogItem)|
|az devcenter catalog-item|CatalogItems|[commands](#CommandsInCatalogItems)|
|az devcenter catalog-item-version|CatalogItemVersions|[commands](#CommandsInCatalogItemVersions)|
|az devcenter dev-box|DevBox|[commands](#CommandsInDevBox)|
|az devcenter environment|Environments|[commands](#CommandsInEnvironments)|
|az devcenter environment-type|EnvironmentType|[commands](#CommandsInEnvironmentType)|
|az devcenter pool|Pool|[commands](#CommandsInPool)|
|az devcenter project|Project|[commands](#CommandsInProject)|
|az devcenter schedule|Schedule|[commands](#CommandsInSchedule)|

## COMMANDS
### <a name="CommandsInArtifacts">Commands in `az devcenter artifact` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter artifact list](#ArtifactsListByPath)|ListByPath|[Parameters](#ParametersArtifactsListByPath)|[Example](#ExamplesArtifactsListByPath)|
|[az devcenter artifact list](#ArtifactsListByEnvironment)|ListByEnvironment|[Parameters](#ParametersArtifactsListByEnvironment)|[Example](#ExamplesArtifactsListByEnvironment)|

### <a name="CommandsInCatalogItem">Commands in `az devcenter catalog-item` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter catalog-item list](#CatalogItemListByProject)|ListByProject|[Parameters](#ParametersCatalogItemListByProject)|[Example](#ExamplesCatalogItemListByProject)|

### <a name="CommandsInCatalogItems">Commands in `az devcenter catalog-item` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter catalog-item show](#CatalogItemsGet)|Get|[Parameters](#ParametersCatalogItemsGet)|[Example](#ExamplesCatalogItemsGet)|

### <a name="CommandsInCatalogItemVersions">Commands in `az devcenter catalog-item-version` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter catalog-item-version list](#CatalogItemVersionsListByProject)|ListByProject|[Parameters](#ParametersCatalogItemVersionsListByProject)|[Example](#ExamplesCatalogItemVersionsListByProject)|
|[az devcenter catalog-item-version show](#CatalogItemVersionsGet)|Get|[Parameters](#ParametersCatalogItemVersionsGet)|[Example](#ExamplesCatalogItemVersionsGet)|

### <a name="CommandsInDevBox">Commands in `az devcenter dev-box` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter dev-box list](#DevBoxListByProject)|ListByProject|[Parameters](#ParametersDevBoxListByProject)|[Example](#ExamplesDevBoxListByProject)|
|[az devcenter dev-box list](#DevBoxListByUser)|ListByUser|[Parameters](#ParametersDevBoxListByUser)|[Example](#ExamplesDevBoxListByUser)|
|[az devcenter dev-box list](#DevBoxList)|List|[Parameters](#ParametersDevBoxList)|[Example](#ExamplesDevBoxList)|
|[az devcenter dev-box show](#DevBoxGet)|Get|[Parameters](#ParametersDevBoxGet)|[Example](#ExamplesDevBoxGet)|
|[az devcenter dev-box create](#DevBoxCreate)|Create|[Parameters](#ParametersDevBoxCreate)|[Example](#ExamplesDevBoxCreate)|
|[az devcenter dev-box delete](#DevBoxDelete)|Delete|[Parameters](#ParametersDevBoxDelete)|[Example](#ExamplesDevBoxDelete)|
|[az devcenter dev-box show-remote-connection](#DevBoxGetRemoteConnection)|GetRemoteConnection|[Parameters](#ParametersDevBoxGetRemoteConnection)|[Example](#ExamplesDevBoxGetRemoteConnection)|
|[az devcenter dev-box start](#DevBoxStart)|Start|[Parameters](#ParametersDevBoxStart)|[Example](#ExamplesDevBoxStart)|
|[az devcenter dev-box stop](#DevBoxStop)|Stop|[Parameters](#ParametersDevBoxStop)|[Example](#ExamplesDevBoxStop)|

### <a name="CommandsInEnvironments">Commands in `az devcenter environment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter environment list](#EnvironmentsListByProject)|ListByProject|[Parameters](#ParametersEnvironmentsListByProject)|[Example](#ExamplesEnvironmentsListByProject)|
|[az devcenter environment show](#EnvironmentsGet)|Get|[Parameters](#ParametersEnvironmentsGet)|[Example](#ExamplesEnvironmentsGet)|
|[az devcenter environment create](#EnvironmentsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersEnvironmentsCreateOrUpdate#Create)|[Example](#ExamplesEnvironmentsCreateOrUpdate#Create)|
|[az devcenter environment update](#EnvironmentsUpdate)|Update|[Parameters](#ParametersEnvironmentsUpdate)|[Example](#ExamplesEnvironmentsUpdate)|
|[az devcenter environment delete](#EnvironmentsDelete)|Delete|[Parameters](#ParametersEnvironmentsDelete)|[Example](#ExamplesEnvironmentsDelete)|
|[az devcenter environment custom-action](#EnvironmentsCustomAction)|CustomAction|[Parameters](#ParametersEnvironmentsCustomAction)|[Example](#ExamplesEnvironmentsCustomAction)|
|[az devcenter environment delete-action](#EnvironmentsDeleteAction)|DeleteAction|[Parameters](#ParametersEnvironmentsDeleteAction)|[Example](#ExamplesEnvironmentsDeleteAction)|
|[az devcenter environment deploy-action](#EnvironmentsDeployAction)|DeployAction|[Parameters](#ParametersEnvironmentsDeployAction)|[Example](#ExamplesEnvironmentsDeployAction)|
|[az devcenter environment list-by-project](#EnvironmentsListByProjectByUser)|ListByProjectByUser|[Parameters](#ParametersEnvironmentsListByProjectByUser)|[Example](#ExamplesEnvironmentsListByProjectByUser)|

### <a name="CommandsInEnvironmentType">Commands in `az devcenter environment-type` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter environment-type list](#EnvironmentTypeListByProject)|ListByProject|[Parameters](#ParametersEnvironmentTypeListByProject)|[Example](#ExamplesEnvironmentTypeListByProject)|

### <a name="CommandsInPool">Commands in `az devcenter pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter pool list](#PoolList)|List|[Parameters](#ParametersPoolList)|[Example](#ExamplesPoolList)|
|[az devcenter pool show](#PoolGet)|Get|[Parameters](#ParametersPoolGet)|[Example](#ExamplesPoolGet)|

### <a name="CommandsInProject">Commands in `az devcenter project` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter project list](#ProjectListByDevCenter)|ListByDevCenter|[Parameters](#ParametersProjectListByDevCenter)|[Example](#ExamplesProjectListByDevCenter)|
|[az devcenter project show](#ProjectGet)|Get|[Parameters](#ParametersProjectGet)|[Example](#ExamplesProjectGet)|

### <a name="CommandsInSchedule">Commands in `az devcenter schedule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az devcenter schedule list](#ScheduleList)|List|[Parameters](#ParametersScheduleList)|[Example](#ExamplesScheduleList)|
|[az devcenter schedule show](#ScheduleGet)|Get|[Parameters](#ParametersScheduleGet)|[Example](#ExamplesScheduleGet)|


## COMMAND DETAILS
### group `az devcenter artifact`
#### <a name="ArtifactsListByPath">Command `az devcenter artifact list`</a>

##### <a name="ExamplesArtifactsListByPath">Example</a>
```
az devcenter artifact list --artifact-path "{artifactPath}" --environment-name "{environmentName}" --project-name \
"myProject" --user-id "me"
```
##### <a name="ParametersArtifactsListByPath">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--artifact-path**|string|The path of the artifact.|artifact_path|artifactPath|

#### <a name="ArtifactsListByEnvironment">Command `az devcenter artifact list`</a>

##### <a name="ExamplesArtifactsListByEnvironment">Example</a>
```
az devcenter artifact list --environment-name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersArtifactsListByEnvironment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|

### group `az devcenter catalog-item`
#### <a name="CatalogItemListByProject">Command `az devcenter catalog-item list`</a>

##### <a name="ExamplesCatalogItemListByProject">Example</a>
```
az devcenter catalog-item list --project-name "myProject"
```
##### <a name="ParametersCatalogItemListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|

### group `az devcenter catalog-item`
#### <a name="CatalogItemsGet">Command `az devcenter catalog-item show`</a>

##### <a name="ExamplesCatalogItemsGet">Example</a>
```
az devcenter catalog-item show --catalog-item-id "foo" --project-name "myProject"
```
##### <a name="ParametersCatalogItemsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--catalog-item-id**|string|The unique id of the catalog item.|catalog_item_id|catalogItemId|

### group `az devcenter catalog-item-version`
#### <a name="CatalogItemVersionsListByProject">Command `az devcenter catalog-item-version list`</a>

##### <a name="ExamplesCatalogItemVersionsListByProject">Example</a>
```
az devcenter catalog-item-version list --catalog-item-id "foo" --project-name "myProject"
```
##### <a name="ParametersCatalogItemVersionsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--catalog-item-id**|string|The unique id of the catalog item.|catalog_item_id|catalogItemId|

#### <a name="CatalogItemVersionsGet">Command `az devcenter catalog-item-version show`</a>

##### <a name="ExamplesCatalogItemVersionsGet">Example</a>
```
az devcenter catalog-item-version show --catalog-item-id "foo" --project-name "myProject" --version "1.0.0"
```
##### <a name="ParametersCatalogItemVersionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--catalog-item-id**|string|The unique id of the catalog item.|catalog_item_id|catalogItemId|
|**--version**|string|The version of the catalog item.|version|version|

### group `az devcenter dev-box`
#### <a name="DevBoxListByProject">Command `az devcenter dev-box list`</a>

##### <a name="ExamplesDevBoxListByProject">Example</a>
```
az devcenter dev-box list --project-name "myProject" --user-id "me"
```
##### <a name="ParametersDevBoxListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|An OData filter clause to apply to the operation.|filter|filter|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|

#### <a name="DevBoxListByUser">Command `az devcenter dev-box list`</a>

##### <a name="ExamplesDevBoxListByUser">Example</a>
```
az devcenter dev-box list --user-id "me"
```
##### <a name="ParametersDevBoxListByUser">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|An OData filter clause to apply to the operation.|filter|filter|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|

#### <a name="DevBoxList">Command `az devcenter dev-box list`</a>

##### <a name="ExamplesDevBoxList">Example</a>
```
az devcenter dev-box list
```
##### <a name="ParametersDevBoxList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|An OData filter clause to apply to the operation.|filter|filter|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|

#### <a name="DevBoxGet">Command `az devcenter dev-box show`</a>

##### <a name="ExamplesDevBoxGet">Example</a>
```
az devcenter dev-box show --name "MyDevBox" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersDevBoxGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--dev-box-name**|string|The name of a Dev Box.|dev_box_name|devBoxName|

#### <a name="DevBoxCreate">Command `az devcenter dev-box create`</a>

##### <a name="ExamplesDevBoxCreate">Example</a>
```
az devcenter dev-box create --pool-name "LargeDevWorkStationPool" --name "MyDevBox" --project-name "myProject" \
--user-id "me"
```
##### <a name="ParametersDevBoxCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--dev-box-name**|string|The name of a Dev Box.|dev_box_name|devBoxName|
|**--pool-name**|string|The name of the Dev Box pool this machine belongs to.|pool_name|poolName|
|**--local-administrator**|choice|Indicates whether the owner of the Dev Box is a local administrator.|local_administrator|localAdministrator|

#### <a name="DevBoxDelete">Command `az devcenter dev-box delete`</a>

##### <a name="ExamplesDevBoxDelete">Example</a>
```
az devcenter dev-box delete --name "MyDevBox" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersDevBoxDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--dev-box-name**|string|The name of a Dev Box.|dev_box_name|devBoxName|

#### <a name="DevBoxGetRemoteConnection">Command `az devcenter dev-box show-remote-connection`</a>

##### <a name="ExamplesDevBoxGetRemoteConnection">Example</a>
```
az devcenter dev-box show-remote-connection --name "MyDevBox" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersDevBoxGetRemoteConnection">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--dev-box-name**|string|The name of a Dev Box.|dev_box_name|devBoxName|

#### <a name="DevBoxStart">Command `az devcenter dev-box start`</a>

##### <a name="ExamplesDevBoxStart">Example</a>
```
az devcenter dev-box start --name "MyDevBox" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersDevBoxStart">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--dev-box-name**|string|The name of a Dev Box.|dev_box_name|devBoxName|

#### <a name="DevBoxStop">Command `az devcenter dev-box stop`</a>

##### <a name="ExamplesDevBoxStop">Example</a>
```
az devcenter dev-box stop --name "MyDevBox" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersDevBoxStop">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--dev-box-name**|string|The name of a Dev Box.|dev_box_name|devBoxName|

### group `az devcenter environment`
#### <a name="EnvironmentsListByProject">Command `az devcenter environment list`</a>

##### <a name="ExamplesEnvironmentsListByProject">Example</a>
```
az devcenter environment list --project-name "myProject"
```
##### <a name="ParametersEnvironmentsListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|

#### <a name="EnvironmentsGet">Command `az devcenter environment show`</a>

##### <a name="ExamplesEnvironmentsGet">Example</a>
```
az devcenter environment show --name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|

#### <a name="EnvironmentsCreateOrUpdate#Create">Command `az devcenter environment create`</a>

##### <a name="ExamplesEnvironmentsCreateOrUpdate#Create">Example</a>
```
az devcenter environment create --description "Personal Dev Environment" --catalog-item-name "helloworld" \
--catalog-name "main" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"storageAccount\
Type\\":\\"Standard_LRS\\"}" --name "{environmentName}" --project-name "myProject" --user-id "me"
az devcenter environment create --description "Personal Dev Environment" --catalog-item-name "helloworld" \
--catalog-name "main" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"storageAccount\
Type\\":\\"Standard_LRS\\"}" --scheduled-tasks "{\\"autoExpire\\":{\\"type\\":\\"AutoExpire\\",\\"startTime\\":\\"2022-\
01-01T00:01:00Z\\"}}" --name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--description**|string|Description of the Environment.|description|description|
|**--catalog-name**|string|Name of the catalog.|catalog_name|catalogName|
|**--catalog-item-name**|string|Name of the catalog item.|catalog_item_name|catalogItemName|
|**--parameters**|any|Parameters object for the deploy action|parameters|parameters|
|**--scheduled-tasks**|dictionary|Set of supported scheduled tasks to help manage cost.|scheduled_tasks|scheduledTasks|
|**--tags**|dictionary|Key value pairs that will be applied to resources deployed in this environment as tags.|tags|tags|
|**--environment-type**|string|Environment type.|environment_type|environmentType|
|**--owner**|string|Identifier of the owner of this Environment.|owner|owner|

#### <a name="EnvironmentsUpdate">Command `az devcenter environment update`</a>

##### <a name="ExamplesEnvironmentsUpdate">Example</a>
```
az devcenter environment update --description "Personal Dev Environment 2" --name "{environmentName}" --project-name \
"myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--description**|string|Description of the Environment.|description|description|
|**--catalog-name**|string|Name of the catalog.|catalog_name|catalogName|
|**--catalog-item-name**|string|Name of the catalog item.|catalog_item_name|catalogItemName|
|**--parameters**|any|Parameters object for the deploy action|parameters|parameters|
|**--scheduled-tasks**|dictionary|Set of supported scheduled tasks to help manage cost.|scheduled_tasks|scheduledTasks|
|**--tags**|dictionary|Key value pairs that will be applied to resources deployed in this environment as tags.|tags|tags|

#### <a name="EnvironmentsDelete">Command `az devcenter environment delete`</a>

##### <a name="ExamplesEnvironmentsDelete">Example</a>
```
az devcenter environment delete --name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|

#### <a name="EnvironmentsCustomAction">Command `az devcenter environment custom-action`</a>

##### <a name="ExamplesEnvironmentsCustomAction">Example</a>
```
az devcenter environment custom-action --action-id "someCustomActionId" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsCustomAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--action-id**|string|The Catalog Item action id to execute|action_id|actionId|
|**--parameters**|any|Parameters object for the Action|parameters|parameters|

#### <a name="EnvironmentsDeleteAction">Command `az devcenter environment delete-action`</a>

##### <a name="ExamplesEnvironmentsDeleteAction">Example</a>
```
az devcenter environment delete-action --action-id "delete" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"stora\
geAccountType\\":\\"Standard_LRS\\"}" --name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsDeleteAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--action-id**|string|The Catalog Item action id to execute|action_id|actionId|
|**--parameters**|any|Parameters object for the Action|parameters|parameters|

#### <a name="EnvironmentsDeployAction">Command `az devcenter environment deploy-action`</a>

##### <a name="ExamplesEnvironmentsDeployAction">Example</a>
```
az devcenter environment deploy-action --action-id "deploy" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"stora\
geAccountType\\":\\"Standard_LRS\\"}" --name "{environmentName}" --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsDeployAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|
|**--environment-name**|string|The name of the environment.|environment_name|environmentName|
|**--action-id**|string|The Catalog Item action id to execute|action_id|actionId|
|**--parameters**|any|Parameters object for the Action|parameters|parameters|

#### <a name="EnvironmentsListByProjectByUser">Command `az devcenter environment list-by-project`</a>

##### <a name="ExamplesEnvironmentsListByProjectByUser">Example</a>
```
az devcenter environment list-by-project --project-name "myProject" --user-id "me"
```
##### <a name="ParametersEnvironmentsListByProjectByUser">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--user-id**|string|The AAD object id of the user. If value is 'me', the identity is taken from the authentication context|user_id|userId|

### group `az devcenter environment-type`
#### <a name="EnvironmentTypeListByProject">Command `az devcenter environment-type list`</a>

##### <a name="ExamplesEnvironmentTypeListByProject">Example</a>
```
az devcenter environment-type list --project-name "myProject"
```
##### <a name="ParametersEnvironmentTypeListByProject">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|

### group `az devcenter pool`
#### <a name="PoolList">Command `az devcenter pool list`</a>

##### <a name="ExamplesPoolList">Example</a>
```
az devcenter pool list --project-name "myProject"
```
##### <a name="ParametersPoolList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--filter**|string|An OData filter clause to apply to the operation.|filter|filter|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|

#### <a name="PoolGet">Command `az devcenter pool show`</a>

##### <a name="ExamplesPoolGet">Example</a>
```
az devcenter pool show --name "DevPool" --project-name "myProject"
```
##### <a name="ParametersPoolGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--pool-name**|string|The name of a pool of Dev Boxes.|pool_name|poolName|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|

### group `az devcenter project`
#### <a name="ProjectListByDevCenter">Command `az devcenter project list`</a>

##### <a name="ExamplesProjectListByDevCenter">Example</a>
```
az devcenter project list
```
##### <a name="ParametersProjectListByDevCenter">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--filter**|string|An OData filter clause to apply to the operation.|filter|filter|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|

#### <a name="ProjectGet">Command `az devcenter project show`</a>

##### <a name="ExamplesProjectGet">Example</a>
```
az devcenter project show --name "myProject"
```
##### <a name="ParametersProjectGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|

### group `az devcenter schedule`
#### <a name="ScheduleList">Command `az devcenter schedule list`</a>

##### <a name="ExamplesScheduleList">Example</a>
```
az devcenter schedule list --pool-name "DevPool" --project-name "myProject"
```
##### <a name="ParametersScheduleList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--top**|integer|The maximum number of resources to return from the operation. Example: 'top=10'.|top|top|
|**--filter**|string|An OData filter clause to apply to the operation.|filter|filter|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--pool-name**|string|The name of a pool of Dev Boxes.|pool_name|poolName|

#### <a name="ScheduleGet">Command `az devcenter schedule show`</a>

##### <a name="ExamplesScheduleGet">Example</a>
```
az devcenter schedule show --pool-name "DevPool" --project-name "myProject" --name "{scheduleName}"
```
##### <a name="ParametersScheduleGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--project-name**|string|The DevCenter Project upon which to execute operations.|project_name|projectName|
|**--pool-name**|string|The name of a pool of Dev Boxes.|pool_name|poolName|
|**--schedule-name**|string|The name of a schedule.|schedule_name|scheduleName|
