# Azure CLI Module Creation Report

### storagesync cloud-endpoint create

create a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--storage-account-resource-id**|string|Storage Account Resource Id|storage_account_resource_id|storageAccountResourceId|
|**--azure-file-share-name**|string|Azure file share name|azure_file_share_name|azureFileShareName|
|**--storage-account-tenant-id**|string|Storage Account Tenant Id|storage_account_tenant_id|storageAccountTenantId|
|**--friendly-name**|string|Friendly Name|friendly_name|friendlyName|

### storagesync cloud-endpoint delete

delete a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|

### storagesync cloud-endpoint list

list a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListBySyncGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

### storagesync cloud-endpoint post-backup

post-backup a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|post-backup|PostBackup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--azure-file-share**|string|Azure File Share.|azure_file_share|azureFileShare|

### storagesync cloud-endpoint post-restore

post-restore a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|post-restore|PostRestore|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--partition**|string|Post Restore partition.|partition|partition|
|**--replica-group**|string|Post Restore replica group.|replica_group|replicaGroup|
|**--request-id**|string|Post Restore request id.|request_id|requestId|
|**--azure-file-share-uri**|string|Post Restore Azure file share uri.|azure_file_share_uri|azureFileShareUri|
|**--status**|string|Post Restore Azure status.|status|status|
|**--source-azure-file-share-uri**|string|Post Restore Azure source azure file share uri.|source_azure_file_share_uri|sourceAzureFileShareUri|
|**--failed-file-list**|string|Post Restore Azure failed file list.|failed_file_list|failedFileList|
|**--restore-file-spec**|array|Post Restore restore file spec array.|restore_file_spec|restoreFileSpec|

### storagesync cloud-endpoint pre-backup

pre-backup a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|pre-backup|PreBackup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--azure-file-share**|string|Azure File Share.|azure_file_share|azureFileShare|

### storagesync cloud-endpoint pre-restore

pre-restore a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|pre-restore|PreRestore|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--partition**|string|Pre Restore partition.|partition|partition|
|**--replica-group**|string|Pre Restore replica group.|replica_group|replicaGroup|
|**--request-id**|string|Pre Restore request id.|request_id|requestId|
|**--azure-file-share-uri**|string|Pre Restore Azure file share uri.|azure_file_share_uri|azureFileShareUri|
|**--status**|string|Pre Restore Azure status.|status|status|
|**--source-azure-file-share-uri**|string|Pre Restore Azure source azure file share uri.|source_azure_file_share_uri|sourceAzureFileShareUri|
|**--backup-metadata-property-bag**|string|Pre Restore backup metadata property bag.|backup_metadata_property_bag|backupMetadataPropertyBag|
|**--restore-file-spec**|array|Pre Restore restore file spec array.|restore_file_spec|restoreFileSpec|
|**--pause-wait-for-sync-drain-time-period-in-seconds**|integer|Pre Restore pause wait for sync drain time period in seconds.|pause_wait_for_sync_drain_time_period_in_seconds|pauseWaitForSyncDrainTimePeriodInSeconds|

### storagesync cloud-endpoint restoreheartbeat

restoreheartbeat a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|restoreheartbeat|restoreheartbeat|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|

### storagesync cloud-endpoint show

show a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|

### storagesync cloud-endpoint trigger-change-detection

trigger-change-detection a storagesync cloud-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync cloud-endpoint|CloudEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|trigger-change-detection|TriggerChangeDetection|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--directory-path**|string|Relative path to a directory Azure File share for which change detection is to be performed.|directory_path|directoryPath|
|**--change-detection-mode**|choice|Change Detection Mode. Applies to a directory specified in directoryPath parameter.|change_detection_mode|changeDetectionMode|
|**--paths**|array|Array of relative paths on the Azure File share to be included in the change detection. Can be files and directories.|paths|paths|

### storagesync operation-status show

show a storagesync operation-status.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync operation-status|OperationStatus|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--location-name**|string|The desired region to obtain information from.|location_name|locationName|
|**--workflow-id**|string|workflow Id|workflow_id|workflowId|
|**--operation-id**|string|operation Id|operation_id|operationId|

### storagesync private-endpoint-connection create

create a storagesync private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

### storagesync private-endpoint-connection delete

delete a storagesync private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

### storagesync private-endpoint-connection list

list a storagesync private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByStorageSyncService|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### storagesync private-endpoint-connection show

show a storagesync private-endpoint-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync private-endpoint-connection|PrivateEndpointConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

### storagesync private-link-resource list

list a storagesync private-link-resource.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync private-link-resource|PrivateLinkResources|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByStorageSyncService|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|

### storagesync registered-server create

create a storagesync registered-server.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync registered-server|RegisteredServers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|serverId|
|**--server-certificate**|string|Registered Server Certificate|server_certificate|serverCertificate|
|**--agent-version**|string|Registered Server Agent Version|agent_version|agentVersion|
|**--server-osversion**|string|Registered Server OS Version|server_os_version|serverOSVersion|
|**--last-heart-beat**|string|Registered Server last heart beat|last_heart_beat|lastHeartBeat|
|**--server-role**|string|Registered Server serverRole|server_role|serverRole|
|**--cluster-id**|string|Registered Server clusterId|cluster_id|clusterId|
|**--cluster-name**|string|Registered Server clusterName|cluster_name|clusterName|
|**--properties-server-id**|string|Registered Server serverId|registered_server_create_parameters_properties_server_id|serverId|
|**--friendly-name**|string|Friendly Name|friendly_name|friendlyName|

### storagesync registered-server delete

delete a storagesync registered-server.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync registered-server|RegisteredServers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|serverId|

### storagesync registered-server list

list a storagesync registered-server.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync registered-server|RegisteredServers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByStorageSyncService|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### storagesync registered-server show

show a storagesync registered-server.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync registered-server|RegisteredServers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|serverId|

### storagesync registered-server trigger-rollover

trigger-rollover a storagesync registered-server.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync registered-server|RegisteredServers|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|trigger-rollover|triggerRollover|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|Server Id|server_id|serverId|
|**--server-certificate**|string|Certificate Data|server_certificate|serverCertificate|

### storagesync server-endpoint create

create a storagesync server-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync server-endpoint|ServerEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|
|**--server-local-path**|string|Server Local path.|server_local_path|serverLocalPath|
|**--cloud-tiering**|choice|Cloud Tiering.|cloud_tiering|cloudTiering|
|**--volume-free-space-percent**|integer|Level of free space to be maintained by Cloud Tiering if it is enabled.|volume_free_space_percent|volumeFreeSpacePercent|
|**--tier-files-older-than-days**|integer|Tier files older than days.|tier_files_older_than_days|tierFilesOlderThanDays|
|**--friendly-name**|string|Friendly Name|friendly_name|friendlyName|
|**--server-resource-id**|string|Server Resource Id.|server_resource_id|serverResourceId|
|**--offline-data-transfer**|choice|Offline data transfer|offline_data_transfer|offlineDataTransfer|
|**--offline-data-transfer-share-name**|string|Offline data transfer share name|offline_data_transfer_share_name|offlineDataTransferShareName|
|**--initial-download-policy**|choice|Policy for how namespace and files are recalled during FastDr.|initial_download_policy|initialDownloadPolicy|
|**--local-cache-mode**|choice|Policy for enabling follow-the-sun business models: link local cache to cloud behavior to pre-populate before local access.|local_cache_mode|localCacheMode|

### storagesync server-endpoint delete

delete a storagesync server-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync server-endpoint|ServerEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|

### storagesync server-endpoint list

list a storagesync server-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync server-endpoint|ServerEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListBySyncGroup|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

### storagesync server-endpoint recall-action

recall-action a storagesync server-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync server-endpoint|ServerEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|recall-action|recallAction|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|
|**--pattern**|string|Pattern of the files.|pattern|pattern|
|**--recall-path**|string|Recall path.|recall_path|recallPath|

### storagesync server-endpoint show

show a storagesync server-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync server-endpoint|ServerEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|

### storagesync server-endpoint update

update a storagesync server-endpoint.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync server-endpoint|ServerEndpoints|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|
|**--cloud-tiering**|choice|Cloud Tiering.|cloud_tiering|cloudTiering|
|**--volume-free-space-percent**|integer|Level of free space to be maintained by Cloud Tiering if it is enabled.|volume_free_space_percent|volumeFreeSpacePercent|
|**--tier-files-older-than-days**|integer|Tier files older than days.|tier_files_older_than_days|tierFilesOlderThanDays|
|**--offline-data-transfer**|choice|Offline data transfer|offline_data_transfer|offlineDataTransfer|
|**--offline-data-transfer-share-name**|string|Offline data transfer share name|offline_data_transfer_share_name|offlineDataTransferShareName|
|**--local-cache-mode**|choice|Policy for enabling follow-the-sun business models: link local cache to cloud behavior to pre-populate before local access.|local_cache_mode|localCacheMode|

### storagesync storage-sync-service create

create a storagesync storage-sync-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync storage-sync-service|StorageSyncServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--location**|string|Required. Gets or sets the location of the resource. This will be one of the supported and registered Azure Geo Regions (e.g. West US, East US, Southeast Asia, etc.). The geo region of a resource cannot be changed once it is created, but if an identical geo region is specified on update, the request will succeed.|location|location|
|**--tags**|dictionary|Gets or sets a list of key value pairs that describe the resource. These tags can be used for viewing and grouping this resource (across resource groups). A maximum of 15 tags can be provided for a resource. Each tag must have a key with a length no greater than 128 characters and a value with a length no greater than 256 characters.|tags|tags|
|**--incoming-traffic-policy**|choice|Incoming Traffic Policy|incoming_traffic_policy|incomingTrafficPolicy|

### storagesync storage-sync-service delete

delete a storagesync storage-sync-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync storage-sync-service|StorageSyncServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### storagesync storage-sync-service list

list a storagesync storage-sync-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync storage-sync-service|StorageSyncServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|ListBySubscription|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

### storagesync storage-sync-service show

show a storagesync storage-sync-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync storage-sync-service|StorageSyncServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### storagesync storage-sync-service update

update a storagesync storage-sync-service.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync storage-sync-service|StorageSyncServices|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--tags**|dictionary|The user-specified tags associated with the storage sync service.|tags|tags|
|**--incoming-traffic-policy**|choice|Incoming Traffic Policy|incoming_traffic_policy|incomingTrafficPolicy|

### storagesync sync-group create

create a storagesync sync-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync sync-group|SyncGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--properties**|any|The parameters used to create the sync group|properties|properties|

### storagesync sync-group delete

delete a storagesync sync-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync sync-group|SyncGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

### storagesync sync-group list

list a storagesync sync-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync sync-group|SyncGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByStorageSyncService|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### storagesync sync-group show

show a storagesync sync-group.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync sync-group|SyncGroups|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

### storagesync workflow abort

abort a storagesync workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|abort|Abort|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--workflow-id**|string|workflow Id|workflow_id|workflowId|

### storagesync workflow list

list a storagesync workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByStorageSyncService|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### storagesync workflow show

show a storagesync workflow.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|storagesync workflow|Workflows|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--workflow-id**|string|workflow Id|workflow_id|workflowId|
