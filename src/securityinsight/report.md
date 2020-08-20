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
|**--etag**|string|Etag of the azure resource|etag|
|**--logic-app-resource-id**|string|Logic App Resource Id, /subscriptions/{my-subscription}/resourceGroups/{my-resource-group}/providers/Microsoft.Logic/workflows/{my-workflow-id}.|logic_app_resource_id|
|**--trigger-uri**|string|Logic App Callback URL for this specific workflow.|trigger_uri|
|**--fusion-alert-rule**|object|Represents Fusion alert rule.|fusion_alert_rule|
|**--microsoft-security-incident-creation-alert-rule**|object|Represents MicrosoftSecurityIncidentCreation rule.|microsoft_security_incident_creation_alert_rule|
|**--scheduled-alert-rule**|object|Represents scheduled alert rule.|scheduled_alert_rule|
### sentinel alert-rule delete

delete a sentinel alert-rule.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--rule-id**|string|Alert rule ID|rule_id|
|**--action-id**|string|Action ID|action_id|
### sentinel alert-rule get-action

get-action a sentinel alert-rule.

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
### sentinel alert-rule-template list

list a sentinel alert-rule-template.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
### sentinel alert-rule-template show

show a sentinel alert-rule-template.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--alert-rule-template-id**|string|Alert rule template ID|alert_rule_template_id|
### sentinel bookmark create

create a sentinel bookmark.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|
|**--etag**|string|Etag of the azure resource|etag|
|**--created**|date-time|The time the bookmark was created|created|
|**--display-name**|string|The display name of the bookmark|display_name|
|**--labels**|array|List of labels relevant to this bookmark|labels|
|**--notes**|string|The notes of the bookmark|notes|
|**--query**|string|The query of the bookmark.|query|
|**--query-result**|string|The query result of the bookmark.|query_result|
|**--updated**|date-time|The last time the bookmark was updated|updated|
|**--incident-info**|object|Describes an incident that relates to bookmark|incident_info|
|**--updated-by-object-id**|uuid|The object id of the user.|object_id_properties_updated_by_object_id|
|**--created-by-object-id**|uuid|The object id of the user.|object_id_properties_updated_by_object_id|
### sentinel bookmark delete

delete a sentinel bookmark.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|
### sentinel bookmark list

list a sentinel bookmark.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
### sentinel bookmark show

show a sentinel bookmark.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|
### sentinel bookmark update

create a sentinel bookmark.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|
|**--etag**|string|Etag of the azure resource|etag|
|**--created**|date-time|The time the bookmark was created|created|
|**--display-name**|string|The display name of the bookmark|display_name|
|**--labels**|array|List of labels relevant to this bookmark|labels|
|**--notes**|string|The notes of the bookmark|notes|
|**--query**|string|The query of the bookmark.|query|
|**--query-result**|string|The query result of the bookmark.|query_result|
|**--updated**|date-time|The last time the bookmark was updated|updated|
|**--incident-info**|object|Describes an incident that relates to bookmark|incident_info|
|**--updated-by-object-id**|uuid|The object id of the user.|object_id_properties_updated_by_object_id|
|**--created-by-object-id**|uuid|The object id of the user.|object_id_properties_updated_by_object_id|
### sentinel data-connector create

create a sentinel data-connector.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--data-connector-id**|string|Connector ID|data_connector_id|
|**--aad-data-connector**|object|Represents AAD (Azure Active Directory) data connector.|aad_data_connector|
|**--aatp-data-connector**|object|Represents AATP (Azure Advanced Threat Protection) data connector.|aatp_data_connector|
|**--asc-data-connector**|object|Represents ASC (Azure Security Center) data connector.|asc_data_connector|
|**--aws-cloud-trail-data-connector**|object|Represents Amazon Web Services CloudTrail data connector.|aws_cloud_trail_data_connector|
|**--m-c-a-s-data-connector**|object|Represents MCAS (Microsoft Cloud App Security) data connector.|m_c_a_s_data_connector|
|**--mdatp-data-connector**|object|Represents MDATP (Microsoft Defender Advanced Threat Protection) data connector.|mdatp_data_connector|
|**--office-data-connector**|object|Represents office data connector.|office_data_connector|
|**--t-i-data-connector**|object|Represents threat intelligence data connector.|t_i_data_connector|
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
|**--aad-data-connector**|object|Represents AAD (Azure Active Directory) data connector.|aad_data_connector|
|**--aatp-data-connector**|object|Represents AATP (Azure Advanced Threat Protection) data connector.|aatp_data_connector|
|**--asc-data-connector**|object|Represents ASC (Azure Security Center) data connector.|asc_data_connector|
|**--aws-cloud-trail-data-connector**|object|Represents Amazon Web Services CloudTrail data connector.|aws_cloud_trail_data_connector|
|**--m-c-a-s-data-connector**|object|Represents MCAS (Microsoft Cloud App Security) data connector.|m_c_a_s_data_connector|
|**--mdatp-data-connector**|object|Represents MDATP (Microsoft Defender Advanced Threat Protection) data connector.|mdatp_data_connector|
|**--office-data-connector**|object|Represents office data connector.|office_data_connector|
|**--t-i-data-connector**|object|Represents threat intelligence data connector.|t_i_data_connector|
### sentinel incident create

create a sentinel incident.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
|**--etag**|string|Etag of the azure resource|etag|
|**--classification**|choice|The reason the incident was closed|classification|
|**--classification-comment**|string|Describes the reason the incident was closed|classification_comment|
|**--classification-reason**|choice|The classification reason the incident was closed with|classification_reason|
|**--description**|string|The description of the incident|description|
|**--first-activity-time-utc**|date-time|The time of the first activity in the incident|first_activity_time_utc|
|**--labels**|array|List of labels relevant to this incident|labels|
|**--last-activity-time-utc**|date-time|The time of the last activity in the incident|last_activity_time_utc|
|**--owner**|object|Describes a user that the incident is assigned to|owner|
|**--severity**|choice|The severity of the incident|severity|
|**--status**|choice|The status of the incident|status|
|**--title**|string|The title of the incident|title|
### sentinel incident delete

delete a sentinel incident.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
### sentinel incident list

list a sentinel incident.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--filter**|string|Filters the results, based on a Boolean condition. Optional.|filter|
|**--orderby**|string|Sorts the results. Optional.|orderby|
|**--top**|integer|Returns only the first n results. Optional.|top|
|**--skip-token**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls. Optional.|skip_token|
### sentinel incident show

show a sentinel incident.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
### sentinel incident update

create a sentinel incident.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
|**--etag**|string|Etag of the azure resource|etag|
|**--classification**|choice|The reason the incident was closed|classification|
|**--classification-comment**|string|Describes the reason the incident was closed|classification_comment|
|**--classification-reason**|choice|The classification reason the incident was closed with|classification_reason|
|**--description**|string|The description of the incident|description|
|**--first-activity-time-utc**|date-time|The time of the first activity in the incident|first_activity_time_utc|
|**--labels**|array|List of labels relevant to this incident|labels|
|**--last-activity-time-utc**|date-time|The time of the last activity in the incident|last_activity_time_utc|
|**--owner**|object|Describes a user that the incident is assigned to|owner|
|**--severity**|choice|The severity of the incident|severity|
|**--status**|choice|The status of the incident|status|
|**--title**|string|The title of the incident|title|
### sentinel incident-comment create

create a sentinel incident-comment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
|**--incident-comment-id**|string|Incident comment ID|incident_comment_id|
|**--message**|string|The comment message|message|
### sentinel incident-comment list

list a sentinel incident-comment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
|**--filter**|string|Filters the results, based on a Boolean condition. Optional.|filter|
|**--orderby**|string|Sorts the results. Optional.|orderby|
|**--top**|integer|Returns only the first n results. Optional.|top|
|**--skip-token**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls. Optional.|skip_token|
### sentinel incident-comment show

show a sentinel incident-comment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|
|**--workspace-name**|string|The name of the workspace.|workspace_name|
|**--incident-id**|string|Incident ID|incident_id|
|**--incident-comment-id**|string|Incident comment ID|incident_comment_id|