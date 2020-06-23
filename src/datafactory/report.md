# Azure CLI Module Creation Report

### datafactory activity-run query-by-pipeline-run

query-by-pipeline-run a datafactory activity-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory activity-run|ActivityRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|query-by-pipeline-run|QueryByPipelineRun|

#### Parameters
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

### datafactory dataset create

create a datafactory dataset.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory dataset|Datasets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|
|**--properties**|object|Dataset properties.|properties|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|

### datafactory dataset delete

delete a datafactory dataset.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory dataset|Datasets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|

### datafactory dataset list

list a datafactory dataset.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory dataset|Datasets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

### datafactory dataset show

show a datafactory dataset.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory dataset|Datasets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--dataset-name**|string|The dataset name.|dataset_name|datasetName|
|**--if-none-match**|string|ETag of the dataset entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

### datafactory factory configure-factory-repo

configure-factory-repo a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|configure-factory-repo|ConfigureFactoryRepo|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The location identifier.|location|locationId|
|**--factory-resource-id**|string|The factory resource id.|factory_resource_id|factoryResourceId|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|FactoryVSTSConfiguration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|FactoryGitHubConfiguration|

### datafactory factory create

create a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--if-match**|string|ETag of the factory entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|FactoryVSTSConfiguration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|FactoryGitHubConfiguration|
|**--global-parameters**|dictionary|List of parameters for factory.|global_parameters|globalParameters|

### datafactory factory delete

delete a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

### datafactory factory get-data-plane-access

get-data-plane-access a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-data-plane-access|GetDataPlaneAccess|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|permissions|permissions|
|**--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|access_resource_path|accessResourcePath|
|**--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|profile_name|profileName|
|**--start-time**|string|Start time for the token. If not specified the current time will be used.|start_time|startTime|
|**--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|expire_time|expireTime|

### datafactory factory get-git-hub-access-token

get-git-hub-access-token a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-git-hub-access-token|GetGitHubAccessToken|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--git-hub-access-code**|string|GitHub access code.|git_hub_access_code|gitHubAccessCode|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|git_hub_access_token_base_url|gitHubAccessTokenBaseUrl|
|**--git-hub-client-id**|string|GitHub application client ID.|git_hub_client_id|gitHubClientId|

### datafactory factory list

list a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|

### datafactory factory show

show a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--if-none-match**|string|ETag of the factory entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

### datafactory factory update

update a datafactory factory.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory factory|Factories|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--tags**|dictionary|The resource tags.|tags|tags|

### datafactory integration-runtime delete

delete a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime get-connection-info

get-connection-info a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-connection-info|GetConnectionInfo|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime get-monitoring-data

get-monitoring-data a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-monitoring-data|GetMonitoringData|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime get-status

get-status a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-status|GetStatus|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime linked-integration-runtime create

linked-integration-runtime create a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|linked-integration-runtime create|CreateLinkedIntegrationRuntime|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--name**|string|The name of the linked integration runtime.|name|name|
|**--subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|subscription_id|subscriptionId|
|**--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|data_factory_name|dataFactoryName|
|**--location**|string|The location of the data factory that the linked integration runtime belongs to.|location|dataFactoryLocation|

### datafactory integration-runtime list

list a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

### datafactory integration-runtime list-auth-key

list-auth-key a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-auth-key|ListAuthKeys|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime managed create

managed create a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|managed create|CreateOrUpdate#Create#Managed|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|Integration runtime description.|managed_description|description|
|**--type-properties-compute-properties**|object|The compute resource for managed integration runtime.|managed_compute_properties|computeProperties|
|**--type-properties-ssis-properties**|object|SSIS properties for managed integration runtime.|managed_ssis_properties|ssisProperties|

### datafactory integration-runtime regenerate-auth-key

regenerate-auth-key a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|regenerate-auth-key|RegenerateAuthKey|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--key-name**|choice|The name of the authentication key to regenerate.|key_name|keyName|

### datafactory integration-runtime remove-link

remove-link a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|remove-link|RemoveLinks|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|linked_factory_name|linkedFactoryName|

### datafactory integration-runtime self-hosted create

self-hosted create a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|self-hosted create|CreateOrUpdate#Create#SelfHosted|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|Integration runtime description.|self_hosted_description|description|
|**--type-properties-linked-info**|object|The base definition of a linked integration runtime.|self_hosted_linked_info|linkedInfo|

### datafactory integration-runtime show

show a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--if-none-match**|string|ETag of the integration runtime entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

### datafactory integration-runtime start

start a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start|Start|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime stop

stop a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|stop|Stop|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime sync-credentials

sync-credentials a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|sync-credentials|SyncCredentials|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime update

update a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--auto-update**|choice|Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.|auto_update|autoUpdate|
|**--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|update_delay_offset|updateDelayOffset|

### datafactory integration-runtime upgrade

upgrade a datafactory integration-runtime.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime|IntegrationRuntimes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|upgrade|Upgrade|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|

### datafactory integration-runtime-node delete

delete a datafactory integration-runtime-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime-node|IntegrationRuntimeNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|

### datafactory integration-runtime-node get-ip-address

get-ip-address a datafactory integration-runtime-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime-node|IntegrationRuntimeNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-ip-address|GetIpAddress|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|

### datafactory integration-runtime-node show

show a datafactory integration-runtime-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime-node|IntegrationRuntimeNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|

### datafactory integration-runtime-node update

update a datafactory integration-runtime-node.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory integration-runtime-node|IntegrationRuntimeNodes|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|integrationRuntimeName|
|**--node-name**|string|The integration runtime node name.|node_name|nodeName|
|**--concurrent-jobs-limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|concurrent_jobs_limit|concurrentJobsLimit|

### datafactory linked-service create

create a datafactory linked-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory linked-service|LinkedServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|
|**--properties**|object|Properties of linked service.|properties|properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|

### datafactory linked-service delete

delete a datafactory linked-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory linked-service|LinkedServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|

### datafactory linked-service list

list a datafactory linked-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory linked-service|LinkedServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

### datafactory linked-service show

show a datafactory linked-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory linked-service|LinkedServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--linked-service-name**|string|The linked service name.|linked_service_name|linkedServiceName|
|**--if-none-match**|string|ETag of the linked service entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

### datafactory pipeline create

create a datafactory pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--pipeline**|object|Pipeline resource definition.|pipeline|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|

### datafactory pipeline create-run

create-run a datafactory pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create-run|CreateRun|

#### Parameters
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

### datafactory pipeline delete

delete a datafactory pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|

### datafactory pipeline list

list a datafactory pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

### datafactory pipeline show

show a datafactory pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--if-none-match**|string|ETag of the pipeline entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

### datafactory pipeline update

update a datafactory pipeline.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline|Pipelines|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|pipelineName|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|
|**--description**|string|The description of the pipeline.|pipeline_description|description|
|**--activities**|array|List of activities in pipeline.|pipeline_activities|activities|
|**--parameters**|dictionary|List of parameters for pipeline.|pipeline_parameters|parameters|
|**--variables**|dictionary|List of variables for pipeline.|pipeline_variables|variables|
|**--concurrency**|integer|The max number of concurrent runs for the pipeline.|pipeline_concurrency|concurrency|
|**--annotations**|array|List of tags that can be used for describing the Pipeline.|pipeline_annotations|annotations|
|**--run-dimensions**|dictionary|Dimensions emitted by Pipeline.|pipeline_run_dimensions|runDimensions|
|**--folder-name**|string|The name of the folder that this Pipeline is in.|pipeline_name_properties_folder_name|name|

### datafactory pipeline-run cancel

cancel a datafactory pipeline-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline-run|PipelineRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|cancel|Cancel|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|
|**--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|is_recursive|isRecursive|

### datafactory pipeline-run query-by-factory

query-by-factory a datafactory pipeline-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline-run|PipelineRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|query-by-factory|QueryByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|lastUpdatedAfter|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|lastUpdatedBefore|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|orderBy|

### datafactory pipeline-run show

show a datafactory pipeline-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory pipeline-run|PipelineRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|

### datafactory trigger create

create a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--properties**|object|Properties of the trigger.|properties|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|If-Match|

### datafactory trigger delete

delete a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### datafactory trigger get-event-subscription-status

get-event-subscription-status a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-event-subscription-status|GetEventSubscriptionStatus|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### datafactory trigger list

list a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|

### datafactory trigger query-by-factory

query-by-factory a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|query-by-factory|QueryByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|parent_trigger_name|parentTriggerName|

### datafactory trigger show

show a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--if-none-match**|string|ETag of the trigger entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|If-None-Match|

### datafactory trigger start

start a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start|Start|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### datafactory trigger stop

stop a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|stop|Stop|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### datafactory trigger subscribe-to-event

subscribe-to-event a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|subscribe-to-event|SubscribeToEvents|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### datafactory trigger unsubscribe-from-event

unsubscribe-from-event a datafactory trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|unsubscribe-from-event|UnsubscribeFromEvents|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|

### datafactory trigger-run query-by-factory

query-by-factory a datafactory trigger-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger-run|TriggerRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|query-by-factory|QueryByFactory|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|lastUpdatedAfter|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|lastUpdatedBefore|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuationToken|
|**--filters**|array|List of filters.|filters|filters|
|**--order-by**|array|List of OrderBy option.|order_by|orderBy|

### datafactory trigger-run rerun

rerun a datafactory trigger-run.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datafactory trigger-run|TriggerRuns|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|rerun|Rerun|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--factory-name**|string|The factory name.|factory_name|factoryName|
|**--trigger-name**|string|The trigger name.|trigger_name|triggerName|
|**--run-id**|string|The pipeline run identifier.|run_id|runId|
