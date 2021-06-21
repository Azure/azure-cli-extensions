# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az loganalytics|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az loganalytics` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az loganalytics data-export|DataExports|[commands](#CommandsInDataExports)|
|az loganalytics data-source|DataSources|[commands](#CommandsInDataSources)|
|az loganalytics intelligence-pack|IntelligencePacks|[commands](#CommandsInIntelligencePacks)|
|az loganalytics linked-service|LinkedServices|[commands](#CommandsInLinkedServices)|
|az loganalytics linked-storage-account|LinkedStorageAccounts|[commands](#CommandsInLinkedStorageAccounts)|
|az loganalytics management-group|ManagementGroups|[commands](#CommandsInManagementGroups)|
|az loganalytics operation-statuses|OperationStatuses|[commands](#CommandsInOperationStatuses)|
|az loganalytics shared-key|SharedKeys|[commands](#CommandsInSharedKeys)|
|az loganalytics usage|Usages|[commands](#CommandsInUsages)|
|az loganalytics storage-insight-config|StorageInsightConfigs|[commands](#CommandsInStorageInsightConfigs)|
|az loganalytics saved-search|SavedSearches|[commands](#CommandsInSavedSearches)|
|az loganalytics available-service-tier|AvailableServiceTiers|[commands](#CommandsInAvailableServiceTiers)|
|az loganalytics gateway|Gateways|[commands](#CommandsInGateways)|
|az loganalytics schema|Schema|[commands](#CommandsInSchema)|
|az loganalytics workspace-purge|WorkspacePurge|[commands](#CommandsInWorkspacePurge)|
|az loganalytics table|Tables|[commands](#CommandsInTables)|
|az loganalytics cluster|Clusters|[commands](#CommandsInClusters)|
|az loganalytics workspace|Workspaces|[commands](#CommandsInWorkspaces)|
|az loganalytics deleted-workspace|DeletedWorkspaces|[commands](#CommandsInDeletedWorkspaces)|

## COMMANDS
### <a name="CommandsInAvailableServiceTiers">Commands in `az loganalytics available-service-tier` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics available-service-tier list](#AvailableServiceTiersListByWorkspace)|ListByWorkspace|[Parameters](#ParametersAvailableServiceTiersListByWorkspace)|[Example](#ExamplesAvailableServiceTiersListByWorkspace)|

### <a name="CommandsInClusters">Commands in `az loganalytics cluster` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics cluster list](#ClustersListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersClustersListByResourceGroup)|[Example](#ExamplesClustersListByResourceGroup)|
|[az loganalytics cluster list](#ClustersList)|List|[Parameters](#ParametersClustersList)|[Example](#ExamplesClustersList)|
|[az loganalytics cluster show](#ClustersGet)|Get|[Parameters](#ParametersClustersGet)|[Example](#ExamplesClustersGet)|
|[az loganalytics cluster create](#ClustersCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersClustersCreateOrUpdate#Create)|[Example](#ExamplesClustersCreateOrUpdate#Create)|
|[az loganalytics cluster update](#ClustersUpdate)|Update|[Parameters](#ParametersClustersUpdate)|[Example](#ExamplesClustersUpdate)|
|[az loganalytics cluster delete](#ClustersDelete)|Delete|[Parameters](#ParametersClustersDelete)|[Example](#ExamplesClustersDelete)|

### <a name="CommandsInDataExports">Commands in `az loganalytics data-export` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics data-export list](#DataExportsListByWorkspace)|ListByWorkspace|[Parameters](#ParametersDataExportsListByWorkspace)|[Example](#ExamplesDataExportsListByWorkspace)|
|[az loganalytics data-export show](#DataExportsGet)|Get|[Parameters](#ParametersDataExportsGet)|[Example](#ExamplesDataExportsGet)|
|[az loganalytics data-export create](#DataExportsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDataExportsCreateOrUpdate#Create)|[Example](#ExamplesDataExportsCreateOrUpdate#Create)|
|[az loganalytics data-export update](#DataExportsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersDataExportsCreateOrUpdate#Update)|Not Found|
|[az loganalytics data-export delete](#DataExportsDelete)|Delete|[Parameters](#ParametersDataExportsDelete)|[Example](#ExamplesDataExportsDelete)|

### <a name="CommandsInDataSources">Commands in `az loganalytics data-source` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics data-source list](#DataSourcesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersDataSourcesListByWorkspace)|[Example](#ExamplesDataSourcesListByWorkspace)|
|[az loganalytics data-source show](#DataSourcesGet)|Get|[Parameters](#ParametersDataSourcesGet)|[Example](#ExamplesDataSourcesGet)|
|[az loganalytics data-source create](#DataSourcesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDataSourcesCreateOrUpdate#Create)|[Example](#ExamplesDataSourcesCreateOrUpdate#Create)|
|[az loganalytics data-source update](#DataSourcesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersDataSourcesCreateOrUpdate#Update)|Not Found|
|[az loganalytics data-source delete](#DataSourcesDelete)|Delete|[Parameters](#ParametersDataSourcesDelete)|[Example](#ExamplesDataSourcesDelete)|

### <a name="CommandsInDeletedWorkspaces">Commands in `az loganalytics deleted-workspace` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics deleted-workspace list](#DeletedWorkspacesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersDeletedWorkspacesListByResourceGroup)|[Example](#ExamplesDeletedWorkspacesListByResourceGroup)|
|[az loganalytics deleted-workspace list](#DeletedWorkspacesList)|List|[Parameters](#ParametersDeletedWorkspacesList)|[Example](#ExamplesDeletedWorkspacesList)|

### <a name="CommandsInGateways">Commands in `az loganalytics gateway` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics gateway delete](#GatewaysDelete)|Delete|[Parameters](#ParametersGatewaysDelete)|[Example](#ExamplesGatewaysDelete)|

### <a name="CommandsInIntelligencePacks">Commands in `az loganalytics intelligence-pack` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics intelligence-pack list](#IntelligencePacksList)|List|[Parameters](#ParametersIntelligencePacksList)|[Example](#ExamplesIntelligencePacksList)|
|[az loganalytics intelligence-pack disable](#IntelligencePacksDisable)|Disable|[Parameters](#ParametersIntelligencePacksDisable)|[Example](#ExamplesIntelligencePacksDisable)|
|[az loganalytics intelligence-pack enable](#IntelligencePacksEnable)|Enable|[Parameters](#ParametersIntelligencePacksEnable)|[Example](#ExamplesIntelligencePacksEnable)|

### <a name="CommandsInLinkedServices">Commands in `az loganalytics linked-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics linked-service list](#LinkedServicesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersLinkedServicesListByWorkspace)|[Example](#ExamplesLinkedServicesListByWorkspace)|
|[az loganalytics linked-service show](#LinkedServicesGet)|Get|[Parameters](#ParametersLinkedServicesGet)|[Example](#ExamplesLinkedServicesGet)|
|[az loganalytics linked-service create](#LinkedServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersLinkedServicesCreateOrUpdate#Create)|[Example](#ExamplesLinkedServicesCreateOrUpdate#Create)|
|[az loganalytics linked-service update](#LinkedServicesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersLinkedServicesCreateOrUpdate#Update)|Not Found|
|[az loganalytics linked-service delete](#LinkedServicesDelete)|Delete|[Parameters](#ParametersLinkedServicesDelete)|[Example](#ExamplesLinkedServicesDelete)|

### <a name="CommandsInLinkedStorageAccounts">Commands in `az loganalytics linked-storage-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics linked-storage-account list](#LinkedStorageAccountsListByWorkspace)|ListByWorkspace|[Parameters](#ParametersLinkedStorageAccountsListByWorkspace)|[Example](#ExamplesLinkedStorageAccountsListByWorkspace)|
|[az loganalytics linked-storage-account show](#LinkedStorageAccountsGet)|Get|[Parameters](#ParametersLinkedStorageAccountsGet)|[Example](#ExamplesLinkedStorageAccountsGet)|
|[az loganalytics linked-storage-account create](#LinkedStorageAccountsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersLinkedStorageAccountsCreateOrUpdate#Create)|[Example](#ExamplesLinkedStorageAccountsCreateOrUpdate#Create)|
|[az loganalytics linked-storage-account update](#LinkedStorageAccountsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersLinkedStorageAccountsCreateOrUpdate#Update)|Not Found|
|[az loganalytics linked-storage-account delete](#LinkedStorageAccountsDelete)|Delete|[Parameters](#ParametersLinkedStorageAccountsDelete)|[Example](#ExamplesLinkedStorageAccountsDelete)|

### <a name="CommandsInManagementGroups">Commands in `az loganalytics management-group` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics management-group list](#ManagementGroupsList)|List|[Parameters](#ParametersManagementGroupsList)|[Example](#ExamplesManagementGroupsList)|

### <a name="CommandsInOperationStatuses">Commands in `az loganalytics operation-statuses` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics operation-statuses show](#OperationStatusesGet)|Get|[Parameters](#ParametersOperationStatusesGet)|[Example](#ExamplesOperationStatusesGet)|

### <a name="CommandsInSavedSearches">Commands in `az loganalytics saved-search` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics saved-search list](#SavedSearchesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersSavedSearchesListByWorkspace)|[Example](#ExamplesSavedSearchesListByWorkspace)|
|[az loganalytics saved-search show](#SavedSearchesGet)|Get|[Parameters](#ParametersSavedSearchesGet)|[Example](#ExamplesSavedSearchesGet)|
|[az loganalytics saved-search create](#SavedSearchesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSavedSearchesCreateOrUpdate#Create)|[Example](#ExamplesSavedSearchesCreateOrUpdate#Create)|
|[az loganalytics saved-search update](#SavedSearchesCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersSavedSearchesCreateOrUpdate#Update)|Not Found|
|[az loganalytics saved-search delete](#SavedSearchesDelete)|Delete|[Parameters](#ParametersSavedSearchesDelete)|[Example](#ExamplesSavedSearchesDelete)|

### <a name="CommandsInSchema">Commands in `az loganalytics schema` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics schema get](#SchemaGet)|Get|[Parameters](#ParametersSchemaGet)|[Example](#ExamplesSchemaGet)|

### <a name="CommandsInSharedKeys">Commands in `az loganalytics shared-key` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics shared-key get-shared-key](#SharedKeysGetSharedKeys)|GetSharedKeys|[Parameters](#ParametersSharedKeysGetSharedKeys)|[Example](#ExamplesSharedKeysGetSharedKeys)|
|[az loganalytics shared-key regenerate](#SharedKeysRegenerate)|Regenerate|[Parameters](#ParametersSharedKeysRegenerate)|[Example](#ExamplesSharedKeysRegenerate)|

### <a name="CommandsInStorageInsightConfigs">Commands in `az loganalytics storage-insight-config` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics storage-insight-config list](#StorageInsightConfigsListByWorkspace)|ListByWorkspace|[Parameters](#ParametersStorageInsightConfigsListByWorkspace)|[Example](#ExamplesStorageInsightConfigsListByWorkspace)|
|[az loganalytics storage-insight-config show](#StorageInsightConfigsGet)|Get|[Parameters](#ParametersStorageInsightConfigsGet)|[Example](#ExamplesStorageInsightConfigsGet)|
|[az loganalytics storage-insight-config create](#StorageInsightConfigsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersStorageInsightConfigsCreateOrUpdate#Create)|[Example](#ExamplesStorageInsightConfigsCreateOrUpdate#Create)|
|[az loganalytics storage-insight-config update](#StorageInsightConfigsCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersStorageInsightConfigsCreateOrUpdate#Update)|Not Found|
|[az loganalytics storage-insight-config delete](#StorageInsightConfigsDelete)|Delete|[Parameters](#ParametersStorageInsightConfigsDelete)|[Example](#ExamplesStorageInsightConfigsDelete)|

### <a name="CommandsInTables">Commands in `az loganalytics table` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics table list](#TablesListByWorkspace)|ListByWorkspace|[Parameters](#ParametersTablesListByWorkspace)|[Example](#ExamplesTablesListByWorkspace)|
|[az loganalytics table show](#TablesGet)|Get|[Parameters](#ParametersTablesGet)|[Example](#ExamplesTablesGet)|
|[az loganalytics table update](#TablesUpdate)|Update|[Parameters](#ParametersTablesUpdate)|[Example](#ExamplesTablesUpdate)|

### <a name="CommandsInUsages">Commands in `az loganalytics usage` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics usage list](#UsagesList)|List|[Parameters](#ParametersUsagesList)|[Example](#ExamplesUsagesList)|

### <a name="CommandsInWorkspaces">Commands in `az loganalytics workspace` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics workspace list](#WorkspacesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersWorkspacesListByResourceGroup)|[Example](#ExamplesWorkspacesListByResourceGroup)|
|[az loganalytics workspace list](#WorkspacesList)|List|[Parameters](#ParametersWorkspacesList)|[Example](#ExamplesWorkspacesList)|
|[az loganalytics workspace show](#WorkspacesGet)|Get|[Parameters](#ParametersWorkspacesGet)|[Example](#ExamplesWorkspacesGet)|
|[az loganalytics workspace create](#WorkspacesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersWorkspacesCreateOrUpdate#Create)|[Example](#ExamplesWorkspacesCreateOrUpdate#Create)|
|[az loganalytics workspace update](#WorkspacesUpdate)|Update|[Parameters](#ParametersWorkspacesUpdate)|[Example](#ExamplesWorkspacesUpdate)|
|[az loganalytics workspace delete](#WorkspacesDelete)|Delete|[Parameters](#ParametersWorkspacesDelete)|[Example](#ExamplesWorkspacesDelete)|

### <a name="CommandsInWorkspacePurge">Commands in `az loganalytics workspace-purge` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az loganalytics workspace-purge purge](#WorkspacePurgePurge)|Purge|[Parameters](#ParametersWorkspacePurgePurge)|[Example](#ExamplesWorkspacePurgePurge)|
|[az loganalytics workspace-purge show-purge-status](#WorkspacePurgeGetPurgeStatus)|GetPurgeStatus|[Parameters](#ParametersWorkspacePurgeGetPurgeStatus)|[Example](#ExamplesWorkspacePurgeGetPurgeStatus)|


## COMMAND DETAILS

### group `az loganalytics available-service-tier`
#### <a name="AvailableServiceTiersListByWorkspace">Command `az loganalytics available-service-tier list`</a>

##### <a name="ExamplesAvailableServiceTiersListByWorkspace">Example</a>
```
az loganalytics available-service-tier list --resource-group "rg1" --workspace-name "workspace1"
```
##### <a name="ParametersAvailableServiceTiersListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### group `az loganalytics cluster`
#### <a name="ClustersListByResourceGroup">Command `az loganalytics cluster list`</a>

##### <a name="ExamplesClustersListByResourceGroup">Example</a>
```
az loganalytics cluster list --resource-group "oiautorest6685"
```
##### <a name="ParametersClustersListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="ClustersList">Command `az loganalytics cluster list`</a>

##### <a name="ExamplesClustersList">Example</a>
```
az loganalytics cluster list
```
##### <a name="ParametersClustersList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="ClustersGet">Command `az loganalytics cluster show`</a>

##### <a name="ExamplesClustersGet">Example</a>
```
az loganalytics cluster show --name "oiautorest6685" --resource-group "oiautorest6685"
```
##### <a name="ParametersClustersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|Name of the Log Analytics Cluster.|cluster_name|clusterName|

#### <a name="ClustersCreateOrUpdate#Create">Command `az loganalytics cluster create`</a>

##### <a name="ExamplesClustersCreateOrUpdate#Create">Example</a>
```
az loganalytics cluster create --name "oiautorest6685" --location "australiasoutheast" --sku \
name="CapacityReservation" capacity=1000 --tags tag1="val1" --resource-group "oiautorest6685"
```
##### <a name="ParametersClustersCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Log Analytics cluster.|cluster_name|clusterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--sku**|object|The sku properties.|sku|sku|
|**--is-double-encryption-enabled**|boolean|Configures whether cluster will use double encryption. This Property can not be modified after cluster creation. Default value is 'true'|is_double_encryption_enabled|isDoubleEncryptionEnabled|
|**--is-availability-zones-enabled**|boolean|Sets whether the cluster will support availability zones. This can be set as true only in regions where Azure Data Explorer support Availability Zones. This Property can not be modified after cluster creation. Default value is 'true' if region supports Availability Zones.|is_availability_zones_enabled|isAvailabilityZonesEnabled|
|**--billing-type**|choice|The cluster's billing type.|billing_type|billingType|
|**--key-vault-properties**|object|The associated key properties.|key_vault_properties|keyVaultProperties|
|**--type**|sealed-choice|Type of managed service identity.|type|type|
|**--user-assigned-identities**|dictionary|The list of user identities associated with the resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|

#### <a name="ClustersUpdate">Command `az loganalytics cluster update`</a>

##### <a name="ExamplesClustersUpdate">Example</a>
```
az loganalytics cluster update --name "oiautorest6685" --type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/00000000-0000-0000-0000-00000000000/resourcegroups/oiautorest6685/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/myidentity\\":{}}" --key-vault-properties key-name="aztest2170cert" key-rsa-size=1024 \
key-vault-uri="https://aztest2170.vault.azure.net" key-version="654ft6c4e63845cbb50fd6fg51540429" --sku \
name="CapacityReservation" capacity=1000 --tags tag1="val1" --resource-group "oiautorest6685"
```
##### <a name="ParametersClustersUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|Name of the Log Analytics Cluster.|cluster_name|clusterName|
|**--sku**|object|The sku properties.|sku|sku|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--key-vault-properties**|object|The associated key properties.|key_vault_properties|keyVaultProperties|
|**--billing-type**|choice|The cluster's billing type.|billing_type|billingType|
|**--type**|sealed-choice|Type of managed service identity.|type|type|
|**--user-assigned-identities**|dictionary|The list of user identities associated with the resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|

#### <a name="ClustersDelete">Command `az loganalytics cluster delete`</a>

##### <a name="ExamplesClustersDelete">Example</a>
```
az loganalytics cluster delete --name "oiautorest6685" --resource-group "oiautorest6685"
```
##### <a name="ParametersClustersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|Name of the Log Analytics Cluster.|cluster_name|clusterName|

### group `az loganalytics data-export`
#### <a name="DataExportsListByWorkspace">Command `az loganalytics data-export list`</a>

##### <a name="ExamplesDataExportsListByWorkspace">Example</a>
```
az loganalytics data-export list --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### <a name="ParametersDataExportsListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="DataExportsGet">Command `az loganalytics data-export show`</a>

##### <a name="ExamplesDataExportsGet">Example</a>
```
az loganalytics data-export show --name "export1" --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### <a name="ParametersDataExportsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-export-name**|string|The data export rule name.|data_export_name|dataExportName|

#### <a name="DataExportsCreateOrUpdate#Create">Command `az loganalytics data-export create`</a>

##### <a name="ExamplesDataExportsCreateOrUpdate#Create">Example</a>
```
az loganalytics data-export create --name "export1" --resource-id "/subscriptions/192b9f85-a39a-4276-b96d-d5cd351703f9/\
resourceGroups/OIAutoRest1234/providers/Microsoft.EventHub/namespaces/test" --table-names "Heartbeat" --resource-group \
"RgTest1" --workspace-name "DeWnTest1234"
```
##### <a name="ParametersDataExportsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-export-name**|string|The data export rule name.|data_export_name|dataExportName|
|**--data-export-id**|string|The data export rule ID.|data_export_id|dataExportId|
|**--table-names**|array|An array of tables to export, for example: [“Heartbeat, SecurityEvent”].|table_names|tableNames|
|**--enable**|boolean|Active when enabled.|enable|enable|
|**--created-date**|string|The latest data export rule modification time.|created_date|createdDate|
|**--last-modified-date**|string|Date and time when the export was last modified.|last_modified_date|lastModifiedDate|
|**--resource-id**|string|The destination resource ID. This can be copied from the Properties entry of the destination resource in Azure.|resource_id|resourceId|
|**--event-hub-name**|string|Optional. Allows to define an Event Hub name. Not applicable when destination is Storage Account.|event_hub_name|eventHubName|

#### <a name="DataExportsCreateOrUpdate#Update">Command `az loganalytics data-export update`</a>

##### <a name="ParametersDataExportsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-export-name**|string|The data export rule name.|data_export_name|dataExportName|
|**--data-export-id**|string|The data export rule ID.|data_export_id|dataExportId|
|**--table-names**|array|An array of tables to export, for example: [“Heartbeat, SecurityEvent”].|table_names|tableNames|
|**--enable**|boolean|Active when enabled.|enable|enable|
|**--created-date**|string|The latest data export rule modification time.|created_date|createdDate|
|**--last-modified-date**|string|Date and time when the export was last modified.|last_modified_date|lastModifiedDate|
|**--resource-id**|string|The destination resource ID. This can be copied from the Properties entry of the destination resource in Azure.|resource_id|resourceId|
|**--event-hub-name**|string|Optional. Allows to define an Event Hub name. Not applicable when destination is Storage Account.|event_hub_name|eventHubName|

#### <a name="DataExportsDelete">Command `az loganalytics data-export delete`</a>

##### <a name="ExamplesDataExportsDelete">Example</a>
```
az loganalytics data-export delete --name "export1" --resource-group "RgTest1" --workspace-name "DeWnTest1234"
```
##### <a name="ParametersDataExportsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-export-name**|string|The data export rule name.|data_export_name|dataExportName|

### group `az loganalytics data-source`
#### <a name="DataSourcesListByWorkspace">Command `az loganalytics data-source list`</a>

##### <a name="ExamplesDataSourcesListByWorkspace">Example</a>
```
az loganalytics data-source list --filter "kind=\'WindowsEvent\'" --resource-group "OIAutoRest5123" --workspace-name \
"AzTest9724"
```
##### <a name="ParametersDataSourcesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--filter**|string|The filter to apply on the operation.|filter|$filter|
|**--skiptoken**|string|Starting point of the collection of data source instances.|skiptoken|$skiptoken|

#### <a name="DataSourcesGet">Command `az loganalytics data-source show`</a>

##### <a name="ExamplesDataSourcesGet">Example</a>
```
az loganalytics data-source show --name "AzTestDS774" --resource-group "OIAutoRest5123" --workspace-name "AzTest9724"
```
##### <a name="ParametersDataSourcesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-name**|string|Name of the datasource|data_source_name|dataSourceName|

#### <a name="DataSourcesCreateOrUpdate#Create">Command `az loganalytics data-source create`</a>

##### <a name="ExamplesDataSourcesCreateOrUpdate#Create">Example</a>
```
az loganalytics data-source create --name "AzTestDS774" --kind "AzureActivityLog" --properties \
"{\\"LinkedResourceId\\":\\"/subscriptions/00000000-0000-0000-0000-00000000000/providers/microsoft.insights/eventtypes/\
management\\"}" --resource-group "OIAutoRest5123" --workspace-name "AzTest9724"
```
##### <a name="ParametersDataSourcesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-name**|string|The name of the datasource resource.|data_source_name|dataSourceName|
|**--properties**|any|The data source properties in raw json format, each kind of data source have it's own schema.|properties|properties|
|**--kind**|choice|The kind of the DataSource.|kind|kind|
|**--etag**|string|The ETag of the data source.|etag|etag|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="DataSourcesCreateOrUpdate#Update">Command `az loganalytics data-source update`</a>

##### <a name="ParametersDataSourcesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-name**|string|The name of the datasource resource.|data_source_name|dataSourceName|
|**--properties**|any|The data source properties in raw json format, each kind of data source have it's own schema.|properties|properties|
|**--kind**|choice|The kind of the DataSource.|kind|kind|
|**--etag**|string|The ETag of the data source.|etag|etag|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="DataSourcesDelete">Command `az loganalytics data-source delete`</a>

##### <a name="ExamplesDataSourcesDelete">Example</a>
```
az loganalytics data-source delete --name "AzTestDS774" --resource-group "OIAutoRest5123" --workspace-name \
"AzTest9724"
```
##### <a name="ParametersDataSourcesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-name**|string|Name of the datasource.|data_source_name|dataSourceName|

### group `az loganalytics deleted-workspace`
#### <a name="DeletedWorkspacesListByResourceGroup">Command `az loganalytics deleted-workspace list`</a>

##### <a name="ExamplesDeletedWorkspacesListByResourceGroup">Example</a>
```
az loganalytics deleted-workspace list --resource-group "oiautorest6685"
```
##### <a name="ParametersDeletedWorkspacesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="DeletedWorkspacesList">Command `az loganalytics deleted-workspace list`</a>

##### <a name="ExamplesDeletedWorkspacesList">Example</a>
```
az loganalytics deleted-workspace list
```
##### <a name="ParametersDeletedWorkspacesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
### group `az loganalytics gateway`
#### <a name="GatewaysDelete">Command `az loganalytics gateway delete`</a>

##### <a name="ExamplesGatewaysDelete">Example</a>
```
az loganalytics gateway delete --gateway-id "00000000-0000-0000-0000-00000000000" --resource-group "OIAutoRest5123" \
--workspace-name "aztest5048"
```
##### <a name="ParametersGatewaysDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--gateway-id**|string|The Log Analytics gateway Id.|gateway_id|gatewayId|

### group `az loganalytics intelligence-pack`
#### <a name="IntelligencePacksList">Command `az loganalytics intelligence-pack list`</a>

##### <a name="ExamplesIntelligencePacksList">Example</a>
```
az loganalytics intelligence-pack list --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersIntelligencePacksList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="IntelligencePacksDisable">Command `az loganalytics intelligence-pack disable`</a>

##### <a name="ExamplesIntelligencePacksDisable">Example</a>
```
az loganalytics intelligence-pack disable --name "ChangeTracking" --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersIntelligencePacksDisable">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--intelligence-pack-name**|string|The name of the intelligence pack to be disabled.|intelligence_pack_name|intelligencePackName|

#### <a name="IntelligencePacksEnable">Command `az loganalytics intelligence-pack enable`</a>

##### <a name="ExamplesIntelligencePacksEnable">Example</a>
```
az loganalytics intelligence-pack enable --name "ChangeTracking" --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersIntelligencePacksEnable">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--intelligence-pack-name**|string|The name of the intelligence pack to be enabled.|intelligence_pack_name|intelligencePackName|

### group `az loganalytics linked-service`
#### <a name="LinkedServicesListByWorkspace">Command `az loganalytics linked-service list`</a>

##### <a name="ExamplesLinkedServicesListByWorkspace">Example</a>
```
az loganalytics linked-service list --resource-group "mms-eus" --workspace-name "TestLinkWS"
```
##### <a name="ParametersLinkedServicesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="LinkedServicesGet">Command `az loganalytics linked-service show`</a>

##### <a name="ExamplesLinkedServicesGet">Example</a>
```
az loganalytics linked-service show --name "Cluster" --resource-group "mms-eus" --workspace-name "TestLinkWS"
```
##### <a name="ParametersLinkedServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--linked-service-name**|string|Name of the linked service.|linked_service_name|linkedServiceName|

#### <a name="LinkedServicesCreateOrUpdate#Create">Command `az loganalytics linked-service create`</a>

##### <a name="ExamplesLinkedServicesCreateOrUpdate#Create">Example</a>
```
az loganalytics linked-service create --name "Cluster" --write-access-resource-id "/subscriptions/00000000-0000-0000-00\
00-00000000000/resourceGroups/mms-eus/providers/Microsoft.OperationalInsights/clusters/testcluster" --resource-group \
"mms-eus" --workspace-name "TestLinkWS"
```
##### <a name="ParametersLinkedServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--linked-service-name**|string|Name of the linkedServices resource|linked_service_name|linkedServiceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--resource-id**|string|The resource id of the resource that will be linked to the workspace. This should be used for linking resources which require read access|resource_id|resourceId|
|**--write-access-resource-id**|string|The resource id of the resource that will be linked to the workspace. This should be used for linking resources which require write access|write_access_resource_id|writeAccessResourceId|
|**--provisioning-state**|choice|The provisioning state of the linked service.|provisioning_state|provisioningState|

#### <a name="LinkedServicesCreateOrUpdate#Update">Command `az loganalytics linked-service update`</a>

##### <a name="ParametersLinkedServicesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--linked-service-name**|string|Name of the linkedServices resource|linked_service_name|linkedServiceName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--resource-id**|string|The resource id of the resource that will be linked to the workspace. This should be used for linking resources which require read access|resource_id|resourceId|
|**--write-access-resource-id**|string|The resource id of the resource that will be linked to the workspace. This should be used for linking resources which require write access|write_access_resource_id|writeAccessResourceId|
|**--provisioning-state**|choice|The provisioning state of the linked service.|provisioning_state|provisioningState|

#### <a name="LinkedServicesDelete">Command `az loganalytics linked-service delete`</a>

##### <a name="ExamplesLinkedServicesDelete">Example</a>
```
az loganalytics linked-service delete --name "Cluster" --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersLinkedServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--linked-service-name**|string|Name of the linked service.|linked_service_name|linkedServiceName|

### group `az loganalytics linked-storage-account`
#### <a name="LinkedStorageAccountsListByWorkspace">Command `az loganalytics linked-storage-account list`</a>

##### <a name="ExamplesLinkedStorageAccountsListByWorkspace">Example</a>
```
az loganalytics linked-storage-account list --resource-group "mms-eus" --workspace-name "testLinkStorageAccountsWS"
```
##### <a name="ParametersLinkedStorageAccountsListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="LinkedStorageAccountsGet">Command `az loganalytics linked-storage-account show`</a>

##### <a name="ExamplesLinkedStorageAccountsGet">Example</a>
```
az loganalytics linked-storage-account show --data-source-type "CustomLogs" --resource-group "mms-eus" \
--workspace-name "testLinkStorageAccountsWS"
```
##### <a name="ParametersLinkedStorageAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-type**|sealed-choice|Linked storage accounts type.|data_source_type|dataSourceType|

#### <a name="LinkedStorageAccountsCreateOrUpdate#Create">Command `az loganalytics linked-storage-account create`</a>

##### <a name="ExamplesLinkedStorageAccountsCreateOrUpdate#Create">Example</a>
```
az loganalytics linked-storage-account create --data-source-type "CustomLogs" --storage-account-ids \
"/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.Storage/storageAccounts/\
testStorageA" "/subscriptions/00000000-0000-0000-0000-00000000000/resourceGroups/mms-eus/providers/Microsoft.Storage/st\
orageAccounts/testStorageB" --resource-group "mms-eus" --workspace-name "testLinkStorageAccountsWS"
```
##### <a name="ParametersLinkedStorageAccountsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-type**|sealed-choice|Linked storage accounts type.|data_source_type|dataSourceType|
|**--storage-account-ids**|array|Linked storage accounts resources ids.|storage_account_ids|storageAccountIds|

#### <a name="LinkedStorageAccountsCreateOrUpdate#Update">Command `az loganalytics linked-storage-account update`</a>

##### <a name="ParametersLinkedStorageAccountsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-type**|sealed-choice|Linked storage accounts type.|data_source_type|dataSourceType|
|**--storage-account-ids**|array|Linked storage accounts resources ids.|storage_account_ids|storageAccountIds|

#### <a name="LinkedStorageAccountsDelete">Command `az loganalytics linked-storage-account delete`</a>

##### <a name="ExamplesLinkedStorageAccountsDelete">Example</a>
```
az loganalytics linked-storage-account delete --data-source-type "CustomLogs" --resource-group "mms-eus" \
--workspace-name "testLinkStorageAccountsWS"
```
##### <a name="ParametersLinkedStorageAccountsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--data-source-type**|sealed-choice|Linked storage accounts type.|data_source_type|dataSourceType|

### group `az loganalytics management-group`
#### <a name="ManagementGroupsList">Command `az loganalytics management-group list`</a>

##### <a name="ExamplesManagementGroupsList">Example</a>
```
az loganalytics management-group list --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersManagementGroupsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### group `az loganalytics operation-statuses`
#### <a name="OperationStatusesGet">Command `az loganalytics operation-statuses show`</a>

##### <a name="ExamplesOperationStatusesGet">Example</a>
```
az loganalytics operation-statuses show --async-operation-id "713192d7-503f-477a-9cfe-4efc3ee2bd11" --location "West \
US"
```
##### <a name="ParametersOperationStatusesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The region name of operation.|location|location|
|**--async-operation-id**|string|The operation Id.|async_operation_id|asyncOperationId|

### group `az loganalytics saved-search`
#### <a name="SavedSearchesListByWorkspace">Command `az loganalytics saved-search list`</a>

##### <a name="ExamplesSavedSearchesListByWorkspace">Example</a>
```
az loganalytics saved-search list --resource-group "TestRG" --workspace-name "TestWS"
```
##### <a name="ParametersSavedSearchesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="SavedSearchesGet">Command `az loganalytics saved-search show`</a>

##### <a name="ExamplesSavedSearchesGet">Example</a>
```
az loganalytics saved-search show --resource-group "TestRG" --saved-search-id "00000000-0000-0000-0000-00000000000" \
--workspace-name "TestWS"
```
##### <a name="ParametersSavedSearchesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--saved-search-id**|string|The id of the saved search.|saved_search_id|savedSearchId|

#### <a name="SavedSearchesCreateOrUpdate#Create">Command `az loganalytics saved-search create`</a>

##### <a name="ExamplesSavedSearchesCreateOrUpdate#Create">Example</a>
```
az loganalytics saved-search create --category "Saved Search Test Category" --display-name "Create or Update Saved \
Search Test" --function-alias "heartbeat_func" --function-parameters "a:int=1" --query "Heartbeat | summarize Count() \
by Computer | take a" --tags name="Group" value="Computer" --version 2 --resource-group "TestRG" --saved-search-id \
"00000000-0000-0000-0000-00000000000" --workspace-name "TestWS"
```
##### <a name="ParametersSavedSearchesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--saved-search-id**|string|The id of the saved search.|saved_search_id|savedSearchId|
|**--category**|string|The category of the saved search. This helps the user to find a saved search faster. |category|category|
|**--display-name**|string|Saved search display name.|display_name|displayName|
|**--query**|string|The query expression for the saved search.|query|query|
|**--etag**|string|The ETag of the saved search.|etag|etag|
|**--function-alias**|string|The function alias if query serves as a function.|function_alias|functionAlias|
|**--function-parameters**|string|The optional function parameters if query serves as a function. Value should be in the following format: 'param-name1:type1 = default_value1, param-name2:type2 = default_value2'. For more examples and proper syntax please refer to https://docs.microsoft.com/en-us/azure/kusto/query/functions/user-defined-functions.|function_parameters|functionParameters|
|**--version**|integer|The version number of the query language. The current version is 2 and is the default.|version|version|
|**--tags**|array|The tags attached to the saved search.|tags|tags|

#### <a name="SavedSearchesCreateOrUpdate#Update">Command `az loganalytics saved-search update`</a>

##### <a name="ParametersSavedSearchesCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--saved-search-id**|string|The id of the saved search.|saved_search_id|savedSearchId|
|**--category**|string|The category of the saved search. This helps the user to find a saved search faster. |category|category|
|**--display-name**|string|Saved search display name.|display_name|displayName|
|**--query**|string|The query expression for the saved search.|query|query|
|**--etag**|string|The ETag of the saved search.|etag|etag|
|**--function-alias**|string|The function alias if query serves as a function.|function_alias|functionAlias|
|**--function-parameters**|string|The optional function parameters if query serves as a function. Value should be in the following format: 'param-name1:type1 = default_value1, param-name2:type2 = default_value2'. For more examples and proper syntax please refer to https://docs.microsoft.com/en-us/azure/kusto/query/functions/user-defined-functions.|function_parameters|functionParameters|
|**--version**|integer|The version number of the query language. The current version is 2 and is the default.|version|version|
|**--tags**|array|The tags attached to the saved search.|tags|tags|

#### <a name="SavedSearchesDelete">Command `az loganalytics saved-search delete`</a>

##### <a name="ExamplesSavedSearchesDelete">Example</a>
```
az loganalytics saved-search delete --resource-group "TestRG" --saved-search-id "00000000-0000-0000-0000-00000000000" \
--workspace-name "TestWS"
```
##### <a name="ParametersSavedSearchesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--saved-search-id**|string|The id of the saved search.|saved_search_id|savedSearchId|

### group `az loganalytics schema`
#### <a name="SchemaGet">Command `az loganalytics schema get`</a>

##### <a name="ExamplesSchemaGet">Example</a>
```
az loganalytics schema get --resource-group "mms-eus" --workspace-name "atlantisdemo"
```
##### <a name="ParametersSchemaGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### group `az loganalytics shared-key`
#### <a name="SharedKeysGetSharedKeys">Command `az loganalytics shared-key get-shared-key`</a>

##### <a name="ExamplesSharedKeysGetSharedKeys">Example</a>
```
az loganalytics shared-key get-shared-key --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersSharedKeysGetSharedKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="SharedKeysRegenerate">Command `az loganalytics shared-key regenerate`</a>

##### <a name="ExamplesSharedKeysRegenerate">Example</a>
```
az loganalytics shared-key regenerate --resource-group "rg1" --workspace-name "workspace1"
```
##### <a name="ParametersSharedKeysRegenerate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### group `az loganalytics storage-insight-config`
#### <a name="StorageInsightConfigsListByWorkspace">Command `az loganalytics storage-insight-config list`</a>

##### <a name="ExamplesStorageInsightConfigsListByWorkspace">Example</a>
```
az loganalytics storage-insight-config list --resource-group "OIAutoRest5123" --workspace-name "aztest5048"
```
##### <a name="ParametersStorageInsightConfigsListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="StorageInsightConfigsGet">Command `az loganalytics storage-insight-config show`</a>

##### <a name="ExamplesStorageInsightConfigsGet">Example</a>
```
az loganalytics storage-insight-config show --resource-group "OIAutoRest5123" --storage-insight-name "AzTestSI1110" \
--workspace-name "aztest5048"
```
##### <a name="ParametersStorageInsightConfigsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--storage-insight-name**|string|Name of the storageInsightsConfigs resource|storage_insight_name|storageInsightName|

#### <a name="StorageInsightConfigsCreateOrUpdate#Create">Command `az loganalytics storage-insight-config create`</a>

##### <a name="ExamplesStorageInsightConfigsCreateOrUpdate#Create">Example</a>
```
az loganalytics storage-insight-config create --containers "wad-iis-logfiles" --storage-account \
id="/subscriptions/00000000-0000-0000-0000-000000000005/resourcegroups/OIAutoRest6987/providers/microsoft.storage/stora\
geaccounts/AzTestFakeSA9945" key="1234" --tables "WADWindowsEventLogsTable" "LinuxSyslogVer2v0" --resource-group \
"OIAutoRest5123" --storage-insight-name "AzTestSI1110" --workspace-name "aztest5048"
```
##### <a name="ParametersStorageInsightConfigsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--storage-insight-name**|string|Name of the storageInsightsConfigs resource|storage_insight_name|storageInsightName|
|**--e-tag**|string|The ETag of the storage insight.|e_tag|eTag|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--containers**|array|The names of the blob containers that the workspace should read|containers|containers|
|**--tables**|array|The names of the Azure tables that the workspace should read|tables|tables|
|**--storage-account**|object|The storage account connection details|storage_account|storageAccount|

#### <a name="StorageInsightConfigsCreateOrUpdate#Update">Command `az loganalytics storage-insight-config update`</a>

##### <a name="ParametersStorageInsightConfigsCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--storage-insight-name**|string|Name of the storageInsightsConfigs resource|storage_insight_name|storageInsightName|
|**--e-tag**|string|The ETag of the storage insight.|e_tag|eTag|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--containers**|array|The names of the blob containers that the workspace should read|containers|containers|
|**--tables**|array|The names of the Azure tables that the workspace should read|tables|tables|
|**--storage-account**|object|The storage account connection details|storage_account|storageAccount|

#### <a name="StorageInsightConfigsDelete">Command `az loganalytics storage-insight-config delete`</a>

##### <a name="ExamplesStorageInsightConfigsDelete">Example</a>
```
az loganalytics storage-insight-config delete --resource-group "OIAutoRest5123" --storage-insight-name "AzTestSI1110" \
--workspace-name "aztest5048"
```
##### <a name="ParametersStorageInsightConfigsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--storage-insight-name**|string|Name of the storageInsightsConfigs resource|storage_insight_name|storageInsightName|

### group `az loganalytics table`
#### <a name="TablesListByWorkspace">Command `az loganalytics table list`</a>

##### <a name="ExamplesTablesListByWorkspace">Example</a>
```
az loganalytics table list --resource-group "oiautorest6685" --workspace-name "oiautorest6685"
```
##### <a name="ParametersTablesListByWorkspace">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="TablesGet">Command `az loganalytics table show`</a>

##### <a name="ExamplesTablesGet">Example</a>
```
az loganalytics table show --resource-group "oiautorest6685" --name "table1" --workspace-name "oiautorest6685"
```
##### <a name="ParametersTablesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--table-name**|string|The name of the table.|table_name|tableName|

#### <a name="TablesUpdate">Command `az loganalytics table update`</a>

##### <a name="ExamplesTablesUpdate">Example</a>
```
az loganalytics table update --retention-in-days 30 --resource-group "oiautorest6685" --name "table1" --workspace-name \
"oiautorest6685"
```
##### <a name="ParametersTablesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--table-name**|string|The name of the table.|table_name|tableName|
|**--retention-in-days**|integer|The data table data retention in days, between 30 and 730. Setting this property to null will default to the workspace retention.|retention_in_days|retentionInDays|

### group `az loganalytics usage`
#### <a name="UsagesList">Command `az loganalytics usage list`</a>

##### <a name="ExamplesUsagesList">Example</a>
```
az loganalytics usage list --resource-group "rg1" --workspace-name "TestLinkWS"
```
##### <a name="ParametersUsagesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

### group `az loganalytics workspace`
#### <a name="WorkspacesListByResourceGroup">Command `az loganalytics workspace list`</a>

##### <a name="ExamplesWorkspacesListByResourceGroup">Example</a>
```
az loganalytics workspace list --resource-group "oiautorest6685"
```
##### <a name="ParametersWorkspacesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="WorkspacesList">Command `az loganalytics workspace list`</a>

##### <a name="ExamplesWorkspacesList">Example</a>
```
az loganalytics workspace list
```
##### <a name="ParametersWorkspacesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="WorkspacesGet">Command `az loganalytics workspace show`</a>

##### <a name="ExamplesWorkspacesGet">Example</a>
```
az loganalytics workspace show --resource-group "oiautorest6685" --name "oiautorest6685"
```
##### <a name="ParametersWorkspacesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|

#### <a name="WorkspacesCreateOrUpdate#Create">Command `az loganalytics workspace create`</a>

##### <a name="ExamplesWorkspacesCreateOrUpdate#Create">Example</a>
```
az loganalytics workspace create --location "australiasoutheast" --retention-in-days 30 --sku name="PerGB2018" --tags \
tag1="val1" --resource-group "oiautorest6685" --name "oiautorest6685"
```
##### <a name="ParametersWorkspacesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--e-tag**|string|The ETag of the workspace.|e_tag|eTag|
|**--provisioning-state**|choice|The provisioning state of the workspace.|provisioning_state|provisioningState|
|**--sku**|object|The SKU of the workspace.|sku|sku|
|**--retention-in-days**|integer|The workspace data retention in days. Allowed values are per pricing plan. See pricing tiers documentation for details.|retention_in_days|retentionInDays|
|**--public-network-access-for-ingestion**|choice|The network access type for accessing Log Analytics ingestion.|public_network_access_for_ingestion|publicNetworkAccessForIngestion|
|**--public-network-access-for-query**|choice|The network access type for accessing Log Analytics query.|public_network_access_for_query|publicNetworkAccessForQuery|
|**--force-cmk-for-query**|boolean|Indicates whether customer managed storage is mandatory for query management.|force_cmk_for_query|forceCmkForQuery|
|**--enable-data-export**|boolean|Flag that indicate if data should be exported.|enable_data_export|enableDataExport|
|**--immediate-purge-data-on30-days**|boolean|Flag that describes if we want to remove the data after 30 days.|immediate_purge_data_on30_days|immediatePurgeDataOn30Days|
|**--enable-log-access-using-only-resource-permissions**|boolean|Flag that indicate which permission to use - resource or workspace or both.|enable_log_access_using_only_resource_permissions|enableLogAccessUsingOnlyResourcePermissions|
|**--cluster-resource-id**|string|Dedicated LA cluster resourceId that is linked to the workspaces.|cluster_resource_id|clusterResourceId|
|**--disable-local-auth**|boolean|Disable Non-AAD based Auth.|disable_local_auth|disableLocalAuth|
|**--daily-quota-gb**|number|The workspace daily quota for ingestion.|daily_quota_gb|dailyQuotaGb|

#### <a name="WorkspacesUpdate">Command `az loganalytics workspace update`</a>

##### <a name="ExamplesWorkspacesUpdate">Example</a>
```
az loganalytics workspace update --retention-in-days 30 --sku name="PerGB2018" --daily-quota-gb -1 --resource-group \
"oiautorest6685" --name "oiautorest6685"
```
##### <a name="ParametersWorkspacesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--tags**|dictionary|Resource tags. Optional.|tags|tags|
|**--provisioning-state**|choice|The provisioning state of the workspace.|provisioning_state|provisioningState|
|**--sku**|object|The SKU of the workspace.|sku|sku|
|**--retention-in-days**|integer|The workspace data retention in days. Allowed values are per pricing plan. See pricing tiers documentation for details.|retention_in_days|retentionInDays|
|**--public-network-access-for-ingestion**|choice|The network access type for accessing Log Analytics ingestion.|public_network_access_for_ingestion|publicNetworkAccessForIngestion|
|**--public-network-access-for-query**|choice|The network access type for accessing Log Analytics query.|public_network_access_for_query|publicNetworkAccessForQuery|
|**--force-cmk-for-query**|boolean|Indicates whether customer managed storage is mandatory for query management.|force_cmk_for_query|forceCmkForQuery|
|**--enable-data-export**|boolean|Flag that indicate if data should be exported.|enable_data_export|enableDataExport|
|**--immediate-purge-data-on30-days**|boolean|Flag that describes if we want to remove the data after 30 days.|immediate_purge_data_on30_days|immediatePurgeDataOn30Days|
|**--enable-log-access-using-only-resource-permissions**|boolean|Flag that indicate which permission to use - resource or workspace or both.|enable_log_access_using_only_resource_permissions|enableLogAccessUsingOnlyResourcePermissions|
|**--cluster-resource-id**|string|Dedicated LA cluster resourceId that is linked to the workspaces.|cluster_resource_id|clusterResourceId|
|**--disable-local-auth**|boolean|Disable Non-AAD based Auth.|disable_local_auth|disableLocalAuth|
|**--daily-quota-gb**|number|The workspace daily quota for ingestion.|daily_quota_gb|dailyQuotaGb|

#### <a name="WorkspacesDelete">Command `az loganalytics workspace delete`</a>

##### <a name="ExamplesWorkspacesDelete">Example</a>
```
az loganalytics workspace delete --resource-group "oiautorest6685" --name "oiautorest6685"
```
##### <a name="ParametersWorkspacesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--force**|boolean|Deletes the workspace without the recovery option. A workspace that was deleted with this flag cannot be recovered.|force|force|

### group `az loganalytics workspace-purge`
#### <a name="WorkspacePurgePurge">Command `az loganalytics workspace-purge purge`</a>

##### <a name="ExamplesWorkspacePurgePurge">Example</a>
```
az loganalytics workspace-purge purge --filters "[{\\"column\\":\\"TimeGenerated\\",\\"operator\\":\\">\\",\\"value\\":\
\\"2017-09-01T00:00:00\\"}]" --table "Heartbeat" --resource-group "OIAutoRest5123" --workspace-name "aztest5048"
```
##### <a name="ParametersWorkspacePurgePurge">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--table**|string|Table from which to purge data.|table|table|
|**--filters**|array|The set of columns and filters (queries) to run over them to purge the resulting data.|filters|filters|

#### <a name="WorkspacePurgeGetPurgeStatus">Command `az loganalytics workspace-purge show-purge-status`</a>

##### <a name="ExamplesWorkspacePurgeGetPurgeStatus">Example</a>
```
az loganalytics workspace-purge show-purge-status --purge-id "purge-970318e7-b859-4edb-8903-83b1b54d0b74" \
--resource-group "OIAutoRest5123" --workspace-name "aztest5048"
```
##### <a name="ParametersWorkspacePurgeGetPurgeStatus">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--workspace-name**|string|The name of the workspace.|workspace_name|workspaceName|
|**--purge-id**|string|In a purge status request, this is the Id of the operation the status of which is returned.|purge_id|purgeId|
