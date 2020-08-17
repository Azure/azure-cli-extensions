# Azure CLI Module Creation Report

### kusto attached-database-configuration create

create a kusto attached-database-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|
|**--location**|string|Resource location.|location|
|**--database-name**|string|The name of the database which you would like to attach, use * if you want to follow all current and future databases.|database_name|
|**--cluster-resource-id**|string|The resource id of the cluster where the databases you would like to attach reside.|cluster_resource_id|
|**--default-principals-modification-kind**|choice|The default principals modification kind|default_principals_modification_kind|
### kusto attached-database-configuration delete

delete a kusto attached-database-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|
### kusto attached-database-configuration list

list a kusto attached-database-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto attached-database-configuration show

show a kusto attached-database-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|
### kusto attached-database-configuration update

create a kusto attached-database-configuration.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--attached-database-configuration-name**|string|The name of the attached database configuration.|attached_database_configuration_name|
|**--location**|string|Resource location.|location|
|**--database-name**|string|The name of the database which you would like to attach, use * if you want to follow all current and future databases.|database_name|
|**--cluster-resource-id**|string|The resource id of the cluster where the databases you would like to attach reside.|cluster_resource_id|
|**--default-principals-modification-kind**|choice|The default principals modification kind|default_principals_modification_kind|
### kusto cluster add-language-extension

add-language-extension a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--value**|array|The list of language extensions.|value|
### kusto cluster create

create a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--location**|string|The geo-location where the resource lives|location|
|**--sku**|object|The SKU of the cluster.|sku|
|**--tags**|dictionary|Resource tags.|tags|
|**--zones**|array|The availability zones of the cluster.|zones|
|**--trusted-external-tenants**|array|The cluster's external tenants.|trusted_external_tenants|
|**--optimized-autoscale**|object|Optimized auto scale definition.|optimized_autoscale|
|**--enable-disk-encryption**|boolean|A boolean value that indicates if the cluster's disks are encrypted.|enable_disk_encryption|
|**--enable-streaming-ingest**|boolean|A boolean value that indicates if the streaming ingest is enabled.|enable_streaming_ingest|
|**--virtual-network-configuration**|object|Virtual network definition.|virtual_network_configuration|
|**--key-vault-properties**|object|KeyVault properties for the cluster encryption.|key_vault_properties|
|**--enable-purge**|boolean|A boolean value that indicates if the purge operations are enabled.|enable_purge|
|**--enable-double-encryption**|boolean|A boolean value that indicates if double encryption is enabled.|enable_double_encryption|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with the Kusto cluster. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
### kusto cluster delete

delete a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster detach-follower-database

detach-follower-database a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--cluster-resource-id**|string|Resource id of the cluster that follows a database owned by this cluster.|cluster_resource_id|
|**--attached-database-configuration-name**|string|Resource name of the attached database configuration in the follower cluster.|attached_database_configuration_name|
### kusto cluster diagnose-virtual-network

diagnose-virtual-network a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster list

list a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
### kusto cluster list-follower-database

list-follower-database a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster list-language-extension

list-language-extension a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster list-sku

list-sku a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster remove-language-extension

remove-language-extension a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--value**|array|The list of language extensions.|value|
### kusto cluster show

show a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster start

start a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster stop

stop a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster update

update a kusto cluster.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--tags**|dictionary|Resource tags.|tags|
|**--location**|string|Resource location.|location|
|**--sku**|object|The SKU of the cluster.|sku|
|**--trusted-external-tenants**|array|The cluster's external tenants.|trusted_external_tenants|
|**--optimized-autoscale**|object|Optimized auto scale definition.|optimized_autoscale|
|**--enable-disk-encryption**|boolean|A boolean value that indicates if the cluster's disks are encrypted.|enable_disk_encryption|
|**--enable-streaming-ingest**|boolean|A boolean value that indicates if the streaming ingest is enabled.|enable_streaming_ingest|
|**--virtual-network-configuration**|object|Virtual network definition.|virtual_network_configuration|
|**--key-vault-properties**|object|KeyVault properties for the cluster encryption.|key_vault_properties|
|**--enable-purge**|boolean|A boolean value that indicates if the purge operations are enabled.|enable_purge|
|**--enable-double-encryption**|boolean|A boolean value that indicates if double encryption is enabled.|enable_double_encryption|
|**--identity-type**|sealed-choice|The identity type.|type_identity_type|
|**--identity-user-assigned-identities**|dictionary|The list of user identities associated with the Kusto cluster. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}'.|user_assigned_identities|
### kusto cluster-principal-assignment create

create a kusto cluster-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
|**--principal-id**|string|The principal ID assigned to the cluster principal. It can be a user email, application ID, or security group name.|principal_id|
|**--role**|choice|Cluster principal role.|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|
|**--principal-type**|choice|Principal type.|principal_type|
### kusto cluster-principal-assignment delete

delete a kusto cluster-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
### kusto cluster-principal-assignment list

list a kusto cluster-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto cluster-principal-assignment show

show a kusto cluster-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
### kusto cluster-principal-assignment update

create a kusto cluster-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
|**--principal-id**|string|The principal ID assigned to the cluster principal. It can be a user email, application ID, or security group name.|principal_id|
|**--role**|choice|Cluster principal role.|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|
|**--principal-type**|choice|Principal type.|principal_type|
### kusto data-connection delete

delete a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
### kusto data-connection event-grid create

event-grid create a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|event_grid_location|
|**--storage-account-resource-id**|string|The resource ID of the storage account where the data resides.|event_grid_storage_account_resource_id|
|**--event-hub-resource-id**|string|The resource ID where the event grid is configured to send events.|event_grid_event_hub_resource_id|
|**--consumer-group**|string|The event hub consumer group.|event_grid_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_grid_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_grid_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_grid_data_format|
|**--ignore-first-record**|boolean|A Boolean value that, if set to true, indicates that ingestion should ignore the first record of every file|event_grid_ignore_first_record|
|**--blob-storage-event-type**|choice|The name of blob storage event type to process.|event_grid_blob_storage_event_type|
### kusto data-connection event-grid data-connection-validation

event-grid data-connection-validation a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|event_grid_location|
|**--storage-account-resource-id**|string|The resource ID of the storage account where the data resides.|event_grid_storage_account_resource_id|
|**--event-hub-resource-id**|string|The resource ID where the event grid is configured to send events.|event_grid_event_hub_resource_id|
|**--consumer-group**|string|The event hub consumer group.|event_grid_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_grid_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_grid_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_grid_data_format|
|**--ignore-first-record**|boolean|A Boolean value that, if set to true, indicates that ingestion should ignore the first record of every file|event_grid_ignore_first_record|
|**--blob-storage-event-type**|choice|The name of blob storage event type to process.|event_grid_blob_storage_event_type|
### kusto data-connection event-grid update

event-grid update a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|event_grid_location|
|**--storage-account-resource-id**|string|The resource ID of the storage account where the data resides.|event_grid_storage_account_resource_id|
|**--event-hub-resource-id**|string|The resource ID where the event grid is configured to send events.|event_grid_event_hub_resource_id|
|**--consumer-group**|string|The event hub consumer group.|event_grid_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_grid_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_grid_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_grid_data_format|
|**--ignore-first-record**|boolean|A Boolean value that, if set to true, indicates that ingestion should ignore the first record of every file|event_grid_ignore_first_record|
|**--blob-storage-event-type**|choice|The name of blob storage event type to process.|event_grid_blob_storage_event_type|
### kusto data-connection event-hub create

event-hub create a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|event_hub_location|
|**--event-hub-resource-id**|string|The resource ID of the event hub to be used to create a data connection.|event_hub_event_hub_resource_id|
|**--consumer-group**|string|The event hub consumer group.|event_hub_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_hub_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_hub_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_hub_data_format|
|**--event-system-properties**|array|System properties of the event hub|event_hub_event_system_properties|
|**--compression**|choice|The event hub messages compression type|event_hub_compression|
### kusto data-connection event-hub data-connection-validation

event-hub data-connection-validation a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|event_hub_location|
|**--event-hub-resource-id**|string|The resource ID of the event hub to be used to create a data connection.|event_hub_event_hub_resource_id|
|**--consumer-group**|string|The event hub consumer group.|event_hub_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_hub_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_hub_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_hub_data_format|
|**--event-system-properties**|array|System properties of the event hub|event_hub_event_system_properties|
|**--compression**|choice|The event hub messages compression type|event_hub_compression|
### kusto data-connection event-hub update

event-hub update a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|event_hub_location|
|**--event-hub-resource-id**|string|The resource ID of the event hub to be used to create a data connection.|event_hub_event_hub_resource_id|
|**--consumer-group**|string|The event hub consumer group.|event_hub_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|event_hub_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|event_hub_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|event_hub_data_format|
|**--event-system-properties**|array|System properties of the event hub|event_hub_event_system_properties|
|**--compression**|choice|The event hub messages compression type|event_hub_compression|
### kusto data-connection iot-hub create

iot-hub create a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|iot_hub_location|
|**--iot-hub-resource-id**|string|The resource ID of the Iot hub to be used to create a data connection.|iot_hub_iot_hub_resource_id|
|**--consumer-group**|string|The iot hub consumer group.|iot_hub_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|iot_hub_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|iot_hub_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|iot_hub_data_format|
|**--event-system-properties**|array|System properties of the iot hub|iot_hub_event_system_properties|
|**--shared-access-policy-name**|string|The name of the share access policy|iot_hub_shared_access_policy_name|
### kusto data-connection iot-hub data-connection-validation

iot-hub data-connection-validation a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|iot_hub_location|
|**--iot-hub-resource-id**|string|The resource ID of the Iot hub to be used to create a data connection.|iot_hub_iot_hub_resource_id|
|**--consumer-group**|string|The iot hub consumer group.|iot_hub_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|iot_hub_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|iot_hub_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|iot_hub_data_format|
|**--event-system-properties**|array|System properties of the iot hub|iot_hub_event_system_properties|
|**--shared-access-policy-name**|string|The name of the share access policy|iot_hub_shared_access_policy_name|
### kusto data-connection iot-hub update

iot-hub update a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
|**--location**|string|Resource location.|iot_hub_location|
|**--iot-hub-resource-id**|string|The resource ID of the Iot hub to be used to create a data connection.|iot_hub_iot_hub_resource_id|
|**--consumer-group**|string|The iot hub consumer group.|iot_hub_consumer_group|
|**--table-name**|string|The table where the data should be ingested. Optionally the table information can be added to each message.|iot_hub_table_name|
|**--mapping-rule-name**|string|The mapping rule to be used to ingest the data. Optionally the mapping information can be added to each message.|iot_hub_mapping_rule_name|
|**--data-format**|choice|The data format of the message. Optionally the data format can be added to each message.|iot_hub_data_format|
|**--event-system-properties**|array|System properties of the iot hub|iot_hub_event_system_properties|
|**--shared-access-policy-name**|string|The name of the share access policy|iot_hub_shared_access_policy_name|
### kusto data-connection list

list a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
### kusto data-connection show

show a kusto data-connection.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--data-connection-name**|string|The name of the data connection.|data_connection_name|
### kusto database add-principal

add-principal a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--value**|array|The list of Kusto database principals.|value|
### kusto database create

create a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--read-write-database**|object|Class representing a read write database.|read_write_database|
|**--read-only-following-database**|object|Class representing a read only following database.|read_only_following_database|
### kusto database delete

delete a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
### kusto database list

list a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
### kusto database list-principal

list-principal a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
### kusto database remove-principal

remove-principal a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--value**|array|The list of Kusto database principals.|value|
### kusto database show

show a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
### kusto database update

update a kusto database.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--read-write-database**|object|Class representing a read write database.|read_write_database|
|**--read-only-following-database**|object|Class representing a read only following database.|read_only_following_database|
### kusto database-principal-assignment create

create a kusto database-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
|**--principal-id**|string|The principal ID assigned to the database principal. It can be a user email, application ID, or security group name.|principal_id|
|**--role**|choice|Database principal role.|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|
|**--principal-type**|choice|Principal type.|principal_type|
### kusto database-principal-assignment delete

delete a kusto database-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
### kusto database-principal-assignment list

list a kusto database-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
### kusto database-principal-assignment show

show a kusto database-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
### kusto database-principal-assignment update

create a kusto database-principal-assignment.

|Option|Type|Description|Path (SDK)|Path (swagger)|
|------|----|-----------|----------|--------------|
|**--resource-group-name**|string|The name of the resource group containing the Kusto cluster.|resource_group_name|
|**--cluster-name**|string|The name of the Kusto cluster.|cluster_name|
|**--database-name**|string|The name of the database in the Kusto cluster.|database_name|
|**--principal-assignment-name**|string|The name of the Kusto principalAssignment.|principal_assignment_name|
|**--principal-id**|string|The principal ID assigned to the database principal. It can be a user email, application ID, or security group name.|principal_id|
|**--role**|choice|Database principal role.|role|
|**--tenant-id**|string|The tenant id of the principal|tenant_id|
|**--principal-type**|choice|Principal type.|principal_type|