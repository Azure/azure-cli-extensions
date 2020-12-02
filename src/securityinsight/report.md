# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az sentinel|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az sentinel` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az sentinel alert-rule|AlertRules|[commands](#CommandsInAlertRules)|
|az sentinel action|Actions|[commands](#CommandsInActions)|
|az sentinel alert-rule-template|AlertRuleTemplates|[commands](#CommandsInAlertRuleTemplates)|
|az sentinel bookmark|Bookmarks|[commands](#CommandsInBookmarks)|
|az sentinel data-connector|DataConnectors|[commands](#CommandsInDataConnectors)|
|az sentinel incident|Incidents|[commands](#CommandsInIncidents)|
|az sentinel incident-comment|IncidentComments|[commands](#CommandsInIncidentComments)|

## COMMANDS
### <a name="CommandsInActions">Commands in `az sentinel action` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel action list](#ActionsListByAlertRule)|ListByAlertRule|[Parameters](#ParametersActionsListByAlertRule)|[Example](#ExamplesActionsListByAlertRule)|

### <a name="CommandsInAlertRules">Commands in `az sentinel alert-rule` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel alert-rule list](#AlertRulesList)|List|[Parameters](#ParametersAlertRulesList)|[Example](#ExamplesAlertRulesList)|
|[az sentinel alert-rule show](#AlertRulesGet)|Get|[Parameters](#ParametersAlertRulesGet)|[Example](#ExamplesAlertRulesGet)|
|[az sentinel alert-rule create](#AlertRulesCreateOrUpdateAction)|CreateOrUpdateAction|[Parameters](#ParametersAlertRulesCreateOrUpdateAction)|[Example](#ExamplesAlertRulesCreateOrUpdateAction)|
|[az sentinel alert-rule create](#AlertRulesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAlertRulesCreateOrUpdate#Create)|[Example](#ExamplesAlertRulesCreateOrUpdate#Create)|
|[az sentinel alert-rule update](#AlertRulesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersAlertRulesCreateOrUpdate#Update)|Not Found|
|[az sentinel alert-rule delete](#AlertRulesDeleteAction)|DeleteAction|[Parameters](#ParametersAlertRulesDeleteAction)|[Example](#ExamplesAlertRulesDeleteAction)|
|[az sentinel alert-rule delete](#AlertRulesDelete)|Delete|[Parameters](#ParametersAlertRulesDelete)|[Example](#ExamplesAlertRulesDelete)|
|[az sentinel alert-rule get-action](#AlertRulesGetAction)|GetAction|[Parameters](#ParametersAlertRulesGetAction)|[Example](#ExamplesAlertRulesGetAction)|

### <a name="CommandsInAlertRuleTemplates">Commands in `az sentinel alert-rule-template` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel alert-rule-template list](#AlertRuleTemplatesList)|List|[Parameters](#ParametersAlertRuleTemplatesList)|[Example](#ExamplesAlertRuleTemplatesList)|
|[az sentinel alert-rule-template show](#AlertRuleTemplatesGet)|Get|[Parameters](#ParametersAlertRuleTemplatesGet)|[Example](#ExamplesAlertRuleTemplatesGet)|

### <a name="CommandsInBookmarks">Commands in `az sentinel bookmark` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel bookmark list](#BookmarksList)|List|[Parameters](#ParametersBookmarksList)|[Example](#ExamplesBookmarksList)|
|[az sentinel bookmark show](#BookmarksGet)|Get|[Parameters](#ParametersBookmarksGet)|[Example](#ExamplesBookmarksGet)|
|[az sentinel bookmark create](#BookmarksCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBookmarksCreateOrUpdate#Create)|[Example](#ExamplesBookmarksCreateOrUpdate#Create)|
|[az sentinel bookmark update](#BookmarksCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersBookmarksCreateOrUpdate#Update)|Not Found|
|[az sentinel bookmark delete](#BookmarksDelete)|Delete|[Parameters](#ParametersBookmarksDelete)|[Example](#ExamplesBookmarksDelete)|

### <a name="CommandsInDataConnectors">Commands in `az sentinel data-connector` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel data-connector list](#DataConnectorsList)|List|[Parameters](#ParametersDataConnectorsList)|[Example](#ExamplesDataConnectorsList)|
|[az sentinel data-connector show](#DataConnectorsGet)|Get|[Parameters](#ParametersDataConnectorsGet)|[Example](#ExamplesDataConnectorsGet)|
|[az sentinel data-connector create](#DataConnectorsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDataConnectorsCreateOrUpdate#Create)|[Example](#ExamplesDataConnectorsCreateOrUpdate#Create)|
|[az sentinel data-connector update](#DataConnectorsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersDataConnectorsCreateOrUpdate#Update)|Not Found|
|[az sentinel data-connector delete](#DataConnectorsDelete)|Delete|[Parameters](#ParametersDataConnectorsDelete)|[Example](#ExamplesDataConnectorsDelete)|

### <a name="CommandsInIncidents">Commands in `az sentinel incident` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel incident list](#IncidentsList)|List|[Parameters](#ParametersIncidentsList)|[Example](#ExamplesIncidentsList)|
|[az sentinel incident show](#IncidentsGet)|Get|[Parameters](#ParametersIncidentsGet)|[Example](#ExamplesIncidentsGet)|
|[az sentinel incident create](#IncidentsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersIncidentsCreateOrUpdate#Create)|[Example](#ExamplesIncidentsCreateOrUpdate#Create)|
|[az sentinel incident update](#IncidentsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersIncidentsCreateOrUpdate#Update)|Not Found|
|[az sentinel incident delete](#IncidentsDelete)|Delete|[Parameters](#ParametersIncidentsDelete)|[Example](#ExamplesIncidentsDelete)|

### <a name="CommandsInIncidentComments">Commands in `az sentinel incident-comment` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az sentinel incident-comment list](#IncidentCommentsListByIncident)|ListByIncident|[Parameters](#ParametersIncidentCommentsListByIncident)|[Example](#ExamplesIncidentCommentsListByIncident)|
|[az sentinel incident-comment show](#IncidentCommentsGet)|Get|[Parameters](#ParametersIncidentCommentsGet)|[Example](#ExamplesIncidentCommentsGet)|
|[az sentinel incident-comment create](#IncidentCommentsCreateComment)|CreateComment|[Parameters](#ParametersIncidentCommentsCreateComment)|[Example](#ExamplesIncidentCommentsCreateComment)|


## COMMAND DETAILS

### group `az sentinel action`
#### <a name="ActionsListByAlertRule">Command `az sentinel action list`</a>

##### <a name="ExamplesActionsListByAlertRule">Example</a>
```
az sentinel action list --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name \
"myWorkspace"
```
##### <a name="ParametersActionsListByAlertRule">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|

### group `az sentinel alert-rule`
#### <a name="AlertRulesList">Command `az sentinel alert-rule list`</a>

##### <a name="ExamplesAlertRulesList">Example</a>
```
az sentinel alert-rule list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRulesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="AlertRulesGet">Command `az sentinel alert-rule show`</a>

##### <a name="ExamplesAlertRulesGet">Example</a>
```
az sentinel alert-rule show --resource-group "myRg" --rule-id "myFirstFusionRule" --workspace-name "myWorkspace"
```
##### <a name="ExamplesAlertRulesGet">Example</a>
```
az sentinel alert-rule show --resource-group "myRg" --rule-id "microsoftSecurityIncidentCreationRuleExample" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesAlertRulesGet">Example</a>
```
az sentinel alert-rule show --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name \
"myWorkspace"
```
##### <a name="ParametersAlertRulesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|

#### <a name="AlertRulesCreateOrUpdateAction">Command `az sentinel alert-rule create`</a>

##### <a name="ExamplesAlertRulesCreateOrUpdateAction">Example</a>
```
az sentinel alert-rule create --etag "\\"0300bf09-0000-0000-0000-5c37296e0000\\"" --logic-app-resource-id \
"/subscriptions/d0cfe6b2-9ac0-4464-9919-dccaee2e48c0/resourceGroups/myRg/providers/Microsoft.Logic/workflows/MyAlerts" \
--trigger-uri "https://prod-31.northcentralus.logic.azure.com:443/workflows/cd3765391efd48549fd7681ded1d48d7/triggers/m\
anual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=signature" --action-id \
"912bec42-cb66-4c03-ac63-1761b6898c3e" --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRulesCreateOrUpdateAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--action-id**|string|Action ID|action_id|actionId|
|**--etag**|string|Etag of the azure resource|etag|etag|
|**--logic-app-resource-id**|string|Logic App Resource Id, /subscriptions/{my-subscription}/resourceGroups/{my-resource-group}/providers/Microsoft.Logic/workflows/{my-workflow-id}.|logic_app_resource_id|logicAppResourceId|
|**--trigger-uri**|string|Logic App Callback URL for this specific workflow.|trigger_uri|triggerUri|

#### <a name="AlertRulesCreateOrUpdate#Create">Command `az sentinel alert-rule create`</a>

##### <a name="ExamplesAlertRulesCreateOrUpdate#Create">Example</a>
```
az sentinel alert-rule create --fusion-alert-rule etag="3d00c3ca-0000-0100-0000-5d42d5010000" \
alert-rule-template-name="f71aba3d-28fb-450b-b192-4e76a83015c8" enabled=true --resource-group "myRg" --rule-id \
"myFirstFusionRule" --workspace-name "myWorkspace"
```
##### <a name="ExamplesAlertRulesCreateOrUpdate#Create">Example</a>
```
az sentinel alert-rule create --microsoft-security-incident-creation-alert-rule etag="\\"260097e0-0000-0d00-0000-5d6fa8\
8f0000\\"" product-filter="Microsoft Cloud App Security" display-name="testing displayname" enabled=true \
--resource-group "myRg" --rule-id "microsoftSecurityIncidentCreationRuleExample" --workspace-name "myWorkspace"
```
##### <a name="ExamplesAlertRulesCreateOrUpdate#Create">Example</a>
```
az sentinel alert-rule create --scheduled-alert-rule etag="\\"0300bf09-0000-0000-0000-5c37296e0000\\"" \
query="ProtectionStatus | extend HostCustomEntity = Computer | extend IPCustomEntity = ComputerIP_Hidden" \
query-frequency="PT1H" query-period="P2DT1H30M" severity="High" trigger-operator="GreaterThan" trigger-threshold=0 \
description="" display-name="Rule2" enabled=true suppression-duration="PT1H" suppression-enabled=false \
tactics="Persistence" tactics="LateralMovement" --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5\
" --workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRulesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--fusion-alert-rule**|object|Represents Fusion alert rule.|fusion_alert_rule|FusionAlertRule|
|**--microsoft-security-incident-creation-alert-rule**|object|Represents MicrosoftSecurityIncidentCreation rule.|microsoft_security_incident_creation_alert_rule|MicrosoftSecurityIncidentCreationAlertRule|
|**--scheduled-alert-rule**|object|Represents scheduled alert rule.|scheduled_alert_rule|ScheduledAlertRule|

#### <a name="AlertRulesCreateOrUpdate#Update">Command `az sentinel alert-rule update`</a>

##### <a name="ParametersAlertRulesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--fusion-alert-rule**|object|Represents Fusion alert rule.|fusion_alert_rule|FusionAlertRule|
|**--microsoft-security-incident-creation-alert-rule**|object|Represents MicrosoftSecurityIncidentCreation rule.|microsoft_security_incident_creation_alert_rule|MicrosoftSecurityIncidentCreationAlertRule|
|**--scheduled-alert-rule**|object|Represents scheduled alert rule.|scheduled_alert_rule|ScheduledAlertRule|

#### <a name="AlertRulesDeleteAction">Command `az sentinel alert-rule delete`</a>

##### <a name="ExamplesAlertRulesDeleteAction">Example</a>
```
az sentinel alert-rule delete --action-id "912bec42-cb66-4c03-ac63-1761b6898c3e" --resource-group "myRg" --rule-id \
"73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRulesDeleteAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--action-id**|string|Action ID|action_id|actionId|

#### <a name="AlertRulesDelete">Command `az sentinel alert-rule delete`</a>

##### <a name="ExamplesAlertRulesDelete">Example</a>
```
az sentinel alert-rule delete --resource-group "myRg" --rule-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRulesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="AlertRulesGetAction">Command `az sentinel alert-rule get-action`</a>

##### <a name="ExamplesAlertRulesGetAction">Example</a>
```
az sentinel alert-rule get-action --action-id "912bec42-cb66-4c03-ac63-1761b6898c3e" --resource-group "myRg" --rule-id \
"73e01a99-5cd7-4139-a149-9f2736ff2ab5" --workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRulesGetAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--rule-id**|string|Alert rule ID|rule_id|ruleId|
|**--action-id**|string|Action ID|action_id|actionId|

### group `az sentinel alert-rule-template`
#### <a name="AlertRuleTemplatesList">Command `az sentinel alert-rule-template list`</a>

##### <a name="ExamplesAlertRuleTemplatesList">Example</a>
```
az sentinel alert-rule-template list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRuleTemplatesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="AlertRuleTemplatesGet">Command `az sentinel alert-rule-template show`</a>

##### <a name="ExamplesAlertRuleTemplatesGet">Example</a>
```
az sentinel alert-rule-template show --alert-rule-template-id "65360bb0-8986-4ade-a89d-af3cf44d28aa" --resource-group \
"myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersAlertRuleTemplatesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--alert-rule-template-id**|string|Alert rule template ID|alert_rule_template_id|alertRuleTemplateId|

### group `az sentinel bookmark`
#### <a name="BookmarksList">Command `az sentinel bookmark list`</a>

##### <a name="ExamplesBookmarksList">Example</a>
```
az sentinel bookmark list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersBookmarksList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="BookmarksGet">Command `az sentinel bookmark show`</a>

##### <a name="ExamplesBookmarksGet">Example</a>
```
az sentinel bookmark show --bookmark-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersBookmarksGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|bookmarkId|

#### <a name="BookmarksCreateOrUpdate#Create">Command `az sentinel bookmark create`</a>

##### <a name="ExamplesBookmarksCreateOrUpdate#Create">Example</a>
```
az sentinel bookmark create --etag "\\"0300bf09-0000-0000-0000-5c37296e0000\\"" --created "2019-01-01T13:15:30Z" \
--display-name "My bookmark" --labels "Tag1" --labels "Tag2" --notes "Found a suspicious activity" --query \
"SecurityEvent | where TimeGenerated > ago(1d) and TimeGenerated < ago(2d)" --query-result "Security Event query \
result" --updated "2019-01-01T13:15:30Z" --bookmark-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersBookmarksCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="BookmarksCreateOrUpdate#Update">Command `az sentinel bookmark update`</a>

##### <a name="ParametersBookmarksCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="BookmarksDelete">Command `az sentinel bookmark delete`</a>

##### <a name="ExamplesBookmarksDelete">Example</a>
```
az sentinel bookmark delete --bookmark-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersBookmarksDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--bookmark-id**|string|Bookmark ID|bookmark_id|bookmarkId|

### group `az sentinel data-connector`
#### <a name="DataConnectorsList">Command `az sentinel data-connector list`</a>

##### <a name="ExamplesDataConnectorsList">Example</a>
```
az sentinel data-connector list --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersDataConnectorsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="DataConnectorsGet">Command `az sentinel data-connector show`</a>

##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "763f9fa1-c2d3-4fa2-93e9-bccd4899aa12" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "b96d014d-b5c2-4a01-9aba-a8058f629d42" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "06b3ccb8-1384-4bcc-aec7-852f6d57161b" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "c345bf40-8509-4ed2-b947-50cb773aaf04" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "f0cd27d2-5f03-4c06-ba31-d2dc82dcb51d" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "07e42cb3-e658-4e90-801c-efa0f29d3d44" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "c345bf40-8509-4ed2-b947-50cb773aaf04" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ExamplesDataConnectorsGet">Example</a>
```
az sentinel data-connector show --data-connector-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersDataConnectorsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-connector-id**|string|Connector ID|data_connector_id|dataConnectorId|

#### <a name="DataConnectorsCreateOrUpdate#Create">Command `az sentinel data-connector create`</a>

##### <a name="ExamplesDataConnectorsCreateOrUpdate#Create">Example</a>
```
az sentinel data-connector create --office-data-connector etag="\\"0300bf09-0000-0000-0000-5c37296e0000\\"" \
tenant-id="2070ecc9-b4d5-4ae4-adaa-936fa1954fa8" --data-connector-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" \
--resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersDataConnectorsCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="DataConnectorsCreateOrUpdate#Update">Command `az sentinel data-connector update`</a>

##### <a name="ParametersDataConnectorsCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="DataConnectorsDelete">Command `az sentinel data-connector delete`</a>

##### <a name="ExamplesDataConnectorsDelete">Example</a>
```
az sentinel data-connector delete --data-connector-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersDataConnectorsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-connector-id**|string|Connector ID|data_connector_id|dataConnectorId|

### group `az sentinel incident`
#### <a name="IncidentsList">Command `az sentinel incident list`</a>

##### <a name="ExamplesIncidentsList">Example</a>
```
az sentinel incident list --orderby "properties/createdTimeUtc desc" --top 1 --resource-group "myRg" --workspace-name \
"myWorkspace"
```
##### <a name="ParametersIncidentsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--filter**|string|Filters the results, based on a Boolean condition. Optional.|filter|$filter|
|**--orderby**|string|Sorts the results. Optional.|orderby|$orderby|
|**--top**|integer|Returns only the first n results. Optional.|top|$top|
|**--skip-token**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls. Optional.|skip_token|$skipToken|

#### <a name="IncidentsGet">Command `az sentinel incident show`</a>

##### <a name="ExamplesIncidentsGet">Example</a>
```
az sentinel incident show --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersIncidentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|

#### <a name="IncidentsCreateOrUpdate#Create">Command `az sentinel incident create`</a>

##### <a name="ExamplesIncidentsCreateOrUpdate#Create">Example</a>
```
az sentinel incident create --etag "\\"0300bf09-0000-0000-0000-5c37296e0000\\"" --description "This is a demo \
incident" --classification "FalsePositive" --classification-comment "Not a malicious activity" --classification-reason \
"IncorrectAlertLogic" --first-activity-time-utc "2019-01-01T13:00:30Z" --last-activity-time-utc "2019-01-01T13:05:30Z" \
--owner object-id="2046feea-040d-4a46-9e2b-91c2941bfa70" --severity "High" --status "Closed" --title "My incident" \
--incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersIncidentsCreateOrUpdate#Create">Parameters</a> 
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

#### <a name="IncidentsCreateOrUpdate#Update">Command `az sentinel incident update`</a>

##### <a name="ParametersIncidentsCreateOrUpdate#Update">Parameters</a> 
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

#### <a name="IncidentsDelete">Command `az sentinel incident delete`</a>

##### <a name="ExamplesIncidentsDelete">Example</a>
```
az sentinel incident delete --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersIncidentsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|

### group `az sentinel incident-comment`
#### <a name="IncidentCommentsListByIncident">Command `az sentinel incident-comment list`</a>

##### <a name="ExamplesIncidentCommentsListByIncident">Example</a>
```
az sentinel incident-comment list --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" \
--workspace-name "myWorkspace"
```
##### <a name="ParametersIncidentCommentsListByIncident">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--filter**|string|Filters the results, based on a Boolean condition. Optional.|filter|$filter|
|**--orderby**|string|Sorts the results. Optional.|orderby|$orderby|
|**--top**|integer|Returns only the first n results. Optional.|top|$top|
|**--skip-token**|string|Skiptoken is only used if a previous operation returned a partial result. If a previous response contains a nextLink element, the value of the nextLink element will include a skiptoken parameter that specifies a starting point to use for subsequent calls. Optional.|skip_token|$skipToken|

#### <a name="IncidentCommentsGet">Command `az sentinel incident-comment show`</a>

##### <a name="ExamplesIncidentCommentsGet">Example</a>
```
az sentinel incident-comment show --incident-comment-id "4bb36b7b-26ff-4d1c-9cbe-0d8ab3da0014" --incident-id \
"73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersIncidentCommentsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--incident-comment-id**|string|Incident comment ID|incident_comment_id|incidentCommentId|

#### <a name="IncidentCommentsCreateComment">Command `az sentinel incident-comment create`</a>

##### <a name="ExamplesIncidentCommentsCreateComment">Example</a>
```
az sentinel incident-comment create --message "Some message" --incident-comment-id "4bb36b7b-26ff-4d1c-9cbe-0d8ab3da001\
4" --incident-id "73e01a99-5cd7-4139-a149-9f2736ff2ab5" --resource-group "myRg" --workspace-name "myWorkspace"
```
##### <a name="ParametersIncidentCommentsCreateComment">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group within the user's subscription. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--incident-id**|string|Incident ID|incident_id|incidentId|
|**--incident-comment-id**|string|Incident comment ID|incident_comment_id|incidentCommentId|
|**--message**|string|The comment message|message|message|
