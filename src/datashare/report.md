# Azure CLI Module Creation Report

### datashare account create

create a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--location**|string|Location of the azure resource.|location|
|**--tags**|dictionary|Tags on the azure resource.|tags|
### datashare account delete

delete a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
### datashare account list

list a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--skip-token**|string|Continuation token|skip_token|
### datashare account show

show a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
### datashare account update

update a datashare account.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--tags**|dictionary|Tags on the azure resource.|tags|
### datashare consumer-invitation list-invitation

list-invitation a datashare consumer-invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--skip-token**|string|The continuation token|skip_token|
### datashare consumer-invitation reject-invitation

reject-invitation a datashare consumer-invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|Location of the invitation|location|
|**--invitation-id**|string|Unique id of the invitation.|invitation_id|
### datashare consumer-invitation show

show a datashare consumer-invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--location**|string|Location of the invitation|location|
|**--invitation-id**|string|An invitation id|invitation_id|
### datashare consumer-source-data-set list

list a datashare consumer-source-data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--skip-token**|string|Continuation token|skip_token|
### datashare data-set create

create a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share to add the data set to.|share_name|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|
|**--a-d-l-s-gen1-file-data-set**|object|An ADLS Gen 1 file data set.|a_d_l_s_gen1_file_data_set|
|**--a-d-l-s-gen1-folder-data-set**|object|An ADLS Gen 1 folder data set.|a_d_l_s_gen1_folder_data_set|
|**--a-d-l-s-gen2-file-data-set**|object|An ADLS Gen 2 file data set.|a_d_l_s_gen2_file_data_set|
|**--a-d-l-s-gen2-file-system-data-set**|object|An ADLS Gen 2 file system data set.|a_d_l_s_gen2_file_system_data_set|
|**--a-d-l-s-gen2-folder-data-set**|object|An ADLS Gen 2 folder data set.|a_d_l_s_gen2_folder_data_set|
|**--blob-container-data-set**|object|An Azure storage blob container data set.|blob_container_data_set|
|**--blob-data-set**|object|An Azure storage blob data set.|blob_data_set|
|**--blob-folder-data-set**|object|An Azure storage blob folder data set.|blob_folder_data_set|
|**--kusto-cluster-data-set**|object|A kusto cluster data set.|kusto_cluster_data_set|
|**--kusto-database-data-set**|object|A kusto database data set.|kusto_database_data_set|
|**--sql-d-b-table-data-set**|object|A SQL DB table data set.|sql_d_b_table_data_set|
|**--sql-d-w-table-data-set**|object|A SQL DW table data set.|sql_d_w_table_data_set|
### datashare data-set delete

delete a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|
### datashare data-set list

list a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--skip-token**|string|continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare data-set show

show a datashare data-set.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|
### datashare data-set-mapping create

create a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the share subscription which will hold the data set sink.|share_subscription_name|
|**--data-set-mapping-name**|string|The name of the data set mapping to be created.|data_set_mapping_name|
|**--a-d-l-s-gen2-file-data-set-mapping**|object|An ADLS Gen2 file data set mapping.|a_d_l_s_gen2_file_data_set_mapping|
|**--a-d-l-s-gen2-file-system-data-set-mapping**|object|An ADLS Gen2 file system data set mapping.|a_d_l_s_gen2_file_system_data_set_mapping|
|**--a-d-l-s-gen2-folder-data-set-mapping**|object|An ADLS Gen2 folder data set mapping.|a_d_l_s_gen2_folder_data_set_mapping|
|**--blob-container-data-set-mapping**|object|A Blob container data set mapping.|blob_container_data_set_mapping|
|**--blob-data-set-mapping**|object|A Blob data set mapping.|blob_data_set_mapping|
|**--blob-folder-data-set-mapping**|object|A Blob folder data set mapping.|blob_folder_data_set_mapping|
|**--kusto-cluster-data-set-mapping**|object|A Kusto cluster data set mapping|kusto_cluster_data_set_mapping|
|**--kusto-database-data-set-mapping**|object|A Kusto database data set mapping|kusto_database_data_set_mapping|
|**--sql-d-b-table-data-set-mapping**|object|A SQL DB Table data set mapping.|sql_d_b_table_data_set_mapping|
|**--sql-d-w-table-data-set-mapping**|object|A SQL DW Table data set mapping.|sql_d_w_table_data_set_mapping|
### datashare data-set-mapping delete

delete a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--data-set-mapping-name**|string|The name of the dataSetMapping.|data_set_mapping_name|
### datashare data-set-mapping list

list a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|
|**--skip-token**|string|Continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare data-set-mapping show

show a datashare data-set-mapping.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--data-set-mapping-name**|string|The name of the dataSetMapping.|data_set_mapping_name|
### datashare invitation create

create a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share to send the invitation for.|share_name|
|**--invitation-name**|string|The name of the invitation.|invitation_name|
|**--target-active-directory-id**|string|The target Azure AD Id. Can't be combined with email.|target_active_directory_id|
|**--target-email**|string|The email the invitation is directed to.|target_email|
|**--target-object-id**|string|The target user or application Id that invitation is being sent to.
Must be specified along TargetActiveDirectoryId. This enables sending
invitations to specific users or applications in an AD tenant.|target_object_id|
### datashare invitation delete

delete a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--invitation-name**|string|The name of the invitation.|invitation_name|
### datashare invitation list

list a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--skip-token**|string|The continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare invitation show

show a datashare invitation.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--invitation-name**|string|The name of the invitation.|invitation_name|
### datashare provider-share-subscription get-by-share

get-by-share a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|
### datashare provider-share-subscription list

list a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--skip-token**|string|Continuation Token|skip_token|
### datashare provider-share-subscription reinstate

reinstate a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|
### datashare provider-share-subscription revoke

revoke a datashare provider-share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|
### datashare share create

create a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--description**|string|Share description.|description|
|**--share-kind**|choice|Share kind.|share_kind|
|**--terms**|string|Share terms.|terms|
### datashare share delete

delete a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
### datashare share list

list a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--skip-token**|string|Continuation Token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare share list-synchronization

list-synchronization a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--skip-token**|string|Continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare share list-synchronization-detail

list-synchronization-detail a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--skip-token**|string|Continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
|**--consumer-email**|string|Email of the user who created the synchronization|consumer_email|
|**--consumer-name**|string|Name of the user who created the synchronization|consumer_name|
|**--consumer-tenant-name**|string|Tenant name of the consumer who created the synchronization|consumer_tenant_name|
|**--duration-ms**|integer|synchronization duration|duration_ms|
|**--end-time**|date-time|End time of synchronization|end_time|
|**--message**|string|message of synchronization|message|
|**--start-time**|date-time|start time of synchronization|start_time|
|**--status**|string|Raw Status|status|
|**--synchronization-id**|string|Synchronization id|synchronization_id|
### datashare share show

show a datashare share.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share to retrieve.|share_name|
### datashare share-subscription cancel-synchronization

cancel-synchronization a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--synchronization-id**|string|Synchronization id|synchronization_id|
### datashare share-subscription create

create a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--invitation-id**|string|The invitation id.|invitation_id|
|**--source-share-location**|string|Source share location.|source_share_location|
### datashare share-subscription delete

delete a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
### datashare share-subscription list

list a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--skip-token**|string|Continuation Token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare share-subscription list-source-share-synchronization-setting

list-source-share-synchronization-setting a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--skip-token**|string|Continuation token|skip_token|
### datashare share-subscription list-synchronization

list-synchronization a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|
|**--skip-token**|string|Continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare share-subscription list-synchronization-detail

list-synchronization-detail a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|
|**--synchronization-id**|string|Synchronization id|synchronization_id|
|**--skip-token**|string|Continuation token|skip_token|
|**--filter**|string|Filters the results using OData syntax.|filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|
### datashare share-subscription show

show a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
### datashare share-subscription synchronize

synchronize a datashare share-subscription.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of share subscription|share_subscription_name|
|**--synchronization-mode**|choice|Mode of synchronization used in triggers and snapshot sync. Incremental by default|synchronization_mode|
### datashare synchronization-setting create

create a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share to add the synchronization setting to.|share_name|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting.|synchronization_setting_name|
|**--scheduled-synchronization-setting**|object|A type of synchronization setting based on schedule|scheduled_synchronization_setting|
### datashare synchronization-setting delete

delete a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting .|synchronization_setting_name|
### datashare synchronization-setting list

list a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--skip-token**|string|continuation token|skip_token|
### datashare synchronization-setting show

show a datashare synchronization-setting.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-name**|string|The name of the share.|share_name|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting.|synchronization_setting_name|
### datashare trigger create

create a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the share subscription which will hold the data set sink.|share_subscription_name|
|**--trigger-name**|string|The name of the trigger.|trigger_name|
|**--scheduled-trigger**|object|A type of trigger based on schedule|scheduled_trigger|
### datashare trigger delete

delete a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--trigger-name**|string|The name of the trigger.|trigger_name|
### datashare trigger list

list a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|
|**--skip-token**|string|Continuation token|skip_token|
### datashare trigger show

show a datashare trigger.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|
|**--account-name**|string|The name of the share account.|account_name|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|
|**--trigger-name**|string|The name of the trigger.|trigger_name|