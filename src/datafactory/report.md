# Azure CLI Module Creation Report

### datafactory activity-run query-by-pipeline-run

query-by-pipeline-run a datafactory activity-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--filters**|array|List of filters.|filters|
|**--order-by**|array|List of OrderBy option.|order_by|
### datafactory data-flow create

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
|**--properties**|object|Data flow properties.|properties|
|**--if-match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory data-flow delete

delete a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
### datafactory data-flow list

list a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory data-flow show

show a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
|**--if-none-match**|string|ETag of the data flow entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory data-flow update

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--data-flow-name**|string|The data flow name.|data_flow_name|
|**--properties**|object|Data flow properties.|properties|
|**--if-match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory data-flow-debug-session add-data-flow

add-data-flow a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|
|**--datasets**|array|List of datasets.|datasets|
|**--linked-services**|array|List of linked services.|linked_services|
|**--debug-settings-source-settings**|array|Source setting for data flow debug.|source_settings|
|**--debug-settings-parameters**|dictionary|Data flow parameters.|parameters_debug_settings_parameters|
|**--debug-settings-dataset-parameters**|any|Parameters for dataset.|dataset_parameters|
|**--staging-folder-path**|string|Folder path for staging blob.|folder_path|
|**--staging-linked-service-reference-name**|string|Reference LinkedService name.|reference_name|
|**--staging-linked-service-parameters**|dictionary|Arguments for LinkedService.|parameters|
|**--data-flow-name**|string|The resource name.|name|
|**--data-flow-properties**|object|Data flow properties.|properties|
### datafactory data-flow-debug-session create

create a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--compute-type**|string|Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|compute_type|
|**--core-count**|integer|Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|core_count|
|**--time-to-live**|integer|Time to live setting of the cluster in minutes.|time_to_live|
|**--integration-runtime-name**|string|The resource name.|name|
|**--integration-runtime-properties**|object|Integration runtime properties.|properties|
### datafactory data-flow-debug-session delete

delete a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|
### datafactory data-flow-debug-session execute-command

execute-command a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--session-id**|string|The ID of data flow debug session.|session_id|
|**--command**|choice|The command type.|command|
|**--command-payload**|object|The command payload object.|command_payload|
### datafactory data-flow-debug-session query-by-factory

query-by-factory a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory dataset create

create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--properties**|object|Dataset properties.|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory dataset delete

delete a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
### datafactory dataset list

list a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory dataset show

show a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--if-none-match**|string|ETag of the dataset entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory dataset update

create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--dataset-name**|string|The dataset name.|dataset_name|
|**--properties**|object|Dataset properties.|properties|
|**--if-match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory factory configure-factory-repo

configure-factory-repo a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|The location identifier.|location|
|**--factory-resource-id**|string|The factory resource id.|factory_resource_id|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|
### datafactory factory create

create a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--if-match**|string|ETag of the factory entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--location**|string|The resource location.|location|
|**--tags**|dictionary|The resource tags.|tags|
|**--factory-vsts-configuration**|object|Factory's VSTS repo information.|factory_vsts_configuration|
|**--factory-git-hub-configuration**|object|Factory's GitHub repo information.|factory_git_hub_configuration|
|**--global-parameters**|dictionary|List of parameters for factory.|global_parameters|
### datafactory factory delete

delete a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory factory get-data-plane-access

get-data-plane-access a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|permissions|
|**--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|access_resource_path|
|**--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|profile_name|
|**--start-time**|string|Start time for the token. If not specified the current time will be used.|start_time|
|**--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|expire_time|
### datafactory factory get-git-hub-access-token

get-git-hub-access-token a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--git-hub-access-code**|string|GitHub access code.|git_hub_access_code|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|git_hub_access_token_base_url|
|**--git-hub-client-id**|string|GitHub application client ID.|git_hub_client_id|
### datafactory factory list

list a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
### datafactory factory show

show a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--if-none-match**|string|ETag of the factory entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory factory update

update a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--tags**|dictionary|The resource tags.|tags|
### datafactory integration-runtime delete

delete a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime get-connection-info

get-connection-info a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime get-monitoring-data

get-monitoring-data a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime get-status

get-status a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime linked-integration-runtime create

linked-integration-runtime create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--name**|string|The name of the linked integration runtime.|name|
|**--subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|subscription_id|
|**--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|data_factory_name|
|**--location**|string|The location of the data factory that the linked integration runtime belongs to.|location|
### datafactory integration-runtime list

list a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory integration-runtime list-auth-key

list-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime managed create

managed create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Integration runtime description.|managed_description|
|**--type-properties-compute-properties**|object|The compute resource for managed integration runtime.|managed_compute_properties|
|**--type-properties-ssis-properties**|object|SSIS properties for managed integration runtime.|managed_ssis_properties|
### datafactory integration-runtime regenerate-auth-key

regenerate-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--key-name**|choice|The name of the authentication key to regenerate.|key_name|
### datafactory integration-runtime remove-link

remove-link a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|linked_factory_name|
### datafactory integration-runtime self-hosted create

self-hosted create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--if-match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
|**--description**|string|Integration runtime description.|self_hosted_description|
|**--type-properties-linked-info**|object|The base definition of a linked integration runtime.|self_hosted_linked_info|
### datafactory integration-runtime show

show a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--if-none-match**|string|ETag of the integration runtime entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory integration-runtime start

start a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime stop

stop a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime sync-credentials

sync-credentials a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime update

update a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--auto-update**|choice|Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.|auto_update|
|**--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|update_delay_offset|
### datafactory integration-runtime upgrade

upgrade a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
### datafactory integration-runtime-node delete

delete a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
### datafactory integration-runtime-node get-ip-address

get-ip-address a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
### datafactory integration-runtime-node show

show a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
### datafactory integration-runtime-node update

update a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--integration-runtime-name**|string|The integration runtime name.|integration_runtime_name|
|**--node-name**|string|The integration runtime node name.|node_name|
|**--concurrent-jobs-limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|concurrent_jobs_limit|
### datafactory linked-service create

create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--properties**|object|Properties of linked service.|properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory linked-service delete

delete a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
### datafactory linked-service list

list a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory linked-service show

show a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--if-none-match**|string|ETag of the linked service entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory linked-service update

create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--linked-service-name**|string|The linked service name.|linked_service_name|
|**--properties**|object|Properties of linked service.|properties|
|**--if-match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory pipeline create

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--pipeline**|object|Pipeline resource definition.|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory pipeline create-run

create-run a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--reference-pipeline-run-id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|reference_pipeline_run_id|
|**--is-recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|is_recovery|
|**--start-activity-name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|start_activity_name|
|**--start-from-failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|start_from_failure|
|**--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|parameters|
### datafactory pipeline delete

delete a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
### datafactory pipeline list

list a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory pipeline show

show a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--if-none-match**|string|ETag of the pipeline entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory pipeline update

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--pipeline-name**|string|The pipeline name.|pipeline_name|
|**--pipeline**|object|Pipeline resource definition.|pipeline|
|**--if-match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory pipeline-run cancel

cancel a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|
|**--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|is_recursive|
### datafactory pipeline-run query-by-factory

query-by-factory a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--filters**|array|List of filters.|filters|
|**--order-by**|array|List of OrderBy option.|order_by|
### datafactory pipeline-run show

show a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--run-id**|string|The pipeline run identifier.|run_id|
### datafactory trigger create

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory trigger delete

delete a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger get-event-subscription-status

get-event-subscription-status a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger list

list a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
### datafactory trigger query-by-factory

query-by-factory a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|parent_trigger_name|
### datafactory trigger show

show a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--if-none-match**|string|ETag of the trigger entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|
### datafactory trigger start

start a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger stop

stop a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger subscribe-to-event

subscribe-to-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger unsubscribe-from-event

unsubscribe-from-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
### datafactory trigger update

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|
|**--if-match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|
### datafactory trigger-run query-by-factory

query-by-factory a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|
|**--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|
|**--filters**|array|List of filters.|filters|
|**--order-by**|array|List of OrderBy option.|order_by|
### datafactory trigger-run rerun

rerun a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--factory-name**|string|The factory name.|factory_name|
|**--trigger-name**|string|The trigger name.|trigger_name|
|**--run-id**|string|The pipeline run identifier.|run_id|