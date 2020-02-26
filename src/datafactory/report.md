# Azure CLI Module Creation Report

### datafactory activity-runs query-by-pipeline-run

query-by-pipeline-run a datafactory activity-runs.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the pipeline run.|/something/my_option|/something/myOption|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--filters**|array|List of filters.|/something/my_option|/something/myOption|
|--order-by**|array|List of OrderBy option.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session add-data-flow

add-data-flow a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--request**|object|Data flow debug session definition with debug content.|/something/my_option|/something/myOption|
|**--type-staging-linked-service**|constant|Linked service reference type.|/something/my_option|/something/myOption|
|**--reference-name**|string|Reference LinkedService name.|/something/my_option|/something/myOption|
|--session-id**|string|The ID of data flow debug session.|/something/my_option|/something/myOption|
|--name**|string|The resource name.|/something/my_option|/something/myOption|
|--type**|string|Type of data flow.|/something/my_option|/something/myOption|
|--description**|string|The description of the data flow.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the data flow.|/something/my_option|/something/myOption|
|--name-data-flow-properties-folder**|string|The name of the folder that this data flow is in.|/something/my_option|/something/myOption|
|--datasets**|array|List of datasets.|/something/my_option|/something/myOption|
|--linked-services**|array|List of linked services.|/something/my_option|/something/myOption|
|--parameters**|dictionary|An object mapping parameter names to argument values.|/something/my_option|/something/myOption|
|--folder-path**|string|Folder path for staging blob.|/something/my_option|/something/myOption|
|--source-settings**|array|Source setting for data flow debug.|/something/my_option|/something/myOption|
|--parameters-debug-settings**|dictionary|An object mapping parameter names to argument values.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session create

create a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--request**|object|Data flow debug session definition|/something/my_option|/something/myOption|
|**--type**|choice|The type of integration runtime.|/something/my_option|/something/myOption|
|--compute-type**|string|Compute type of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|/something/my_option|/something/myOption|
|--core-count**|integer|Core count of the cluster. The value will be overwritten by the same setting in integration runtime if provided.|/something/my_option|/something/myOption|
|--time-to-live**|integer|Time to live setting of the cluster in minutes.|/something/my_option|/something/myOption|
|--name**|string|The resource name.|/something/my_option|/something/myOption|
|--description**|string|Integration runtime description.|/something/my_option|/something/myOption|
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
|**--stream-name**|string|The stream name which is used for preview.|/something/my_option|/something/myOption|
|--session-id**|string|The ID of data flow debug session.|/something/my_option|/something/myOption|
|--command**|choice|The command type.|/something/my_option|/something/myOption|
|--row-limits**|integer|Row limits for preview response.|/something/my_option|/something/myOption|
|--columns**|array|Array of column names.|/something/my_option|/something/myOption|
|--expression**|string|The expression which is used for preview.|/something/my_option|/something/myOption|
### datafactory data-flow-debug-session query-by-factory

query-by-factory a datafactory data-flow-debug-session.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flows create

create a datafactory data-flows.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--data-flow**|object|Data flow resource definition.|/something/my_option|/something/myOption|
|--type**|string|Type of data flow.|/something/my_option|/something/myOption|
|--description**|string|The description of the data flow.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the data flow.|/something/my_option|/something/myOption|
|--name**|string|The name of the folder that this data flow is in.|/something/my_option|/something/myOption|
### datafactory data-flows delete

delete a datafactory data-flows.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flows list

list a datafactory data-flows.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flows show

show a datafactory data-flows.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory data-flows update

create a datafactory data-flows.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--data-flow**|object|Data flow resource definition.|/something/my_option|/something/myOption|
|--type**|string|Type of data flow.|/something/my_option|/something/myOption|
|--description**|string|The description of the data flow.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the data flow.|/something/my_option|/something/myOption|
|--name**|string|The name of the folder that this data flow is in.|/something/my_option|/something/myOption|
### datafactory datasets create

create a datafactory datasets.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--dataset**|object|Dataset resource definition.|/something/my_option|/something/myOption|
|**--type**|string|Type of dataset.|/something/my_option|/something/myOption|
|**--type-properties-linked-service-name**|constant|Linked service reference type.|/something/my_option|/something/myOption|
|**--reference-name**|string|Reference LinkedService name.|/something/my_option|/something/myOption|
|--description**|string|Dataset description.|/something/my_option|/something/myOption|
|--parameters**|dictionary|An object mapping parameter names to argument values.|/something/my_option|/something/myOption|
|--parameters-properties**|dictionary|Definition of all parameters for an entity.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the Dataset.|/something/my_option|/something/myOption|
|--name**|string|The name of the folder that this Dataset is in.|/something/my_option|/something/myOption|
### datafactory datasets delete

delete a datafactory datasets.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory datasets list

list a datafactory datasets.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory datasets show

show a datafactory datasets.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory datasets update

create a datafactory datasets.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--dataset**|object|Dataset resource definition.|/something/my_option|/something/myOption|
|**--type**|string|Type of dataset.|/something/my_option|/something/myOption|
|**--type-properties-linked-service-name**|constant|Linked service reference type.|/something/my_option|/something/myOption|
|**--reference-name**|string|Reference LinkedService name.|/something/my_option|/something/myOption|
|--description**|string|Dataset description.|/something/my_option|/something/myOption|
|--parameters**|dictionary|An object mapping parameter names to argument values.|/something/my_option|/something/myOption|
|--parameters-properties**|dictionary|Definition of all parameters for an entity.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the Dataset.|/something/my_option|/something/myOption|
|--name**|string|The name of the folder that this Dataset is in.|/something/my_option|/something/myOption|
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
### datafactory factories configure-factory-repo

configure-factory-repo a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--factory-repo-update**|object|Update factory repo request definition.|/something/my_option|/something/myOption|
|**--type**|string|Type of repo configuration.|/something/my_option|/something/myOption|
|**--account-name**|string|Account name.|/something/my_option|/something/myOption|
|**--repository-name**|string|Repository name.|/something/my_option|/something/myOption|
|**--collaboration-branch**|string|Collaboration branch.|/something/my_option|/something/myOption|
|**--root-folder**|string|Root folder.|/something/my_option|/something/myOption|
|--factory-resource-id**|string|The factory resource id.|/something/my_option|/something/myOption|
|--last-commit-id**|string|Last commit id.|/something/my_option|/something/myOption|
### datafactory factories create

create a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--factory**|object|Factory resource definition.|/something/my_option|/something/myOption|
|**--type**|constant|The identity type. Currently the only supported type is 'SystemAssigned'.|/something/my_option|/something/myOption|
|**--type-repo-configuration**|string|Type of repo configuration.|/something/my_option|/something/myOption|
|**--account-name**|string|Account name.|/something/my_option|/something/myOption|
|**--repository-name**|string|Repository name.|/something/my_option|/something/myOption|
|**--collaboration-branch**|string|Collaboration branch.|/something/my_option|/something/myOption|
|**--root-folder**|string|Root folder.|/something/my_option|/something/myOption|
|--location**|string|The resource location.|/something/my_option|/something/myOption|
|--tags**|dictionary|The resource tags.|/something/my_option|/something/myOption|
|--last-commit-id**|string|Last commit id.|/something/my_option|/something/myOption|
### datafactory factories delete

delete a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory factories get-data-plane-access

get-data-plane-access a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--policy**|object|Data Plane user access policy definition.|/something/my_option|/something/myOption|
|--permissions**|string|The string with permissions for Data Plane access. Currently only 'r' is supported which grants read only access.|/something/my_option|/something/myOption|
|--access-resource-path**|string|The resource path to get access relative to factory. Currently only empty string is supported which corresponds to the factory resource.|/something/my_option|/something/myOption|
|--profile-name**|string|The name of the profile. Currently only the default is supported. The default value is DefaultProfile.|/something/my_option|/something/myOption|
|--start-time**|string|Start time for the token. If not specified the current time will be used.|/something/my_option|/something/myOption|
|--expire-time**|string|Expiration time for the token. Maximum duration for the token is eight hours and by default the token will expire in eight hours.|/something/my_option|/something/myOption|
### datafactory factories get-git-hub-access-token

get-git-hub-access-token a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--git-hub-access-token-request**|object|Get GitHub access token request definition.|/something/my_option|/something/myOption|
|**--git-hub-access-code**|string|GitHub access code.|/something/my_option|/something/myOption|
|**--git-hub-access-token-base-url**|string|GitHub access token base URL.|/something/my_option|/something/myOption|
|--git-hub-client-id**|string|GitHub application client ID.|/something/my_option|/something/myOption|
### datafactory factories list

list a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory factories show

show a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory factories update

update a datafactory factories.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--factory-update-parameters**|object|The parameters for updating a factory.|/something/my_option|/something/myOption|
|**--type**|constant|The identity type. Currently the only supported type is 'SystemAssigned'.|/something/my_option|/something/myOption|
|--tags**|dictionary|The resource tags.|/something/my_option|/something/myOption|
### datafactory integration-runtime-nodes delete

delete a datafactory integration-runtime-nodes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-nodes get-ip-address

get-ip-address a datafactory integration-runtime-nodes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-nodes show

show a datafactory integration-runtime-nodes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtime-nodes update

update a datafactory integration-runtime-nodes.

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
### datafactory integration-runtimes create

create a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--integration-runtime**|object|Integration runtime resource definition.|/something/my_option|/something/myOption|
|**--type**|choice|The type of integration runtime.|/something/my_option|/something/myOption|
|--description**|string|Integration runtime description.|/something/my_option|/something/myOption|
### datafactory integration-runtimes create-linked-integration-runtime

create-linked-integration-runtime a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--create-linked-integration-runtime-request**|object|The linked integration runtime properties.|/something/my_option|/something/myOption|
|--name**|string|The name of the linked integration runtime.|/something/my_option|/something/myOption|
|--create-linked-integration-runtime-request-subscription-id**|string|The ID of the subscription that the linked integration runtime belongs to.|/something/my_option|/something/myOption|
|--data-factory-name**|string|The name of the data factory that the linked integration runtime belongs to.|/something/my_option|/something/myOption|
|--data-factory-location**|string|The location of the data factory that the linked integration runtime belongs to.|/something/my_option|/something/myOption|
### datafactory integration-runtimes delete

delete a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes get-connection-info

get-connection-info a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes get-monitoring-data

get-monitoring-data a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes get-status

get-status a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes list

list a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes list-auth-keys

list-auth-keys a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes regenerate-auth-key

regenerate-auth-key a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--regenerate-key-parameters**|object|The parameters for regenerating integration runtime authentication key.|/something/my_option|/something/myOption|
|--key-name**|choice|The name of the authentication key to regenerate.|/something/my_option|/something/myOption|
### datafactory integration-runtimes remove-links

remove-links a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--linked-integration-runtime-request**|object|The data factory name for the linked integration runtime.|/something/my_option|/something/myOption|
|**--linked-factory-name**|string|The data factory name for linked integration runtime.|/something/my_option|/something/myOption|
### datafactory integration-runtimes show

show a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes start

start a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes stop

stop a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes sync-credentials

sync-credentials a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory integration-runtimes update

update a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--update-integration-runtime-request**|object|The parameters for updating an integration runtime.|/something/my_option|/something/myOption|
|--auto-update**|choice|The state of integration runtime auto update.|/something/my_option|/something/myOption|
|--update-delay-offset**|string|The time offset (in hours) in the day, e.g., PT03H is 3 hours. The integration runtime auto update will happen on that time.|/something/my_option|/something/myOption|
### datafactory integration-runtimes upgrade

upgrade a datafactory integration-runtimes.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-services create

create a datafactory linked-services.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--linked-service**|object|Linked service resource definition.|/something/my_option|/something/myOption|
|**--type**|string|Type of linked service.|/something/my_option|/something/myOption|
|**--type-properties-connect-via**|constant|Type of integration runtime.|/something/my_option|/something/myOption|
|**--reference-name**|string|Reference integration runtime name.|/something/my_option|/something/myOption|
|--parameters**|dictionary|An object mapping parameter names to argument values.|/something/my_option|/something/myOption|
|--description**|string|Linked service description.|/something/my_option|/something/myOption|
|--parameters-properties**|dictionary|Definition of all parameters for an entity.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the linked service.|/something/my_option|/something/myOption|
### datafactory linked-services delete

delete a datafactory linked-services.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-services list

list a datafactory linked-services.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-services show

show a datafactory linked-services.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory linked-services update

create a datafactory linked-services.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--linked-service**|object|Linked service resource definition.|/something/my_option|/something/myOption|
|**--type**|string|Type of linked service.|/something/my_option|/something/myOption|
|**--type-properties-connect-via**|constant|Type of integration runtime.|/something/my_option|/something/myOption|
|**--reference-name**|string|Reference integration runtime name.|/something/my_option|/something/myOption|
|--parameters**|dictionary|An object mapping parameter names to argument values.|/something/my_option|/something/myOption|
|--description**|string|Linked service description.|/something/my_option|/something/myOption|
|--parameters-properties**|dictionary|Definition of all parameters for an entity.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the linked service.|/something/my_option|/something/myOption|
### datafactory operations list

list a datafactory operations.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipeline-runs cancel

cancel a datafactory pipeline-runs.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--is-recursive**|boolean|If true, cancel all the Child pipelines that are triggered by the current pipeline.|/something/my_option|/something/myOption|
### datafactory pipeline-runs query-by-factory

query-by-factory a datafactory pipeline-runs.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the pipeline run.|/something/my_option|/something/myOption|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--filters**|array|List of filters.|/something/my_option|/something/myOption|
|--order-by**|array|List of OrderBy option.|/something/my_option|/something/myOption|
### datafactory pipeline-runs show

show a datafactory pipeline-runs.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipelines create

create a datafactory pipelines.

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
|--name**|string|The name of the folder that this Pipeline is in.|/something/my_option|/something/myOption|
### datafactory pipelines create-run

create-run a datafactory pipelines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|--reference-pipeline-run-id**|string|The pipeline run identifier. If run ID is specified the parameters of the specified run will be used to create a new run.|/something/my_option|/something/myOption|
|--is-recovery**|boolean|Recovery mode flag. If recovery mode is set to true, the specified referenced pipeline run and the new run will be grouped under the same groupId.|/something/my_option|/something/myOption|
|--start-activity-name**|string|In recovery mode, the rerun will start from this activity. If not specified, all activities will run.|/something/my_option|/something/myOption|
|--start-from-failure**|boolean|In recovery mode, if set to true, the rerun will start from failed activities. The property will be used only if startActivityName is not specified.|/something/my_option|/something/myOption|
|--parameters**|dictionary|Parameters of the pipeline run. These parameters will be used only if the runId is not specified.|/something/my_option|/something/myOption|
### datafactory pipelines delete

delete a datafactory pipelines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipelines list

list a datafactory pipelines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipelines show

show a datafactory pipelines.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory pipelines update

create a datafactory pipelines.

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
|--name**|string|The name of the folder that this Pipeline is in.|/something/my_option|/something/myOption|
### datafactory trigger-runs query-by-factory

query-by-factory a datafactory trigger-runs.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the pipeline run.|/something/my_option|/something/myOption|
|**--last-updated-after**|date-time|The time at or after which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|**--last-updated-before**|date-time|The time at or before which the run event was updated in 'ISO 8601' format.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--filters**|array|List of filters.|/something/my_option|/something/myOption|
|--order-by**|array|List of OrderBy option.|/something/my_option|/something/myOption|
### datafactory trigger-runs rerun

rerun a datafactory trigger-runs.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers create

create a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--trigger**|object|Trigger resource definition.|/something/my_option|/something/myOption|
|**--type**|string|Trigger type.|/something/my_option|/something/myOption|
|--description**|string|Trigger description.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the trigger.|/something/my_option|/something/myOption|
### datafactory triggers delete

delete a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers get-event-subscription-status

get-event-subscription-status a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers list

list a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers query-by-factory

query-by-factory a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--filter-parameters**|object|Parameters to filter the triggers.|/something/my_option|/something/myOption|
|--continuation-token**|string|The continuation token for getting the next page of results. Null for first page.|/something/my_option|/something/myOption|
|--parent-trigger-name**|string|The name of the parent TumblingWindowTrigger to get the child rerun triggers|/something/my_option|/something/myOption|
### datafactory triggers show

show a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers start

start a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers stop

stop a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers subscribe-to-events

subscribe-to-events a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers unsubscribe-from-events

unsubscribe-from-events a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
### datafactory triggers update

create a datafactory triggers.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--api-version**|constant|Api Version|/something/my_option|/something/myOption|
|**--trigger**|object|Trigger resource definition.|/something/my_option|/something/myOption|
|**--type**|string|Trigger type.|/something/my_option|/something/myOption|
|--description**|string|Trigger description.|/something/my_option|/something/myOption|
|--annotations**|array|List of tags that can be used for describing the trigger.|/something/my_option|/something/myOption|