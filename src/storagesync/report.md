# Azure CLI Module Creation Report

### storagesync cloud-endpoint create

create a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
|**--storage-account-resource-id**|string|Storage Account Resource Id|storage_account_resource_id|
|**--azure-file-share-name**|string|Azure file share name|azure_file_share_name|
|**--storage-account-tenant-id**|string|Storage Account Tenant Id|storage_account_tenant_id|
|**--friendly-name**|string|Friendly Name|friendly_name|
### storagesync cloud-endpoint delete

delete a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
### storagesync cloud-endpoint list

list a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
### storagesync cloud-endpoint post-backup

post-backup a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
|**--azure-file-share**|string|Azure File Share.|azure_file_share|
### storagesync cloud-endpoint post-restore

post-restore a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
|**--partition**|string|Post Restore partition.|partition|
|**--replica-group**|string|Post Restore replica group.|replica_group|
|**--request-id**|string|Post Restore request id.|request_id|
|**--azure-file-share-uri**|string|Post Restore Azure file share uri.|azure_file_share_uri|
|**--status**|string|Post Restore Azure status.|status|
|**--source-azure-file-share-uri**|string|Post Restore Azure source azure file share uri.|source_azure_file_share_uri|
|**--failed-file-list**|string|Post Restore Azure failed file list.|failed_file_list|
|**--restore-file-spec**|array|Post Restore restore file spec array.|restore_file_spec|
### storagesync cloud-endpoint pre-backup

pre-backup a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
|**--azure-file-share**|string|Azure File Share.|azure_file_share|
### storagesync cloud-endpoint pre-restore

pre-restore a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
|**--partition**|string|Pre Restore partition.|partition|
|**--replica-group**|string|Pre Restore replica group.|replica_group|
|**--request-id**|string|Pre Restore request id.|request_id|
|**--azure-file-share-uri**|string|Pre Restore Azure file share uri.|azure_file_share_uri|
|**--status**|string|Pre Restore Azure status.|status|
|**--source-azure-file-share-uri**|string|Pre Restore Azure source azure file share uri.|source_azure_file_share_uri|
|**--backup-metadata-property-bag**|string|Pre Restore backup metadata property bag.|backup_metadata_property_bag|
|**--restore-file-spec**|array|Pre Restore restore file spec array.|restore_file_spec|
|**--pause-wait-for-sync-drain-time-period-in-seconds**|integer|Pre Restore pause wait for sync drain time period in seconds.|pause_wait_for_sync_drain_time_period_in_seconds|
### storagesync cloud-endpoint restoreheartbeat

restoreheartbeat a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
### storagesync cloud-endpoint show

show a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
### storagesync cloud-endpoint trigger-change-detection

trigger-change-detection a storagesync cloud-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|
|**--directory-path**|string|Relative path to a directory Azure File share for which change detection is to be performed.|directory_path|
|**--change-detection-mode**|choice|Change Detection Mode. Applies to a directory specified in directoryPath parameter.|change_detection_mode|
|**--paths**|array|Array of relative paths on the Azure File share to be included in the change detection. Can be files and directories.|paths|
### storagesync operation-status show

show a storagesync operation-status.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--location-name**|string|The desired region to obtain information from.|location_name|
|**--workflow-id**|string|workflow Id|workflow_id|
|**--operation-id**|string|operation Id|operation_id|
### storagesync private-endpoint-connection create

create a storagesync private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|
|**--private-endpoint**|object|The resource of private end point.|private_endpoint|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|
### storagesync private-endpoint-connection delete

delete a storagesync private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|
### storagesync private-endpoint-connection list

list a storagesync private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
### storagesync private-endpoint-connection show

show a storagesync private-endpoint-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|
### storagesync private-link-resource list

list a storagesync private-link-resource.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|
### storagesync registered-server create

create a storagesync registered-server.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|
|**--server-certificate**|string|Registered Server Certificate|server_certificate|
|**--agent-version**|string|Registered Server Agent Version|agent_version|
|**--server-osversion**|string|Registered Server OS Version|server_os_version|
|**--last-heart-beat**|string|Registered Server last heart beat|last_heart_beat|
|**--server-role**|string|Registered Server serverRole|server_role|
|**--cluster-id**|string|Registered Server clusterId|cluster_id|
|**--cluster-name**|string|Registered Server clusterName|cluster_name|
|**--properties-server-id**|string|Registered Server serverId|server_id|
|**--friendly-name**|string|Friendly Name|friendly_name|
### storagesync registered-server delete

delete a storagesync registered-server.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|
### storagesync registered-server list

list a storagesync registered-server.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
### storagesync registered-server show

show a storagesync registered-server.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|
### storagesync registered-server trigger-rollover

trigger-rollover a storagesync registered-server.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--server-id**|string|Server Id|server_id|
|**--server-certificate**|string|Certificate Data|server_certificate|
### storagesync server-endpoint create

create a storagesync server-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|
|**--server-local-path**|string|Server Local path.|server_local_path|
|**--cloud-tiering**|choice|Cloud Tiering.|cloud_tiering|
|**--volume-free-space-percent**|integer|Level of free space to be maintained by Cloud Tiering if it is enabled.|volume_free_space_percent|
|**--tier-files-older-than-days**|integer|Tier files older than days.|tier_files_older_than_days|
|**--friendly-name**|string|Friendly Name|friendly_name|
|**--server-resource-id**|string|Server Resource Id.|server_resource_id|
|**--offline-data-transfer**|choice|Offline data transfer|offline_data_transfer|
|**--offline-data-transfer-share-name**|string|Offline data transfer share name|offline_data_transfer_share_name|
|**--initial-download-policy**|sealed-choice|Policy for how namespace and files are recalled during FastDr.|initial_download_policy|
|**--local-cache-mode**|sealed-choice|Policy for enabling follow-the-sun business models: link local cache to cloud behavior to pre-populate before local access.|local_cache_mode|
### storagesync server-endpoint delete

delete a storagesync server-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|
### storagesync server-endpoint list

list a storagesync server-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
### storagesync server-endpoint recall-action

recall-action a storagesync server-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|
|**--pattern**|string|Pattern of the files.|pattern|
|**--recall-path**|string|Recall path.|recall_path|
### storagesync server-endpoint show

show a storagesync server-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|
### storagesync server-endpoint update

update a storagesync server-endpoint.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|
|**--cloud-tiering**|choice|Cloud Tiering.|cloud_tiering|
|**--volume-free-space-percent**|integer|Level of free space to be maintained by Cloud Tiering if it is enabled.|volume_free_space_percent|
|**--tier-files-older-than-days**|integer|Tier files older than days.|tier_files_older_than_days|
|**--offline-data-transfer**|choice|Offline data transfer|offline_data_transfer|
|**--offline-data-transfer-share-name**|string|Offline data transfer share name|offline_data_transfer_share_name|
|**--local-cache-mode**|sealed-choice|Policy for enabling follow-the-sun business models: link local cache to cloud behavior to pre-populate before local access.|local_cache_mode|
### storagesync storage-sync-service create

create a storagesync storage-sync-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--location**|string|Required. Gets or sets the location of the resource. This will be one of the supported and registered Azure Geo Regions (e.g. West US, East US, Southeast Asia, etc.). The geo region of a resource cannot be changed once it is created, but if an identical geo region is specified on update, the request will succeed.|location|
|**--tags**|dictionary|Gets or sets a list of key value pairs that describe the resource. These tags can be used for viewing and grouping this resource (across resource groups). A maximum of 15 tags can be provided for a resource. Each tag must have a key with a length no greater than 128 characters and a value with a length no greater than 256 characters.|tags|
|**--incoming-traffic-policy**|choice|Incoming Traffic Policy|incoming_traffic_policy|
### storagesync storage-sync-service delete

delete a storagesync storage-sync-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
### storagesync storage-sync-service list

list a storagesync storage-sync-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
### storagesync storage-sync-service show

show a storagesync storage-sync-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
### storagesync storage-sync-service update

update a storagesync storage-sync-service.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--tags**|dictionary|The user-specified tags associated with the storage sync service.|tags|
|**--incoming-traffic-policy**|choice|Incoming Traffic Policy|incoming_traffic_policy|
### storagesync sync-group create

create a storagesync sync-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
|**--properties**|any|The parameters used to create the sync group|properties|
### storagesync sync-group delete

delete a storagesync sync-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
### storagesync sync-group list

list a storagesync sync-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
### storagesync sync-group show

show a storagesync sync-group.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|
### storagesync workflow abort

abort a storagesync workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--workflow-id**|string|workflow Id|workflow_id|
### storagesync workflow list

list a storagesync workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
### storagesync workflow show

show a storagesync workflow.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|
|**--workflow-id**|string|workflow Id|workflow_id|