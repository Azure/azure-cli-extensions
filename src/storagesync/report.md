# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az storagesync|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az storagesync` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az storagesync storage-sync-service|StorageSyncServices|[commands](#CommandsInStorageSyncServices)|
|az storagesync private-link-resource|PrivateLinkResources|[commands](#CommandsInPrivateLinkResources)|
|az storagesync private-endpoint-connection|PrivateEndpointConnections|[commands](#CommandsInPrivateEndpointConnections)|
|az storagesync sync-group|SyncGroups|[commands](#CommandsInSyncGroups)|
|az storagesync cloud-endpoint|CloudEndpoints|[commands](#CommandsInCloudEndpoints)|
|az storagesync server-endpoint|ServerEndpoints|[commands](#CommandsInServerEndpoints)|
|az storagesync registered-server|RegisteredServers|[commands](#CommandsInRegisteredServers)|
|az storagesync workflow|Workflows|[commands](#CommandsInWorkflows)|
|az storagesync operation-status|OperationStatus|[commands](#CommandsInOperationStatus)|

## COMMANDS
### <a name="CommandsInCloudEndpoints">Commands in `az storagesync cloud-endpoint` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync cloud-endpoint list](#CloudEndpointsListBySyncGroup)|ListBySyncGroup|[Parameters](#ParametersCloudEndpointsListBySyncGroup)|[Example](#ExamplesCloudEndpointsListBySyncGroup)|
|[az storagesync cloud-endpoint show](#CloudEndpointsGet)|Get|[Parameters](#ParametersCloudEndpointsGet)|[Example](#ExamplesCloudEndpointsGet)|
|[az storagesync cloud-endpoint create](#CloudEndpointsCreate)|Create|[Parameters](#ParametersCloudEndpointsCreate)|[Example](#ExamplesCloudEndpointsCreate)|
|[az storagesync cloud-endpoint delete](#CloudEndpointsDelete)|Delete|[Parameters](#ParametersCloudEndpointsDelete)|[Example](#ExamplesCloudEndpointsDelete)|
|[az storagesync cloud-endpoint post-backup](#CloudEndpointsPostBackup)|PostBackup|[Parameters](#ParametersCloudEndpointsPostBackup)|[Example](#ExamplesCloudEndpointsPostBackup)|
|[az storagesync cloud-endpoint post-restore](#CloudEndpointsPostRestore)|PostRestore|[Parameters](#ParametersCloudEndpointsPostRestore)|[Example](#ExamplesCloudEndpointsPostRestore)|
|[az storagesync cloud-endpoint pre-backup](#CloudEndpointsPreBackup)|PreBackup|[Parameters](#ParametersCloudEndpointsPreBackup)|[Example](#ExamplesCloudEndpointsPreBackup)|
|[az storagesync cloud-endpoint pre-restore](#CloudEndpointsPreRestore)|PreRestore|[Parameters](#ParametersCloudEndpointsPreRestore)|[Example](#ExamplesCloudEndpointsPreRestore)|
|[az storagesync cloud-endpoint restoreheartbeat](#CloudEndpointsrestoreheartbeat)|restoreheartbeat|[Parameters](#ParametersCloudEndpointsrestoreheartbeat)|[Example](#ExamplesCloudEndpointsrestoreheartbeat)|
|[az storagesync cloud-endpoint trigger-change-detection](#CloudEndpointsTriggerChangeDetection)|TriggerChangeDetection|[Parameters](#ParametersCloudEndpointsTriggerChangeDetection)|[Example](#ExamplesCloudEndpointsTriggerChangeDetection)|

### <a name="CommandsInOperationStatus">Commands in `az storagesync operation-status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync operation-status show](#OperationStatusGet)|Get|[Parameters](#ParametersOperationStatusGet)|[Example](#ExamplesOperationStatusGet)|

### <a name="CommandsInPrivateEndpointConnections">Commands in `az storagesync private-endpoint-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync private-endpoint-connection list](#PrivateEndpointConnectionsListByStorageSyncService)|ListByStorageSyncService|[Parameters](#ParametersPrivateEndpointConnectionsListByStorageSyncService)|[Example](#ExamplesPrivateEndpointConnectionsListByStorageSyncService)|
|[az storagesync private-endpoint-connection show](#PrivateEndpointConnectionsGet)|Get|[Parameters](#ParametersPrivateEndpointConnectionsGet)|[Example](#ExamplesPrivateEndpointConnectionsGet)|
|[az storagesync private-endpoint-connection create](#PrivateEndpointConnectionsCreate)|Create|[Parameters](#ParametersPrivateEndpointConnectionsCreate)|[Example](#ExamplesPrivateEndpointConnectionsCreate)|
|[az storagesync private-endpoint-connection delete](#PrivateEndpointConnectionsDelete)|Delete|[Parameters](#ParametersPrivateEndpointConnectionsDelete)|[Example](#ExamplesPrivateEndpointConnectionsDelete)|

### <a name="CommandsInPrivateLinkResources">Commands in `az storagesync private-link-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync private-link-resource list](#PrivateLinkResourcesListByStorageSyncService)|ListByStorageSyncService|[Parameters](#ParametersPrivateLinkResourcesListByStorageSyncService)|[Example](#ExamplesPrivateLinkResourcesListByStorageSyncService)|

### <a name="CommandsInRegisteredServers">Commands in `az storagesync registered-server` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync registered-server list](#RegisteredServersListByStorageSyncService)|ListByStorageSyncService|[Parameters](#ParametersRegisteredServersListByStorageSyncService)|[Example](#ExamplesRegisteredServersListByStorageSyncService)|
|[az storagesync registered-server show](#RegisteredServersGet)|Get|[Parameters](#ParametersRegisteredServersGet)|[Example](#ExamplesRegisteredServersGet)|
|[az storagesync registered-server create](#RegisteredServersCreate)|Create|[Parameters](#ParametersRegisteredServersCreate)|[Example](#ExamplesRegisteredServersCreate)|
|[az storagesync registered-server delete](#RegisteredServersDelete)|Delete|[Parameters](#ParametersRegisteredServersDelete)|[Example](#ExamplesRegisteredServersDelete)|
|[az storagesync registered-server trigger-rollover](#RegisteredServerstriggerRollover)|triggerRollover|[Parameters](#ParametersRegisteredServerstriggerRollover)|[Example](#ExamplesRegisteredServerstriggerRollover)|

### <a name="CommandsInServerEndpoints">Commands in `az storagesync server-endpoint` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync server-endpoint list](#ServerEndpointsListBySyncGroup)|ListBySyncGroup|[Parameters](#ParametersServerEndpointsListBySyncGroup)|[Example](#ExamplesServerEndpointsListBySyncGroup)|
|[az storagesync server-endpoint show](#ServerEndpointsGet)|Get|[Parameters](#ParametersServerEndpointsGet)|[Example](#ExamplesServerEndpointsGet)|
|[az storagesync server-endpoint create](#ServerEndpointsCreate)|Create|[Parameters](#ParametersServerEndpointsCreate)|[Example](#ExamplesServerEndpointsCreate)|
|[az storagesync server-endpoint update](#ServerEndpointsUpdate)|Update|[Parameters](#ParametersServerEndpointsUpdate)|[Example](#ExamplesServerEndpointsUpdate)|
|[az storagesync server-endpoint delete](#ServerEndpointsDelete)|Delete|[Parameters](#ParametersServerEndpointsDelete)|[Example](#ExamplesServerEndpointsDelete)|
|[az storagesync server-endpoint recall-action](#ServerEndpointsrecallAction)|recallAction|[Parameters](#ParametersServerEndpointsrecallAction)|[Example](#ExamplesServerEndpointsrecallAction)|

### <a name="CommandsInStorageSyncServices">Commands in `az storagesync storage-sync-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync storage-sync-service list](#StorageSyncServicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersStorageSyncServicesListByResourceGroup)|[Example](#ExamplesStorageSyncServicesListByResourceGroup)|
|[az storagesync storage-sync-service list](#StorageSyncServicesListBySubscription)|ListBySubscription|[Parameters](#ParametersStorageSyncServicesListBySubscription)|[Example](#ExamplesStorageSyncServicesListBySubscription)|
|[az storagesync storage-sync-service show](#StorageSyncServicesGet)|Get|[Parameters](#ParametersStorageSyncServicesGet)|[Example](#ExamplesStorageSyncServicesGet)|
|[az storagesync storage-sync-service create](#StorageSyncServicesCreate)|Create|[Parameters](#ParametersStorageSyncServicesCreate)|[Example](#ExamplesStorageSyncServicesCreate)|
|[az storagesync storage-sync-service update](#StorageSyncServicesUpdate)|Update|[Parameters](#ParametersStorageSyncServicesUpdate)|[Example](#ExamplesStorageSyncServicesUpdate)|
|[az storagesync storage-sync-service delete](#StorageSyncServicesDelete)|Delete|[Parameters](#ParametersStorageSyncServicesDelete)|[Example](#ExamplesStorageSyncServicesDelete)|

### <a name="CommandsInSyncGroups">Commands in `az storagesync sync-group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync sync-group list](#SyncGroupsListByStorageSyncService)|ListByStorageSyncService|[Parameters](#ParametersSyncGroupsListByStorageSyncService)|[Example](#ExamplesSyncGroupsListByStorageSyncService)|
|[az storagesync sync-group show](#SyncGroupsGet)|Get|[Parameters](#ParametersSyncGroupsGet)|[Example](#ExamplesSyncGroupsGet)|
|[az storagesync sync-group create](#SyncGroupsCreate)|Create|[Parameters](#ParametersSyncGroupsCreate)|[Example](#ExamplesSyncGroupsCreate)|
|[az storagesync sync-group delete](#SyncGroupsDelete)|Delete|[Parameters](#ParametersSyncGroupsDelete)|[Example](#ExamplesSyncGroupsDelete)|

### <a name="CommandsInWorkflows">Commands in `az storagesync workflow` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az storagesync workflow list](#WorkflowsListByStorageSyncService)|ListByStorageSyncService|[Parameters](#ParametersWorkflowsListByStorageSyncService)|[Example](#ExamplesWorkflowsListByStorageSyncService)|
|[az storagesync workflow show](#WorkflowsGet)|Get|[Parameters](#ParametersWorkflowsGet)|[Example](#ExamplesWorkflowsGet)|
|[az storagesync workflow abort](#WorkflowsAbort)|Abort|[Parameters](#ParametersWorkflowsAbort)|[Example](#ExamplesWorkflowsAbort)|


## COMMAND DETAILS

### group `az storagesync cloud-endpoint`
#### <a name="CloudEndpointsListBySyncGroup">Command `az storagesync cloud-endpoint list`</a>

##### <a name="ExamplesCloudEndpointsListBySyncGroup">Example</a>
```
az storagesync cloud-endpoint list --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsListBySyncGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

#### <a name="CloudEndpointsGet">Command `az storagesync cloud-endpoint show`</a>

##### <a name="ExamplesCloudEndpointsGet">Example</a>
```
az storagesync cloud-endpoint show --name "SampleCloudEndpoint_1" --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|

#### <a name="CloudEndpointsCreate">Command `az storagesync cloud-endpoint create`</a>

##### <a name="ExamplesCloudEndpointsCreate">Example</a>
```
az storagesync cloud-endpoint create --name "SampleCloudEndpoint_1" --azure-file-share-name \
"cvcloud-afscv-0719-058-a94a1354-a1fd-4e9a-9a50-919fad8c4ba4" --friendly-name "ankushbsubscriptionmgmtmab" \
--storage-account-resource-id "/subscriptions/744f4d70-6d17-4921-8970-a765d14f763f/resourceGroups/tminienv59svc/provide\
rs/Microsoft.Storage/storageAccounts/tminienv59storage" --storage-account-tenant-id "\\"72f988bf-86f1-41af-91ab-2d7cd01\
1db47\\"" --resource-group "SampleResourceGroup_1" --storage-sync-service-name "SampleStorageSyncService_1" \
--sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsCreate">Parameters</a> 
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

#### <a name="CloudEndpointsDelete">Command `az storagesync cloud-endpoint delete`</a>

##### <a name="ExamplesCloudEndpointsDelete">Example</a>
```
az storagesync cloud-endpoint delete --name "SampleCloudEndpoint_1" --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|

#### <a name="CloudEndpointsPostBackup">Command `az storagesync cloud-endpoint post-backup`</a>

##### <a name="ExamplesCloudEndpointsPostBackup">Example</a>
```
az storagesync cloud-endpoint post-backup --name "SampleCloudEndpoint_1" --azure-file-share \
"https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare" --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsPostBackup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--azure-file-share**|string|Azure File Share.|azure_file_share|azureFileShare|

#### <a name="CloudEndpointsPostRestore">Command `az storagesync cloud-endpoint post-restore`</a>

##### <a name="ExamplesCloudEndpointsPostRestore">Example</a>
```
az storagesync cloud-endpoint post-restore --name "SampleCloudEndpoint_1" --azure-file-share-uri \
"https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare" --restore-file-spec \
path="text1.txt" isdir=false --restore-file-spec path="MyDir" isdir=true --restore-file-spec path="MyDir/SubDir" \
isdir=false --restore-file-spec path="MyDir/SubDir/File1.pdf" isdir=false --source-azure-file-share-uri \
"https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare" --status "Succeeded" \
--resource-group "SampleResourceGroup_1" --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \
"SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsPostRestore">Parameters</a> 
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

#### <a name="CloudEndpointsPreBackup">Command `az storagesync cloud-endpoint pre-backup`</a>

##### <a name="ExamplesCloudEndpointsPreBackup">Example</a>
```
az storagesync cloud-endpoint pre-backup --name "SampleCloudEndpoint_1" --azure-file-share \
"https://sampleserver.file.core.test-cint.azure-test.net/sampleFileShare" --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsPreBackup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--azure-file-share**|string|Azure File Share.|azure_file_share|azureFileShare|

#### <a name="CloudEndpointsPreRestore">Command `az storagesync cloud-endpoint pre-restore`</a>

##### <a name="ExamplesCloudEndpointsPreRestore">Example</a>
```
az storagesync cloud-endpoint pre-restore --name "SampleCloudEndpoint_1" --azure-file-share-uri \
"https://hfsazbackupdevintncus2.file.core.test-cint.azure-test.net/sampleFileShare" --restore-file-spec \
path="text1.txt" isdir=false --restore-file-spec path="MyDir" isdir=true --restore-file-spec path="MyDir/SubDir" \
isdir=false --restore-file-spec path="MyDir/SubDir/File1.pdf" isdir=false --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsPreRestore">Parameters</a> 
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

#### <a name="CloudEndpointsrestoreheartbeat">Command `az storagesync cloud-endpoint restoreheartbeat`</a>

##### <a name="ExamplesCloudEndpointsrestoreheartbeat">Example</a>
```
az storagesync cloud-endpoint restoreheartbeat --name "SampleCloudEndpoint_1" --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsrestoreheartbeat">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|

#### <a name="CloudEndpointsTriggerChangeDetection">Command `az storagesync cloud-endpoint trigger-change-detection`</a>

##### <a name="ExamplesCloudEndpointsTriggerChangeDetection">Example</a>
```
az storagesync cloud-endpoint trigger-change-detection --name "SampleCloudEndpoint_1" --change-detection-mode \
"Recursive" --directory-path "NewDirectory" --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersCloudEndpointsTriggerChangeDetection">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--cloud-endpoint-name**|string|Name of Cloud Endpoint object.|cloud_endpoint_name|cloudEndpointName|
|**--directory-path**|string|Relative path to a directory Azure File share for which change detection is to be performed.|directory_path|directoryPath|
|**--change-detection-mode**|choice|Change Detection Mode. Applies to a directory specified in directoryPath parameter.|change_detection_mode|changeDetectionMode|
|**--paths**|array|Array of relative paths on the Azure File share to be included in the change detection. Can be files and directories.|paths|paths|

### group `az storagesync operation-status`
#### <a name="OperationStatusGet">Command `az storagesync operation-status show`</a>

##### <a name="ExamplesOperationStatusGet">Example</a>
```
az storagesync operation-status show --operation-id "14b50e24-f68d-4b29-a882-38be9dfb8bd1" --location-name "westus" \
--resource-group "SampleResourceGroup_1" --workflow-id "828219ea-083e-48b5-89ea-8fd9991b2e75"
```
##### <a name="ParametersOperationStatusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--location-name**|string|The desired region to obtain information from.|location_name|locationName|
|**--workflow-id**|string|workflow Id|workflow_id|workflowId|
|**--operation-id**|string|operation Id|operation_id|operationId|

### group `az storagesync private-endpoint-connection`
#### <a name="PrivateEndpointConnectionsListByStorageSyncService">Command `az storagesync private-endpoint-connection list`</a>

##### <a name="ExamplesPrivateEndpointConnectionsListByStorageSyncService">Example</a>
```
az storagesync private-endpoint-connection list --resource-group "res6977" --storage-sync-service-name "sss2527"
```
##### <a name="ParametersPrivateEndpointConnectionsListByStorageSyncService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

#### <a name="PrivateEndpointConnectionsGet">Command `az storagesync private-endpoint-connection show`</a>

##### <a name="ExamplesPrivateEndpointConnectionsGet">Example</a>
```
az storagesync private-endpoint-connection show --name "{privateEndpointConnectionName}" --resource-group "res6977" \
--storage-sync-service-name "sss2527"
```
##### <a name="ParametersPrivateEndpointConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsCreate">Command `az storagesync private-endpoint-connection create`</a>

##### <a name="ExamplesPrivateEndpointConnectionsCreate">Example</a>
```
az storagesync private-endpoint-connection create --name "{privateEndpointConnectionName}" \
--private-link-service-connection-state description="Auto-Approved" status="Approved" --resource-group "res7687" \
--storage-sync-service-name "sss2527"
```
##### <a name="ParametersPrivateEndpointConnectionsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

#### <a name="PrivateEndpointConnectionsDelete">Command `az storagesync private-endpoint-connection delete`</a>

##### <a name="ExamplesPrivateEndpointConnectionsDelete">Example</a>
```
az storagesync private-endpoint-connection delete --name "{privateEndpointConnectionName}" --resource-group "res6977" \
--storage-sync-service-name "sss2527"
```
##### <a name="ParametersPrivateEndpointConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

### group `az storagesync private-link-resource`
#### <a name="PrivateLinkResourcesListByStorageSyncService">Command `az storagesync private-link-resource list`</a>

##### <a name="ExamplesPrivateLinkResourcesListByStorageSyncService">Example</a>
```
az storagesync private-link-resource list --resource-group "res6977" --storage-sync-service-name "sss2527"
```
##### <a name="ParametersPrivateLinkResourcesListByStorageSyncService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|The name of the storage sync service name within the specified resource group.|storage_sync_service_name|storageSyncServiceName|

### group `az storagesync registered-server`
#### <a name="RegisteredServersListByStorageSyncService">Command `az storagesync registered-server list`</a>

##### <a name="ExamplesRegisteredServersListByStorageSyncService">Example</a>
```
az storagesync registered-server list --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1"
```
##### <a name="ParametersRegisteredServersListByStorageSyncService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

#### <a name="RegisteredServersGet">Command `az storagesync registered-server show`</a>

##### <a name="ExamplesRegisteredServersGet">Example</a>
```
az storagesync registered-server show --resource-group "SampleResourceGroup_1" --server-id \
"080d4133-bdb5-40a0-96a0-71a6057bfe9a" --storage-sync-service-name "SampleStorageSyncService_1"
```
##### <a name="ParametersRegisteredServersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|serverId|

#### <a name="RegisteredServersCreate">Command `az storagesync registered-server create`</a>

##### <a name="ExamplesRegisteredServersCreate">Example</a>
```
az storagesync registered-server create --agent-version "1.0.277.0" --friendly-name "afscv-2304-139" \
--server-certificate "MIIDFjCCAf6gAwIBAgIQQS+DS8uhc4VNzUkTw7wbRjANBgkqhkiG9w0BAQ0FADAzMTEwLwYDVQQDEyhhbmt1c2hiLXByb2QzL\
nJlZG1vbmQuY29ycC5taWNyb3NvZnQuY29tMB4XDTE3MDgwMzE3MDQyNFoXDTE4MDgwNDE3MDQyNFowMzExMC8GA1UEAxMoYW5rdXNoYi1wcm9kMy5yZWRt\
b25kLmNvcnAubWljcm9zb2Z0LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALDRvV4gmsIy6jGDPiHsXmvgVP749NNP7DopdlbHaNhjFmY\
INHl0uWylyaZmgJrROt2mnxN/zEyJtGnqYHlzUr4xvGq/qV5pqgdB9tag/sw9i22gfe9PRZ0FmSOZnXMbLYgLiDFqLtut5gHcOuWMj03YnkfoBEKlFBxWba\
gvW2yxz/Sxi9OVSJOKCaXra0RpcIHrO/KFl6ho2eE1/7Ykmfa8hZvSdoPd5gHdLiQcMB/pxq+mWp1fI6c8vFZoDu7Atn+NXTzYPKUxKzaisF12TsaKpohUs\
JpbB3Wocb0F5frn614D2pg14ERB5otjAMWw1m65csQWPI6dP8KIYe0+QPkCAwEAAaMmMCQwIgYDVR0lAQH/BBgwFgYIKwYBBQUHAwIGCisGAQQBgjcKAwww\
DQYJKoZIhvcNAQENBQADggEBAA4RhVIBkw34M1RwakJgHvtjsOFxF1tVQA941NtLokx1l2Z8+GFQkcG4xpZSt+UN6wLerdCbnNhtkCErWUDeaT0jxk4g71O\
fex7iM04crT4iHJr8mi96/XnhnkTUs+GDk12VgdeeNEczMZz+8Mxw9dJ5NCnYgTwO0SzGlclRsDvjzkLo8rh2ZG6n/jKrEyNXXo+hOqhupij0QbRP2Tvexd\
fw201kgN1jdZify8XzJ8Oi0bTS0KpJf2pNPOlooK2bjMUei9ANtEdXwwfVZGWvVh6tJjdv6k14wWWJ1L7zhA1IIVb1J+sQUzJji5iX0DrezjTz1Fg+gAzIT\
aA/WsuujlM=" --registered-server-create-parameters-properties-server-id "080d4133-bdb5-40a0-96a0-71a6057bfe9a" \
--server-os-version "10.0.14393.0" --server-role "Standalone" --resource-group "SampleResourceGroup_1" --server-id \
"080d4133-bdb5-40a0-96a0-71a6057bfe9a" --storage-sync-service-name "SampleStorageSyncService_1"
```
##### <a name="ParametersRegisteredServersCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|serverId|
|**--server-certificate**|string|Registered Server Certificate|server_certificate|serverCertificate|
|**--agent-version**|string|Registered Server Agent Version|agent_version|agentVersion|
|**--server-os-version**|string|Registered Server OS Version|server_os_version|serverOSVersion|
|**--last-heart-beat**|string|Registered Server last heart beat|last_heart_beat|lastHeartBeat|
|**--server-role**|string|Registered Server serverRole|server_role|serverRole|
|**--cluster-id**|string|Registered Server clusterId|cluster_id|clusterId|
|**--cluster-name**|string|Registered Server clusterName|cluster_name|clusterName|
|**--registered-server-create-parameters-properties-server-id**|string|Registered Server serverId|registered_server_create_parameters_properties_server_id|serverId|
|**--friendly-name**|string|Friendly Name|friendly_name|friendlyName|

#### <a name="RegisteredServersDelete">Command `az storagesync registered-server delete`</a>

##### <a name="ExamplesRegisteredServersDelete">Example</a>
```
az storagesync registered-server delete --resource-group "SampleResourceGroup_1" --server-id \
"41166691-ab03-43e9-ab3e-0330eda162ac" --storage-sync-service-name "SampleStorageSyncService_1"
```
##### <a name="ParametersRegisteredServersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|GUID identifying the on-premises server.|server_id|serverId|

#### <a name="RegisteredServerstriggerRollover">Command `az storagesync registered-server trigger-rollover`</a>

##### <a name="ExamplesRegisteredServerstriggerRollover">Example</a>
```
az storagesync registered-server trigger-rollover --server-certificate "\\"MIIDFjCCAf6gAwIBAgIQQS+DS8uhc4VNzUkTw7wbRjAN\
BgkqhkiG9w0BAQ0FADAzMTEwLwYDVQQDEyhhbmt1c2hiLXByb2QzLnJlZG1vbmQuY29ycC5taWNyb3NvZnQuY29tMB4XDTE3MDgwMzE3MDQyNFoXDTE4MDg\
wNDE3MDQyNFowMzExMC8GA1UEAxMoYW5rdXNoYi1wcm9kMy5yZWRtb25kLmNvcnAubWljcm9zb2Z0LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQ\
oCggEBALDRvV4gmsIy6jGDPiHsXmvgVP749NNP7DopdlbHaNhjFmYINHl0uWylyaZmgJrROt2mnxN/zEyJtGnqYHlzUr4xvGq/qV5pqgdB9tag/sw9i22gf\
e9PRZ0FmSOZnXMbLYgLiDFqLtut5gHcOuWMj03YnkfoBEKlFBxWbagvW2yxz/Sxi9OVSJOKCaXra0RpcIHrO/KFl6ho2eE1/7Ykmfa8hZvSdoPd5gHdLiQc\
MB/pxq+mWp1fI6c8vFZoDu7Atn+NXTzYPKUxKzaisF12TsaKpohUsJpbB3Wocb0F5frn614D2pg14ERB5otjAMWw1m65csQWPI6dP8KIYe0+QPkCAwEAAaM\
mMCQwIgYDVR0lAQH/BBgwFgYIKwYBBQUHAwIGCisGAQQBgjcKAwwwDQYJKoZIhvcNAQENBQADggEBAA4RhVIBkw34M1RwakJgHvtjsOFxF1tVQA941NtLok\
x1l2Z8+GFQkcG4xpZSt+UN6wLerdCbnNhtkCErWUDeaT0jxk4g71Ofex7iM04crT4iHJr8mi96/XnhnkTUs+GDk12VgdeeNEczMZz+8Mxw9dJ5NCnYgTwO0\
SzGlclRsDvjzkLo8rh2ZG6n/jKrEyNXXo+hOqhupij0QbRP2Tvexdfw201kgN1jdZify8XzJ8Oi0bTS0KpJf2pNPOlooK2bjMUei9ANtEdXwwfVZGWvVh6t\
Jjdv6k14wWWJ1L7zhA1IIVb1J+sQUzJji5iX0DrezjTz1Fg+gAzITaA/WsuujlM=\\"" --resource-group "SampleResourceGroup_1" \
--server-id "d166ca76-dad2-49df-b409-12345642d730" --storage-sync-service-name "SampleStorageSyncService_1"
```
##### <a name="ParametersRegisteredServerstriggerRollover">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--server-id**|string|Server Id|server_id|serverId|
|**--server-certificate**|string|Certificate Data|server_certificate|serverCertificate|

### group `az storagesync server-endpoint`
#### <a name="ServerEndpointsListBySyncGroup">Command `az storagesync server-endpoint list`</a>

##### <a name="ExamplesServerEndpointsListBySyncGroup">Example</a>
```
az storagesync server-endpoint list --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersServerEndpointsListBySyncGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

#### <a name="ServerEndpointsGet">Command `az storagesync server-endpoint show`</a>

##### <a name="ExamplesServerEndpointsGet">Example</a>
```
az storagesync server-endpoint show --resource-group "SampleResourceGroup_1" --name "SampleServerEndpoint_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersServerEndpointsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|

#### <a name="ServerEndpointsCreate">Command `az storagesync server-endpoint create`</a>

##### <a name="ExamplesServerEndpointsCreate">Example</a>
```
az storagesync server-endpoint create --cloud-tiering "off" --initial-download-policy "NamespaceThenModifiedFiles" \
--local-cache-mode "UpdateLocallyCachedFiles" --offline-data-transfer "on" --offline-data-transfer-share-name \
"myfileshare" --server-local-path "D:\\\\SampleServerEndpoint_1" --server-resource-id "/subscriptions/52b8da2f-61e0-4a1\
f-8dde-336911f367fb/resourceGroups/SampleResourceGroup_1/providers/Microsoft.StorageSync/storageSyncServices/SampleStor\
ageSyncService_1/registeredServers/080d4133-bdb5-40a0-96a0-71a6057bfe9a" --tier-files-older-than-days 0 \
--volume-free-space-percent 100 --resource-group "SampleResourceGroup_1" --name "SampleServerEndpoint_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersServerEndpointsCreate">Parameters</a> 
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

#### <a name="ServerEndpointsUpdate">Command `az storagesync server-endpoint update`</a>

##### <a name="ExamplesServerEndpointsUpdate">Example</a>
```
az storagesync server-endpoint update --cloud-tiering "off" --local-cache-mode "UpdateLocallyCachedFiles" \
--offline-data-transfer "off" --tier-files-older-than-days 0 --volume-free-space-percent 100 --resource-group \
"SampleResourceGroup_1" --name "SampleServerEndpoint_1" --storage-sync-service-name "SampleStorageSyncService_1" \
--sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersServerEndpointsUpdate">Parameters</a> 
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

#### <a name="ServerEndpointsDelete">Command `az storagesync server-endpoint delete`</a>

##### <a name="ExamplesServerEndpointsDelete">Example</a>
```
az storagesync server-endpoint delete --resource-group "SampleResourceGroup_1" --name "SampleServerEndpoint_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name "SampleSyncGroup_1"
```
##### <a name="ParametersServerEndpointsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|

#### <a name="ServerEndpointsrecallAction">Command `az storagesync server-endpoint recall-action`</a>

##### <a name="ExamplesServerEndpointsrecallAction">Example</a>
```
az storagesync server-endpoint recall-action --pattern "" --recall-path "" --resource-group "SampleResourceGroup_1" \
--name "SampleServerEndpoint_1" --storage-sync-service-name "SampleStorageSyncService_1" --sync-group-name \
"SampleSyncGroup_1"
```
##### <a name="ParametersServerEndpointsrecallAction">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--server-endpoint-name**|string|Name of Server Endpoint object.|server_endpoint_name|serverEndpointName|
|**--pattern**|string|Pattern of the files.|pattern|pattern|
|**--recall-path**|string|Recall path.|recall_path|recallPath|

### group `az storagesync storage-sync-service`
#### <a name="StorageSyncServicesListByResourceGroup">Command `az storagesync storage-sync-service list`</a>

##### <a name="ExamplesStorageSyncServicesListByResourceGroup">Example</a>
```
az storagesync storage-sync-service list --resource-group "SampleResourceGroup_1"
```
##### <a name="ParametersStorageSyncServicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="StorageSyncServicesListBySubscription">Command `az storagesync storage-sync-service list`</a>

##### <a name="ExamplesStorageSyncServicesListBySubscription">Example</a>
```
az storagesync storage-sync-service list
```
##### <a name="ParametersStorageSyncServicesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="StorageSyncServicesGet">Command `az storagesync storage-sync-service show`</a>

##### <a name="ExamplesStorageSyncServicesGet">Example</a>
```
az storagesync storage-sync-service show --resource-group "SampleResourceGroup_1" --name "SampleStorageSyncService_1"
```
##### <a name="ParametersStorageSyncServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

#### <a name="StorageSyncServicesCreate">Command `az storagesync storage-sync-service create`</a>

##### <a name="ExamplesStorageSyncServicesCreate">Example</a>
```
az storagesync storage-sync-service create --location "WestUS" --incoming-traffic-policy "AllowAllTraffic" \
--resource-group "SampleResourceGroup_1" --name "SampleStorageSyncService_1"
```
##### <a name="ParametersStorageSyncServicesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--location**|string|Required. Gets or sets the location of the resource. This will be one of the supported and registered Azure Geo Regions (e.g. West US, East US, Southeast Asia, etc.). The geo region of a resource cannot be changed once it is created, but if an identical geo region is specified on update, the request will succeed.|location|location|
|**--tags**|dictionary|Gets or sets a list of key value pairs that describe the resource. These tags can be used for viewing and grouping this resource (across resource groups). A maximum of 15 tags can be provided for a resource. Each tag must have a key with a length no greater than 128 characters and a value with a length no greater than 256 characters.|tags|tags|
|**--incoming-traffic-policy**|choice|Incoming Traffic Policy|incoming_traffic_policy|incomingTrafficPolicy|

#### <a name="StorageSyncServicesUpdate">Command `az storagesync storage-sync-service update`</a>

##### <a name="ExamplesStorageSyncServicesUpdate">Example</a>
```
az storagesync storage-sync-service update --incoming-traffic-policy "AllowAllTraffic" --tags Dept="IT" \
Environment="Test" --resource-group "SampleResourceGroup_1" --name "SampleStorageSyncService_1"
```
##### <a name="ParametersStorageSyncServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--tags**|dictionary|The user-specified tags associated with the storage sync service.|tags|tags|
|**--incoming-traffic-policy**|choice|Incoming Traffic Policy|incoming_traffic_policy|incomingTrafficPolicy|

#### <a name="StorageSyncServicesDelete">Command `az storagesync storage-sync-service delete`</a>

##### <a name="ExamplesStorageSyncServicesDelete">Example</a>
```
az storagesync storage-sync-service delete --resource-group "SampleResourceGroup_1" --name \
"SampleStorageSyncService_1"
```
##### <a name="ParametersStorageSyncServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

### group `az storagesync sync-group`
#### <a name="SyncGroupsListByStorageSyncService">Command `az storagesync sync-group list`</a>

##### <a name="ExamplesSyncGroupsListByStorageSyncService">Example</a>
```
az storagesync sync-group list --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1"
```
##### <a name="ParametersSyncGroupsListByStorageSyncService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

#### <a name="SyncGroupsGet">Command `az storagesync sync-group show`</a>

##### <a name="ExamplesSyncGroupsGet">Example</a>
```
az storagesync sync-group show --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --name "SampleSyncGroup_1"
```
##### <a name="ParametersSyncGroupsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

#### <a name="SyncGroupsCreate">Command `az storagesync sync-group create`</a>

##### <a name="ExamplesSyncGroupsCreate">Example</a>
```
az storagesync sync-group create --properties "{}" --resource-group "SampleResourceGroup_1" \
--storage-sync-service-name "SampleStorageSyncService_1" --name "SampleSyncGroup_1"
```
##### <a name="ParametersSyncGroupsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|
|**--properties**|any|The parameters used to create the sync group|properties|properties|

#### <a name="SyncGroupsDelete">Command `az storagesync sync-group delete`</a>

##### <a name="ExamplesSyncGroupsDelete">Example</a>
```
az storagesync sync-group delete --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --name "SampleSyncGroup_1"
```
##### <a name="ParametersSyncGroupsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--sync-group-name**|string|Name of Sync Group resource.|sync_group_name|syncGroupName|

### group `az storagesync workflow`
#### <a name="WorkflowsListByStorageSyncService">Command `az storagesync workflow list`</a>

##### <a name="ExamplesWorkflowsListByStorageSyncService">Example</a>
```
az storagesync workflow list --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1"
```
##### <a name="ParametersWorkflowsListByStorageSyncService">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|

#### <a name="WorkflowsGet">Command `az storagesync workflow show`</a>

##### <a name="ExamplesWorkflowsGet">Example</a>
```
az storagesync workflow show --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --workflow-id "828219ea-083e-48b5-89ea-8fd9991b2e75"
```
##### <a name="ParametersWorkflowsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--workflow-id**|string|workflow Id|workflow_id|workflowId|

#### <a name="WorkflowsAbort">Command `az storagesync workflow abort`</a>

##### <a name="ExamplesWorkflowsAbort">Example</a>
```
az storagesync workflow abort --resource-group "SampleResourceGroup_1" --storage-sync-service-name \
"SampleStorageSyncService_1" --workflow-id "7ffd50b3-5574-478d-9ff2-9371bc42ce68"
```
##### <a name="ParametersWorkflowsAbort">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--storage-sync-service-name**|string|Name of Storage Sync Service resource.|storage_sync_service_name|storageSyncServiceName|
|**--workflow-id**|string|workflow Id|workflow_id|workflowId|
