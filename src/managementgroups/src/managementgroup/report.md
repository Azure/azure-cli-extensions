# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az managementgroup|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az managementgroup` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az managementgroup||[commands](#CommandsIn)|
|az managementgroup entity|Entities|[commands](#CommandsInEntities)|
|az managementgroup hierarchy-setting|HierarchySettings|[commands](#CommandsInHierarchySettings)|
|az managementgroup management-group|ManagementGroups|[commands](#CommandsInManagementGroups)|
|az managementgroup management-group-subscription|ManagementGroupSubscriptions|[commands](#CommandsInManagementGroupSubscriptions)|

## COMMANDS
### <a name="CommandsIn">Commands in `az managementgroup` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az managementgroup start-tenant-backfill](#StartTenantBackfill)|StartTenantBackfill|[Parameters](#ParametersStartTenantBackfill)|[Example](#ExamplesStartTenantBackfill)|
|[az managementgroup tenant-backfill-status](#TenantBackfillStatus)|TenantBackfillStatus|[Parameters](#ParametersTenantBackfillStatus)|[Example](#ExamplesTenantBackfillStatus)|

### <a name="CommandsInEntities">Commands in `az managementgroup entity` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az managementgroup entity list](#EntitiesList)|List|[Parameters](#ParametersEntitiesList)|[Example](#ExamplesEntitiesList)|

### <a name="CommandsInHierarchySettings">Commands in `az managementgroup hierarchy-setting` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az managementgroup hierarchy-setting list](#HierarchySettingsList)|List|[Parameters](#ParametersHierarchySettingsList)|[Example](#ExamplesHierarchySettingsList)|
|[az managementgroup hierarchy-setting show](#HierarchySettingsGet)|Get|[Parameters](#ParametersHierarchySettingsGet)|[Example](#ExamplesHierarchySettingsGet)|
|[az managementgroup hierarchy-setting create](#HierarchySettingsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersHierarchySettingsCreateOrUpdate#Create)|[Example](#ExamplesHierarchySettingsCreateOrUpdate#Create)|
|[az managementgroup hierarchy-setting update](#HierarchySettingsUpdate)|Update|[Parameters](#ParametersHierarchySettingsUpdate)|[Example](#ExamplesHierarchySettingsUpdate)|
|[az managementgroup hierarchy-setting delete](#HierarchySettingsDelete)|Delete|[Parameters](#ParametersHierarchySettingsDelete)|[Example](#ExamplesHierarchySettingsDelete)|

### <a name="CommandsInManagementGroups">Commands in `az managementgroup management-group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az managementgroup management-group list](#ManagementGroupsList)|List|[Parameters](#ParametersManagementGroupsList)|[Example](#ExamplesManagementGroupsList)|
|[az managementgroup management-group show](#ManagementGroupsGet)|Get|[Parameters](#ParametersManagementGroupsGet)|[Example](#ExamplesManagementGroupsGet)|
|[az managementgroup management-group create](#ManagementGroupsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersManagementGroupsCreateOrUpdate#Create)|[Example](#ExamplesManagementGroupsCreateOrUpdate#Create)|
|[az managementgroup management-group update](#ManagementGroupsUpdate)|Update|[Parameters](#ParametersManagementGroupsUpdate)|[Example](#ExamplesManagementGroupsUpdate)|
|[az managementgroup management-group delete](#ManagementGroupsDelete)|Delete|[Parameters](#ParametersManagementGroupsDelete)|[Example](#ExamplesManagementGroupsDelete)|
|[az managementgroup management-group show-descendant](#ManagementGroupsGetDescendants)|GetDescendants|[Parameters](#ParametersManagementGroupsGetDescendants)|[Example](#ExamplesManagementGroupsGetDescendants)|

### <a name="CommandsInManagementGroupSubscriptions">Commands in `az managementgroup management-group-subscription` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az managementgroup management-group-subscription create](#ManagementGroupSubscriptionsCreate)|Create|[Parameters](#ParametersManagementGroupSubscriptionsCreate)|[Example](#ExamplesManagementGroupSubscriptionsCreate)|
|[az managementgroup management-group-subscription delete](#ManagementGroupSubscriptionsDelete)|Delete|[Parameters](#ParametersManagementGroupSubscriptionsDelete)|[Example](#ExamplesManagementGroupSubscriptionsDelete)|
|[az managementgroup management-group-subscription show-subscription](#ManagementGroupSubscriptionsGetSubscription)|GetSubscription|[Parameters](#ParametersManagementGroupSubscriptionsGetSubscription)|[Example](#ExamplesManagementGroupSubscriptionsGetSubscription)|
|[az managementgroup management-group-subscription show-subscription-under-management-group](#ManagementGroupSubscriptionsGetSubscriptionsUnderManagementGroup)|GetSubscriptionsUnderManagementGroup|[Parameters](#ParametersManagementGroupSubscriptionsGetSubscriptionsUnderManagementGroup)|[Example](#ExamplesManagementGroupSubscriptionsGetSubscriptionsUnderManagementGroup)|


## COMMAND DETAILS
### group `az managementgroup`
#### <a name="StartTenantBackfill">Command `az managementgroup start-tenant-backfill`</a>

##### <a name="ExamplesStartTenantBackfill">Example</a>
```
az managementgroup start-tenant-backfill
```
##### <a name="ParametersStartTenantBackfill">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="TenantBackfillStatus">Command `az managementgroup tenant-backfill-status`</a>

##### <a name="ExamplesTenantBackfillStatus">Example</a>
```
az managementgroup tenant-backfill-status
```
##### <a name="ParametersTenantBackfillStatus">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### group `az managementgroup entity`
#### <a name="EntitiesList">Command `az managementgroup entity list`</a>

##### <a name="ExamplesEntitiesList">Example</a>
```
az managementgroup entity list
```
##### <a name="ParametersEntitiesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skiptoken**|string|Page continuation token is only used if a previous operation returned a partial result.  If a previous response contains a nextLink element, the value of the nextLink element will include a token parameter that specifies a starting point to use for subsequent calls. |skiptoken|$skiptoken|
|**--skip**|integer|Number of entities to skip over when retrieving results. Passing this in will override $skipToken.|skip|$skip|
|**--top**|integer|Number of elements to return when retrieving results. Passing this in will override $skipToken.|top|$top|
|**--select**|string|This parameter specifies the fields to include in the response. Can include any combination of Name,DisplayName,Type,ParentDisplayNameChain,ParentChain, e.g. '$select=Name,DisplayName,Type,ParentDisplayNameChain,ParentNameChain'. When specified the $select parameter can override select in $skipToken.|select|$select|
|**--search**|choice|The $search parameter is used in conjunction with the $filter parameter to return three different outputs depending on the parameter passed in.  With $search=AllowedParents the API will return the entity info of all groups that the requested entity will be able to reparent to as determined by the user's permissions. With $search=AllowedChildren the API will return the entity info of all entities that can be added as children of the requested entity. With $search=ParentAndFirstLevelChildren the API will return the parent and  first level of children that the user has either direct access to or indirect access via one of their descendants. With $search=ParentOnly the API will return only the group if the user has access to at least one of the descendants of the group. With $search=ChildrenOnly the API will return only the first level of children of the group entity info specified in $filter.  The user must have direct access to the children entities or one of it's descendants for it to show up in the results.|search|$search|
|**--filter**|string|The filter parameter allows you to filter on the the name or display name fields. You can check for equality on the name field (e.g. name eq '{entityName}')  and you can check for substrings on either the name or display name fields(e.g. contains(name, '{substringToSearch}'), contains(displayName, '{substringToSearch')). Note that the '{entityName}' and '{substringToSearch}' fields are checked case insensitively.|filter|$filter|
|**--view**|choice|The view parameter allows clients to filter the type of data that is returned by the getEntities call.|view|$view|
|**--group-name**|string|A filter which allows the get entities call to focus on a particular group (i.e. "$filter=name eq 'groupName'")|group_name|groupName|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|

### group `az managementgroup hierarchy-setting`
#### <a name="HierarchySettingsList">Command `az managementgroup hierarchy-setting list`</a>

##### <a name="ExamplesHierarchySettingsList">Example</a>
```
az managementgroup hierarchy-setting list --group-id "root"
```
##### <a name="ParametersHierarchySettingsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

#### <a name="HierarchySettingsGet">Command `az managementgroup hierarchy-setting show`</a>

##### <a name="ExamplesHierarchySettingsGet">Example</a>
```
az managementgroup hierarchy-setting show --group-id "root"
```
##### <a name="ParametersHierarchySettingsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

#### <a name="HierarchySettingsCreateOrUpdate#Create">Command `az managementgroup hierarchy-setting create`</a>

##### <a name="ExamplesHierarchySettingsCreateOrUpdate#Create">Example</a>
```
az managementgroup hierarchy-setting create --default-management-group "/providers/Microsoft.Management/managementGroup\
s/DefaultGroup" --require-authorization-for-group-creation true --group-id "root"
```
##### <a name="ParametersHierarchySettingsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--require-authorization-for-group-creation**|boolean|Indicates whether RBAC access is required upon group creation under the root Management Group. If set to true, user will require Microsoft.Management/managementGroups/write action on the root Management Group scope in order to create new Groups directly under the root. This will prevent new users from creating new Management Groups, unless they are given access.|require_authorization_for_group_creation|requireAuthorizationForGroupCreation|
|**--default-management-group**|string|Settings that sets the default Management Group under which new subscriptions get added in this tenant. For example, /providers/Microsoft.Management/managementGroups/defaultGroup|default_management_group|defaultManagementGroup|

#### <a name="HierarchySettingsUpdate">Command `az managementgroup hierarchy-setting update`</a>

##### <a name="ExamplesHierarchySettingsUpdate">Example</a>
```
az managementgroup hierarchy-setting update --default-management-group "/providers/Microsoft.Management/managementGroup\
s/DefaultGroup" --require-authorization-for-group-creation true --group-id "root"
```
##### <a name="ParametersHierarchySettingsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--require-authorization-for-group-creation**|boolean|Indicates whether RBAC access is required upon group creation under the root Management Group. If set to true, user will require Microsoft.Management/managementGroups/write action on the root Management Group scope in order to create new Groups directly under the root. This will prevent new users from creating new Management Groups, unless they are given access.|require_authorization_for_group_creation|requireAuthorizationForGroupCreation|
|**--default-management-group**|string|Settings that sets the default Management Group under which new subscriptions get added in this tenant. For example, /providers/Microsoft.Management/managementGroups/defaultGroup|default_management_group|defaultManagementGroup|

#### <a name="HierarchySettingsDelete">Command `az managementgroup hierarchy-setting delete`</a>

##### <a name="ExamplesHierarchySettingsDelete">Example</a>
```
az managementgroup hierarchy-setting delete --group-id "root"
```
##### <a name="ParametersHierarchySettingsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

### group `az managementgroup management-group`
#### <a name="ManagementGroupsList">Command `az managementgroup management-group list`</a>

##### <a name="ExamplesManagementGroupsList">Example</a>
```
az managementgroup management-group list --cache-control "no-cache"
```
##### <a name="ParametersManagementGroupsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|
|**--skiptoken**|string|Page continuation token is only used if a previous operation returned a partial result.  If a previous response contains a nextLink element, the value of the nextLink element will include a token parameter that specifies a starting point to use for subsequent calls. |skiptoken|$skiptoken|

#### <a name="ManagementGroupsGet">Command `az managementgroup management-group show`</a>

##### <a name="ExamplesManagementGroupsGet">Example</a>
```
az managementgroup management-group show --cache-control "no-cache" --group-id "20000000-0001-0000-0000-000000000000"
az managementgroup management-group show --expand "ancestors" --cache-control "no-cache" --group-id \
"20000000-0001-0000-0000-00000000000"
az managementgroup management-group show --expand "children" --cache-control "no-cache" --group-id \
"20000000-0001-0000-0000-000000000000"
az managementgroup management-group show --expand "path" --cache-control "no-cache" --group-id \
"20000000-0001-0000-0000-000000000000"
az managementgroup management-group show --expand "children" --recurse true --cache-control "no-cache" --group-id \
"20000000-0001-0000-0000-000000000000"
```
##### <a name="ParametersManagementGroupsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--expand**|choice|The $expand=children query string parameter allows clients to request inclusion of children in the response payload.  $expand=path includes the path from the root group to the current group.  $expand=ancestors includes the ancestor Ids of the current group.|expand|$expand|
|**--recurse**|boolean|The $recurse=true query string parameter allows clients to request inclusion of entire hierarchy in the response payload. Note that  $expand=children must be passed up if $recurse is set to true.|recurse|$recurse|
|**--filter**|string|A filter which allows the exclusion of subscriptions from results (i.e. '$filter=children.childType ne Subscription')|filter|$filter|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|

#### <a name="ManagementGroupsCreateOrUpdate#Create">Command `az managementgroup management-group create`</a>

##### <a name="ExamplesManagementGroupsCreateOrUpdate#Create">Example</a>
```
az managementgroup management-group create --cache-control "no-cache" --display-name "ChildGroup" --id \
"/providers/Microsoft.Management/managementGroups/RootGroup" --group-id "ChildGroup"
```
##### <a name="ParametersManagementGroupsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|
|**--name**|string|The name of the management group. For example, 00000000-0000-0000-0000-000000000000|name|name|
|**--display-name**|string|The friendly name of the management group. If no value is passed then this  field will be set to the groupId.|display_name|displayName|
|**--id**|string|The fully qualified ID for the parent management group.  For example, /providers/Microsoft.Management/managementGroups/0000000-0000-0000-0000-000000000000|id|id|

#### <a name="ManagementGroupsUpdate">Command `az managementgroup management-group update`</a>

##### <a name="ExamplesManagementGroupsUpdate">Example</a>
```
az managementgroup management-group update --cache-control "no-cache" --group-id "ChildGroup" --display-name \
"AlternateDisplayName" --parent-group-id "/providers/Microsoft.Management/managementGroups/AlternateRootGroup"
```
##### <a name="ParametersManagementGroupsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|
|**--display-name**|string|The friendly name of the management group.|display_name|displayName|
|**--parent-group-id**|string|(Optional) The fully qualified ID for the parent management group.  For example, /providers/Microsoft.Management/managementGroups/0000000-0000-0000-0000-000000000000|parent_group_id|parentGroupId|

#### <a name="ManagementGroupsDelete">Command `az managementgroup management-group delete`</a>

##### <a name="ExamplesManagementGroupsDelete">Example</a>
```
az managementgroup management-group delete --cache-control "no-cache" --group-id "GroupToDelete"
```
##### <a name="ParametersManagementGroupsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|

#### <a name="ManagementGroupsGetDescendants">Command `az managementgroup management-group show-descendant`</a>

##### <a name="ExamplesManagementGroupsGetDescendants">Example</a>
```
az managementgroup management-group show-descendant --group-id "20000000-0000-0000-0000-000000000000"
```
##### <a name="ParametersManagementGroupsGetDescendants">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--skiptoken**|string|Page continuation token is only used if a previous operation returned a partial result.  If a previous response contains a nextLink element, the value of the nextLink element will include a token parameter that specifies a starting point to use for subsequent calls. |skiptoken|$skiptoken|
|**--top**|integer|Number of elements to return when retrieving results. Passing this in will override $skipToken.|top|$top|

### group `az managementgroup management-group-subscription`
#### <a name="ManagementGroupSubscriptionsCreate">Command `az managementgroup management-group-subscription create`</a>

##### <a name="ExamplesManagementGroupSubscriptionsCreate">Example</a>
```
az managementgroup management-group-subscription create --cache-control "no-cache" --group-id "Group" \
--subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc"
```
##### <a name="ParametersManagementGroupSubscriptionsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--subscription-id**|string|Subscription ID.|subscription_id|subscriptionId|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|

#### <a name="ManagementGroupSubscriptionsDelete">Command `az managementgroup management-group-subscription delete`</a>

##### <a name="ExamplesManagementGroupSubscriptionsDelete">Example</a>
```
az managementgroup management-group-subscription delete --cache-control "no-cache" --group-id "Group" \
--subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc"
```
##### <a name="ParametersManagementGroupSubscriptionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--subscription-id**|string|Subscription ID.|subscription_id|subscriptionId|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|

#### <a name="ManagementGroupSubscriptionsGetSubscription">Command `az managementgroup management-group-subscription show-subscription`</a>

##### <a name="ExamplesManagementGroupSubscriptionsGetSubscription">Example</a>
```
az managementgroup management-group-subscription show-subscription --cache-control "no-cache" --group-id "Group" \
--subscription-id "728bcbe4-8d56-4510-86c2-4921b8beefbc"
```
##### <a name="ParametersManagementGroupSubscriptionsGetSubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--subscription-id**|string|Subscription ID.|subscription_id|subscriptionId|
|**--cache-control**|string|Indicates whether the request should utilize any caches. Populate the header with 'no-cache' value to bypass existing caches.|cache_control|Cache-Control|

#### <a name="ManagementGroupSubscriptionsGetSubscriptionsUnderManagementGroup">Command `az managementgroup management-group-subscription show-subscription-under-management-group`</a>

##### <a name="ExamplesManagementGroupSubscriptionsGetSubscriptionsUnderManagementGroup">Example</a>
```
az managementgroup management-group-subscription show-subscription-under-management-group --group-id "Group"
```
##### <a name="ParametersManagementGroupSubscriptionsGetSubscriptionsUnderManagementGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--skiptoken**|string|Page continuation token is only used if a previous operation returned a partial result.  If a previous response contains a nextLink element, the value of the nextLink element will include a token parameter that specifies a starting point to use for subsequent calls. |skiptoken|$skiptoken|
