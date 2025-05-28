# Azure CLI Module Creation Report

## EXTENSION

|CLI Extension|Command Groups|
|---------|------------|
|az datafactory|[groups](#CommandGroups)

## GROUPS

### <a name="CommandGroups">Command groups in `az datafactory` extension </a>

|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az datafactory|Factories|[commands](#CommandsInFactories)|
|az datafactory activity-run|ActivityRuns|[commands](#CommandsInActivityRuns)|
|az datafactory dataset|Datasets|[commands](#CommandsInDatasets)|
|az datafactory integration-runtime|IntegrationRuntimes|[commands](#CommandsInIntegrationRuntimes)|
|az datafactory integration-runtime-node|IntegrationRuntimeNodes|[commands](#CommandsInIntegrationRuntimeNodes)|
|az datafactory linked-service|LinkedServices|[commands](#CommandsInLinkedServices)|
|az datafactory managed-private-endpoint|ManagedPrivateEndpoints|[commands](#CommandsInManagedPrivateEndpoints)|
|az datafactory managed-virtual-network|ManagedVirtualNetworks|[commands](#CommandsInManagedVirtualNetworks)|
|az datafactory pipeline|Pipelines|[commands](#CommandsInPipelines)|
|az datafactory pipeline-run|PipelineRuns|[commands](#CommandsInPipelineRuns)|
|az datafactory trigger|Triggers|[commands](#CommandsInTriggers)|
|az datafactory trigger-run|TriggerRuns|[commands](#CommandsInTriggerRuns)|

## COMMANDS

### <a name="CommandsInFactories">Commands in `az datafactory` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory list](#FactoriesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersFactoriesListByResourceGroup)|[Example](#ExamplesFactoriesListByResourceGroup)|
|[az datafactory list](#FactoriesList)|List|[Parameters](#ParametersFactoriesList)|[Example](#ExamplesFactoriesList)|
|[az datafactory show](#FactoriesGet)|Get|[Parameters](#ParametersFactoriesGet)|[Example](#ExamplesFactoriesGet)|
|[az datafactory create](#FactoriesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersFactoriesCreateOrUpdate#Create)|[Example](#ExamplesFactoriesCreateOrUpdate#Create)|
|[az datafactory update](#FactoriesUpdate)|Update|[Parameters](#ParametersFactoriesUpdate)|[Example](#ExamplesFactoriesUpdate)|
|[az datafactory delete](#FactoriesDelete)|Delete|[Parameters](#ParametersFactoriesDelete)|[Example](#ExamplesFactoriesDelete)|
|[az datafactory configure-factory-repo](#FactoriesConfigureFactoryRepo)|ConfigureFactoryRepo|[Parameters](#ParametersFactoriesConfigureFactoryRepo)|[Example](#ExamplesFactoriesConfigureFactoryRepo)|
|[az datafactory get-data-plane-access](#FactoriesGetDataPlaneAccess)|GetDataPlaneAccess|[Parameters](#ParametersFactoriesGetDataPlaneAccess)|[Example](#ExamplesFactoriesGetDataPlaneAccess)|
|[az datafactory get-git-hub-access-token](#FactoriesGetGitHubAccessToken)|GetGitHubAccessToken|[Parameters](#ParametersFactoriesGetGitHubAccessToken)|[Example](#ExamplesFactoriesGetGitHubAccessToken)|

### <a name="CommandsInActivityRuns">Commands in `az datafactory activity-run` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory activity-run query-by-pipeline-run](#ActivityRunsQueryByPipelineRun)|QueryByPipelineRun|[Parameters](#ParametersActivityRunsQueryByPipelineRun)|[Example](#ExamplesActivityRunsQueryByPipelineRun)|

### <a name="CommandsInDatasets">Commands in `az datafactory dataset` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory dataset list](#DatasetsListByFactory)|ListByFactory|[Parameters](#ParametersDatasetsListByFactory)|[Example](#ExamplesDatasetsListByFactory)|
|[az datafactory dataset show](#DatasetsGet)|Get|[Parameters](#ParametersDatasetsGet)|[Example](#ExamplesDatasetsGet)|
|[az datafactory dataset create](#DatasetsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDatasetsCreateOrUpdate#Create)|[Example](#ExamplesDatasetsCreateOrUpdate#Create)|
|[az datafactory dataset update](#DatasetsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersDatasetsCreateOrUpdate#Update)|Not Found|
|[az datafactory dataset delete](#DatasetsDelete)|Delete|[Parameters](#ParametersDatasetsDelete)|[Example](#ExamplesDatasetsDelete)|

### <a name="CommandsInIntegrationRuntimes">Commands in `az datafactory integration-runtime` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory integration-runtime list](#IntegrationRuntimesListByFactory)|ListByFactory|[Parameters](#ParametersIntegrationRuntimesListByFactory)|[Example](#ExamplesIntegrationRuntimesListByFactory)|
|[az datafactory integration-runtime show](#IntegrationRuntimesGet)|Get|[Parameters](#ParametersIntegrationRuntimesGet)|[Example](#ExamplesIntegrationRuntimesGet)|
|[az datafactory integration-runtime linked-integration-runtime create](#IntegrationRuntimesCreateLinkedIntegrationRuntime)|CreateLinkedIntegrationRuntime|[Parameters](#ParametersIntegrationRuntimesCreateLinkedIntegrationRuntime)|[Example](#ExamplesIntegrationRuntimesCreateLinkedIntegrationRuntime)|
|[az datafactory integration-runtime managed create](#IntegrationRuntimesCreateOrUpdate#Create#Managed)|CreateOrUpdate#Create#Managed|[Parameters](#ParametersIntegrationRuntimesCreateOrUpdate#Create#Managed)|Not Found|
|[az datafactory integration-runtime self-hosted create](#IntegrationRuntimesCreateOrUpdate#Create#SelfHosted)|CreateOrUpdate#Create#SelfHosted|[Parameters](#ParametersIntegrationRuntimesCreateOrUpdate#Create#SelfHosted)|[Example](#ExamplesIntegrationRuntimesCreateOrUpdate#Create#SelfHosted)|
|[az datafactory integration-runtime update](#IntegrationRuntimesUpdate)|Update|[Parameters](#ParametersIntegrationRuntimesUpdate)|[Example](#ExamplesIntegrationRuntimesUpdate)|
|[az datafactory integration-runtime delete](#IntegrationRuntimesDelete)|Delete|[Parameters](#ParametersIntegrationRuntimesDelete)|[Example](#ExamplesIntegrationRuntimesDelete)|
|[az datafactory integration-runtime get-connection-info](#IntegrationRuntimesGetConnectionInfo)|GetConnectionInfo|[Parameters](#ParametersIntegrationRuntimesGetConnectionInfo)|[Example](#ExamplesIntegrationRuntimesGetConnectionInfo)|
|[az datafactory integration-runtime get-monitoring-data](#IntegrationRuntimesGetMonitoringData)|GetMonitoringData|[Parameters](#ParametersIntegrationRuntimesGetMonitoringData)|[Example](#ExamplesIntegrationRuntimesGetMonitoringData)|
|[az datafactory integration-runtime get-status](#IntegrationRuntimesGetStatus)|GetStatus|[Parameters](#ParametersIntegrationRuntimesGetStatus)|[Example](#ExamplesIntegrationRuntimesGetStatus)|
|[az datafactory integration-runtime list-auth-key](#IntegrationRuntimesListAuthKeys)|ListAuthKeys|[Parameters](#ParametersIntegrationRuntimesListAuthKeys)|[Example](#ExamplesIntegrationRuntimesListAuthKeys)|
|[az datafactory integration-runtime regenerate-auth-key](#IntegrationRuntimesRegenerateAuthKey)|RegenerateAuthKey|[Parameters](#ParametersIntegrationRuntimesRegenerateAuthKey)|[Example](#ExamplesIntegrationRuntimesRegenerateAuthKey)|
|[az datafactory integration-runtime remove-link](#IntegrationRuntimesRemoveLinks)|RemoveLinks|[Parameters](#ParametersIntegrationRuntimesRemoveLinks)|[Example](#ExamplesIntegrationRuntimesRemoveLinks)|
|[az datafactory integration-runtime start](#IntegrationRuntimesStart)|Start|[Parameters](#ParametersIntegrationRuntimesStart)|[Example](#ExamplesIntegrationRuntimesStart)|
|[az datafactory integration-runtime stop](#IntegrationRuntimesStop)|Stop|[Parameters](#ParametersIntegrationRuntimesStop)|[Example](#ExamplesIntegrationRuntimesStop)|
|[az datafactory integration-runtime sync-credentials](#IntegrationRuntimesSyncCredentials)|SyncCredentials|[Parameters](#ParametersIntegrationRuntimesSyncCredentials)|[Example](#ExamplesIntegrationRuntimesSyncCredentials)|
|[az datafactory integration-runtime upgrade](#IntegrationRuntimesUpgrade)|Upgrade|[Parameters](#ParametersIntegrationRuntimesUpgrade)|[Example](#ExamplesIntegrationRuntimesUpgrade)|

### <a name="CommandsInIntegrationRuntimeNodes">Commands in `az datafactory integration-runtime-node` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory integration-runtime-node show](#IntegrationRuntimeNodesGet)|Get|[Parameters](#ParametersIntegrationRuntimeNodesGet)|[Example](#ExamplesIntegrationRuntimeNodesGet)|
|[az datafactory integration-runtime-node update](#IntegrationRuntimeNodesUpdate)|Update|[Parameters](#ParametersIntegrationRuntimeNodesUpdate)|[Example](#ExamplesIntegrationRuntimeNodesUpdate)|
|[az datafactory integration-runtime-node delete](#IntegrationRuntimeNodesDelete)|Delete|[Parameters](#ParametersIntegrationRuntimeNodesDelete)|[Example](#ExamplesIntegrationRuntimeNodesDelete)|
|[az datafactory integration-runtime-node get-ip-address](#IntegrationRuntimeNodesGetIpAddress)|GetIpAddress|[Parameters](#ParametersIntegrationRuntimeNodesGetIpAddress)|[Example](#ExamplesIntegrationRuntimeNodesGetIpAddress)|

### <a name="CommandsInLinkedServices">Commands in `az datafactory linked-service` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory linked-service list](#LinkedServicesListByFactory)|ListByFactory|[Parameters](#ParametersLinkedServicesListByFactory)|[Example](#ExamplesLinkedServicesListByFactory)|
|[az datafactory linked-service show](#LinkedServicesGet)|Get|[Parameters](#ParametersLinkedServicesGet)|[Example](#ExamplesLinkedServicesGet)|
|[az datafactory linked-service create](#LinkedServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersLinkedServicesCreateOrUpdate#Create)|[Example](#ExamplesLinkedServicesCreateOrUpdate#Create)|
|[az datafactory linked-service update](#LinkedServicesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersLinkedServicesCreateOrUpdate#Update)|Not Found|
|[az datafactory linked-service delete](#LinkedServicesDelete)|Delete|[Parameters](#ParametersLinkedServicesDelete)|[Example](#ExamplesLinkedServicesDelete)|

### <a name="CommandsInManagedPrivateEndpoints">Commands in `az datafactory managed-private-endpoint` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory managed-private-endpoint list](#ManagedPrivateEndpointsListByFactory)|ListByFactory|[Parameters](#ParametersManagedPrivateEndpointsListByFactory)|[Example](#ExamplesManagedPrivateEndpointsListByFactory)|
|[az datafactory managed-private-endpoint show](#ManagedPrivateEndpointsGet)|Get|[Parameters](#ParametersManagedPrivateEndpointsGet)|[Example](#ExamplesManagedPrivateEndpointsGet)|
|[az datafactory managed-private-endpoint create](#ManagedPrivateEndpointsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersManagedPrivateEndpointsCreateOrUpdate#Create)|[Example](#ExamplesManagedPrivateEndpointsCreateOrUpdate#Create)|
|[az datafactory managed-private-endpoint update](#ManagedPrivateEndpointsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersManagedPrivateEndpointsCreateOrUpdate#Update)|Not Found|
|[az datafactory managed-private-endpoint delete](#ManagedPrivateEndpointsDelete)|Delete|[Parameters](#ParametersManagedPrivateEndpointsDelete)|[Example](#ExamplesManagedPrivateEndpointsDelete)|

### <a name="CommandsInManagedVirtualNetworks">Commands in `az datafactory managed-virtual-network` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory managed-virtual-network list](#ManagedVirtualNetworksListByFactory)|ListByFactory|[Parameters](#ParametersManagedVirtualNetworksListByFactory)|[Example](#ExamplesManagedVirtualNetworksListByFactory)|
|[az datafactory managed-virtual-network show](#ManagedVirtualNetworksGet)|Get|[Parameters](#ParametersManagedVirtualNetworksGet)|[Example](#ExamplesManagedVirtualNetworksGet)|
|[az datafactory managed-virtual-network create](#ManagedVirtualNetworksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersManagedVirtualNetworksCreateOrUpdate#Create)|[Example](#ExamplesManagedVirtualNetworksCreateOrUpdate#Create)|
|[az datafactory managed-virtual-network update](#ManagedVirtualNetworksCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersManagedVirtualNetworksCreateOrUpdate#Update)|Not Found|

### <a name="CommandsInPipelines">Commands in `az datafactory pipeline` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory pipeline list](#PipelinesListByFactory)|ListByFactory|[Parameters](#ParametersPipelinesListByFactory)|[Example](#ExamplesPipelinesListByFactory)|
|[az datafactory pipeline show](#PipelinesGet)|Get|[Parameters](#ParametersPipelinesGet)|[Example](#ExamplesPipelinesGet)|
|[az datafactory pipeline create](#PipelinesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersPipelinesCreateOrUpdate#Create)|[Example](#ExamplesPipelinesCreateOrUpdate#Create)|
|[az datafactory pipeline update](#PipelinesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersPipelinesCreateOrUpdate#Update)|[Example](#ExamplesPipelinesCreateOrUpdate#Update)|
|[az datafactory pipeline delete](#PipelinesDelete)|Delete|[Parameters](#ParametersPipelinesDelete)|[Example](#ExamplesPipelinesDelete)|
|[az datafactory pipeline create-run](#PipelinesCreateRun)|CreateRun|[Parameters](#ParametersPipelinesCreateRun)|[Example](#ExamplesPipelinesCreateRun)|

### <a name="CommandsInPipelineRuns">Commands in `az datafactory pipeline-run` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory pipeline-run show](#PipelineRunsGet)|Get|[Parameters](#ParametersPipelineRunsGet)|[Example](#ExamplesPipelineRunsGet)|
|[az datafactory pipeline-run cancel](#PipelineRunsCancel)|Cancel|[Parameters](#ParametersPipelineRunsCancel)|[Example](#ExamplesPipelineRunsCancel)|
|[az datafactory pipeline-run query-by-factory](#PipelineRunsQueryByFactory)|QueryByFactory|[Parameters](#ParametersPipelineRunsQueryByFactory)|[Example](#ExamplesPipelineRunsQueryByFactory)|

### <a name="CommandsInTriggers">Commands in `az datafactory trigger` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory trigger list](#TriggersListByFactory)|ListByFactory|[Parameters](#ParametersTriggersListByFactory)|[Example](#ExamplesTriggersListByFactory)|
|[az datafactory trigger show](#TriggersGet)|Get|[Parameters](#ParametersTriggersGet)|[Example](#ExamplesTriggersGet)|
|[az datafactory trigger create](#TriggersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersTriggersCreateOrUpdate#Create)|[Example](#ExamplesTriggersCreateOrUpdate#Create)|
|[az datafactory trigger update](#TriggersCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersTriggersCreateOrUpdate#Update)|Not Found|
|[az datafactory trigger delete](#TriggersDelete)|Delete|[Parameters](#ParametersTriggersDelete)|[Example](#ExamplesTriggersDelete)|
|[az datafactory trigger get-event-subscription-status](#TriggersGetEventSubscriptionStatus)|GetEventSubscriptionStatus|[Parameters](#ParametersTriggersGetEventSubscriptionStatus)|[Example](#ExamplesTriggersGetEventSubscriptionStatus)|
|[az datafactory trigger query-by-factory](#TriggersQueryByFactory)|QueryByFactory|[Parameters](#ParametersTriggersQueryByFactory)|[Example](#ExamplesTriggersQueryByFactory)|
|[az datafactory trigger start](#TriggersStart)|Start|[Parameters](#ParametersTriggersStart)|[Example](#ExamplesTriggersStart)|
|[az datafactory trigger stop](#TriggersStop)|Stop|[Parameters](#ParametersTriggersStop)|[Example](#ExamplesTriggersStop)|
|[az datafactory trigger subscribe-to-event](#TriggersSubscribeToEvents)|SubscribeToEvents|[Parameters](#ParametersTriggersSubscribeToEvents)|[Example](#ExamplesTriggersSubscribeToEvents)|
|[az datafactory trigger unsubscribe-from-event](#TriggersUnsubscribeFromEvents)|UnsubscribeFromEvents|[Parameters](#ParametersTriggersUnsubscribeFromEvents)|[Example](#ExamplesTriggersUnsubscribeFromEvents)|

### <a name="CommandsInTriggerRuns">Commands in `az datafactory trigger-run` group</a>

|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datafactory trigger-run cancel](#TriggerRunsCancel)|Cancel|[Parameters](#ParametersTriggerRunsCancel)|[Example](#ExamplesTriggerRunsCancel)|
|[az datafactory trigger-run query-by-factory](#TriggerRunsQueryByFactory)|QueryByFactory|[Parameters](#ParametersTriggerRunsQueryByFactory)|[Example](#ExamplesTriggerRunsQueryByFactory)|
|[az datafactory trigger-run rerun](#TriggerRunsRerun)|Rerun|[Parameters](#ParametersTriggerRunsRerun)|[Example](#ExamplesTriggerRunsRerun)|

## COMMAND DETAILS

### group `az datafactory`

#### <a name="FactoriesListByResourceGroup">Command `az datafactory list`</a>

##### <a name="ExamplesFactoriesListByResourceGroup">Example</a>

```
az datafactory list --resource-group "exampleResourceGroup"
```

##### <a name="ParametersFactoriesListByResourceGroup">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

#### <a name="FactoriesList">Command `az datafactory list`</a>

##### <a name="ExamplesFactoriesList">Example</a>

```
az datafactory list
```

##### <a name="ParametersFactoriesList">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="FactoriesGet">Command `az datafactory show`</a>

##### <a name="ExamplesFactoriesGet">Example</a>

```
az datafactory show --name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersFactoriesGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--if-none-match**|string|ETag of the factory entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="FactoriesCreateOrUpdate#Create">Command `az datafactory create`</a>

##### <a name="ExamplesFactoriesCreateOrUpdate#Create">Example</a>

```
az datafactory create --location "East US" --name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersFactoriesCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--if-match**|string|ETag of the factory entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--location**|string|The resource location.|location|location|
|**--public-network-access**|string|Whether or not public network access is allowed for the data factory.|public_network_access|publicNetworkAccess|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|FactoryVSTSConfiguration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|FactoryGitHubConfiguration|
|**--global-parameters**|dictionary|List of parameters for factory.|global_parameters|globalParameters|

#### <a name="FactoriesUpdate">Command `az datafactory update`</a>

##### <a name="ExamplesFactoriesUpdate">Example</a>

```
az datafactory update --name "exampleFactoryName" --tags exampleTag="exampleValue" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersFactoriesUpdate">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--public-network-access**|string|Whether or not public network access is allowed for the data factory.|public_network_access|publicNetworkAccess|
|**--tags**|dictionary|The resource tags.|tags|tags|

#### <a name="FactoriesDelete">Command `az datafactory delete`</a>

##### <a name="ExamplesFactoriesDelete">Example</a>

```
az datafactory delete --name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersFactoriesDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="FactoriesConfigureFactoryRepo">Command `az datafactory configure-factory-repo`</a>

##### <a name="ExamplesFactoriesConfigureFactoryRepo">Example</a>

```
az datafactory configure-factory-repo --factory-resource-id "/subscriptions/12345678-1234-1234-1234-12345678abc/resourc\
eGroups/exampleResourceGroup/providers/Microsoft.DataFactory/factories/exampleFactoryName" \
--factory-vsts-configuration account-name="ADF" collaboration-branch="master" last-commit-id="" project-name="project" \
repository-name="repo" root-folder="/" tenant-id="" --location "East US"
```

##### <a name="ParametersFactoriesConfigureFactoryRepo">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location identifier.|location|locationId|
|**--factory-resource-id**|string|The factory resource id.|factory_resource_id|factoryResourceId|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|FactoryVSTSConfiguration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|FactoryGitHubConfiguration|

#### <a name="FactoriesGetDataPlaneAccess">Command `az datafactory get-data-plane-access`</a>

##### <a name="ExamplesFactoriesGetDataPlaneAccess">Example</a>

```
az datafactory get-data-plane-access --name "exampleFactoryName" --access-resource-path "" --expire-time \
"2018-11-10T09:46:20.2659347Z" --permissions "r" --profile-name "DefaultProfile" --start-time \
"2018-11-10T02:46:20.2659347Z" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersFactoriesGetDataPlaneAccess">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|permissions|permissions|
|**--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|access_resource_path|accessResourcePath|
|**--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|profile_name|profileName|
|**--start-time**|string|Start time for the token. If not specified the current time will be used.|start_time|startTime|
|**--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|expire_time|expireTime|

#### <a name="FactoriesGetGitHubAccessToken">Command `az datafactory get-git-hub-access-token`</a>

##### <a name="ExamplesFactoriesGetGitHubAccessToken">Example</a>

```
az datafactory get-git-hub-access-token --name "exampleFactoryName" --git-hub-access-code "some" \
--git-hub-access-token-base-url "some" --git-hub-client-id "some" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersFactoriesGetGitHubAccessToken">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--git-hub-access-code**|string|GitHub access code.|git_hub_access_code|gitHubAccessCode|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|git_hub_access_token_base_url|gitHubAccessTokenBaseUrl|
|**--git-hub-client-id**|string|GitHub application client ID.|git_hub_client_id|gitHubClientId|

### group `az datafactory activity-run`

#### <a name="ActivityRunsQueryByPipelineRun">Command `az datafactory activity-run query-by-pipeline-run`</a>

##### <a name="ExamplesActivityRunsQueryByPipelineRun">Example</a>

```
az datafactory activity-run query-by-pipeline-run --factory-name "exampleFactoryName" --last-updated-after \
"2018-06-16T00:36:44.3345758Z" --last-updated-before "2018-06-16T00:49:48.3686473Z" --resource-group \
"exampleResourceGroup" --run-id "2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
```

##### <a name="ParametersActivityRunsQueryByPipelineRun">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|lastUpdatedAfter|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|lastUpdatedBefore|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|orderBy|

### group `az datafactory dataset`

#### <a name="DatasetsListByFactory">Command `az datafactory dataset list`</a>

##### <a name="ExamplesDatasetsListByFactory">Example</a>

```
az datafactory dataset list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersDatasetsListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="DatasetsGet">Command `az datafactory dataset show`</a>

##### <a name="ExamplesDatasetsGet">Example</a>

```
az datafactory dataset show --name "exampleDataset" --factory-name "exampleFactoryName" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersDatasetsGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|
|**--if-none-match**|string|ETag of the dataset entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="DatasetsCreateOrUpdate#Create">Command `az datafactory dataset create`</a>

##### <a name="ExamplesDatasetsCreateOrUpdate#Create">Example</a>

```
az datafactory dataset create --properties "{\\"type\\":\\"AzureBlob\\",\\"linkedServiceName\\":{\\"type\\":\\"LinkedSe\
rviceReference\\",\\"referenceName\\":\\"exampleLinkedService\\"},\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"Str\
ing\\"},\\"MyFolderPath\\":{\\"type\\":\\"String\\"}},\\"typeProperties\\":{\\"format\\":{\\"type\\":\\"TextFormat\\"},\
\\"fileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@dataset().MyFileName\\"},\\"folderPath\\":{\\"type\\":\\"Ex\
pression\\",\\"value\\":\\"@dataset().MyFolderPath\\"}}}" --name "exampleDataset" --factory-name "exampleFactoryName" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersDatasetsCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--properties**|object|Dataset properties.|properties|properties|

#### <a name="DatasetsCreateOrUpdate#Update">Command `az datafactory dataset update`</a>

##### <a name="ParametersDatasetsCreateOrUpdate#Update">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--linked-service-name**|object|Linked service reference.|linked_service_name|linkedServiceName|
|**--description**|string|Dataset description.|description|description|
|**--structure**|any|Columns that define the structure of the dataset. Type: array (or Expression with resultType array), itemType: DatasetDataElement.|structure|structure|
|**--schema**|any|Columns that define the physical type schema of the dataset. Type: array (or Expression with resultType array), itemType: DatasetSchemaDataElement.|schema|schema|
|**--parameters**|dictionary|Parameters for dataset.|parameters|parameters|
|**--annotations**|array|List of tags that can be used for describing the Dataset.|annotations|annotations|
|**--folder**|object|The folder that this Dataset is in. If not specified, Dataset will appear at the root level.|folder|folder|

#### <a name="DatasetsDelete">Command `az datafactory dataset delete`</a>

##### <a name="ExamplesDatasetsDelete">Example</a>

```
az datafactory dataset delete --name "exampleDataset" --factory-name "exampleFactoryName" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersDatasetsDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|

### group `az datafactory integration-runtime`

#### <a name="IntegrationRuntimesListByFactory">Command `az datafactory integration-runtime list`</a>

##### <a name="ExamplesIntegrationRuntimesListByFactory">Example</a>

```
az datafactory integration-runtime list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="IntegrationRuntimesGet">Command `az datafactory integration-runtime show`</a>

##### <a name="ExamplesIntegrationRuntimesGet">Example</a>

```
az datafactory integration-runtime show --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--if-none-match**|string|ETag of the integration runtime entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="IntegrationRuntimesCreateLinkedIntegrationRuntime">Command `az datafactory integration-runtime linked-integration-runtime create`</a>

##### <a name="ExamplesIntegrationRuntimesCreateLinkedIntegrationRuntime">Example</a>

```
az datafactory integration-runtime linked-integration-runtime create --name "bfa92911-9fb6-4fbe-8f23-beae87bc1c83" \
--location "West US" --data-factory-name "e9955d6d-56ea-4be3-841c-52a12c1a9981" --subscription-id \
"061774c7-4b5a-4159-a55b-365581830283" --factory-name "exampleFactoryName" --integration-runtime-name \
"exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesCreateLinkedIntegrationRuntime">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--name**|string|The name of the linked integration runtime.|name|name|
|**--subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|subscription_id|subscriptionId|
|**--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|data_factory_name|dataFactoryName|
|**--location**|string|The location of the data factory that the linked integration runtime belongs to.|location|dataFactoryLocation|

#### <a name="IntegrationRuntimesCreateOrUpdate#Create#Managed">Command `az datafactory integration-runtime managed create`</a>

##### <a name="ParametersIntegrationRuntimesCreateOrUpdate#Create#Managed">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|Integration runtime description.|managed_description|description|
|**--compute-properties**|object|The compute resource for managed integration runtime.|managed_compute_properties|computeProperties|
|**--ssis-properties**|object|SSIS properties for managed integration runtime.|managed_ssis_properties|ssisProperties|

#### <a name="IntegrationRuntimesCreateOrUpdate#Create#SelfHosted">Command `az datafactory integration-runtime self-hosted create`</a>

##### <a name="ExamplesIntegrationRuntimesCreateOrUpdate#Create#SelfHosted">Example</a>

```
az datafactory integration-runtime self-hosted create --factory-name "exampleFactoryName" --description "A selfhosted \
integration runtime" --name "exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesCreateOrUpdate#Create#SelfHosted">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|Integration runtime description.|self_hosted_description|description|
|**--linked-info**|object|The base definition of a linked integration runtime.|self_hosted_linked_info|linkedInfo|
|**--enable-self-contained-interactive-authoring**|string|An alternative option to ensure interactive authoring function when your self-hosted integration runtime is unable to establish a connection with Azure Relay.|--enable_self_contained_interactive_authoring|enableSelfContainedInteractiveAuthoring|

#### <a name="IntegrationRuntimesUpdate">Command `az datafactory integration-runtime update`</a>

##### <a name="ExamplesIntegrationRuntimesUpdate">Example</a>

```
az datafactory integration-runtime update --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" \
--resource-group "exampleResourceGroup" --auto-update "Off" --update-delay-offset "\\"PT3H\\""
```

##### <a name="ParametersIntegrationRuntimesUpdate">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--auto-update**|choice|Enables or disables the auto-update feature of the self-hosted integration runtime. See <https://go.microsoft.com/fwlink/?linkid=854189>.|auto_update|autoUpdate|
|**--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|update_delay_offset|updateDelayOffset|

#### <a name="IntegrationRuntimesDelete">Command `az datafactory integration-runtime delete`</a>

##### <a name="ExamplesIntegrationRuntimesDelete">Example</a>

```
az datafactory integration-runtime delete --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesGetConnectionInfo">Command `az datafactory integration-runtime get-connection-info`</a>

##### <a name="ExamplesIntegrationRuntimesGetConnectionInfo">Example</a>

```
az datafactory integration-runtime get-connection-info --factory-name "exampleFactoryName" --name \
"exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesGetConnectionInfo">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesGetMonitoringData">Command `az datafactory integration-runtime get-monitoring-data`</a>

##### <a name="ExamplesIntegrationRuntimesGetMonitoringData">Example</a>

```
az datafactory integration-runtime get-monitoring-data --factory-name "exampleFactoryName" --name \
"exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesGetMonitoringData">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesGetStatus">Command `az datafactory integration-runtime get-status`</a>

##### <a name="ExamplesIntegrationRuntimesGetStatus">Example</a>

```
az datafactory integration-runtime get-status --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesGetStatus">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesListAuthKeys">Command `az datafactory integration-runtime list-auth-key`</a>

##### <a name="ExamplesIntegrationRuntimesListAuthKeys">Example</a>

```
az datafactory integration-runtime list-auth-key --factory-name "exampleFactoryName" --name \
"exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesListAuthKeys">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesRegenerateAuthKey">Command `az datafactory integration-runtime regenerate-auth-key`</a>

##### <a name="ExamplesIntegrationRuntimesRegenerateAuthKey">Example</a>

```
az datafactory integration-runtime regenerate-auth-key --factory-name "exampleFactoryName" --name \
"exampleIntegrationRuntime" --key-name "authKey2" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesRegenerateAuthKey">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--key-name**|choice|The name of the authentication key to regenerate.|key_name|keyName|

#### <a name="IntegrationRuntimesRemoveLinks">Command `az datafactory integration-runtime remove-link`</a>

##### <a name="ExamplesIntegrationRuntimesRemoveLinks">Example</a>

```
az datafactory integration-runtime remove-link --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" \
--linked-factory-name "exampleFactoryName-linked" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesRemoveLinks">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|linked_factory_name|linkedFactoryName|

#### <a name="IntegrationRuntimesStart">Command `az datafactory integration-runtime start`</a>

##### <a name="ExamplesIntegrationRuntimesStart">Example</a>

```
az datafactory integration-runtime start --factory-name "exampleFactoryName" --name "exampleManagedIntegrationRuntime" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesStart">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesStop">Command `az datafactory integration-runtime stop`</a>

##### <a name="ExamplesIntegrationRuntimesStop">Example</a>

```
az datafactory integration-runtime stop --factory-name "exampleFactoryName" --name "exampleManagedIntegrationRuntime" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesStop">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesSyncCredentials">Command `az datafactory integration-runtime sync-credentials`</a>

##### <a name="ExamplesIntegrationRuntimesSyncCredentials">Example</a>

```
az datafactory integration-runtime sync-credentials --factory-name "exampleFactoryName" --name \
"exampleIntegrationRuntime" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesSyncCredentials">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

#### <a name="IntegrationRuntimesUpgrade">Command `az datafactory integration-runtime upgrade`</a>

##### <a name="ExamplesIntegrationRuntimesUpgrade">Example</a>

```
az datafactory integration-runtime upgrade --factory-name "exampleFactoryName" --name "exampleIntegrationRuntime" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimesUpgrade">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### group `az datafactory integration-runtime-node`

#### <a name="IntegrationRuntimeNodesGet">Command `az datafactory integration-runtime-node show`</a>

##### <a name="ExamplesIntegrationRuntimeNodesGet">Example</a>

```
az datafactory integration-runtime-node show --factory-name "exampleFactoryName" --integration-runtime-name \
"exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimeNodesGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|

#### <a name="IntegrationRuntimeNodesUpdate">Command `az datafactory integration-runtime-node update`</a>

##### <a name="ExamplesIntegrationRuntimeNodesUpdate">Example</a>

```
az datafactory integration-runtime-node update --factory-name "exampleFactoryName" --integration-runtime-name \
"exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup" --concurrent-jobs-limit 2
```

##### <a name="ParametersIntegrationRuntimeNodesUpdate">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|
|**--concurrent-jobs-limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|concurrent_jobs_limit|concurrentJobsLimit|

#### <a name="IntegrationRuntimeNodesDelete">Command `az datafactory integration-runtime-node delete`</a>

##### <a name="ExamplesIntegrationRuntimeNodesDelete">Example</a>

```
az datafactory integration-runtime-node delete --factory-name "exampleFactoryName" --integration-runtime-name \
"exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimeNodesDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|

#### <a name="IntegrationRuntimeNodesGetIpAddress">Command `az datafactory integration-runtime-node get-ip-address`</a>

##### <a name="ExamplesIntegrationRuntimeNodesGetIpAddress">Example</a>

```
az datafactory integration-runtime-node get-ip-address --factory-name "exampleFactoryName" --integration-runtime-name \
"exampleIntegrationRuntime" --node-name "Node_1" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersIntegrationRuntimeNodesGetIpAddress">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|

### group `az datafactory linked-service`

#### <a name="LinkedServicesListByFactory">Command `az datafactory linked-service list`</a>

##### <a name="ExamplesLinkedServicesListByFactory">Example</a>

```
az datafactory linked-service list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersLinkedServicesListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="LinkedServicesGet">Command `az datafactory linked-service show`</a>

##### <a name="ExamplesLinkedServicesGet">Example</a>

```
az datafactory linked-service show --factory-name "exampleFactoryName" --name "exampleLinkedService" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersLinkedServicesGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|
|**--if-none-match**|string|ETag of the linked service entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="LinkedServicesCreateOrUpdate#Create">Command `az datafactory linked-service create`</a>

##### <a name="ExamplesLinkedServicesCreateOrUpdate#Create">Example</a>

```
az datafactory linked-service create --factory-name "exampleFactoryName" --properties "{\\"type\\":\\"AzureStorage\\",\
\\"typeProperties\\":{\\"connectionString\\":{\\"type\\":\\"SecureString\\",\\"value\\":\\"DefaultEndpointsProtocol=htt\
ps;AccountName=examplestorageaccount;AccountKey=<storage key>\\"}}}" --name "exampleLinkedService" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersLinkedServicesCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--properties**|object|Properties of linked service.|properties|properties|

#### <a name="LinkedServicesCreateOrUpdate#Update">Command `az datafactory linked-service update`</a>

##### <a name="ParametersLinkedServicesCreateOrUpdate#Update">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--connect-via**|object|The integration runtime reference.|connect_via|connectVia|
|**--description**|string|Linked service description.|description|description|
|**--parameters**|dictionary|Parameters for linked service.|parameters|parameters|
|**--annotations**|array|List of tags that can be used for describing the linked service.|annotations|annotations|

#### <a name="LinkedServicesDelete">Command `az datafactory linked-service delete`</a>

##### <a name="ExamplesLinkedServicesDelete">Example</a>

```
az datafactory linked-service delete --factory-name "exampleFactoryName" --name "exampleLinkedService" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersLinkedServicesDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|

### group `az datafactory managed-private-endpoint`

#### <a name="ManagedPrivateEndpointsListByFactory">Command `az datafactory managed-private-endpoint list`</a>

##### <a name="ExamplesManagedPrivateEndpointsListByFactory">Example</a>

```
az datafactory managed-private-endpoint list --factory-name "exampleFactoryName" --managed-virtual-network-name \
"exampleManagedVirtualNetworkName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersManagedPrivateEndpointsListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|

#### <a name="ManagedPrivateEndpointsGet">Command `az datafactory managed-private-endpoint show`</a>

##### <a name="ExamplesManagedPrivateEndpointsGet">Example</a>

```
az datafactory managed-private-endpoint show --factory-name "exampleFactoryName" --name "exampleManagedPrivateEndpointN\
ame" --managed-virtual-network-name "exampleManagedVirtualNetworkName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersManagedPrivateEndpointsGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--managed-private-endpoint-name**|string|Managed private endpoint name|managed_private_endpoint_name|managedPrivateEndpointName|
|**--if-none-match**|string|ETag of the managed private endpoint entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="ManagedPrivateEndpointsCreateOrUpdate#Create">Command `az datafactory managed-private-endpoint create`</a>

##### <a name="ExamplesManagedPrivateEndpointsCreateOrUpdate#Create">Example</a>

```
az datafactory managed-private-endpoint create --factory-name "exampleFactoryName" --group-id "blob" \
--private-link-resource-id "/subscriptions/12345678-1234-1234-1234-12345678abc/resourceGroups/exampleResourceGroup/prov\
iders/Microsoft.Storage/storageAccounts/exampleBlobStorage" --name "exampleManagedPrivateEndpointName" \
--managed-virtual-network-name "exampleManagedVirtualNetworkName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersManagedPrivateEndpointsCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--managed-private-endpoint-name**|string|Managed private endpoint name|managed_private_endpoint_name|managedPrivateEndpointName|
|**--if-match**|string|ETag of the managed private endpoint entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--fqdns**|array|Fully qualified domain names|fqdns|fqdns|
|**--group-id**|string|The groupId to which the managed private endpoint is created|group_id|groupId|
|**--private-link-resource-id**|string|The ARM resource ID of the resource to which the managed private endpoint is created|private_link_resource_id|privateLinkResourceId|

#### <a name="ManagedPrivateEndpointsCreateOrUpdate#Update">Command `az datafactory managed-private-endpoint update`</a>

##### <a name="ParametersManagedPrivateEndpointsCreateOrUpdate#Update">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--managed-private-endpoint-name**|string|Managed private endpoint name|managed_private_endpoint_name|managedPrivateEndpointName|
|**--if-match**|string|ETag of the managed private endpoint entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--fqdns**|array|Fully qualified domain names|fqdns|fqdns|
|**--group-id**|string|The groupId to which the managed private endpoint is created|group_id|groupId|
|**--private-link-resource-id**|string|The ARM resource ID of the resource to which the managed private endpoint is created|private_link_resource_id|privateLinkResourceId|

#### <a name="ManagedPrivateEndpointsDelete">Command `az datafactory managed-private-endpoint delete`</a>

##### <a name="ExamplesManagedPrivateEndpointsDelete">Example</a>

```
az datafactory managed-private-endpoint delete --factory-name "exampleFactoryName" --name \
"exampleManagedPrivateEndpointName" --managed-virtual-network-name "exampleManagedVirtualNetworkName" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersManagedPrivateEndpointsDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--managed-private-endpoint-name**|string|Managed private endpoint name|managed_private_endpoint_name|managedPrivateEndpointName|

### group `az datafactory managed-virtual-network`

#### <a name="ManagedVirtualNetworksListByFactory">Command `az datafactory managed-virtual-network list`</a>

##### <a name="ExamplesManagedVirtualNetworksListByFactory">Example</a>

```
az datafactory managed-virtual-network list --factory-name "exampleFactoryName" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersManagedVirtualNetworksListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="ManagedVirtualNetworksGet">Command `az datafactory managed-virtual-network show`</a>

##### <a name="ExamplesManagedVirtualNetworksGet">Example</a>

```
az datafactory managed-virtual-network show --factory-name "exampleFactoryName" --name "exampleManagedVirtualNetworkNam\
e" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersManagedVirtualNetworksGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--if-none-match**|string|ETag of the managed Virtual Network entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="ManagedVirtualNetworksCreateOrUpdate#Create">Command `az datafactory managed-virtual-network create`</a>

##### <a name="ExamplesManagedVirtualNetworksCreateOrUpdate#Create">Example</a>

```
az datafactory managed-virtual-network create --factory-name "exampleFactoryName" --name \
"exampleManagedVirtualNetworkName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersManagedVirtualNetworksCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--if-match**|string|ETag of the managed Virtual Network entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|

#### <a name="ManagedVirtualNetworksCreateOrUpdate#Update">Command `az datafactory managed-virtual-network update`</a>

##### <a name="ParametersManagedVirtualNetworksCreateOrUpdate#Update">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--managed-virtual-network-name**|string|Managed virtual network name|managed_virtual_network_name|managedVirtualNetworkName|
|**--if-match**|string|ETag of the managed Virtual Network entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|

### group `az datafactory pipeline`

#### <a name="PipelinesListByFactory">Command `az datafactory pipeline list`</a>

##### <a name="ExamplesPipelinesListByFactory">Example</a>

```
az datafactory pipeline list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersPipelinesListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="PipelinesGet">Command `az datafactory pipeline show`</a>

##### <a name="ExamplesPipelinesGet">Example</a>

```
az datafactory pipeline show --factory-name "exampleFactoryName" --name "examplePipeline" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersPipelinesGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--if-none-match**|string|ETag of the pipeline entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="PipelinesCreateOrUpdate#Create">Command `az datafactory pipeline create`</a>

##### <a name="ExamplesPipelinesCreateOrUpdate#Create">Example</a>

```
az datafactory pipeline create --factory-name "exampleFactoryName" --pipeline "{\\"activities\\":[{\\"name\\":\\"Exampl\
eForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{\\"activities\\":[{\\"name\\":\\"ExampleCopyActivity\
\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":\\"exampl\
econtainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"outputs\\":[\
{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@item\
()\\"},\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\"typeProperties\\":{\\"d\
ataIntegrationUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"},\\"source\\":{\\"type\\":\\"BlobSource\\"}}}],\\"isSeq\
uential\\":true,\\"items\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.OutputBlobNameList\\"}}}\
],\\"parameters\\":{\\"JobId\\":{\\"type\\":\\"String\\"},\\"OutputBlobNameList\\":{\\"type\\":\\"Array\\"}},\\"variabl\
es\\":{\\"TestVariableArray\\":{\\"type\\":\\"Array\\"}},\\"runDimensions\\":{\\"JobId\\":{\\"type\\":\\"Expression\\",\
\\"value\\":\\"@pipeline().parameters.JobId\\"}},\\"duration\\":\\"0.00:10:00\\"}" --name "examplePipeline" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersPipelinesCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--pipeline**|object|Pipeline resource definition.|pipeline|pipeline|

#### <a name="PipelinesCreateOrUpdate#Update">Command `az datafactory pipeline update`</a>

##### <a name="ExamplesPipelinesCreateOrUpdate#Update">Example</a>

```
az datafactory pipeline update --factory-name "exampleFactoryName" --description "Example description" --activities \
"[{\\"name\\":\\"ExampleForeachActivity\\",\\"type\\":\\"ForEach\\",\\"typeProperties\\":{\\"activities\\":[{\\"name\\"\
:\\"ExampleCopyActivity\\",\\"type\\":\\"Copy\\",\\"inputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"\
MyFileName\\":\\"examplecontainer.csv\\",\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDatas\
et\\"}],\\"outputs\\":[{\\"type\\":\\"DatasetReference\\",\\"parameters\\":{\\"MyFileName\\":{\\"type\\":\\"Expression\
\\",\\"value\\":\\"@item()\\"},\\"MyFolderPath\\":\\"examplecontainer\\"},\\"referenceName\\":\\"exampleDataset\\"}],\\\
"typeProperties\\":{\\"dataIntegrationUnits\\":32,\\"sink\\":{\\"type\\":\\"BlobSink\\"},\\"source\\":{\\"type\\":\\"Bl\
obSource\\"}}}],\\"isSequential\\":true,\\"items\\":{\\"type\\":\\"Expression\\",\\"value\\":\\"@pipeline().parameters.\
OutputBlobNameList\\"}}}]" --parameters "{\\"OutputBlobNameList\\":{\\"type\\":\\"Array\\"}}" --duration "0.00:10:00" \
--name "examplePipeline" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersPipelinesCreateOrUpdate#Update">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|The description of the pipeline.|description|description|
|**--activities**|array|List of activities in pipeline.|activities|activities|
|**--parameters**|dictionary|List of parameters for pipeline.|parameters|parameters|
|**--variables**|dictionary|List of variables for pipeline.|variables|variables|
|**--concurrency**|integer|The max number of concurrent runs for the pipeline.|concurrency|concurrency|
|**--annotations**|array|List of tags that can be used for describing the Pipeline.|annotations|annotations|
|**--run-dimensions**|dictionary|Dimensions emitted by Pipeline.|run_dimensions|runDimensions|
|**--duration**|any|TimeSpan value, after which an Azure Monitoring Metric is fired.|duration|duration|
|**--folder-name**|string|The name of the folder that this Pipeline is in.|folder_name|name|

#### <a name="PipelinesDelete">Command `az datafactory pipeline delete`</a>

##### <a name="ExamplesPipelinesDelete">Example</a>

```
az datafactory pipeline delete --factory-name "exampleFactoryName" --name "examplePipeline" --resource-group \
"exampleResourceGroup"
```

##### <a name="ParametersPipelinesDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|

#### <a name="PipelinesCreateRun">Command `az datafactory pipeline create-run`</a>

##### <a name="ExamplesPipelinesCreateRun">Example</a>

```
az datafactory pipeline create-run --factory-name "exampleFactoryName" --parameters "{\\"OutputBlobNameList\\":[\\"exam\
pleoutput.csv\\"]}" --name "examplePipeline" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersPipelinesCreateRun">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--reference-pipeline-run-id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|reference_pipeline_run_id|referencePipelineRunId|
|**--is-recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|is_recovery|isRecovery|
|**--start-activity-name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|start_activity_name|startActivityName|
|**--start-from-failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|start_from_failure|startFromFailure|
|**--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|parameters|parameters|

### group `az datafactory pipeline-run`

#### <a name="PipelineRunsGet">Command `az datafactory pipeline-run show`</a>

##### <a name="ExamplesPipelineRunsGet">Example</a>

```
az datafactory pipeline-run show --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --run-id \
"2f7fdb90-5df1-4b8e-ac2f-064cfa58202b"
```

##### <a name="ParametersPipelineRunsGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|

#### <a name="PipelineRunsCancel">Command `az datafactory pipeline-run cancel`</a>

##### <a name="ExamplesPipelineRunsCancel">Example</a>

```
az datafactory pipeline-run cancel --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" \
--run-id "16ac5348-ff82-4f95-a80d-638c1d47b721"
```

##### <a name="ParametersPipelineRunsCancel">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|
|**--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|is_recursive|isRecursive|

#### <a name="PipelineRunsQueryByFactory">Command `az datafactory pipeline-run query-by-factory`</a>

##### <a name="ExamplesPipelineRunsQueryByFactory">Example</a>

```
az datafactory pipeline-run query-by-factory --factory-name "exampleFactoryName" --filters operand="PipelineName" \
operator="Equals" values="examplePipeline" --last-updated-after "2018-06-16T00:36:44.3345758Z" --last-updated-before \
"2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersPipelineRunsQueryByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|lastUpdatedAfter|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|lastUpdatedBefore|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|orderBy|

### group `az datafactory trigger`

#### <a name="TriggersListByFactory">Command `az datafactory trigger list`</a>

##### <a name="ExamplesTriggersListByFactory">Example</a>

```
az datafactory trigger list --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersTriggersListByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

#### <a name="TriggersGet">Command `az datafactory trigger show`</a>

##### <a name="ExamplesTriggersGet">Example</a>

```
az datafactory trigger show --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --name \
"exampleTrigger"
```

##### <a name="ParametersTriggersGet">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--if-none-match**|string|ETag of the trigger entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

#### <a name="TriggersCreateOrUpdate#Create">Command `az datafactory trigger create`</a>

##### <a name="ExamplesTriggersCreateOrUpdate#Create">Example</a>

```
az datafactory trigger create --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --properties \
"{\\"type\\":\\"ScheduleTrigger\\",\\"pipelines\\":[{\\"parameters\\":{\\"OutputBlobNameList\\":[\\"exampleoutput.csv\\\
"]},\\"pipelineReference\\":{\\"type\\":\\"PipelineReference\\",\\"referenceName\\":\\"examplePipeline\\"}}],\\"typePro\
perties\\":{\\"recurrence\\":{\\"endTime\\":\\"2018-06-16T00:55:13.8441801Z\\",\\"frequency\\":\\"Minute\\",\\"interval\
\\":4,\\"startTime\\":\\"2018-06-16T00:39:13.8441801Z\\",\\"timeZone\\":\\"UTC\\"}}}" --name "exampleTrigger"
```

##### <a name="ParametersTriggersCreateOrUpdate#Create">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--properties**|object|Properties of the trigger.|properties|properties|

#### <a name="TriggersCreateOrUpdate#Update">Command `az datafactory trigger update`</a>

##### <a name="ParametersTriggersCreateOrUpdate#Update">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|Trigger description.|description|description|
|**--annotations**|array|List of tags that can be used for describing the trigger.|annotations|annotations|

#### <a name="TriggersDelete">Command `az datafactory trigger delete`</a>

##### <a name="ExamplesTriggersDelete">Example</a>

```
az datafactory trigger delete --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --name \
"exampleTrigger"
```

##### <a name="ParametersTriggersDelete">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

#### <a name="TriggersGetEventSubscriptionStatus">Command `az datafactory trigger get-event-subscription-status`</a>

##### <a name="ExamplesTriggersGetEventSubscriptionStatus">Example</a>

```
az datafactory trigger get-event-subscription-status --factory-name "exampleFactoryName" --resource-group \
"exampleResourceGroup" --name "exampleTrigger"
```

##### <a name="ParametersTriggersGetEventSubscriptionStatus">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

#### <a name="TriggersQueryByFactory">Command `az datafactory trigger query-by-factory`</a>

##### <a name="ExamplesTriggersQueryByFactory">Example</a>

```
az datafactory trigger query-by-factory --factory-name "exampleFactoryName" --parent-trigger-name "exampleTrigger" \
--resource-group "exampleResourceGroup"
```

##### <a name="ParametersTriggersQueryByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|parent_trigger_name|parentTriggerName|

#### <a name="TriggersStart">Command `az datafactory trigger start`</a>

##### <a name="ExamplesTriggersStart">Example</a>

```
az datafactory trigger start --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --name \
"exampleTrigger"
```

##### <a name="ParametersTriggersStart">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

#### <a name="TriggersStop">Command `az datafactory trigger stop`</a>

##### <a name="ExamplesTriggersStop">Example</a>

```
az datafactory trigger stop --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --name \
"exampleTrigger"
```

##### <a name="ParametersTriggersStop">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

#### <a name="TriggersSubscribeToEvents">Command `az datafactory trigger subscribe-to-event`</a>

##### <a name="ExamplesTriggersSubscribeToEvents">Example</a>

```
az datafactory trigger subscribe-to-event --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" \
--name "exampleTrigger"
```

##### <a name="ParametersTriggersSubscribeToEvents">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

#### <a name="TriggersUnsubscribeFromEvents">Command `az datafactory trigger unsubscribe-from-event`</a>

##### <a name="ExamplesTriggersUnsubscribeFromEvents">Example</a>

```
az datafactory trigger unsubscribe-from-event --factory-name "exampleFactoryName" --resource-group \
"exampleResourceGroup" --name "exampleTrigger"
```

##### <a name="ParametersTriggersUnsubscribeFromEvents">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### group `az datafactory trigger-run`

#### <a name="TriggerRunsCancel">Command `az datafactory trigger-run cancel`</a>

##### <a name="ExamplesTriggerRunsCancel">Example</a>

```
az datafactory trigger-run cancel --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --run-id \
"2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" --trigger-name "exampleTrigger"
```

##### <a name="ParametersTriggerRunsCancel">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|

#### <a name="TriggerRunsQueryByFactory">Command `az datafactory trigger-run query-by-factory`</a>

##### <a name="ExamplesTriggerRunsQueryByFactory">Example</a>

```
az datafactory trigger-run query-by-factory --factory-name "exampleFactoryName" --filters operand="TriggerName" \
operator="Equals" values="exampleTrigger" --last-updated-after "2018-06-16T00:36:44.3345758Z" --last-updated-before \
"2018-06-16T00:49:48.3686473Z" --resource-group "exampleResourceGroup"
```

##### <a name="ParametersTriggerRunsQueryByFactory">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|lastUpdatedAfter|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|lastUpdatedBefore|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|orderBy|

#### <a name="TriggerRunsRerun">Command `az datafactory trigger-run rerun`</a>

##### <a name="ExamplesTriggerRunsRerun">Example</a>

```
az datafactory trigger-run rerun --factory-name "exampleFactoryName" --resource-group "exampleResourceGroup" --run-id \
"2f7fdb90-5df1-4b8e-ac2f-064cfa58202b" --trigger-name "exampleTrigger"
```

##### <a name="ParametersTriggerRunsRerun">Parameters</a>

|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|
