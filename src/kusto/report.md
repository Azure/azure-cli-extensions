# Azure CLI Module Creation Report

### kusto attached-database-configuration create

create a kusto attached-database-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto attached-database-configuration|AttachedDatabaseConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|attachedDatabaseConfigurationName|
|**--location**|string|Resource location.|location|location|
|**--database-name**|string|The name of the database which you would like to attach, use * if you want to follow all current and future databases.|database_name|databaseName|
|**--cluster-resource-id**|string|The resource id of the cluster where the databases you would like to attach reside.|cluster_resource_id|clusterResourceId|
|**--default-principals-modification-kind**|choice|The default principals modification kind|default_principals_modification_kind|defaultPrincipalsModificationKind|

### kusto attached-database-configuration delete

delete a kusto attached-database-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto attached-database-configuration|AttachedDatabaseConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|attachedDatabaseConfigurationName|

### kusto attached-database-configuration list

list a kusto attached-database-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto attached-database-configuration|AttachedDatabaseConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByCluster|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto attached-database-configuration show

show a kusto attached-database-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto attached-database-configuration|AttachedDatabaseConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|attachedDatabaseConfigurationName|

### kusto attached-database-configuration update

update a kusto attached-database-configuration.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto attached-database-configuration|AttachedDatabaseConfigurations|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|attachedDatabaseConfigurationName|
|**--location**|string|Resource location.|location|location|
|**--database-name**|string|The name of the database which you would like to attach, use * if you want to follow all current and future databases.|database_name|databaseName|
|**--cluster-resource-id**|string|The resource id of the cluster where the databases you would like to attach reside.|cluster_resource_id|clusterResourceId|
|**--default-principals-modification-kind**|choice|The default principals modification kind|default_principals_modification_kind|defaultPrincipalsModificationKind|

### kusto cluster add-language-extension

add-language-extension a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|add-language-extension|AddLanguageExtensions|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--value**|array|The list of language extensions.|value|value|

### kusto cluster create

create a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--sku**|object|The SKU of the cluster.|sku|sku|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--zones**|array|The availability zones of the cluster.|zones|zones|
|**--trusted-external-tenants**|array|The cluster's external tenants.|trusted_external_tenants|trustedExternalTenants|
|**--optimized-autoscale**|object|Optimized auto scale definition.|optimized_autoscale|optimizedAutoscale|
|**--enable-disk-encryption**|boolean|A boolean value that indicates if the cluster's disks are encrypted.|enable_disk_encryption|enableDiskEncryption|
|**--enable-streaming-ingest**|boolean|A boolean value that indicates if the streaming ingest is enabled.|enable_streaming_ingest|enableStreamingIngest|
|**--virtual-network-configuration**|object|Virtual network definition.|virtual_network_configuration|virtualNetworkConfiguration|
|**--key-vault-properties**|object|KeyVault properties for the cluster encryption.|key_vault_properties|keyVaultProperties|
|**--enable-purge**|boolean|A boolean value that indicates if the purge operations are enabled.|enable_purge|enablePurge|
|**--enable-double-encryption**|boolean|A boolean value that indicates if double encryption is enabled.|enable_double_encryption|enableDoubleEncryption|
|**--engine-type**|choice|The engine type|engine_type|engineType|
|**--identity-type**|choice|The type of managed identity used. The type 'SystemAssigned, UserAssigned' includes both an implicitly created identity and a set of user-assigned identities. The type 'None' will remove all identities.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with the Kusto cluster. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|

### kusto cluster delete

delete a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster detach-follower-database

detach-follower-database a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|detach-follower-database|DetachFollowerDatabases|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--cluster-resource-id**|string|Resource id of the cluster that follows a database owned by this cluster.|cluster_resource_id|clusterResourceId|
|**--attached-database-configuration-name**|string|Resource name of the attached database configuration in the follower cluster.|attached_database_configuration_name|attachedDatabaseConfigurationName|

### kusto cluster diagnose-virtual-network

diagnose-virtual-network a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|diagnose-virtual-network|DiagnoseVirtualNetwork|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster list

list a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|

### kusto cluster list-follower-database

list-follower-database a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-follower-database|ListFollowerDatabases|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster list-language-extension

list-language-extension a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-language-extension|ListLanguageExtensions|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster list-sku

list-sku a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-sku|ListSkusByResource|
|list-sku|ListSkus|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster remove-language-extension

remove-language-extension a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|remove-language-extension|RemoveLanguageExtensions|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--value**|array|The list of language extensions.|value|value|

### kusto cluster show

show a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster start

start a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|start|Start|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster stop

stop a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|stop|Stop|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster update

update a kusto cluster.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster|Clusters|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|Resource location.|location|location|
|**--sku**|object|The SKU of the cluster.|sku|sku|
|**--trusted-external-tenants**|array|The cluster's external tenants.|trusted_external_tenants|trustedExternalTenants|
|**--optimized-autoscale**|object|Optimized auto scale definition.|optimized_autoscale|optimizedAutoscale|
|**--enable-disk-encryption**|boolean|A boolean value that indicates if the cluster's disks are encrypted.|enable_disk_encryption|enableDiskEncryption|
|**--enable-streaming-ingest**|boolean|A boolean value that indicates if the streaming ingest is enabled.|enable_streaming_ingest|enableStreamingIngest|
|**--virtual-network-configuration**|object|Virtual network definition.|virtual_network_configuration|virtualNetworkConfiguration|
|**--key-vault-properties**|object|KeyVault properties for the cluster encryption.|key_vault_properties|keyVaultProperties|
|**--enable-purge**|boolean|A boolean value that indicates if the purge operations are enabled.|enable_purge|enablePurge|
|**--enable-double-encryption**|boolean|A boolean value that indicates if double encryption is enabled.|enable_double_encryption|enableDoubleEncryption|
|**--engine-type**|choice|The engine type|engine_type|engineType|
|**--identity-type**|choice|The type of managed identity used. The type 'SystemAssigned, UserAssigned' includes both an implicitly created identity and a set of user-assigned identities. The type 'None' will remove all identities.|type|type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with the Kusto cluster. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|userAssignedIdentities|

### kusto cluster-principal-assignment create

create a kusto cluster-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster-principal-assignment|ClusterPrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|
|**--principal-id**|string|The principal ID assigned to the cluster principal. It can be a user email, application ID, or security group name.|principal_id|principalId|
|**--role**|choice|Cluster principal role.|role|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|tenantId|
|**--principal-type**|choice|Principal type.|principal_type|principalType|

### kusto cluster-principal-assignment delete

delete a kusto cluster-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster-principal-assignment|ClusterPrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|

### kusto cluster-principal-assignment list

list a kusto cluster-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster-principal-assignment|ClusterPrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto cluster-principal-assignment show

show a kusto cluster-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster-principal-assignment|ClusterPrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|

### kusto cluster-principal-assignment update

update a kusto cluster-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto cluster-principal-assignment|ClusterPrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|
|**--principal-id**|string|The principal ID assigned to the cluster principal. It can be a user email, application ID, or security group name.|principal_id|principalId|
|**--role**|choice|Cluster principal role.|role|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|tenantId|
|**--principal-type**|choice|Principal type.|principal_type|principalType|

### kusto data-connection delete

delete a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|

### kusto data-connection event-grid create

event-grid create a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|event-grid create|CreateOrUpdate#Create#EventGrid|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|event_grid_location|location|
|**--storage-account-resource-id**|string|The resource ID of the storage account where the data resides.|event_grid_storage_account_resource_id|storageAccountResourceId|
|**--event-hub-resource-id**|string|The resource ID where the event grid is configured to send events.|event_grid_event_hub_resource_id|eventHubResourceId|
|**--consumer-group**|string|The event hub consumer group.|event_grid_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_grid_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_grid_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_grid_data_format|dataFormat|
|**--ignore-first-record**|boolean|A Boolean value that, if set to true, indicates that ingestion should ignore the first record of every file|event_grid_ignore_first_record|ignoreFirstRecord|
|**--blob-storage-event-type**|choice|The name of blob storage event type to process.|event_grid_blob_storage_event_type|blobStorageEventType|

### kusto data-connection event-grid data-connection-validation

event-grid data-connection-validation a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|event-grid data-connection-validation|dataConnectionValidation#EventGrid|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|event_grid_location|location|
|**--storage-account-resource-id**|string|The resource ID of the storage account where the data resides.|event_grid_storage_account_resource_id|storageAccountResourceId|
|**--event-hub-resource-id**|string|The resource ID where the event grid is configured to send events.|event_grid_event_hub_resource_id|eventHubResourceId|
|**--consumer-group**|string|The event hub consumer group.|event_grid_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_grid_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_grid_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_grid_data_format|dataFormat|
|**--ignore-first-record**|boolean|A Boolean value that, if set to true, indicates that ingestion should ignore the first record of every file|event_grid_ignore_first_record|ignoreFirstRecord|
|**--blob-storage-event-type**|choice|The name of blob storage event type to process.|event_grid_blob_storage_event_type|blobStorageEventType|

### kusto data-connection event-grid update

event-grid update a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|event-grid update|Update#EventGrid|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|event_grid_location|location|
|**--storage-account-resource-id**|string|The resource ID of the storage account where the data resides.|event_grid_storage_account_resource_id|storageAccountResourceId|
|**--event-hub-resource-id**|string|The resource ID where the event grid is configured to send events.|event_grid_event_hub_resource_id|eventHubResourceId|
|**--consumer-group**|string|The event hub consumer group.|event_grid_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_grid_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_grid_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_grid_data_format|dataFormat|
|**--ignore-first-record**|boolean|A Boolean value that, if set to true, indicates that ingestion should ignore the first record of every file|event_grid_ignore_first_record|ignoreFirstRecord|
|**--blob-storage-event-type**|choice|The name of blob storage event type to process.|event_grid_blob_storage_event_type|blobStorageEventType|

### kusto data-connection event-hub create

event-hub create a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|event-hub create|CreateOrUpdate#Create#EventHub|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|event_hub_location|location|
|**--event-hub-resource-id**|string|The resource ID of the event hub to be used to create a data connection.|event_hub_event_hub_resource_id|eventHubResourceId|
|**--consumer-group**|string|The event hub consumer group.|event_hub_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_hub_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_hub_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_hub_data_format|dataFormat|
|**--event-system-properties**|array|System properties of the event hub|event_hub_event_system_properties|eventSystemProperties|
|**--compression**|choice|The event hub messages compression type|event_hub_compression|compression|

### kusto data-connection event-hub data-connection-validation

event-hub data-connection-validation a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|event-hub data-connection-validation|dataConnectionValidation#EventHub|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|event_hub_location|location|
|**--event-hub-resource-id**|string|The resource ID of the event hub to be used to create a data connection.|event_hub_event_hub_resource_id|eventHubResourceId|
|**--consumer-group**|string|The event hub consumer group.|event_hub_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_hub_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_hub_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_hub_data_format|dataFormat|
|**--event-system-properties**|array|System properties of the event hub|event_hub_event_system_properties|eventSystemProperties|
|**--compression**|choice|The event hub messages compression type|event_hub_compression|compression|

### kusto data-connection event-hub update

event-hub update a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|event-hub update|Update#EventHub|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|event_hub_location|location|
|**--event-hub-resource-id**|string|The resource ID of the event hub to be used to create a data connection.|event_hub_event_hub_resource_id|eventHubResourceId|
|**--consumer-group**|string|The event hub consumer group.|event_hub_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_hub_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_hub_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_hub_data_format|dataFormat|
|**--event-system-properties**|array|System properties of the event hub|event_hub_event_system_properties|eventSystemProperties|
|**--compression**|choice|The event hub messages compression type|event_hub_compression|compression|

### kusto data-connection iot-hub create

iot-hub create a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|iot-hub create|CreateOrUpdate#Create#IotHub|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|iot_hub_location|location|
|**--iot-hub-resource-id**|string|The resource ID of the Iot hub to be used to create a data connection.|iot_hub_iot_hub_resource_id|iotHubResourceId|
|**--consumer-group**|string|The iot hub consumer group.|iot_hub_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|iot_hub_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|iot_hub_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|iot_hub_data_format|dataFormat|
|**--event-system-properties**|array|System properties of the iot hub|iot_hub_event_system_properties|eventSystemProperties|
|**--shared-access-policy-name**|string|The name of the share access policy|iot_hub_shared_access_policy_name|sharedAccessPolicyName|

### kusto data-connection iot-hub data-connection-validation

iot-hub data-connection-validation a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|iot-hub data-connection-validation|dataConnectionValidation#IotHub|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|iot_hub_location|location|
|**--iot-hub-resource-id**|string|The resource ID of the Iot hub to be used to create a data connection.|iot_hub_iot_hub_resource_id|iotHubResourceId|
|**--consumer-group**|string|The iot hub consumer group.|iot_hub_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|iot_hub_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|iot_hub_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|iot_hub_data_format|dataFormat|
|**--event-system-properties**|array|System properties of the iot hub|iot_hub_event_system_properties|eventSystemProperties|
|**--shared-access-policy-name**|string|The name of the share access policy|iot_hub_shared_access_policy_name|sharedAccessPolicyName|

### kusto data-connection iot-hub update

iot-hub update a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|iot-hub update|Update#IotHub|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|
|**--location**|string|Resource location.|iot_hub_location|location|
|**--iot-hub-resource-id**|string|The resource ID of the Iot hub to be used to create a data connection.|iot_hub_iot_hub_resource_id|iotHubResourceId|
|**--consumer-group**|string|The iot hub consumer group.|iot_hub_consumer_group|consumerGroup|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|iot_hub_table_name|tableName|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|iot_hub_mapping_rule_name|mappingRuleName|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|iot_hub_data_format|dataFormat|
|**--event-system-properties**|array|System properties of the iot hub|iot_hub_event_system_properties|eventSystemProperties|
|**--shared-access-policy-name**|string|The name of the share access policy|iot_hub_shared_access_policy_name|sharedAccessPolicyName|

### kusto data-connection list

list a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByDatabase|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|

### kusto data-connection show

show a kusto data-connection.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto data-connection|DataConnections|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|dataConnectionName|

### kusto database add-principal

add-principal a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|add-principal|AddPrincipals|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--value**|array|The list of Kusto database principals.|value|value|

### kusto database create

create a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--read-write-database**|object|Class representing a read write database.|read_write_database|ReadWriteDatabase|
|**--read-only-following-database**|object|Class representing a read only following database.|read_only_following_database|ReadOnlyFollowingDatabase|

### kusto database delete

delete a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|

### kusto database list

list a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByCluster|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|

### kusto database list-principal

list-principal a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list-principal|ListPrincipals|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|

### kusto database remove-principal

remove-principal a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|remove-principal|RemovePrincipals|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--value**|array|The list of Kusto database principals.|value|value|

### kusto database show

show a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|

### kusto database update

update a kusto database.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database|Databases|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--read-write-database**|object|Class representing a read write database.|read_write_database|ReadWriteDatabase|
|**--read-only-following-database**|object|Class representing a read only following database.|read_only_following_database|ReadOnlyFollowingDatabase|

### kusto database-principal-assignment create

create a kusto database-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database-principal-assignment|DatabasePrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|
|**--principal-id**|string|The principal ID assigned to the database principal. It can be a user email, application ID, or security group name.|principal_id|principalId|
|**--role**|choice|Database principal role.|role|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|tenantId|
|**--principal-type**|choice|Principal type.|principal_type|principalType|

### kusto database-principal-assignment delete

delete a kusto database-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database-principal-assignment|DatabasePrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|

### kusto database-principal-assignment list

list a kusto database-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database-principal-assignment|DatabasePrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|

### kusto database-principal-assignment show

show a kusto database-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database-principal-assignment|DatabasePrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|

### kusto database-principal-assignment update

update a kusto database-principal-assignment.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|kusto database-principal-assignment|DatabasePrincipalAssignments|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|CreateOrUpdate#Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|databaseName|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|principalAssignmentName|
|**--principal-id**|string|The principal ID assigned to the database principal. It can be a user email, application ID, or security group name.|principal_id|principalId|
|**--role**|choice|Database principal role.|role|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|tenantId|
|**--principal-type**|choice|Principal type.|principal_type|principalType|
