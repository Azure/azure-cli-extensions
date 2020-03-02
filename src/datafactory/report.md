# Azure CLI Module Creation Report

### datafactory activity-run query-by-pipeline-run

query-by-pipeline-run a datafactory activity-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the pipeline run.|/something/my_option|/something/myOption|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--filters**|array|List of filters.|/something/my_option|/something/myOption|
|--order-by**|array|List of OrderBy option.|/something/my_option|/something/myOption|
### datafactory data-flow create

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--data-flow**|object|Data flow resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|Azure Data Factory nested object which contains a flow with data movements and transformations.|/something/my_option|/something/myOption|
### datafactory data-flow delete

delete a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flow list

list a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flow show

show a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flow update

create a datafactory data-flow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--data-flow**|object|Data flow resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|Azure Data Factory nested object which contains a flow with data movements and transformations.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session add-data-flow

add-data-flow a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--request**|object|Data flow debug session definition with debug content.|/something/my_option|/something/myOption|
|--session-id**|string|The ID of data flow debug session.|/something/my_option|/something/myOption|
|--data-flow**|object|Data flow debug resource.|/something/my_option|/something/myOption|
|--datasets**|array|List of datasets.|/something/my_option|/something/myOption|
|--linked-services**|array|List of linked services.|/something/my_option|/something/myOption|
|--staging**|object|Staging info for execute data flow activity.|/something/my_option|/something/myOption|
|--debug-settings**|object|Data flow debug settings.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session create

create a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--request**|object|Data flow debug session definition|/something/my_option|/something/myOption|
|--compute-type**|string|Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|/something/my_option|/something/myOption|
|--core-count**|integer|Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|/something/my_option|/something/myOption|
|--time-to-live**|integer|Time to live setting of the cluster in minutes.|/something/my_option|/something/myOption|
|--integration-runtime**|object|Integration runtime debug resource.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session delete

delete a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--request**|object|Data flow debug session definition for deletion|/something/my_option|/something/myOption|
|--session-id**|string|The ID of data flow debug session.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session execute-command

execute-command a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--request**|object|Data flow debug command definition.|/something/my_option|/something/myOption|
|--session-id**|string|The ID of data flow debug session.|/something/my_option|/something/myOption|
|--command**|choice|The command type.|/something/my_option|/something/myOption|
|--command-payload**|object|Structure of command payload.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session query-by-factory

query-by-factory a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory dataset create

create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--dataset**|object|Dataset resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|The Azure Data Factory nested object which identifies data within different data stores, such as tables, files, folders, and documents.|/something/my_option|/something/myOption|
### datafactory dataset delete

delete a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory dataset list

list a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory dataset show

show a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory dataset update

create a datafactory dataset.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--dataset**|object|Dataset resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|The Azure Data Factory nested object which identifies data within different data stores, such as tables, files, folders, and documents.|/something/my_option|/something/myOption|
### datafactory exposure-control get-feature-value

get-feature-value a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--exposure-control-request**|object|The exposure control request.|/something/my_option|/something/myOption|
|--feature-name**|string|The feature name.|/something/my_option|/something/myOption|
|--feature-type**|string|The feature type.|/something/my_option|/something/myOption|
### datafactory exposure-control get-feature-value-by-factory

get-feature-value-by-factory a datafactory exposure-control.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--exposure-control-request**|object|The exposure control request.|/something/my_option|/something/myOption|
|--feature-name**|string|The feature name.|/something/my_option|/something/myOption|
|--feature-type**|string|The feature type.|/something/my_option|/something/myOption|
### datafactory factory configure-factory-repo

configure-factory-repo a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--factory-repo-update**|object|Update factory repo request definition.|/something/my_option|/something/myOption|
|--factory-resource-id**|string|The factory resource id.|/something/my_option|/something/myOption|
|--repo-configuration**|object|Factory's git repo information.|/something/my_option|/something/myOption|
### datafactory factory create

create a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--factory**|object|Factory resource definition.|/something/my_option|/something/myOption|
|--location**|string|The resource location.|/something/my_option|/something/myOption|
|--tags**|dictionary|The resource tags.|/something/my_option|/something/myOption|
|--identity**|object|Identity properties of the factory resource.|/something/my_option|/something/myOption|
|--repo-configuration**|object|Factory's git repo information.|/something/my_option|/something/myOption|
### datafactory factory delete

delete a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory factory get-data-plane-access

get-data-plane-access a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--policy**|object|Data Plane user access policy definition.|/something/my_option|/something/myOption|
|--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|/something/my_option|/something/myOption|
|--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|/something/my_option|/something/myOption|
|--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|/something/my_option|/something/myOption|
|--start-time**|string|Start time for the token. If not specified the current time will be used.|/something/my_option|/something/myOption|
|--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|/something/my_option|/something/myOption|
### datafactory factory get-git-hub-access-token

get-git-hub-access-token a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--git-hub-access-token-request**|object|Get GitHub access token request definition.|/something/my_option|/something/myOption|
|**--git-hub-access-code**|string|GitHub access code.|/something/my_option|/something/myOption|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|/something/my_option|/something/myOption|
|--git-hub-client-id**|string|GitHub application client ID.|/something/my_option|/something/myOption|
### datafactory factory list

list a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory factory show

show a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory factory update

update a datafactory factory.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--factory-update-parameters**|object|The parameters for updating a factory.|/something/my_option|/something/myOption|
|--tags**|dictionary|The resource tags.|/something/my_option|/something/myOption|
|--identity**|object|Identity properties of the factory resource.|/something/my_option|/something/myOption|
### datafactory integration-runtime create

create a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--integration-runtime**|object|Integration runtime resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|Azure Data Factory nested object which serves as a compute resource for activities.|/something/my_option|/something/myOption|
### datafactory integration-runtime create-linked-integration-runtime

create-linked-integration-runtime a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--create-linked-integration-runtime-request**|object|The linked integration runtime properties.|/something/my_option|/something/myOption|
|--name**|string|The name of the linked integration runtime.|/something/my_option|/something/myOption|
|--subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|/something/my_option|/something/myOption|
|--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|/something/my_option|/something/myOption|
|--data-factory-location**|string|The location of the data factory that the linked integration runtime belongs to.|/something/my_option|/something/myOption|
### datafactory integration-runtime delete

delete a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime get-connection-info

get-connection-info a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime get-monitoring-data

get-monitoring-data a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime get-status

get-status a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime list

list a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime list-auth-key

list-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime regenerate-auth-key

regenerate-auth-key a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--regenerate-key-parameters**|object|The parameters for regenerating integration runtime authentication key.|/something/my_option|/something/myOption|
|--key-name**|choice|The name of the authentication key to regenerate.|/something/my_option|/something/myOption|
### datafactory integration-runtime remove-link

remove-link a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--linked-integration-runtime-request**|object|The data factory name for the linked integration runtime.|/something/my_option|/something/myOption|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|/something/my_option|/something/myOption|
### datafactory integration-runtime show

show a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime start

start a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime stop

stop a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime sync-credentials

sync-credentials a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime update

update a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--update-integration-runtime-request**|object|The parameters for updating an integration runtime.|/something/my_option|/something/myOption|
|--auto-update**|choice|The state of integration runtime auto update.|/something/my_option|/something/myOption|
|--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|/something/my_option|/something/myOption|
### datafactory integration-runtime upgrade

upgrade a datafactory integration-runtime.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-node delete

delete a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-node get-ip-address

get-ip-address a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-node show

show a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-node update

update a datafactory integration-runtime-node.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--update-integration-runtime-node-request**|object|The parameters for updating an integration runtime node.|/something/my_option|/something/myOption|
|--concurrent-jobs-limit**|integer|The number of concurrent jobs permitted to run on the integration runtime node. Values between 1 and maxConcurrentJobs(inclusive) are allowed.|/something/my_option|/something/myOption|
### datafactory integration-runtime-object-metadata get

get a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--get-metadata-request**|object|The parameters for getting a SSIS object metadata.|/something/my_option|/something/myOption|
|--metadata-path**|string|Metadata path.|/something/my_option|/something/myOption|
### datafactory integration-runtime-object-metadata refresh

refresh a datafactory integration-runtime-object-metadata.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-service create

create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--linked-service**|object|Linked service resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|The Azure Data Factory nested object which contains the information and credential which can be used to connect with related store or compute resource.|/something/my_option|/something/myOption|
### datafactory linked-service delete

delete a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-service list

list a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-service show

show a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-service update

create a datafactory linked-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--linked-service**|object|Linked service resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|The Azure Data Factory nested object which contains the information and credential which can be used to connect with related store or compute resource.|/something/my_option|/something/myOption|
### datafactory pipeline create

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--pipeline**|object|Pipeline resource definition.|/something/my_option|/something/myOption|
|--description**|string|The description of the pipeline.|/something/my_option|/something/myOption|
|--activities**|array|List of activities in pipeline.|/something/my_option|/something/myOption|
|--parameters**|dictionary|Definition of all parameters for an entity.|/something/my_option|/something/myOption|
|--variables**|dictionary|Definition of variable for a Pipeline.|/something/my_option|/something/myOption|
|--concurrency**|integer|The max number of concurrent runs for the pipeline.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the Pipeline.|/something/my_option|/something/myOption|
|--run-dimensions**|dictionary|Dimensions emitted by Pipeline.|/something/my_option|/something/myOption|
|--folder**|object|The folder that this Pipeline is in. If not specified, Pipeline will appear at the root level.|/something/my_option|/something/myOption|
### datafactory pipeline create-run

create-run a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--reference-pipeline-run-id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|/something/my_option|/something/myOption|
|--is-recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|/something/my_option|/something/myOption|
|--start-activity-name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|/something/my_option|/something/myOption|
|--start-from-failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|/something/my_option|/something/myOption|
|--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|/something/my_option|/something/myOption|
### datafactory pipeline delete

delete a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipeline list

list a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipeline show

show a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipeline update

create a datafactory pipeline.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--pipeline**|object|Pipeline resource definition.|/something/my_option|/something/myOption|
|--description**|string|The description of the pipeline.|/something/my_option|/something/myOption|
|--activities**|array|List of activities in pipeline.|/something/my_option|/something/myOption|
|--parameters**|dictionary|Definition of all parameters for an entity.|/something/my_option|/something/myOption|
|--variables**|dictionary|Definition of variable for a Pipeline.|/something/my_option|/something/myOption|
|--concurrency**|integer|The max number of concurrent runs for the pipeline.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the Pipeline.|/something/my_option|/something/myOption|
|--run-dimensions**|dictionary|Dimensions emitted by Pipeline.|/something/my_option|/something/myOption|
|--folder**|object|The folder that this Pipeline is in. If not specified, Pipeline will appear at the root level.|/something/my_option|/something/myOption|
### datafactory pipeline-run cancel

cancel a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|/something/my_option|/something/myOption|
### datafactory pipeline-run query-by-factory

query-by-factory a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the pipeline run.|/something/my_option|/something/myOption|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--filters**|array|List of filters.|/something/my_option|/something/myOption|
|--order-by**|array|List of OrderBy option.|/something/my_option|/something/myOption|
### datafactory pipeline-run show

show a datafactory pipeline-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger create

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--trigger**|object|Trigger resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|Azure data factory nested object which contains information about creating pipeline run|/something/my_option|/something/myOption|
### datafactory trigger delete

delete a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger get-event-subscription-status

get-event-subscription-status a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger list

list a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger query-by-factory

query-by-factory a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the triggers.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|/something/my_option|/something/myOption|
### datafactory trigger show

show a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger start

start a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger stop

stop a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger subscribe-to-event

subscribe-to-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger unsubscribe-from-event

unsubscribe-from-event a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory trigger update

create a datafactory trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--trigger**|object|Trigger resource definition.|/something/my_option|/something/myOption|
|**--properties**|object|Azure data factory nested object which contains information about creating pipeline run|/something/my_option|/something/myOption|
### datafactory trigger-run query-by-factory

query-by-factory a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the pipeline run.|/something/my_option|/something/myOption|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--filters**|array|List of filters.|/something/my_option|/something/myOption|
|--order-by**|array|List of OrderBy option.|/something/my_option|/something/myOption|
### datafactory trigger-run rerun

rerun a datafactory trigger-run.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|