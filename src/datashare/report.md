# Azure CLI Module Creation Report

### datashare account create

create a datashare account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--location**|string|Location of the azure resource.|location|location|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|

### datashare account delete

delete a datashare account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|

### datashare account list

list a datashare account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

### datashare account show

show a datashare account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|

### datashare account update

update a datashare account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|

### datashare consumer-invitation list-invitation

list-invitation a datashare consumer-invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare consumer-invitation|ConsumerInvitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-invitation|ListInvitations|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|The continuation token|skip_token|$skipToken|

### datashare consumer-invitation reject-invitation

reject-invitation a datashare consumer-invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare consumer-invitation|ConsumerInvitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|reject-invitation|RejectInvitation|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|Location of the invitation|location|location|
|**--invitation-id**|string|Unique id of the invitation.|invitation_id|invitationId|

### datashare consumer-invitation show

show a datashare consumer-invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare consumer-invitation|ConsumerInvitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|Location of the invitation|location|location|
|**--invitation-id**|string|An invitation id|invitation_id|invitationId|

### datashare consumer-source-data-set list

list a datashare consumer-source-data-set.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare consumer-source-data-set|ConsumerSourceDataSets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShareSubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

### datashare data-set create

create a datashare data-set.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set|DataSets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to add the data set to.|share_name|shareName|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|dataSetName|
|**--adls-gen1-file-data-set**|object|An ADLS Gen 1 file data set.|adls_gen1_file_data_set|ADLSGen1FileDataSet|
|**--adls-gen1-folder-data-set**|object|An ADLS Gen 1 folder data set.|adls_gen1_folder_data_set|ADLSGen1FolderDataSet|
|**--adls-gen2-file-data-set**|object|An ADLS Gen 2 file data set.|adls_gen2_file_data_set|ADLSGen2FileDataSet|
|**--adls-gen2-file-system-data-set**|object|An ADLS Gen 2 file system data set.|adls_gen2_file_system_data_set|ADLSGen2FileSystemDataSet|
|**--adls-gen2-folder-data-set**|object|An ADLS Gen 2 folder data set.|adls_gen2_folder_data_set|ADLSGen2FolderDataSet|
|**--blob-container-data-set**|object|An Azure storage blob container data set.|blob_container_data_set|BlobContainerDataSet|
|**--blob-data-set**|object|An Azure storage blob data set.|blob_data_set|BlobDataSet|
|**--blob-folder-data-set**|object|An Azure storage blob folder data set.|blob_folder_data_set|BlobFolderDataSet|
|**--kusto-cluster-data-set**|object|A kusto cluster data set.|kusto_cluster_data_set|KustoClusterDataSet|
|**--kusto-database-data-set**|object|A kusto database data set.|kusto_database_data_set|KustoDatabaseDataSet|
|**--sqldb-table-data-set**|object|A SQL DB table data set.|sqldb_table_data_set|SqlDBTableDataSet|
|**--sqldw-table-data-set**|object|A SQL DW table data set.|sqldw_table_data_set|SqlDWTableDataSet|

### datashare data-set delete

delete a datashare data-set.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set|DataSets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|dataSetName|

### datashare data-set list

list a datashare data-set.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set|DataSets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShare|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare data-set show

show a datashare data-set.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set|DataSets|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|dataSetName|

### datashare data-set-mapping create

create a datashare data-set-mapping.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set-mapping|DataSetMappings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription which will hold the data set sink.|share_subscription_name|shareSubscriptionName|
|**--data-set-mapping-name**|string|The name of the data set mapping to be created.|data_set_mapping_name|dataSetMappingName|
|**--adls-gen2-file-data-set-mapping**|object|An ADLS Gen2 file data set mapping.|adls_gen2_file_data_set_mapping|ADLSGen2FileDataSetMapping|
|**--adls-gen2-file-system-data-set-mapping**|object|An ADLS Gen2 file system data set mapping.|adls_gen2_file_system_data_set_mapping|ADLSGen2FileSystemDataSetMapping|
|**--adls-gen2-folder-data-set-mapping**|object|An ADLS Gen2 folder data set mapping.|adls_gen2_folder_data_set_mapping|ADLSGen2FolderDataSetMapping|
|**--blob-container-data-set-mapping**|object|A Blob container data set mapping.|blob_container_data_set_mapping|BlobContainerDataSetMapping|
|**--blob-data-set-mapping**|object|A Blob data set mapping.|blob_data_set_mapping|BlobDataSetMapping|
|**--blob-folder-data-set-mapping**|object|A Blob folder data set mapping.|blob_folder_data_set_mapping|BlobFolderDataSetMapping|
|**--kusto-cluster-data-set-mapping**|object|A Kusto cluster data set mapping|kusto_cluster_data_set_mapping|KustoClusterDataSetMapping|
|**--kusto-database-data-set-mapping**|object|A Kusto database data set mapping|kusto_database_data_set_mapping|KustoDatabaseDataSetMapping|
|**--sqldb-table-data-set-mapping**|object|A SQL DB Table data set mapping.|sqldb_table_data_set_mapping|SqlDBTableDataSetMapping|
|**--sqldw-table-data-set-mapping**|object|A SQL DW Table data set mapping.|sqldw_table_data_set_mapping|SqlDWTableDataSetMapping|

### datashare data-set-mapping delete

delete a datashare data-set-mapping.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set-mapping|DataSetMappings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--data-set-mapping-name**|string|The name of the dataSetMapping.|data_set_mapping_name|dataSetMappingName|

### datashare data-set-mapping list

list a datashare data-set-mapping.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set-mapping|DataSetMappings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShareSubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare data-set-mapping show

show a datashare data-set-mapping.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare data-set-mapping|DataSetMappings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--data-set-mapping-name**|string|The name of the dataSetMapping.|data_set_mapping_name|dataSetMappingName|

### datashare invitation create

create a datashare invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare invitation|Invitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to send the invitation for.|share_name|shareName|
|**--invitation-name**|string|The name of the invitation.|invitation_name|invitationName|
|**--target-active-directory-id**|string|The target Azure AD Id. Can't be combined with email.|target_active_directory_id|targetActiveDirectoryId|
|**--target-email**|string|The email the invitation is directed to.|target_email|targetEmail|
|**--target-object-id**|string|The target user or application Id that invitation is being sent to. Must be specified along TargetActiveDirectoryId. This enables sending invitations to specific users or applications in an AD tenant.|target_object_id|targetObjectId|

### datashare invitation delete

delete a datashare invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare invitation|Invitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--invitation-name**|string|The name of the invitation.|invitation_name|invitationName|

### datashare invitation list

list a datashare invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare invitation|Invitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShare|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|The continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare invitation show

show a datashare invitation.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare invitation|Invitations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--invitation-name**|string|The name of the invitation.|invitation_name|invitationName|

### datashare provider-share-subscription get-by-share

get-by-share a datashare provider-share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare provider-share-subscription|ProviderShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|get-by-share|GetByShare|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|

### datashare provider-share-subscription list

list a datashare provider-share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare provider-share-subscription|ProviderShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShare|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|Continuation Token|skip_token|$skipToken|

### datashare provider-share-subscription reinstate

reinstate a datashare provider-share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare provider-share-subscription|ProviderShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|reinstate|Reinstate|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|

### datashare provider-share-subscription revoke

revoke a datashare provider-share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare provider-share-subscription|ProviderShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|revoke|Revoke|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|

### datashare share create

create a datashare share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--description**|string|Share description.|description|description|
|**--share-kind**|choice|Share kind.|share_kind|shareKind|
|**--terms**|string|Share terms.|terms|terms|

### datashare share delete

delete a datashare share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|

### datashare share list

list a datashare share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByAccount|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--skip-token**|string|Continuation Token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare share list-synchronization

list-synchronization a datashare share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-synchronization|ListSynchronizations|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare share list-synchronization-detail

list-synchronization-detail a datashare share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-synchronization-detail|ListSynchronizationDetails|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|
|**--consumer-email**|string|Email of the user who created the synchronization|consumer_email|consumerEmail|
|**--consumer-name**|string|Name of the user who created the synchronization|consumer_name|consumerName|
|**--consumer-tenant-name**|string|Tenant name of the consumer who created the synchronization|consumer_tenant_name|consumerTenantName|
|**--duration-ms**|integer|synchronization duration|duration_ms|durationMs|
|**--end-time**|date-time|End time of synchronization|end_time|endTime|
|**--message**|string|message of synchronization|message|message|
|**--start-time**|date-time|start time of synchronization|start_time|startTime|
|**--status**|string|Raw Status|status|status|
|**--synchronization-id**|string|Synchronization id|synchronization_id|synchronizationId|

### datashare share show

show a datashare share.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share|Shares|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to retrieve.|share_name|shareName|

### datashare share-subscription cancel-synchronization

cancel-synchronization a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|cancel-synchronization|CancelSynchronization|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--synchronization-id**|string|Synchronization id|synchronization_id|synchronizationId|

### datashare share-subscription create

create a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--invitation-id**|string|The invitation id.|invitation_id|invitationId|
|**--source-share-location**|string|Source share location.|source_share_location|sourceShareLocation|

### datashare share-subscription delete

delete a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|

### datashare share-subscription list

list a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByAccount|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--skip-token**|string|Continuation Token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare share-subscription list-source-share-synchronization-setting

list-source-share-synchronization-setting a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-source-share-synchronization-setting|ListSourceShareSynchronizationSettings|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

### datashare share-subscription list-synchronization

list-synchronization a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-synchronization|ListSynchronizations|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare share-subscription list-synchronization-detail

list-synchronization-detail a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-synchronization-detail|ListSynchronizationDetails|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--synchronization-id**|string|Synchronization id|synchronization_id|synchronizationId|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

### datashare share-subscription show

show a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|

### datashare share-subscription synchronize

synchronize a datashare share-subscription.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare share-subscription|ShareSubscriptions|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|synchronize|Synchronize|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of share subscription|share_subscription_name|shareSubscriptionName|
|**--synchronization-mode**|choice|Mode of synchronization used in triggers and snapshot sync. Incremental by default|synchronization_mode|synchronizationMode|

### datashare synchronization-setting create

create a datashare synchronization-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare synchronization-setting|SynchronizationSettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to add the synchronization setting to.|share_name|shareName|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronizationSettingName|
|**--scheduled-synchronization-setting**|object|A type of synchronization setting based on schedule|scheduled_synchronization_setting|ScheduledSynchronizationSetting|

### datashare synchronization-setting delete

delete a datashare synchronization-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare synchronization-setting|SynchronizationSettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting .|synchronization_setting_name|synchronizationSettingName|

### datashare synchronization-setting list

list a datashare synchronization-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare synchronization-setting|SynchronizationSettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShare|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|continuation token|skip_token|$skipToken|

### datashare synchronization-setting show

show a datashare synchronization-setting.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare synchronization-setting|SynchronizationSettings|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronizationSettingName|

### datashare trigger create

create a datashare trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription which will hold the data set sink.|share_subscription_name|shareSubscriptionName|
|**--trigger-name**|string|The name of the trigger.|trigger_name|triggerName|
|**--scheduled-trigger**|object|A type of trigger based on schedule|scheduled_trigger|ScheduledTrigger|

### datashare trigger delete

delete a datashare trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--trigger-name**|string|The name of the trigger.|trigger_name|triggerName|

### datashare trigger list

list a datashare trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByShareSubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

### datashare trigger show

show a datashare trigger.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|datashare trigger|Triggers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--trigger-name**|string|The name of the trigger.|trigger_name|triggerName|
