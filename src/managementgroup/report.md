# Azure CLI Module Creation Report

### managementgroup  start-tenant-backfill

start-tenant-backfill a managementgroup .

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup ||

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start-tenant-backfill|StartTenantBackfill|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### managementgroup  tenant-backfill-status

tenant-backfill-status a managementgroup .

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup ||

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|tenant-backfill-status|TenantBackfillStatus|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

### managementgroup entity list

list a managementgroup entity.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup entity|Entities|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--select**|string|This parameter specifies the fields to include in the response. Can include any combination of Name,DisplayName,Type,ParentDisplayNameChain,ParentChain, e.g. '$select=Name,DisplayName,Type,ParentDisplayNameChain,ParentNameChain'. When specified the $select parameter can override select in $skipToken.|select|$select|
|**--search**|choice|The $search parameter is used in conjunction with the $filter parameter to return three different outputs depending on the parameter passed in.  With $search=AllowedParents the API will return the entity info of all groups that the requested entity will be able to reparent to as determined by the user's permissions. With $search=AllowedChildren the API will return the entity info of all entities that can be added as children of the requested entity. With $search=ParentAndFirstLevelChildren the API will return the parent and  first level of children that the user has either direct access to or indirect access via one of their descendants. With $search=ParentOnly the API will return only the group if the user has access to at least one of the descendants of the group. With $search=ChildrenOnly the API will return only the first level of children of the group entity info specified in $filter.  The user must have direct access to the children entities or one of it's descendants for it to show up in the results.|search|$search|
|**--filter**|string|The filter parameter allows you to filter on the the name or display name fields. You can check for equality on the name field (e.g. name eq '{entityName}')  and you can check for substrings on either the name or display name fields(e.g. contains(name, '{substringToSearch}'), contains(displayName, '{substringToSearch')). Note that the '{entityName}' and '{substringToSearch}' fields are checked case insensitively.|filter|$filter|
|**--view**|choice|The view parameter allows clients to filter the type of data that is returned by the getEntities call.|view|$view|
|**--group-name**|string|A filter which allows the get entities call to focus on a particular group (i.e. "$filter=name eq 'groupName'")|group_name|groupName|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup hierarchy-setting create

create a managementgroup hierarchy-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup hierarchy-setting|HierarchySettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--require-authorization-for-group-creation**|boolean|Indicates whether RBAC access is required upon group creation under the root Management Group. If set to true, user will require Microsoft.Management/managementGroups/write action on the root Management Group scope in order to create new Groups directly under the root. This will prevent new users from creating new Management Groups, unless they are given access.|require_authorization_for_group_creation|requireAuthorizationForGroupCreation|
|**--default-management-group**|string|Settings that sets the default Management Group under which new subscriptions get added in this tenant. For example, /providers/Microsoft.Management/managementGroups/defaultGroup|default_management_group|defaultManagementGroup|

### managementgroup hierarchy-setting delete

delete a managementgroup hierarchy-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup hierarchy-setting|HierarchySettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

### managementgroup hierarchy-setting list

list a managementgroup hierarchy-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup hierarchy-setting|HierarchySettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

### managementgroup hierarchy-setting show

show a managementgroup hierarchy-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup hierarchy-setting|HierarchySettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

### managementgroup hierarchy-setting update

update a managementgroup hierarchy-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup hierarchy-setting|HierarchySettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--require-authorization-for-group-creation**|boolean|Indicates whether RBAC access is required upon group creation under the root Management Group. If set to true, user will require Microsoft.Management/managementGroups/write action on the root Management Group scope in order to create new Groups directly under the root. This will prevent new users from creating new Management Groups, unless they are given access.|require_authorization_for_group_creation|requireAuthorizationForGroupCreation|
|**--default-management-group**|string|Settings that sets the default Management Group under which new subscriptions get added in this tenant. For example, /providers/Microsoft.Management/managementGroups/defaultGroup|default_management_group|defaultManagementGroup|

### managementgroup management-group create

create a managementgroup management-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group|ManagementGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|
|**--name**|string|The name of the management group. For example, 00000000-0000-0000-0000-000000000000|name|name|
|**--display-name**|string|The friendly name of the management group. If no value is passed then this  field will be set to the groupId.|display_name|displayName|
|**--details-parent-id**|string|The fully qualified ID for the parent management group.  For example, /providers/Microsoft.Management/managementGroups/0000000-0000-0000-0000-000000000000|id|id|

### managementgroup management-group delete

delete a managementgroup management-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group|ManagementGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup management-group get-descendant

get-descendant a managementgroup management-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group|ManagementGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-descendant|GetDescendants|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|

### managementgroup management-group list

list a managementgroup management-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group|ManagementGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup management-group show

show a managementgroup management-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group|ManagementGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--expand**|choice|The $expand=children query string parameter allows clients to request inclusion of children in the response payload.  $expand=path includes the path from the root group to the current group.|expand|$expand|
|**--recurse**|boolean|The $recurse=true query string parameter allows clients to request inclusion of entire hierarchy in the response payload. Note that  $expand=children must be passed up if $recurse is set to true.|recurse|$recurse|
|**--filter**|string|A filter which allows the exclusion of subscriptions from results (i.e. '$filter=children.childType ne Subscription')|filter|$filter|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup management-group update

update a managementgroup management-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group|ManagementGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|
|**--display-name**|string|The friendly name of the management group.|display_name|displayName|
|**--parent-group-id**|string|(Optional) The fully qualified ID for the parent management group.  For example, /providers/Microsoft.Management/managementGroups/0000000-0000-0000-0000-000000000000|parent_group_id|parentGroupId|

### managementgroup management-group-subscription create

create a managementgroup management-group-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group-subscription|ManagementGroupSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--subscription-id**|string|Subscription ID.|subscription_id|subscriptionId|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup management-group-subscription delete

delete a managementgroup management-group-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group-subscription|ManagementGroupSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--subscription-id**|string|Subscription ID.|subscription_id|subscriptionId|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup management-group-subscription get-subscription

get-subscription a managementgroup management-group-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group-subscription|ManagementGroupSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-subscription|GetSubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
|**--subscription-id**|string|Subscription ID.|subscription_id|subscriptionId|
|**--cache-control**|string|Indicates that the request shouldn't utilize any caches.|cache_control|Cache-Control|

### managementgroup management-group-subscription get-subscription-under-management-group

get-subscription-under-management-group a managementgroup management-group-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|managementgroup management-group-subscription|ManagementGroupSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-subscription-under-management-group|GetSubscriptionsUnderManagementGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--group-id**|string|Management Group ID.|group_id|groupId|
