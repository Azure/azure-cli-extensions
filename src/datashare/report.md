# Azure CLI Module Creation Report

### datashare account create

create a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--identity**|object|Identity of resource|identity|identity|
|**--location**|string|Location of the azure resource.|location|location|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|
### datashare account delete

delete a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
### datashare account list

list a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare account show

show a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
### datashare account update

update a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|
### datashare consumer-invitation list

list a datashare consumer-invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare consumer-invitation reject-invitation

reject-invitation a datashare consumer-invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|Location of the invitation|location|location|
|**--invitation_id**|string|Unique id of the invitation.|invitation_id|properties_invitation_id|
### datashare consumer-invitation show

show a datashare consumer-invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|Location of the invitation|location|location|
|**--invitation_id**|string|An invitation id|invitation_id|invitation_id|
### datashare consumer-source-data-set list

list a datashare consumer-source-data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare data-set create

create a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--data_set_name**|string|The name of the dataSet.|data_set_name|data_set_name|
|**--kind**|choice|Kind of data set.|kind|kind|
### datashare data-set delete

delete a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--data_set_name**|string|The name of the dataSet.|data_set_name|data_set_name|
### datashare data-set list

list a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare data-set show

show a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--data_set_name**|string|The name of the dataSet.|data_set_name|data_set_name|
### datashare data-set-mapping create

create a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--data_set_mapping_name**|string|The name of the dataSetMapping.|data_set_mapping_name|data_set_mapping_name|
|**--kind**|choice|Kind of data set.|kind|kind|
### datashare data-set-mapping delete

delete a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--data_set_mapping_name**|string|The name of the dataSetMapping.|data_set_mapping_name|data_set_mapping_name|
### datashare data-set-mapping list

list a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare data-set-mapping show

show a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--data_set_mapping_name**|string|The name of the dataSetMapping.|data_set_mapping_name|data_set_mapping_name|
### datashare invitation create

create a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--invitation_name**|string|The name of the invitation.|invitation_name|invitation_name|
|**--target_active_directory_id**|string|The target Azure AD Id. Can't be combined with email.|target_active_directory_id|properties_target_active_directory_id|
|**--target_email**|string|The email the invitation is directed to.|target_email|properties_target_email|
|**--target_object_id**|string|The target user or application Id that invitation is being sent to. Must be specified along TargetActiveDirectoryId. This enables sending invitations to specific users or applications in an AD tenant.|target_object_id|properties_target_object_id|
### datashare invitation delete

delete a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--invitation_name**|string|The name of the invitation.|invitation_name|invitation_name|
### datashare invitation list

list a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare invitation show

show a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--invitation_name**|string|The name of the invitation.|invitation_name|invitation_name|
### datashare provider-share-subscription list

list a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare provider-share-subscription reinstate

reinstate a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--provider_share_subscription_id**|string|To locate shareSubscription|provider_share_subscription_id|provider_share_subscription_id|
### datashare provider-share-subscription revoke

revoke a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--provider_share_subscription_id**|string|To locate shareSubscription|provider_share_subscription_id|provider_share_subscription_id|
### datashare provider-share-subscription show

show a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--provider_share_subscription_id**|string|To locate shareSubscription|provider_share_subscription_id|provider_share_subscription_id|
### datashare share create

create a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--description**|string|Share description.|description|properties_description|
|**--share_kind**|choice|Share kind.|share_kind|properties_share_kind|
|**--terms**|string|Share terms.|terms|properties_terms|
### datashare share delete

delete a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
### datashare share list

list a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare share list-synchronization

list-synchronization a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare share list-synchronization-detail

list-synchronization-detail a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
|**--consumer_email**|string|Email of the user who created the synchronization|consumer_email|consumer_email|
|**--consumer_name**|string|Name of the user who created the synchronization|consumer_name|consumer_name|
|**--consumer_tenant_name**|string|Tenant name of the consumer who created the synchronization|consumer_tenant_name|consumer_tenant_name|
|**--duration_ms**|integer|synchronization duration|duration_ms|duration_ms|
|**--end_time**|date-time|End time of synchronization|end_time|end_time|
|**--message**|string|message of synchronization|message|message|
|**--start_time**|date-time|start time of synchronization|start_time|start_time|
|**--status**|string|Raw Status|status|status|
|**--synchronization_id**|string|Synchronization id|synchronization_id|synchronization_id|
### datashare share show

show a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
### datashare share-subscription cancel-synchronization

cancel-synchronization a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--synchronization_id**|string|Synchronization id|synchronization_id|synchronization_id|
### datashare share-subscription create

create a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--invitation_id**|string|The invitation id.|invitation_id|properties_invitation_id|
|**--source_share_location**|string|Source share location.|source_share_location|properties_source_share_location|
### datashare share-subscription delete

delete a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
### datashare share-subscription list

list a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare share-subscription list-source-share-synchronization-setting

list-source-share-synchronization-setting a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare share-subscription list-synchronization

list-synchronization a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare share-subscription list-synchronization-detail

list-synchronization-detail a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--synchronization_id**|string|Synchronization id|synchronization_id|synchronization_id|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare share-subscription show

show a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
### datashare share-subscription synchronize

synchronize a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--synchronization_mode**|choice|Synchronization mode|synchronization_mode|synchronization_mode|
### datashare synchronization-setting create

create a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--synchronization_setting_name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronization_setting_name|
|**--kind**|choice|Kind of data set.|kind|kind|
### datashare synchronization-setting delete

delete a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--synchronization_setting_name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronization_setting_name|
### datashare synchronization-setting list

list a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare synchronization-setting show

show a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_name**|string|The name of the share.|share_name|share_name|
|**--synchronization_setting_name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronization_setting_name|
### datashare trigger create

create a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--trigger_name**|string|The name of the trigger.|trigger_name|trigger_name|
|**--kind**|choice|Kind of data set.|kind|kind|
### datashare trigger delete

delete a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--trigger_name**|string|The name of the trigger.|trigger_name|trigger_name|
### datashare trigger list

list a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--skip_token**|string|Continuation token|skip_token|skip_token|
### datashare trigger show

show a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource_group_name**|string|The resource group name.|resource_group_name|resource_group_name|
|**--account_name**|string|The name of the share account.|account_name|account_name|
|**--share_subscription_name**|string|The name of the shareSubscription.|share_subscription_name|share_subscription_name|
|**--trigger_name**|string|The name of the trigger.|trigger_name|trigger_name|