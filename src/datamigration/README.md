# Azure CLI datamigration Extension #
This is the extension for datamigration

### How to use ###
Install this extension using the below CLI command
```
az extension add --name datamigration
```

### Included Features ###
#### datamigration to-sql-managed-instance ####
##### Create #####
```
az datamigration to-sql-managed-instance create --managed-instance-name "managedInstance1" \
    --source-location "{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\ccc\\",\\"password\\":\\"placeholder\\",\\"username\\":\\"name\\"}}" \
    --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Sql/managedInstances/instance" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --target-db-name "db1" 
```
##### Create #####
```
az datamigration to-sql-managed-instance create --managed-instance-name "managedInstance1" \
    --source-location "{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\ccc\\",\\"password\\":\\"placeholder\\",\\"username\\":\\"name\\"}}" \
    --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Sql/managedInstances/instance" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --target-db-name "db1" 
```
##### Show #####
```
az datamigration to-sql-managed-instance show --managed-instance-name "managedInstance1" --resource-group "testrg" \
    --target-db-name "db1" 
```
##### Cancel #####
```
az datamigration to-sql-managed-instance cancel --managed-instance-name "managedInstance1" \
    --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group "testrg" --target-db-name "db1" 
```
##### Cutover #####
```
az datamigration to-sql-managed-instance cutover --managed-instance-name "managedInstance1" \
    --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group "testrg" --target-db-name "db1" 
```
#### datamigration to-sql-vm ####
##### Create #####
```
az datamigration to-sql-vm create \
    --source-location "{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\ccc\\",\\"password\\":\\"placeholder\\",\\"username\\":\\"name\\"}}" \
    --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
##### Create #####
```
az datamigration to-sql-vm create \
    --source-location "{\\"fileShare\\":{\\"path\\":\\"C:\\\\\\\\aaa\\\\\\\\bbb\\\\\\\\ccc\\",\\"password\\":\\"placeholder\\",\\"username\\":\\"name\\"}}" \
    --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
##### Show #####
```
az datamigration to-sql-vm show --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1"
```
##### Cancel #####
```
az datamigration to-sql-vm cancel --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
##### Cutover #####
```
az datamigration to-sql-vm cutover --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
#### datamigration sql-service ####
##### Create #####
```
az datamigration sql-service create --location "northeurope" --resource-group "testrg" --name "testagent"

az datamigration sql-service wait --created --resource-group "{rg}" --name "{mySqlMigrationService}"
```
##### Create #####
```
az datamigration sql-service create --location "northeurope" --resource-group "testrg" --name "testagent"

az datamigration sql-service wait --created --resource-group "{rg}" --name "{mySqlMigrationService}"
```
##### List #####
```
az datamigration sql-service list --resource-group "testrg"
```
##### Show #####
```
az datamigration sql-service show --resource-group "testrg" --name "service1"
```
##### Update #####
```
az datamigration sql-service update --tags mytag="myval" --resource-group "testrg" --name "testagent"
```
##### Delete-node #####
```
az datamigration sql-service delete-node --integration-runtime-name "IRName" --node-name "nodeName" \
    --resource-group "testrg" --name "service1" 
```
##### List-auth-key #####
```
az datamigration sql-service list-auth-key --resource-group "testrg" --name "service1"
```
##### List-integration-runtime-metric #####
```
az datamigration sql-service list-integration-runtime-metric --resource-group "testrg" --name "service1"
```
##### List-migration #####
```
az datamigration sql-service list-migration --resource-group "testrg" --name "service1"
```
##### Regenerate-auth-key #####
```
az datamigration sql-service regenerate-auth-key --key-name "authKey1" --resource-group "testrg" --name "service1"
```
##### Delete #####
```
az datamigration sql-service delete --resource-group "testrg" --name "service1"
```