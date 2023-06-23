# Azure CLI datamigration Extension #
This is the extension for datamigration

### How to use ###
Install this extension using the below CLI command
```
az extension add --name datamigration
```

### Included Features ###

##### Get-assessment #####
```
az datamigration get-assessment --connection-string "Data Source=LabServer.database.net;Initial Catalog=master;Integrated Security=False;User Id=User;Password=password" --output-folder "C:\AssessmentOutput" --overwrite
```

##### Register-integration-runtime #####
```
az datamigration register-integration-runtime --auth-key "IR@00000-0000000-000000-aaaaa-bbbb-cccc"
```

##### Performance-data-collection #####
```
az datamigration performance-data-collection --connection-string "Data Source=LabServer.database.net;Initial Catalog=master;Integrated Security=False;User Id=User;Password=password" --output-folder "C:\\PerfCollectionOutput" --number-of-interation 5 --perf-query-interval 10 --static-query-interval 60
```

##### Get-sku-recommendation #####
```
az datamigration get-sku-recommendation --output-folder "C:\\PerfCollectionOutput" --database-allow-list AdventureWorks AdventureWorks2 --display-result --overwrite
```

##### Login-migration #####
```
az datamigration login-migration --src-sql-connection-str  "data source=servername;user id=userid;password=;initial catalog=master;TrustServerCertificate=True" --tgt-sql-connection-str  "data source=servername;user id=userid;password=;initial catalog=master;TrustServerCertificate=True" --csv-file-path "C:\\CSVFile" --list-of-login "loginname1" "loginname2" --output-folder "C:\\OutputFolder" --aad-domain-name "AADDomainName" --display-result --overwrite
```

##### TDE-migration #####
```
az datamigration tde-migration --source-sql-connection-string "data source=servername;user id=userid;password=;initial catalog=master;TrustServerCertificate=True" --target-subscription-id "00000000-0000-0000-0000-000000000000" --target-resource-group-name "ResourceGroupName" --target-managed-instance-name "TargetManagedInstanceName" --network-share-path "\\NetworkShare\Folder" --network-share-domain "" --network-share-user-name "NetworkShareUserName" --network-share-password "" --database-name "TdeDb_0" "TdeDb_1" "TdeDb_2"
```

##### Sql-server-schema #####
```
az datamigration sql-server-schema --action "MigrateSchema" --src-sql-connection-str  "Server=;Initial Catalog=;User ID=;Password=" --tgt-sql-connection-str  "Server=;Initial Catalog=;User ID=;Password=" --input-script-file-path "C:\inputFile" --output-folder "C:\OutputFolder" --display-result --overwrite
```

#### datamigration sql-managed-instance ####
##### Create (Backup source Fileshare) #####
```
az datamigration sql-managed-instance create --managed-instance-name "managedInstance1" \
    --source-location '{\"fileShare\":{\"path\":\"\\\\SharedBackup\\user\",\"password\":\"placeholder\",\"username\":\"Server\\name\"}}' \
    --target-location account-key="abcd" storage-account-resource-id="account.database.windows.net" \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Sql/managedInstances/instance" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --target-db-name "db1" 
```
##### Create (Backup source Azure Blob) #####
```
az datamigration sql-managed-instance create --managed-instance-name "managedInstance1" \
    --source-location '{\"AzureBlob\":{\"storageAccountResourceId\":\"/subscriptions/1111-2222-3333-4444/resourceGroups/RG/prooviders/Microsoft.Storage/storageAccounts/MyStorage\",\"accountKey\":\"======AccountKey====\",\"blobContainerName\":\"ContainerName-X\"}}' \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.Sql/managedInstances/instance" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --target-db-name "db1" 
```
##### Show #####
```
az datamigration sql-managed-instance show --managed-instance-name "managedInstance1" --resource-group "testrg" \
    --target-db-name "db1" 
```
##### Cancel #####
```
az datamigration sql-managed-instance cancel --managed-instance-name "managedInstance1" \
    --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group "testrg" --target-db-name "db1" 
```
##### Cutover #####
```
az datamigration sql-managed-instance cutover --managed-instance-name "managedInstance1" \
    --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" --resource-group "testrg" --target-db-name "db1" 
```
#### datamigration sql-vm ####
##### Create (Backup source Fileshare) #####
```
az datamigration sql-vm create \
    --source-location '{\"fileShare\":{\"path\":\"\\\\SharedBackup\\user\",\"password\":\"placeholder\",\"username\":\"Server\\name\"}}' \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.DataMigration/sqlMigrationServices/testagent" \
    --offline-configuration last-backup-name="last_backup_file_name" offline=true \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/testrg/providers/Microsoft.SqlVirtualMachine/sqlVirtualMachines/testvm" \
    --source-database-name "aaa" \
    --source-sql-connection authentication="WindowsAuthentication" data-source="aaa" encrypt-connection=true password="placeholder" trust-server-certificate=true user-name="bbb" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
##### Create (Backup source Azure Blob) #####
```
az datamigration sql-vm create \
    --source-location '{\"AzureBlob\":{\"storageAccountResourceId\":\"/subscriptions/1111-2222-3333-4444/resourceGroups/RG/prooviders/Microsoft.Storage/storageAccounts/MyStorage\",\"accountKey\":\"======AccountKey====\",\"blobContainerName\":\"ContainerName-X\"}}' \
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
az datamigration sql-vm show --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1"
```
##### Cancel #####
```
az datamigration sql-vm cancel --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
##### Cutover #####
```
az datamigration sql-vm cutover --migration-operation-id "4124fe90-d1b6-4b50-b4d9-46d02381f59a" \
    --resource-group "testrg" --sql-virtual-machine-name "testvm" --target-db-name "db1" 
```
#### datamigration sql-db ####
##### Create #####
```
az datamigration sql-db create \
    --migration-service "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/MyGroup/providers/Microsoft.DataMigration/SqlMigrationServices/MyService" \
    --scope "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/MyGroup/providers/Microsoft.Sql/servers/labserver" \
    --source-database-name "AdventureWorks" \
    --source-sql-connection authentication="SQLAuthentication" data-source="aaa" password="bbb" user-name="ccc" \
    --target-sql-connection authentication="SQLAuthentication" data-source="aaa" password="bbb" user-name="ccc" \
    --resource-group "MyGroup" --sqldb-instance-name "labserver" --target-db-name AdventureWorksTarget
```
##### Show #####
```
az datamigration sql-db show --resource-group "testrg" --sqldb-instance-name "sqldbinstance" \
    --target-db-name "db1"
```
##### Delete #####
```
az datamigration sql-db delete --resource-group "testrg" --sqldb-instance-name "sqldbinstance" \
    --target-db-name "db1"
```
##### Cancel #####
```
az datamigration sql-db cancel --migration-operation-id "9a90bb84-e70f-46f7-b0ae-1aef5b3b9f07" \
    --resource-group "testrg" --sqldb-instance-name "sqldbinstance" --target-db-name "db1" 
```

#### datamigration sql-service ####
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