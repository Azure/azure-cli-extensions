# Azure CLI Module Creation Report

### sentinel action list

list a sentinel action.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--rule-id**|string|Alert rule ID|rule_id|
### sentinel alert-rule create

create a sentinel alert-rule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--rule-id**|string|Alert rule ID|rule_id|
|**--action-id**|string|Action ID|action_id|
|**--kind**|choice|The kind of the alert rule|kind|
|**--etag**|string|Etag of the azure resource|etag|
|**--logic-app-resource-id**|string|Logic App Resource Id, providers/Microsoft.Logic/workflows/{WorkflowID}.|logic_app_resource_id|
|**--trigger-uri**|string|Logic App Callback URL for this specific workflow.|trigger_uri|
### sentinel alert-rule delete

delete a sentinel alert-rule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--rule-id**|string|Alert rule ID|rule_id|
|**--action-id**|string|Action ID|action_id|
### sentinel alert-rule list

list a sentinel alert-rule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
### sentinel alert-rule show

show a sentinel alert-rule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--rule-id**|string|Alert rule ID|rule_id|
|**--action-id**|string|Action ID|action_id|
### sentinel data-connector create

create a sentinel data-connector.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--data-connector-id**|string|Connector ID|data_connector_id|
|**--etag**|string|Etag of the azure resource|etag|
|**--kind**|choice|The kind of the data connector|kind|
### sentinel data-connector delete

delete a sentinel data-connector.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--data-connector-id**|string|Connector ID|data_connector_id|
### sentinel data-connector list

list a sentinel data-connector.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
### sentinel data-connector show

show a sentinel data-connector.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--data-connector-id**|string|Connector ID|data_connector_id|
### sentinel data-connector update

create a sentinel data-connector.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--data-connector-id**|string|Connector ID|data_connector_id|
|**--etag**|string|Etag of the azure resource|etag|
|**--kind**|choice|The kind of the data connector|kind|