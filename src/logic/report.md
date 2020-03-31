# Azure CLI Module Creation Report

### logic integration-account create

create a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--sku**|object|The sku.|sku|sku|
|**--integration_service_environment**|object|The integration service environment.|integration_service_environment|integration_service_environment|
|**--state**|choice|The workflow state.|state|state|
### logic integration-account delete

delete a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
### logic integration-account list

list a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--top**|integer|The number of items to be included in the result.|top|top|
### logic integration-account list-callback-url

list-callback-url a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
|**--not_after**|date-time|The expiry time.|not_after|not_after|
|**--key_type**|choice|The key type.|key_type|key_type|
### logic integration-account list-key-vault-key

list-key-vault-key a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
|**--key_vault**|object|The key vault reference.|key_vault|key_vault|
|**--skip_token**|string|The skip token.|skip_token|skip_token|
### logic integration-account log-tracking-event

log-tracking-event a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
|**--source_type**|string|The source type.|source_type|source_type|
|**--events**|array|The events.|events|events|
|**--track_events_options**|choice|The track events options.|track_events_options|track_events_options|
### logic integration-account regenerate-access-key

regenerate-access-key a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
|**--key_type**|choice|The key type.|key_type|key_type|
### logic integration-account show

show a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
### logic integration-account update

update a logic integration-account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--integration_account_name**|string|The integration account name.|integration_account_name|integration_account_name|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--sku**|object|The sku.|sku|sku|
|**--integration_service_environment**|object|The integration service environment.|integration_service_environment|integration_service_environment|
|**--state**|choice|The workflow state.|state|state|
### logic workflow create

create a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--endpoints_configuration**|object|The endpoints configuration.|endpoints_configuration|endpoints_configuration|
|**--integration_account**|object|The integration account.|integration_account|integration_account|
|**--integration_service_environment**|object|The integration service environment.|integration_service_environment|integration_service_environment|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|
### logic workflow delete

delete a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
### logic workflow disable

disable a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
### logic workflow enable

enable a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
### logic workflow generate-upgraded-definition

generate-upgraded-definition a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--target_schema_version**|string|The target schema version.|target_schema_version|target_schema_version|
### logic workflow list

list a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--top**|integer|The number of items to be included in the result.|top|top|
|**--filter**|string|The filter to apply on the operation. Options for filters include: State, Trigger, and ReferencedResourceId.|filter|filter|
### logic workflow list-callback-url

list-callback-url a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--not_after**|date-time|The expiry time.|not_after|not_after|
|**--key_type**|choice|The key type.|key_type|key_type|
### logic workflow list-swagger

list-swagger a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
### logic workflow move

move a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--endpoints_configuration**|object|The endpoints configuration.|endpoints_configuration|endpoints_configuration|
|**--integration_account**|object|The integration account.|integration_account|integration_account|
|**--integration_service_environment**|object|The integration service environment.|integration_service_environment|integration_service_environment|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|
### logic workflow regenerate-access-key

regenerate-access-key a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--key_type**|choice|The key type.|key_type|key_type|
### logic workflow show

show a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
### logic workflow update

update a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--endpoints_configuration**|object|The endpoints configuration.|endpoints_configuration|endpoints_configuration|
|**--integration_account**|object|The integration account.|integration_account|integration_account|
|**--integration_service_environment**|object|The integration service environment.|integration_service_environment|integration_service_environment|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|
### logic workflow validate-by-location

validate-by-location a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--location**|string|The workflow location.|location|location|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
### logic workflow validate-by-resource-group

validate-by-resource-group a logic workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--workflow_name**|string|The workflow name.|workflow_name|workflow_name|
|**--location**|string|The resource location.|location|location|
|**--tags**|dictionary|The resource tags.|tags|tags|
|**--state**|choice|The state.|state|state|
|**--endpoints_configuration**|object|The endpoints configuration.|endpoints_configuration|endpoints_configuration|
|**--integration_account**|object|The integration account.|integration_account|integration_account|
|**--integration_service_environment**|object|The integration service environment.|integration_service_environment|integration_service_environment|
|**--definition**|any|The definition.|definition|definition|
|**--parameters**|dictionary|The parameters.|parameters|parameters|