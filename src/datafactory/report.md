# Azure CLI Module Creation Report

### datafactory activity-run query-by-pipeline-run

query-by-pipeline-run a datafactory activity-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--run_id**|string|The pipeline run identifier.|run_id|run_id|
|**--last_updated_after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|last_updated_after|
|**--last_updated_before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|last_updated_before|
|**--continuation_token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--filters**|array|List of filters.|filters|filters|
|**--order_by**|array|List of OrderBy option.|order_by|order_by|
### datafactory data-flow create

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--data_flow_name**|string|The data flow name.|data_flow_name|data_flow_name|
|**--properties**|object|Data flow properties.|properties|properties|
|**--if_match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory data-flow delete

delete a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--data_flow_name**|string|The data flow name.|data_flow_name|data_flow_name|
### datafactory data-flow list

list a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory data-flow show

show a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--data_flow_name**|string|The data flow name.|data_flow_name|data_flow_name|
|**--if_none_match**|string|ETag of the data flow entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory data-flow update

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--data_flow_name**|string|The data flow name.|data_flow_name|data_flow_name|
|**--properties**|object|Data flow properties.|properties|properties|
|**--if_match**|string|ETag of the data flow entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory data-flow-debug-session add-data-flow

add-data-flow a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--session_id**|string|The ID of data flow debug session.|session_id|session_id|
|**--data_flow**|object|Data flow instance.|data_flow|data_flow|
|**--datasets**|array|List of datasets.|datasets|datasets|
|**--linked_services**|array|List of linked services.|linked_services|linked_services|
|**--staging**|object|Staging info for debug session.|staging|staging|
|**--debug_settings**|object|Data flow debug settings.|debug_settings|debug_settings|
### datafactory data-flow-debug-session create

create a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--compute_type**|string|Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|compute_type|compute_type|
|**--core_count**|integer|Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|core_count|core_count|
|**--time_to_live**|integer|Time to live setting of the cluster in minutes.|time_to_live|time_to_live|
|**--integration_runtime**|object|Set to use integration runtime setting for data flow debug session.|integration_runtime|integration_runtime|
### datafactory data-flow-debug-session delete

delete a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--session_id**|string|The ID of data flow debug session.|session_id|session_id|
### datafactory data-flow-debug-session execute-command

execute-command a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--session_id**|string|The ID of data flow debug session.|session_id|session_id|
|**--command**|choice|The command type.|command|command|
|**--command_payload**|object|The command payload object.|command_payload|command_payload|
### datafactory data-flow-debug-session query-by-factory

query-by-factory a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory dataset create

create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--dataset_name**|string|The dataset name.|dataset_name|dataset_name|
|**--properties**|object|Dataset properties.|properties|properties|
|**--if_match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory dataset delete

delete a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--dataset_name**|string|The dataset name.|dataset_name|dataset_name|
### datafactory dataset list

list a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory dataset show

show a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--dataset_name**|string|The dataset name.|dataset_name|dataset_name|
|**--if_none_match**|string|ETag of the dataset entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory dataset update

create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--dataset_name**|string|The dataset name.|dataset_name|dataset_name|
|**--properties**|object|Dataset properties.|properties|properties|
|**--if_match**|string|ETag of the dataset entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory exposure-control get-feature-value

get-feature-value a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location_id**|string|The location identifier.|location_id|location_id|
|**--feature_name**|string|The feature name.|feature_name|feature_name|
|**--feature_type**|string|The feature type.|feature_type|feature_type|
### datafactory exposure-control get-feature-value-by-factory

get-feature-value-by-factory a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--feature_name**|string|The feature name.|feature_name|feature_name|
|**--feature_type**|string|The feature type.|feature_type|feature_type|
### datafactory factory configure-factory-repo

configure-factory-repo a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location_id**|string|The location identifier.|location_id|location_id|
|**--factory_resource_id**|string|The factory resource id.|factory_resource_id|factory_resource_id|
|**--repo_configuration**|object|Git repo information of the factory.|repo_configuration|repo_configuration|
### datafactory factory create

create a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--if_match**|string|ETag of the factory entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--identity**|object|Managed service identity of the factory.|identity|identity|
|**--repo_configuration**|object|Git repo information of the factory.|repo_configuration|properties_repo_configuration|
### datafactory factory delete

delete a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory factory get-data-plane-access

get-data-plane-access a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|permissions|permissions|
|**--access_resource_path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|access_resource_path|access_resource_path|
|**--profile_name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|profile_name|profile_name|
|**--start_time**|string|Start time for the token. If not specified the current time will be used.|start_time|start_time|
|**--expire_time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|expire_time|expire_time|
### datafactory factory get-git-hub-access-token

get-git-hub-access-token a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--git_hub_access_code**|string|GitHub access code.|git_hub_access_code|git_hub_access_code|
|**--git_hub_access_token_base_url**|string|GitHub access token base URL.|git_hub_access_token_base_url|git_hub_access_token_base_url|
|**--git_hub_client_id**|string|GitHub application client ID.|git_hub_client_id|git_hub_client_id|
### datafactory factory list

list a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
### datafactory factory show

show a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--if_none_match**|string|ETag of the factory entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory factory update

update a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--identity**|object|Managed service identity of the factory.|identity|identity|
### datafactory integration-runtime create

create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--properties**|object|Integration runtime properties.|properties|properties|
|**--if_match**|string|ETag of the integration runtime entity. Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory integration-runtime create-linked-integration-runtime

create-linked-integration-runtime a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--name**|string|The name of the linked integration runtime.|name|name|
|**--subscription_id**|string|The ID of the subscription that the linked integration runtime belongs to.|subscription_id|subscription_id|
|**--data_factory_name**|string|The name of the data factory that the linked integration runtime belongs to.|data_factory_name|data_factory_name|
|**--data_factory_location**|string|The location of the data factory that the linked integration runtime belongs to.|data_factory_location|data_factory_location|
### datafactory integration-runtime delete

delete a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime get-connection-info

get-connection-info a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime get-monitoring-data

get-monitoring-data a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime get-status

get-status a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime list

list a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory integration-runtime list-auth-key

list-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime regenerate-auth-key

regenerate-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--key_name**|choice|The name of the authentication key to regenerate.|key_name|key_name|
### datafactory integration-runtime remove-link

remove-link a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--linked_factory_name**|string|The data factory name for linked integration runtime.|linked_factory_name|linked_factory_name|
### datafactory integration-runtime show

show a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--if_none_match**|string|ETag of the integration runtime entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory integration-runtime start

start a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime stop

stop a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime sync-credentials

sync-credentials a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime update

update a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--auto_update**|choice|Enables or disables the auto-update feature of the self-hosted integration runtime. See https://go.microsoft.com/fwlink/?linkid=854189.|auto_update|auto_update|
|**--update_delay_offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|update_delay_offset|update_delay_offset|
### datafactory integration-runtime upgrade

upgrade a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory integration-runtime-node delete

delete a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node_name**|string|The integration runtime node name.|node_name|node_name|
### datafactory integration-runtime-node get-ip-address

get-ip-address a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node_name**|string|The integration runtime node name.|node_name|node_name|
### datafactory integration-runtime-node show

show a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node_name**|string|The integration runtime node name.|node_name|node_name|
### datafactory integration-runtime-node update

update a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--node_name**|string|The integration runtime node name.|node_name|node_name|
|**--concurrent_jobs_limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|concurrent_jobs_limit|concurrent_jobs_limit|
### datafactory integration-runtime-object-metadata get

get a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
|**--metadata_path**|string|Metadata path.|metadata_path|metadata_path|
### datafactory integration-runtime-object-metadata refresh

refresh a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--integration_runtime_name**|string|The integration runtime name.|integration_runtime_name|integration_runtime_name|
### datafactory linked-service create

create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--linked_service_name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--properties**|object|Properties of linked service.|properties|properties|
|**--if_match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory linked-service delete

delete a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--linked_service_name**|string|The linked service name.|linked_service_name|linked_service_name|
### datafactory linked-service list

list a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory linked-service show

show a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--linked_service_name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--if_none_match**|string|ETag of the linked service entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory linked-service update

create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--linked_service_name**|string|The linked service name.|linked_service_name|linked_service_name|
|**--properties**|object|Properties of linked service.|properties|properties|
|**--if_match**|string|ETag of the linkedService entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory pipeline create

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--pipeline_name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--if_match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|The description of the pipeline.|description|properties_description|
|**--activities**|array|List of activities in pipeline.|activities|properties_activities|
|**--parameters**|dictionary|List of parameters for pipeline.|parameters|properties_parameters|
|**--variables**|dictionary|List of variables for pipeline.|variables|properties_variables|
|**--concurrency**|integer|The max number of concurrent runs for the pipeline.|concurrency|properties_concurrency|
|**--annotations**|array|List of tags that can be used for describing the Pipeline.|annotations|properties_annotations|
|**--run_dimensions**|dictionary|Dimensions emitted by Pipeline.|run_dimensions|properties_run_dimensions|
|**--folder**|object|The folder that this Pipeline is in. If not specified, Pipeline will appear at the root level.|folder|properties_folder|
### datafactory pipeline create-run

create-run a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--pipeline_name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--reference_pipeline_run_id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|reference_pipeline_run_id|reference_pipeline_run_id|
|**--is_recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|is_recovery|is_recovery|
|**--start_activity_name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|start_activity_name|start_activity_name|
|**--start_from_failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|start_from_failure|start_from_failure|
|**--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|parameters|parameters|
### datafactory pipeline delete

delete a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--pipeline_name**|string|The pipeline name.|pipeline_name|pipeline_name|
### datafactory pipeline list

list a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory pipeline show

show a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--pipeline_name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--if_none_match**|string|ETag of the pipeline entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory pipeline update

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--pipeline_name**|string|The pipeline name.|pipeline_name|pipeline_name|
|**--if_match**|string|ETag of the pipeline entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
|**--description**|string|The description of the pipeline.|description|properties_description|
|**--activities**|array|List of activities in pipeline.|activities|properties_activities|
|**--parameters**|dictionary|List of parameters for pipeline.|parameters|properties_parameters|
|**--variables**|dictionary|List of variables for pipeline.|variables|properties_variables|
|**--concurrency**|integer|The max number of concurrent runs for the pipeline.|concurrency|properties_concurrency|
|**--annotations**|array|List of tags that can be used for describing the Pipeline.|annotations|properties_annotations|
|**--run_dimensions**|dictionary|Dimensions emitted by Pipeline.|run_dimensions|properties_run_dimensions|
|**--folder**|object|The folder that this Pipeline is in. If not specified, Pipeline will appear at the root level.|folder|properties_folder|
### datafactory pipeline-run cancel

cancel a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--run_id**|string|The pipeline run identifier.|run_id|run_id|
|**--is_recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|is_recursive|is_recursive|
### datafactory pipeline-run query-by-factory

query-by-factory a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--last_updated_after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|last_updated_after|
|**--last_updated_before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|last_updated_before|
|**--continuation_token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--filters**|array|List of filters.|filters|filters|
|**--order_by**|array|List of OrderBy option.|order_by|order_by|
### datafactory pipeline-run show

show a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--run_id**|string|The pipeline run identifier.|run_id|run_id|
### datafactory trigger create

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|properties|
|**--if_match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory trigger delete

delete a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger get-event-subscription-status

get-event-subscription-status a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger list

list a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
### datafactory trigger query-by-factory

query-by-factory a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--continuation_token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--parent_trigger_name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|parent_trigger_name|parent_trigger_name|
### datafactory trigger show

show a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
|**--if_none_match**|string|ETag of the trigger entity. Should only be specified for get. If the ETag matches the existing entity tag, or if * was provided, then no content will be returned.|if_none_match|if_none_match|
### datafactory trigger start

start a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger stop

stop a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger subscribe-to-event

subscribe-to-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger unsubscribe-from-event

unsubscribe-from-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
### datafactory trigger update

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
|**--properties**|object|Properties of the trigger.|properties|properties|
|**--if_match**|string|ETag of the trigger entity.  Should only be specified for update, for which it should match existing entity or can be * for unconditional update.|if_match|if_match|
### datafactory trigger-run query-by-factory

query-by-factory a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--last_updated_after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|last_updated_after|last_updated_after|
|**--last_updated_before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|last_updated_before|last_updated_before|
|**--continuation_token**|string|The continuation token for getting the next page of results. Null for first page.|continuation_token|continuation_token|
|**--filters**|array|List of filters.|filters|filters|
|**--order_by**|array|List of OrderBy option.|order_by|order_by|
### datafactory trigger-run rerun

rerun a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--factory_name**|string|The factory name.|factory_name|factory_name|
|**--trigger_name**|string|The trigger name.|trigger_name|trigger_name|
|**--run_id**|string|The pipeline run identifier.|run_id|run_id|