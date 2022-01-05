# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az datamigration|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az datamigration` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az datamigration sql-service|SqlMigrationServices|[commands](#CommandsInSqlMigrationServices)|
|az datamigration to-sql-managed-instance|DatabaseMigrationsSqlMi|[commands](#CommandsInDatabaseMigrationsSqlMi)|
|az datamigration to-sql-vm|DatabaseMigrationsSqlVm|[commands](#CommandsInDatabaseMigrationsSqlVm)|

## COMMANDS
### <a name="CommandsInSqlMigrationServices">Commands in `az datamigration sql-service` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datamigration sql-service list](#SqlMigrationServicesListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersSqlMigrationServicesListByResourceGroup)|[Example](#ExamplesSqlMigrationServicesListByResourceGroup)|
|[az datamigration sql-service list](#SqlMigrationServicesListBySubscription)|ListBySubscription|[Parameters](#ParametersSqlMigrationServicesListBySubscription)|[Example](#ExamplesSqlMigrationServicesListBySubscription)|
|[az datamigration sql-service show](#SqlMigrationServicesGet)|Get|[Parameters](#ParametersSqlMigrationServicesGet)|[Example](#ExamplesSqlMigrationServicesGet)|
|[az datamigration sql-service create](#SqlMigrationServicesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersSqlMigrationServicesCreateOrUpdate#Create)|[Example](#ExamplesSqlMigrationServicesCreateOrUpdate#Create)|
|[az datamigration sql-service update](#SqlMigrationServicesUpdate)|Update|[Parameters](#ParametersSqlMigrationServicesUpdate)|[Example](#ExamplesSqlMigrationServicesUpdate)|
|[az datamigration sql-service delete](#SqlMigrationServicesDelete)|Delete|[Parameters](#ParametersSqlMigrationServicesDelete)|[Example](#ExamplesSqlMigrationServicesDelete)|
|[az datamigration sql-service delete-node](#SqlMigrationServicesdeleteNode)|deleteNode|[Parameters](#ParametersSqlMigrationServicesdeleteNode)|[Example](#ExamplesSqlMigrationServicesdeleteNode)|
|[az datamigration sql-service list-auth-key](#SqlMigrationServiceslistAuthKeys)|listAuthKeys|[Parameters](#ParametersSqlMigrationServiceslistAuthKeys)|[Example](#ExamplesSqlMigrationServiceslistAuthKeys)|
|[az datamigration sql-service list-integration-runtime-metric](#SqlMigrationServiceslistMonitoringData)|listMonitoringData|[Parameters](#ParametersSqlMigrationServiceslistMonitoringData)|[Example](#ExamplesSqlMigrationServiceslistMonitoringData)|
|[az datamigration sql-service list-migration](#SqlMigrationServiceslistMigrations)|listMigrations|[Parameters](#ParametersSqlMigrationServiceslistMigrations)|[Example](#ExamplesSqlMigrationServiceslistMigrations)|
|[az datamigration sql-service regenerate-auth-key](#SqlMigrationServicesregenerateAuthKeys)|regenerateAuthKeys|[Parameters](#ParametersSqlMigrationServicesregenerateAuthKeys)|[Example](#ExamplesSqlMigrationServicesregenerateAuthKeys)|

### <a name="CommandsInDatabaseMigrationsSqlMi">Commands in `az datamigration to-sql-managed-instance` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datamigration to-sql-managed-instance show](#DatabaseMigrationsSqlMiGet)|Get|[Parameters](#ParametersDatabaseMigrationsSqlMiGet)|[Example](#ExamplesDatabaseMigrationsSqlMiGet)|
|[az datamigration to-sql-managed-instance create](#DatabaseMigrationsSqlMiCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDatabaseMigrationsSqlMiCreateOrUpdate#Create)|[Example](#ExamplesDatabaseMigrationsSqlMiCreateOrUpdate#Create)|
|[az datamigration to-sql-managed-instance update](#DatabaseMigrationsSqlMiCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersDatabaseMigrationsSqlMiCreateOrUpdate#Update)|Not Found|
|[az datamigration to-sql-managed-instance cancel](#DatabaseMigrationsSqlMicancel)|cancel|[Parameters](#ParametersDatabaseMigrationsSqlMicancel)|[Example](#ExamplesDatabaseMigrationsSqlMicancel)|
|[az datamigration to-sql-managed-instance cutover](#DatabaseMigrationsSqlMicutover)|cutover|[Parameters](#ParametersDatabaseMigrationsSqlMicutover)|[Example](#ExamplesDatabaseMigrationsSqlMicutover)|

### <a name="CommandsInDatabaseMigrationsSqlVm">Commands in `az datamigration to-sql-vm` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datamigration to-sql-vm show](#DatabaseMigrationsSqlVmGet)|Get|[Parameters](#ParametersDatabaseMigrationsSqlVmGet)|[Example](#ExamplesDatabaseMigrationsSqlVmGet)|
|[az datamigration to-sql-vm create](#DatabaseMigrationsSqlVmCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDatabaseMigrationsSqlVmCreateOrUpdate#Create)|[Example](#ExamplesDatabaseMigrationsSqlVmCreateOrUpdate#Create)|
|[az datamigration to-sql-vm update](#DatabaseMigrationsSqlVmCreateOrUpdate#Update)|CreateOrUpdate#Update|[Parameters](#ParametersDatabaseMigrationsSqlVmCreateOrUpdate#Update)|Not Found|
|[az datamigration to-sql-vm cancel](#DatabaseMigrationsSqlVmcancel)|cancel|[Parameters](#ParametersDatabaseMigrationsSqlVmcancel)|[Example](#ExamplesDatabaseMigrationsSqlVmcancel)|
|[az datamigration to-sql-vm cutover](#DatabaseMigrationsSqlVmcutover)|cutover|[Parameters](#ParametersDatabaseMigrationsSqlVmcutover)|[Example](#ExamplesDatabaseMigrationsSqlVmcutover)|


## COMMAND DETAILS
### group `az datamigration sql-service`
#### <a name="SqlMigrationServicesListByResourceGroup">Command `az datamigration sql-service list`</a>

##### <a name="ExamplesSqlMigrationServicesListByResourceGroup">Example</a>
```
az datamigration sql-service list --resource-group "testrg"
```
##### <a name="ParametersSqlMigrationServicesListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|

#### <a name="SqlMigrationServicesListBySubscription">Command `az datamigration sql-service list`</a>

##### <a name="ExamplesSqlMigrationServicesListBySubscription">Example</a>
```
az datamigration sql-service list
```
##### <a name="ParametersSqlMigrationServicesListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|

#### <a name="SqlMigrationServicesGet">Command `az datamigration sql-service show`</a>

##### <a name="ExamplesSqlMigrationServicesGet">Example</a>
```
az datamigration sql-service show --resource-group "testrg" --name "service1"
```
##### <a name="ParametersSqlMigrationServicesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|

#### <a name="SqlMigrationServicesCreateOrUpdate#Create">Command `az datamigration sql-service create`</a>

##### <a name="ExamplesSqlMigrationServicesCreateOrUpdate#Create">Example</a>
```
az datamigration sql-service create --location "northeurope" --resource-group "testrg" --name "testagent"
az datamigration sql-service create --location "northeurope" --resource-group "testrg" --name "testagent"
```
##### <a name="ParametersSqlMigrationServicesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|
|**--location**|string||location|location|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|

#### <a name="SqlMigrationServicesUpdate">Command `az datamigration sql-service update`</a>

##### <a name="ExamplesSqlMigrationServicesUpdate">Example</a>
```
az datamigration sql-service update --tags mytag="myval" --resource-group "testrg" --name "testagent"
```
##### <a name="ParametersSqlMigrationServicesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|
|**--tags**|dictionary|Dictionary of <string>|tags|tags|

#### <a name="SqlMigrationServicesDelete">Command `az datamigration sql-service delete`</a>

##### <a name="ExamplesSqlMigrationServicesDelete">Example</a>
```
az datamigration sql-service delete --resource-group "testrg" --name "service1"
```
##### <a name="ParametersSqlMigrationServicesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|

#### <a name="SqlMigrationServicesdeleteNode">Command `az datamigration sql-service delete-node`</a>

##### <a name="ExamplesSqlMigrationServicesdeleteNode">Example</a>
```
az datamigration sql-service delete-node --ir-name "IRName" --node-name "nodeName" --resource-group "testrg" --name \
"service1"
```
##### <a name="ParametersSqlMigrationServicesdeleteNode">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|
|**--node-name**|string|The name of node to delete.|node_name|nodeName|
|**--integration-runtime-name**|string|The name of integration runtime.|integration_runtime_name|integrationRuntimeName|

#### <a name="SqlMigrationServiceslistAuthKeys">Command `az datamigration sql-service list-auth-key`</a>

##### <a name="ExamplesSqlMigrationServiceslistAuthKeys">Example</a>
```
az datamigration sql-service list-auth-key --resource-group "testrg" --name "service1"
```
##### <a name="ParametersSqlMigrationServiceslistAuthKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|

#### <a name="SqlMigrationServiceslistMonitoringData">Command `az datamigration sql-service list-integration-runtime-metric`</a>

##### <a name="ExamplesSqlMigrationServiceslistMonitoringData">Example</a>
```
az datamigration sql-service list-integration-runtime-metric --resource-group "testrg" --name "service1"
```
##### <a name="ParametersSqlMigrationServiceslistMonitoringData">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|

#### <a name="SqlMigrationServiceslistMigrations">Command `az datamigration sql-service list-migration`</a>

##### <a name="ExamplesSqlMigrationServiceslistMigrations">Example</a>
```
az datamigration sql-service list-migration --resource-group "testrg" --name "service1"
```
##### <a name="ParametersSqlMigrationServiceslistMigrations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|

#### <a name="SqlMigrationServicesregenerateAuthKeys">Command `az datamigration sql-service regenerate-auth-key`</a>

##### <a name="ExamplesSqlMigrationServicesregenerateAuthKeys">Example</a>
```
az datamigration sql-service regenerate-auth-key --key-name "authKey1" --resource-group "testrg" --name "service1"
```
##### <a name="ParametersSqlMigrationServicesregenerateAuthKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-migration-service-name**|string|Name of the SQL Migration Service.|sql_migration_service_name|sqlMigrationServiceName|
|**--key-name**|string|The name of authentication key to generate.|key_name|keyName|
|**--auth-key1**|string|The first authentication key.|auth_key1|authKey1|
|**--auth-key2**|string|The second authentication key.|auth_key2|authKey2|

### group `az datamigration to-sql-managed-instance`
#### <a name="DatabaseMigrationsSqlMiGet">Command `az datamigration to-sql-managed-instance show`</a>

##### <a name="ExamplesDatabaseMigrationsSqlMiGet">Example</a>
```
az datamigration to-sql-managed-instance show --managed-instance-name "managedInstance1" --resource-group "testrg" \
--target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlMiGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--managed-instance-name**|string|Name of the target SQL Managed Instance.|managed_instance_name|managedInstanceName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--migration-operation-id**|uuid|Optional migration operation ID. If this is provided, then details of migration operation for that ID are retrieved. If not provided (default), then details related to most recent or current operation are retrieved.|migration_operation_id|migrationOperationId|
|**--expand**|string|The child resources to include in the response.|expand|$expand|

#### <a name="DatabaseMigrationsSqlMiCreateOrUpdate#Create">Command `az datamigration to-sql-managed-instance create`</a>

##### <a name="ExamplesDatabaseMigrationsSqlMiCreateOrUpdate#Create">Example</a>
```
az datamigration to-sql-managed-instance create --managed-instance-name "managedInstance1" --source-location \
"{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\ccc\\",\\"password\\":\\"placeholder\\",\\"username\\"\
:\\"name\\"}}" --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
--migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Data\
Migration/sqlMigrationServices/testagent" --offline-configuration last-backup-name="last_backup_file_name" \
offline=true --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Sql\
/managedInstances/instance" --source-database-name "aaa" --source-sql-connection authentication="WindowsAuthentication"\
 data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
--resource-group "testrg" --target-db-name "db1"
az datamigration to-sql-managed-instance create --managed-instance-name "managedInstance1" --source-location \
"{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\ccc\\",\\"password\\":\\"placeholder\\",\\"username\\"\
:\\"name\\"}}" --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
--migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Data\
Migration/sqlMigrationServices/testagent" --offline-configuration last-backup-name="last_backup_file_name" \
offline=true --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Sql\
/managedInstances/instance" --source-database-name "aaa" --source-sql-connection authentication="WindowsAuthentication"\
 data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
--resource-group "testrg" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlMiCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--managed-instance-name**|string|Name of the target SQL Managed Instance.|managed_instance_name|managedInstanceName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--scope**|string|Resource Id of the target resource (SQL VM or SQL Managed Instance)|scope|scope|
|**--source-sql-connection**|object|Source SQL Server connection details.|source_sql_connection|sourceSqlConnection|
|**--source-database-name**|string|Name of the source database.|source_database_name|sourceDatabaseName|
|**--migration-service**|string|Resource Id of the Migration Service.|migration_service|migrationService|
|**--migration-operation-id**|string|ID tracking current migration operation.|migration_operation_id|migrationOperationId|
|**--target-db-collation**|string|Database collation to be used for the target database.|target_db_collation|targetDatabaseCollation|
|**--provisioning-error**|string|Error message for migration provisioning failure, if any.|provisioning_error|provisioningError|
|**--offline-configuration**|object|Offline configuration.|offline_configuration|offlineConfiguration|
|**--source-location**|object|Source location of backups.|source_location|sourceLocation|
|**--target-location**|object|Target location for copying backups.|target_location|targetLocation|

#### <a name="DatabaseMigrationsSqlMiCreateOrUpdate#Update">Command `az datamigration to-sql-managed-instance update`</a>


##### <a name="ParametersDatabaseMigrationsSqlMiCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--managed-instance-name**|string|Name of the target SQL Managed Instance.|managed_instance_name|managedInstanceName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--scope**|string|Resource Id of the target resource (SQL VM or SQL Managed Instance)|scope|scope|
|**--source-sql-connection**|object|Source SQL Server connection details.|source_sql_connection|sourceSqlConnection|
|**--source-database-name**|string|Name of the source database.|source_database_name|sourceDatabaseName|
|**--migration-service**|string|Resource Id of the Migration Service.|migration_service|migrationService|
|**--migration-operation-id**|string|ID tracking current migration operation.|migration_operation_id|migrationOperationId|
|**--target-db-collation**|string|Database collation to be used for the target database.|target_db_collation|targetDatabaseCollation|
|**--provisioning-error**|string|Error message for migration provisioning failure, if any.|provisioning_error|provisioningError|
|**--offline-configuration**|object|Offline configuration.|offline_configuration|offlineConfiguration|
|**--source-location**|object|Source location of backups.|source_location|sourceLocation|
|**--target-location**|object|Target location for copying backups.|target_location|targetLocation|

#### <a name="DatabaseMigrationsSqlMicancel">Command `az datamigration to-sql-managed-instance cancel`</a>

##### <a name="ExamplesDatabaseMigrationsSqlMicancel">Example</a>
```
az datamigration to-sql-managed-instance cancel --managed-instance-name "managedInstance1" --migration-operation-id \
"4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group "testrg" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlMicancel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--managed-instance-name**|string|Name of the target SQL Managed Instance.|managed_instance_name|managedInstanceName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--migration-operation-id**|uuid|ID tracking migration operation.|migration_operation_id|migrationOperationId|

#### <a name="DatabaseMigrationsSqlMicutover">Command `az datamigration to-sql-managed-instance cutover`</a>

##### <a name="ExamplesDatabaseMigrationsSqlMicutover">Example</a>
```
az datamigration to-sql-managed-instance cutover --managed-instance-name "managedInstance1" --migration-operation-id \
"4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group "testrg" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlMicutover">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--managed-instance-name**|string|Name of the target SQL Managed Instance.|managed_instance_name|managedInstanceName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--migration-operation-id**|uuid|ID tracking migration operation.|migration_operation_id|migrationOperationId|

### group `az datamigration to-sql-vm`
#### <a name="DatabaseMigrationsSqlVmGet">Command `az datamigration to-sql-vm show`</a>

##### <a name="ExamplesDatabaseMigrationsSqlVmGet">Example</a>
```
az datamigration to-sql-vm show --resource-group "testrg" --sql-vm-name "testvm" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlVmGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-vm-name**|string|Name of the target SQL Virtual Machine.|sql_vm_name|sqlVirtualMachineName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--migration-operation-id**|uuid|Optional migration operation ID. If this is provided, then details of migration operation for that ID are retrieved. If not provided (default), then details related to most recent or current operation are retrieved.|migration_operation_id|migrationOperationId|
|**--expand**|string|The child resources to include in the response.|expand|$expand|

#### <a name="DatabaseMigrationsSqlVmCreateOrUpdate#Create">Command `az datamigration to-sql-vm create`</a>

##### <a name="ExamplesDatabaseMigrationsSqlVmCreateOrUpdate#Create">Example</a>
```
az datamigration to-sql-vm create --source-location "{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\cc\
c\\",\\"password\\":\\"placeholder\\",\\"username\\":\\"name\\"}}" --target-location account-key="abcd" \
storage-account-resource-id="account.database.windows.net" --migration-service "/subscriptions/00000000-1111-2222-3333-\
444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
--offline-configuration last-backup-name="last_backup_file_name" offline=true --scope "/subscriptions/00000000-1111-222\
2-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm" \
--source-database-name "aaa" --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" \
encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" --resource-group "testrg" \
--sql-vm-name "testvm" --target-db-name "db1"
az datamigration to-sql-vm create --source-location "{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\cc\
c\\",\\"password\\":\\"placeholder\\",\\"username\\":\\"name\\"}}" --target-location account-key="abcd" \
storage-account-resource-id="account.database.windows.net" --migration-service "/subscriptions/00000000-1111-2222-3333-\
444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
--offline-configuration last-backup-name="last_backup_file_name" offline=true --scope "/subscriptions/00000000-1111-222\
2-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm" \
--source-database-name "aaa" --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" \
encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" --resource-group "testrg" \
--sql-vm-name "testvm" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlVmCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-vm-name**|string|Name of the target SQL Virtual Machine.|sql_vm_name|sqlVirtualMachineName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--scope**|string|Resource Id of the target resource (SQL VM or SQL Managed Instance)|scope|scope|
|**--source-sql-connection**|object|Source SQL Server connection details.|source_sql_connection|sourceSqlConnection|
|**--source-database-name**|string|Name of the source database.|source_database_name|sourceDatabaseName|
|**--migration-service**|string|Resource Id of the Migration Service.|migration_service|migrationService|
|**--migration-operation-id**|string|ID tracking current migration operation.|migration_operation_id|migrationOperationId|
|**--target-db-collation**|string|Database collation to be used for the target database.|target_db_collation|targetDatabaseCollation|
|**--provisioning-error**|string|Error message for migration provisioning failure, if any.|provisioning_error|provisioningError|
|**--offline-configuration**|object|Offline configuration.|offline_configuration|offlineConfiguration|
|**--source-location**|object|Source location of backups.|source_location|sourceLocation|
|**--target-location**|object|Target location for copying backups.|target_location|targetLocation|

#### <a name="DatabaseMigrationsSqlVmCreateOrUpdate#Update">Command `az datamigration to-sql-vm update`</a>


##### <a name="ParametersDatabaseMigrationsSqlVmCreateOrUpdate#Update">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-vm-name**|string|Name of the target SQL Virtual Machine.|sql_vm_name|sqlVirtualMachineName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--scope**|string|Resource Id of the target resource (SQL VM or SQL Managed Instance)|scope|scope|
|**--source-sql-connection**|object|Source SQL Server connection details.|source_sql_connection|sourceSqlConnection|
|**--source-database-name**|string|Name of the source database.|source_database_name|sourceDatabaseName|
|**--migration-service**|string|Resource Id of the Migration Service.|migration_service|migrationService|
|**--migration-operation-id**|string|ID tracking current migration operation.|migration_operation_id|migrationOperationId|
|**--target-db-collation**|string|Database collation to be used for the target database.|target_db_collation|targetDatabaseCollation|
|**--provisioning-error**|string|Error message for migration provisioning failure, if any.|provisioning_error|provisioningError|
|**--offline-configuration**|object|Offline configuration.|offline_configuration|offlineConfiguration|
|**--source-location**|object|Source location of backups.|source_location|sourceLocation|
|**--target-location**|object|Target location for copying backups.|target_location|targetLocation|

#### <a name="DatabaseMigrationsSqlVmcancel">Command `az datamigration to-sql-vm cancel`</a>

##### <a name="ExamplesDatabaseMigrationsSqlVmcancel">Example</a>
```
az datamigration to-sql-vm cancel --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group \
"testrg" --sql-vm-name "testvm" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlVmcancel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-vm-name**|string|Name of the target SQL Virtual Machine.|sql_vm_name|sqlVirtualMachineName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--migration-operation-id**|uuid|ID tracking migration operation.|migration_operation_id|migrationOperationId|

#### <a name="DatabaseMigrationsSqlVmcutover">Command `az datamigration to-sql-vm cutover`</a>

##### <a name="ExamplesDatabaseMigrationsSqlVmcutover">Example</a>
```
az datamigration to-sql-vm cutover --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group \
"testrg" --sql-vm-name "testvm" --target-db-name "db1"
```
##### <a name="ParametersDatabaseMigrationsSqlVmcutover">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|Name of the resource group that contains the resource. You can obtain this value from the Azure Resource Manager API or the portal.|resource_group_name|resourceGroupName|
|**--sql-vm-name**|string|Name of the target SQL Virtual Machine.|sql_vm_name|sqlVirtualMachineName|
|**--target-db-name**|string|The name of the target database.|target_db_name|targetDbName|
|**--migration-operation-id**|uuid|ID tracking migration operation.|migration_operation_id|migrationOperationId|
