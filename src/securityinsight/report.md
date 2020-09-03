# Azure CLI Module Creation Report

### sentinel action list

list a sentinel action.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel action|Actions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByAlertRule|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|

### sentinel alert-rule create

create a sentinel alert-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule|AlertRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdateAction|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--action-id**|string|Action ID|action_id|actionId|
|**--etag**|string|Etag of the azure resource|etag|etag|
|**--logic-app-resource-id**|string|Logic App Resource Id, /subscriptions/{my-subscription}/resourceGroups/{my-resource-group}/providers/Microsoft.Logic/workflows/{my-workflow-id}.|logic_app_resource_id|logicAppResourceId|
|**--trigger-uri**|string|Logic App Callback URL for this specific workflow.|trigger_uri|triggerUri|
|**--fusion-alert-rule**|object|Represents Fusion alert rule.|fusion_alert_rule|FusionAlertRule|
|**--microsoft-security-incident-creation-alert-rule**|object|Represents MicrosoftSecurityIncidentCreation rule.|microsoft_security_incident_creation_alert_rule|MicrosoftSecurityIncidentCreationAlertRule|
|**--scheduled-alert-rule**|object|Represents scheduled alert rule.|scheduled_alert_rule|ScheduledAlertRule|

### sentinel alert-rule delete

delete a sentinel alert-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule|AlertRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|DeleteAction|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--action-id**|string|Action ID|action_id|actionId|

### sentinel alert-rule get-action

get-action a sentinel alert-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule|AlertRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-action|GetAction|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--action-id**|string|Action ID|action_id|actionId|

### sentinel alert-rule list

list a sentinel alert-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule|AlertRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### sentinel alert-rule show

show a sentinel alert-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule|AlertRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|

### sentinel alert-rule update

update a sentinel alert-rule.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule|AlertRules|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--fusion-alert-rule**|object|Represents Fusion alert rule.|fusion_alert_rule|FusionAlertRule|
|**--microsoft-security-incident-creation-alert-rule**|object|Represents MicrosoftSecurityIncidentCreation rule.|microsoft_security_incident_creation_alert_rule|MicrosoftSecurityIncidentCreationAlertRule|
|**--scheduled-alert-rule**|object|Represents scheduled alert rule.|scheduled_alert_rule|ScheduledAlertRule|

### sentinel alert-rule-template list

list a sentinel alert-rule-template.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule-template|AlertRuleTemplates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### sentinel alert-rule-template show

show a sentinel alert-rule-template.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel alert-rule-template|AlertRuleTemplates|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--alert-rule-template-id**|string|Alert rule template ID|alert_rule_template_id|alertRuleTemplateId|

### sentinel bookmark create

create a sentinel bookmark.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel bookmark|Bookmarks|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|bookmarkId|
|**--etag**|string|Etag of the azure resource|etag|etag|
|**--created**|date-time|The time the bookmark was created|created|created|
|**--display-name**|string|The display name of the bookmark|display_name|displayName|
|**--labels**|array|List of labels relevant to this bookmark|labels|labels|
|**--notes**|string|The notes of the bookmark|notes|notes|
|**--query**|string|The query of the bookmark.|query|query|
|**--query-result**|string|The query result of the bookmark.|query_result|queryResult|
|**--updated**|date-time|The last time the bookmark was updated|updated|updated|
|**--incident-info**|object|Describes an incident that relates to bookmark|incident_info|incidentInfo|
|**--updated-by-object-id**|uuid|The object id of the user.|object_id|objectId|
|**--created-by-object-id**|uuid|The object id of the user.|user_info_object_id|objectId|

### sentinel bookmark delete

delete a sentinel bookmark.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel bookmark|Bookmarks|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|bookmarkId|

### sentinel bookmark list

list a sentinel bookmark.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel bookmark|Bookmarks|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### sentinel bookmark show

show a sentinel bookmark.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel bookmark|Bookmarks|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|bookmarkId|

### sentinel bookmark update

update a sentinel bookmark.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel bookmark|Bookmarks|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|bookmarkId|
|**--etag**|string|Etag of the azure resource|etag|etag|
|**--created**|date-time|The time the bookmark was created|created|created|
|**--display-name**|string|The display name of the bookmark|display_name|displayName|
|**--labels**|array|List of labels relevant to this bookmark|labels|labels|
|**--notes**|string|The notes of the bookmark|notes|notes|
|**--query**|string|The query of the bookmark.|query|query|
|**--query-result**|string|The query result of the bookmark.|query_result|queryResult|
|**--updated**|date-time|The last time the bookmark was updated|updated|updated|
|**--incident-info**|object|Describes an incident that relates to bookmark|incident_info|incidentInfo|
|**--updated-by-object-id**|uuid|The object id of the user.|object_id|objectId|
|**--created-by-object-id**|uuid|The object id of the user.|user_info_object_id|objectId|

### sentinel data-connector create

create a sentinel data-connector.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel data-connector|DataConnectors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-connector-id**|string|Connector ID|data_connector_id|dataConnectorId|
|**--aad-data-connector**|object|Represents AAD (Azure Active Directory) data connector.|aad_data_connector|AADDataConnector|
|**--aatp-data-connector**|object|Represents AATP (Azure Advanced Threat Protection) data connector.|aatp_data_connector|AATPDataConnector|
|**--asc-data-connector**|object|Represents ASC (Azure Security Center) data connector.|asc_data_connector|ASCDataConnector|
|**--aws-cloud-trail-data-connector**|object|Represents Amazon Web Services CloudTrail data connector.|aws_cloud_trail_data_connector|AwsCloudTrailDataConnector|
|**--mcas-data-connector**|object|Represents MCAS (Microsoft Cloud App Security) data connector.|mcas_data_connector|MCASDataConnector|
|**--mdatp-data-connector**|object|Represents MDATP (Microsoft Defender Advanced Threat Protection) data connector.|mdatp_data_connector|MDATPDataConnector|
|**--office-data-connector**|object|Represents office data connector.|office_data_connector|OfficeDataConnector|
|**--ti-data-connector**|object|Represents threat intelligence data connector.|ti_data_connector|TIDataConnector|

### sentinel data-connector delete

delete a sentinel data-connector.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel data-connector|DataConnectors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-connector-id**|string|Connector ID|data_connector_id|dataConnectorId|

### sentinel data-connector list

list a sentinel data-connector.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel data-connector|DataConnectors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### sentinel data-connector show

show a sentinel data-connector.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel data-connector|DataConnectors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-connector-id**|string|Connector ID|data_connector_id|dataConnectorId|

### sentinel data-connector update

update a sentinel data-connector.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel data-connector|DataConnectors|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-connector-id**|string|Connector ID|data_connector_id|dataConnectorId|
|**--aad-data-connector**|object|Represents AAD (Azure Active Directory) data connector.|aad_data_connector|AADDataConnector|
|**--aatp-data-connector**|object|Represents AATP (Azure Advanced Threat Protection) data connector.|aatp_data_connector|AATPDataConnector|
|**--asc-data-connector**|object|Represents ASC (Azure Security Center) data connector.|asc_data_connector|ASCDataConnector|
|**--aws-cloud-trail-data-connector**|object|Represents Amazon Web Services CloudTrail data connector.|aws_cloud_trail_data_connector|AwsCloudTrailDataConnector|
|**--mcas-data-connector**|object|Represents MCAS (Microsoft Cloud App Security) data connector.|mcas_data_connector|MCASDataConnector|
|**--mdatp-data-connector**|object|Represents MDATP (Microsoft Defender Advanced Threat Protection) data connector.|mdatp_data_connector|MDATPDataConnector|
|**--office-data-connector**|object|Represents office data connector.|office_data_connector|OfficeDataConnector|
|**--ti-data-connector**|object|Represents threat intelligence data connector.|ti_data_connector|TIDataConnector|

### sentinel incident create

create a sentinel incident.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident|Incidents|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--etag**|string|Etag of the azure resource|etag|etag|
|**--classification**|choice|The reason the incident was closed|classification|classification|
|**--classification-comment**|string|Describes the reason the incident was closed|classification_comment|classificationComment|
|**--classification-reason**|choice|The classification reason the incident was closed with|classification_reason|classificationReason|
|**--description**|string|The description of the incident|description|description|
|**--first-activity-time-utc**|date-time|The time of the first activity in the incident|first_activity_time_utc|firstActivityTimeUtc|
|**--labels**|array|List of labels relevant to this incident|labels|labels|
|**--last-activity-time-utc**|date-time|The time of the last activity in the incident|last_activity_time_utc|lastActivityTimeUtc|
|**--owner**|object|Describes a user that the incident is assigned to|owner|owner|
|**--severity**|choice|The severity of the incident|severity|severity|
|**--status**|choice|The status of the incident|status|status|
|**--title**|string|The title of the incident|title|title|

### sentinel incident delete

delete a sentinel incident.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident|Incidents|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|

### sentinel incident list

list a sentinel incident.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident|Incidents|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--filter**|string|Filters the results, based on a Boolean condition. Optional.|filter|$filter|
|**--orderby**|string|Sorts the results. Optional.|orderby|$orderby|
|**--top**|integer|Returns only the first n results. Optional.|top|$top|
|**--skip-token**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls. Optional.|skip_token|$skipToken|

### sentinel incident show

show a sentinel incident.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident|Incidents|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|

### sentinel incident update

update a sentinel incident.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident|Incidents|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--etag**|string|Etag of the azure resource|etag|etag|
|**--classification**|choice|The reason the incident was closed|classification|classification|
|**--classification-comment**|string|Describes the reason the incident was closed|classification_comment|classificationComment|
|**--classification-reason**|choice|The classification reason the incident was closed with|classification_reason|classificationReason|
|**--description**|string|The description of the incident|description|description|
|**--first-activity-time-utc**|date-time|The time of the first activity in the incident|first_activity_time_utc|firstActivityTimeUtc|
|**--labels**|array|List of labels relevant to this incident|labels|labels|
|**--last-activity-time-utc**|date-time|The time of the last activity in the incident|last_activity_time_utc|lastActivityTimeUtc|
|**--owner**|object|Describes a user that the incident is assigned to|owner|owner|
|**--severity**|choice|The severity of the incident|severity|severity|
|**--status**|choice|The status of the incident|status|status|
|**--title**|string|The title of the incident|title|title|

### sentinel incident-comment create

create a sentinel incident-comment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident-comment|IncidentComments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateComment|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--incident-comment-id**|string|Incident comment ID|incident_comment_id|incidentCommentId|
|**--message**|string|The comment message|message|message|

### sentinel incident-comment list

list a sentinel incident-comment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident-comment|IncidentComments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByIncident|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--filter**|string|Filters the results, based on a Boolean condition. Optional.|filter|$filter|
|**--orderby**|string|Sorts the results. Optional.|orderby|$orderby|
|**--top**|integer|Returns only the first n results. Optional.|top|$top|
|**--skip-token**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls. Optional.|skip_token|$skipToken|

### sentinel incident-comment show

show a sentinel incident-comment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|sentinel incident-comment|IncidentComments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--incident-comment-id**|string|Incident comment ID|incident_comment_id|incidentCommentId|
