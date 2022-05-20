# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

import time

# Env setup_scenario
def setup_scenario(test):
    test.kwargs.update({
        "serviceRG": "CLIUnitTest",
        "sqlMigrationService": "dmsCliUnitTest",
        "location": "eastus2euap",
        "createSqlMigrationService": "sqlServiceUnitTest-Pipeline2"
    }),
    test.kwargs.update({
        "miRG": "migrationTesting",
        "managedInstance": "migrationtestmi",
        "miTargetDb": "tsum-CLI-MIOnline"
    }),
    test.kwargs.update({
        "vmRG": "tsum38RG",
        "virtualMachine": "DMSCmdletTest-SqlVM",
        "vmTargetDb": "tsum-Db-VM"
    }),#12. Create Common Params
    test.kwargs.update({
        "migrationService": "/subscriptions/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/resourceGroups/tsum38RG/providers/Microsoft.DataMigration/SqlMigrationServices/tsuman-IR2",
        "miScope": "/subscriptions/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/resourceGroups/MigrationTesting/providers/Microsoft.Sql/managedInstances/migrationtestmi",
        "vmScope": "/subscriptions/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/resourceGroups/tsum38RG/providers/Microsoft.SqlVirtualMachine/SqlVirtualMachines/DMSCmdletTest-SqlVM",
        "sourceDBName": "AdventureWorks",
        "miRG": "MigrationTesting",
        "authentication": "SqlAuthentication",
        "dataSource":"AALAB03-2K8.REDMOND.CORP.MICROSOFT.COM", 
        "password": "XXXXXXXXXXXX",
        "userName": "hijavatestuser1",
        "accountKey": "XXXXXXXXXXXX/XXXXXXXXXXXX",
        "storageAccountId": "/subscriptions/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/resourceGroups/aaskhan/providers/Microsoft.Storage/storageAccounts/aasimmigrationtest"        
    }), # MI Online FileShare
    test.kwargs.update({
        "miOnlineFsTargetDb": "tsum-Db-mi-online-fs9",
        "fsSourceLocation":"'{\"fileShare\":{\"path\":\"\\\\\\\\aalab03-2k8.redmond.corp.microsoft.com\\\\SharedBackup\\\\tsuman\",\"password\":\"XXXXXXXXXXXX\",\"username\":\"AALAB03-2K8\\hijavatestlocaluser\"}}'"
    }), #Blob
    test.kwargs.update({
        "blobSourceLocation": "'{\"AzureBlob\":{\"storageAccountResourceId\":\"/subscriptions/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/resourceGroups/tzppesignoff1211/providers/Microsoft.Storage/storageAccounts/hijavateststorage\",\"accountKey\":\"XXXXXXXXXXXX/XXXXXXXXXXXX\",\"blobContainerName\":\"tsum38-adventureworks\"}}'", 
        "miOnlineBlobTargetDb":"tsum-Db-mi-online-blob9"
    }), # VM DBs
    test.kwargs.update({ 
        "vmOnlineFsTargetDb":"tsum-Db-vm-online-fs9",
        "vmOnlineBlobTargetDb": "tsum-Db-vm-online-blob10"
    })# Offline
    test.kwargs.update({ 
        "lastBackupName":"AdventureWorksTransactionLog2.trn",
        "miOfflineFsTargetDb":"tsum-Db-mi-offline-fs",
        "miOfflineBlobTargetDb": "tsum-Db-mi-offline-blob",
        "vmOfflineFsTargetDb":"tsum-Db-vm-offline-fs",
        "vmOfflineBlobTargetDb": "tsum-Db-vm-offline-blob9"
    }) # Show DB parameters
    test.kwargs.update({ 
        "dbRG":"tsum38RG",
        "sqlserver":"dmstestsqldb",
        "dbTargetDb": "NewDb"
    }) # Db Migration parameters
    test.kwargs.update({ 
        "targetDataSource":"dmstestsqldb.database.windows.net",
        "targetUserName":"demouser",
        "targetPassword": "XXXXXXXXXXXX",
        "targetAuthentication": "SqlAuthentication",
        "dbSourceDBName": "Brih",
        "tableName": "[dbo].[Table_1]",
        "dbScope": "/subscriptions/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX/resourceGroups/tsum38RG/providers/Microsoft.Sql/servers/dmstestsqldb"
    })

#Test Cases
#1.  SQL Service Create 
def step_sql_service_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service create '
             '--location "{location}" '
             '--resource-group "{serviceRG}" '
             '--name "{createSqlMigrationService}"',
             checks=checks)

#2.  SQL Service Show 
def step_sql_service_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service show '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)
#3.  SQL Service List RG
def step_sql_service_list_rg(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list '
             '--resource-group "{serviceRG}"',
             checks=checks)

#4.  SQL Service List Sub
def step_sql_service_list_sub(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list ',
             checks=checks)

#5.  SQL Service List Migration
def step_sql_service_list_migration(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list-migration '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

#6.  SQL Service List Auth Keys
def step_sql_service_list_auth_key(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list-auth-key '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

#7.  SQL Service Regererate Auth Keys
def step_sql_service_regenerate_auth_key(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service regenerate-auth-key '
             '--key-name "authKey1" '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

#8.  SQL Service Regererate Auth Keys
def step_sql_service_list_integration_runtime_metric(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service list-integration-runtime-metric '
             '--resource-group "{serviceRG}" '
             '--name "{sqlMigrationService}"',
             checks=checks)

#9. SQL Service Delete
def step_sql_service_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-service delete -y '
             '--resource-group "{serviceRG}" '
             '--name "{createSqlMigrationService}"',
             checks=checks)

#10. MI Show
def step_sql_managed_instance_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-managed-instance show '
             '--managed-instance-name "{managedInstance}" '
             '--resource-group "{miRG}" '
             '--target-db-name "{miTargetDb}"',
             checks=checks)

#11. VM Show
def step_sql_vm_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-vm show '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmTargetDb}"',
             checks=checks)


#12. MI Online FileShare Create
def step_sql_managed_instance_online_fileshare_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-managed-instance create '
             '--source-location {fsSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{miScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{miOnlineFsTargetDb}" '   
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}"',
             checks=checks)

 #13.1 MI Online FileShare Cutover
def step_sql_managed_instance_online_fileshare_cutover(test, checks=None):
    if checks is None:
        checks = []

    miOnlinefileShareMigrationStats = test.cmd('az datamigration sql-managed-instance show '
                                 '--managed-instance-name "{managedInstance}" '
                                 '--resource-group "{miRG}" '
                                 '--target-db-name "{miOnlineFsTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
    miOnlineFsIsfullBackupRestore = miOnlinefileShareMigrationStats["properties"]["migrationStatusDetails"]["isFullBackupRestored"]
    migrationStatus = miOnlinefileShareMigrationStats["properties"]["migrationStatus"]
    test.kwargs.update({ 
        "miOnlineFsMigrationId": miOnlinefileShareMigrationStats["properties"]["migrationOperationId"]})

    while miOnlineFsIsfullBackupRestore != True and migrationStatus != "Failed":
         time.sleep(10)
         miOnlinefileShareMigrationStats = test.cmd('az datamigration sql-managed-instance show '
                                 '--managed-instance-name "{managedInstance}" '
                                 '--resource-group "{miRG}" '
                                 '--target-db-name "{miOnlineFsTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
         miOnlineFsIsfullBackupRestore = miOnlinefileShareMigrationStats["properties"]["migrationStatusDetails"]["isFullBackupRestored"]
         migrationStatus = miOnlinefileShareMigrationStats["properties"]["migrationStatus"]
         
    test.cmd('az datamigration sql-managed-instance cutover '
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--target-db-name "{miOnlineFsTargetDb}" '
             '--migration-operation-id "{miOnlineFsMigrationId}"',
             checks=checks)

#13.2 MI Online FileShare Cutover
def step_sql_managed_instance_online_fileshare_cutover_Confirm(test, checks=None):
    if checks is None:
        checks = []
    
    miOnlinefileShareMigrationStats = test.cmd('az datamigration sql-managed-instance show '
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--target-db-name "{miOnlineFsTargetDb}"',
             checks=checks).get_output_in_json()

    migrationStatus = miOnlinefileShareMigrationStats["properties"]["migrationStatus"]

    while migrationStatus != "Succeeded" and migrationStatus != "Failed":
        time.sleep(10) 

        miOnlinefileShareMigrationStats = test.cmd('az datamigration sql-vm show '
             '--resource-group "{miRG}" '
             '--sql-vm-name "{managedInstance}" '
             '--target-db-name "{miOnlineFsTargetDb}"',
             checks=checks).get_output_in_json()
        
        migrationStatus = miOnlinefileShareMigrationStats["properties"]["migrationStatus"]

#14. MI Online Blob Create
def step_sql_managed_instance_online_blob_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-managed-instance create '
             '--source-location {blobSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{miScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{miOnlineBlobTargetDb}" '   
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}"',
             checks=checks)



#15.1 MI Online Blob Cancel
def step_sql_managed_instance_online_blob_cancel(test, checks=None):
    if checks is None:
        checks = []
        
    miOnlineBlobMigrationStats = test.cmd('az datamigration sql-managed-instance show '
                                 '--managed-instance-name "{managedInstance}" '
                                 '--resource-group "{miRG}" '
                                 '--target-db-name "{miOnlineBlobTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
    test.kwargs.update({ 
        "miOnlineBlobMigrationId": miOnlineBlobMigrationStats["properties"]["migrationOperationId"]})

    test.cmd('az datamigration sql-managed-instance cancel '
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--target-db-name "{miOnlineBlobTargetDb}" '
             '--migration-operation-id "{miOnlineBlobMigrationId}"',
             checks=checks) 

#15.2 MI Online Blob Cancel Confirm
def step_sql_managed_instance_online_blob_cancel_Confirm(test, checks=None):
    if checks is None:
        checks = []

        miOnlineBlobStats = test.cmd('az datamigration sql-managed-instance show '
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--target-db-name "{miOnlineBlobTargetDb}"',
             checks=checks).get_output_in_json()

        miiOnlineBlobStatus = miOnlineBlobStats["properties"]["migrationStatus"]

        while miiOnlineBlobStatus != "Canceled" and miiOnlineBlobStatus != "Failed":

         time.sleep(10)
         miOnlineBlobStats = test.cmd('az datamigration sql-managed-instance show '
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--target-db-name "{miOnlineBlobTargetDb}"',
             checks=checks).get_output_in_json()

         miiOnlineBlobStatus = miOnlineBlobStats["properties"]["migrationStatus"]

#16. VM Online FileShare Create
def step_sql_vm_online_fileshare_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-vm create '
             '--source-location {fsSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{vmScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{vmOnlineFsTargetDb}" '   
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}"',
             checks=checks)  

#17.1 VM Online FileShare Cutover
def step_sql_vm_online_fileshare_cutover(test, checks=None):
    if checks is None:
        checks = []
    vmOnlinefileShareMigrationStats = test.cmd('az datamigration sql-vm show '
                                 '--sql-vm-name "{virtualMachine}" '
                                 '--resource-group "{vmRG}" '
                                 '--target-db-name "{vmOnlineFsTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
    vmOnlineFsIsfullBackupRestore = vmOnlinefileShareMigrationStats["properties"]["migrationStatusDetails"]["isFullBackupRestored"]
    migrationStatus = vmOnlinefileShareMigrationStats["properties"]["migrationStatus"]
    test.kwargs.update({ 
        "vmOnlineFsMigrationId": vmOnlinefileShareMigrationStats["properties"]["migrationOperationId"]})
    
    while vmOnlineFsIsfullBackupRestore != True and migrationStatus != "Failed":

        time.sleep(10)
        vmOnlinefileShareMigrationStats = test.cmd('az datamigration sql-vm show '
                                 '--sql-vm-name "{virtualMachine}" '
                                 '--resource-group "{vmRG}" '
                                 '--target-db-name "{vmOnlineFsTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
        migrationStatus = vmOnlinefileShareMigrationStats["properties"]["migrationStatus"]
        vmOnlineFsIsfullBackupRestore = vmOnlinefileShareMigrationStats["properties"]["migrationStatusDetails"]["isFullBackupRestored"]
        
    test.cmd('az datamigration sql-vm cutover '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmOnlineFsTargetDb}" '
             '--migration-operation-id "{vmOnlineFsMigrationId}"',
             checks=checks)

#17.2 VM Online FileShare Cutover Confirm
def step_sql_vm_online_fileshare_cutover_Confirm(test, checks=None):
    if checks is None:
        checks = []
    vmOnlinefileShareMigrationStats = test.cmd('az datamigration sql-vm show '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmOnlineFsTargetDb}"',
             checks=checks).get_output_in_json()

    migrationStatus = vmOnlinefileShareMigrationStats["properties"]["migrationStatus"]

    while migrationStatus != "Succeeded" and migrationStatus != "Failed":
        time.sleep(10) 

        vmOnlinefileShareMigrationStats = test.cmd('az datamigration sql-vm show '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmOnlineFsTargetDb}"',
             checks=checks).get_output_in_json()
        
        migrationStatus = vmOnlinefileShareMigrationStats["properties"]["migrationStatus"]

#18. VM Online Blob Create
def step_sql_vm_online_blob_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-vm create '
             '--source-location {blobSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{vmScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{vmOnlineBlobTargetDb}" '   
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}"',
             checks=checks)  

#19.1 VM Online Blob Cancel
def step_sql_vm_online_blob_cancel(test, checks=None):    
    if checks is None:
        checks = []
    vmOnlineBlobMigrationStats = test.cmd('az datamigration sql-vm show '
                                 '--sql-vm-name "{virtualMachine}" '
                                 '--resource-group "{vmRG}" '
                                 '--target-db-name "{vmOnlineBlobTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
    test.kwargs.update({ 
        "vmOnlineBlobMigrationId": vmOnlineBlobMigrationStats["properties"]["migrationOperationId"]
        })

    test.cmd('az datamigration sql-vm cancel '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmOnlineBlobTargetDb}" '
             '--migration-operation-id "{vmOnlineBlobMigrationId}"',
             checks=checks)  

#19.2 VM Online Blob Cancel
def step_sql_vm_online_blob_cancel_Confirm(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-vm show '
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
             '--target-db-name "{vmOnlineBlobTargetDb}"',
             checks=checks)

'''
#20. MI Offline FS Create
def step_sql_managed_instance_offline_fileshare_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-managed-instance create '
             '--source-location {fsSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{miScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{miOfflineFsTargetDb}" '   
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--offline-configuration offline=true last-backup-name="{lastBackupName}"',
             checks=checks) 

#21. MI Offline Blob Create
def step_sql_managed_instance_offline_blob_create (test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-managed-instance create '
             '--source-location {blobSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{miScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{miOfflineBlobTargetDb}" '   
             '--resource-group "{miRG}" '
             '--managed-instance-name "{managedInstance}" '
             '--offline-configuration offline=true last-backup-name="{lastBackupName}"',
             checks=checks)  

#22. VM Offline FS Create
def step_sql_vm_offline_fileshare_create (test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-vm create '
            '--source-location {fsSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{vmScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{vmOfflineFsTargetDb}" '   
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
            '--offline-configuration offline=true last-backup-name="{lastBackupName}"',
             checks=checks) 
'''

#23. VM Offline Blob Create
def step_sql_vm_offline_blob_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-vm create '
               '--source-location {blobSourceLocation} '
             '--target-location account-key="{accountKey}" storage-account-resource-id="{storageAccountId}" '
             '--migration-service "{migrationService}" '
             '--scope "{vmScope}" '
             '--source-database-name "{sourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-db-name "{vmOfflineBlobTargetDb}" '   
             '--resource-group "{vmRG}" '
             '--sql-vm-name "{virtualMachine}" '
            '--offline-configuration offline=true last-backup-name="{lastBackupName}"',
             checks=checks) 

#24. DB Migration Show
def step_sql_db_show(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-db show '
             '--sqldb-instance-name "{sqlserver}" '
             '--resource-group "{dbRG}" '
             '--target-db-name "{dbTargetDb}"',
             checks=checks)

#25. DB Migration create 
def step_sql_db_offline_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-db create '
             '--migration-service "{migrationService}" '
             '--scope "{dbScope}" '
             '--source-database-name "{dbSourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-sql-connection authentication="{targetAuthentication}" data-source="{targetDataSource}"  password="{targetPassword}" user-name="{targetUserName}" '
             '--target-db-name "{dbTargetDb}" '   
             '--resource-group "{dbRG}" '
             '--sqldb-instance-name "{sqlserver}"',
             checks=checks)

#26. DB Migration selected tables create 
def step_sql_db_offline_tablelist_create(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-db create '
             '--migration-service "{migrationService}" '
             '--scope "{dbScope}" '
             '--source-database-name "{dbSourceDBName}" '
             '--source-sql-connection authentication="{authentication}" data-source="{dataSource}"  password="{password}" user-name="{userName}" '
             '--target-sql-connection authentication="{targetAuthentication}" data-source="{targetDataSource}"  password="{targetPassword}" user-name="{targetUserName}" '
             '--table-list "{tableName}" '
             '--target-db-name "{dbTargetDb}" '   
             '--resource-group "{dbRG}" '
             '--sqldb-instance-name "{sqlserver}"',
             checks=checks)

#26. DB Migration Delete
def step_sql_db_offline_delete(test, checks=None):
    if checks is None:
        checks = []
    test.cmd('az datamigration sql-db delete '
             '--sqldb-instance-name "{sqlserver}" '
             '--resource-group "{dbRG}" '
             '--target-db-name "{dbTargetDb}" '
             '--force -y',
             checks=checks)


#26. DB Migration cancel
def step_sql_db_offline_cancel(test, checks=None):    
    if checks is None:
        checks = []
    dbOfflineMigrationStats = test.cmd('az datamigration sql-db show '
                                 '--sqldb-instance-name "{sqlserver}" '
                                 '--resource-group "{dbRG}" '
                                 '--target-db-name "{dbTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
    test.kwargs.update({ 
        "dbOfflineCancelMigrationId": dbOfflineMigrationStats["properties"]["migrationOperationId"]
        })

    test.cmd('az datamigration sql-db cancel '
             '--resource-group "{dbRG}" '
             '--sqldb-instance-name "{sqlserver}" '
             '--target-db-name "{dbTargetDb}" '
             '--migration-operation-id "{dbOfflineCancelMigrationId}"',
             checks=checks)


#26. DB Migration selected tables check for completion
def step_sql_db_offline_tablelist_complete(test, checks=None):
    if checks is None:
        checks = []
    dbOfflineMigrationStats = test.cmd('az datamigration sql-db show '
                                 '--sqldb-instance-name "{sqlserver}" '
                                 '--resource-group "{dbRG}" '
                                 '--target-db-name "{dbTargetDb}" '
                                 '--expand=MigrationStatusDetails').get_output_in_json()
    migrationStatus = dbOfflineMigrationStats["properties"]["migrationStatus"]
    
    while migrationStatus == "InProgress":

        time.sleep(30)
        dbOfflineMigrationStats = test.cmd('az datamigration sql-db show '
                                '--sqldb-instance-name "{sqlserver}" '
                                '--resource-group "{dbRG}" '
                                '--target-db-name "{dbTargetDb}" '
                                '--expand=MigrationStatusDetails').get_output_in_json()
        migrationStatus = dbOfflineMigrationStats["properties"]["migrationStatus"]
        
    test.cmd('az datamigration sql-db show '
             '--sqldb-instance-name "{sqlserver}" '
             '--resource-group "{dbRG}" '
             '--target-db-name "{dbTargetDb}"',
             checks=checks)

# Env cleanup_scenario
def cleanup_scenario(test):
    pass

# # Testcase: Scenario
def call_scenario(test):
    setup_scenario(test)
    try:
        
        #1. SQL Service Create 
        step_sql_service_create(test, checks=[
            test.check("location", "{location}", case_sensitive=False),
            test.check("name", "{createSqlMigrationService}", case_sensitive=False),
            test.check("provisioningState", "Succeeded", case_sensitive=False)
        ])
        
        #2. SQL Service Show 
        step_sql_service_show(test, checks=[
            test.check("location", "{location}", case_sensitive=False),
            test.check("name", "{sqlMigrationService}", case_sensitive=False)
        ])

        #3. SQL Service List RG
        step_sql_service_list_rg(test)

        '''
        #4.  SQL Service List Sub
        step_sql_service_list_sub(test)
        '''
        
        #5.  SQL Service List Migration
        step_sql_service_list_migration(test)

        #6.  SQL Service List Auth Keys
        step_sql_service_list_auth_key(test)

        #7.  SQL Service Regererate Auth Keys
        step_sql_service_regenerate_auth_key(test)

        #8.  SQL Service Regererate Auth Keys
        step_sql_service_list_integration_runtime_metric(test, checks=[
            test.check("name", "default-ir", case_sensitive=False)
        ])

        #9. SQL Service Delete
        step_sql_service_delete(test)

        #10. MI Show
        step_sql_managed_instance_show(test, checks=[
            test.check("name", "{miTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlMi", case_sensitive=False)
        ])

        # #11. VM Show
        step_sql_vm_show(test, checks=[
            test.check("name", "{vmTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlVm", case_sensitive=False)
        ])        
        
        # #12. MI Online FileShare Create
        # step_sql_managed_instance_online_fileshare_create(test, checks=[
        #     test.check("name", "{miOnlineFsTargetDb}", case_sensitive=False),
        #     test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
        #     test.check("properties.kind", "SqlMi", case_sensitive=False),
        #     test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
        #     test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        # ])
                
        # #13.1 MI Online FileShare Cutover
        # step_sql_managed_instance_online_fileshare_cutover(test)

        # #13.2 MI Online FileShare Cutover Confirm
        # step_sql_managed_instance_online_fileshare_cutover_Confirm(test, checks=[
        #     test.check("name", "{miOnlineFsTargetDb}", case_sensitive=False),
        #     test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
        #     test.check("properties.kind", "SqlMi", case_sensitive=False),
        #     test.check("properties.migrationStatus", "Succeeded", case_sensitive=False)
        # ])
        
        #14. MI Online Blob Create
        step_sql_managed_instance_online_blob_create(test, checks=[
            test.check("name", "{miOnlineBlobTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlMi", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])
        
        #15.1 MI Online Blob Cancel
        step_sql_managed_instance_online_blob_cancel(test)
       
        #15.2 MI Online Blob Cancel Confirm
        step_sql_managed_instance_online_blob_cancel_Confirm(test, checks=[
            test.check("name", "{miOnlineBlobTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlMi", case_sensitive=False),
            test.check("properties.migrationStatus", "Canceled", case_sensitive=False)
        ])
        
        # #16. VM Online FileShare Create
        # step_sql_vm_online_fileshare_create(test, checks=[
        #     test.check("name", "{vmOnlineFsTargetDb}", case_sensitive=False),
        #     test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
        #     test.check("properties.kind", "SqlVm", case_sensitive=False),
        #     test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
        #     test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        # ])
       
        # #17.1 VM Online FileShare Cutover
        # step_sql_vm_online_fileshare_cutover(test)
        
        # #17.2 VM Online FileShare Cutover
        # step_sql_vm_online_fileshare_cutover_Confirm(test, checks=[
        #    test.check("name", "{vmOnlineFsTargetDb}", case_sensitive=False),
        #    test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
        #    test.check("properties.kind", "SqlVm", case_sensitive=False),
        #    test.check("properties.migrationStatus", "Succeeded", case_sensitive=False)
        # ])

        
        #18. VM Online Blob Create
        step_sql_vm_online_blob_create(test, checks=[
            test.check("name", "{vmOnlineBlobTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlVm", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])

        time.sleep(120)
        #19.1 VM Online Blob Cancel
        step_sql_vm_online_blob_cancel(test)

        #19.2 VM Online Blob Cancel Confirm
        step_sql_vm_online_blob_cancel_Confirm(test, checks=[
            test.check("name", "{vmOnlineBlobTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlVm", case_sensitive=False),
            test.check("properties.migrationStatus", "Canceled", case_sensitive=False)
        ])
        
        '''
        #20. MI Offline FS Create
        step_sql_managed_instance_offline_fileshare_create(test, checks=[
            test.check("name", "{miOfflineFsTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlMi", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])
        #21. MI Offline Blob Create
        step_sql_managed_instance_offline_blob_create(test, checks=[
            test.check("name", "{miOfflineBlobTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlMi", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])
        #22. VM Offline FS Create
        step_sql_vm_offline_fileshare_create(test, checks=[
            test.check("name", "{vmOfflineFsTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlVm", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])
        
        #23. VM Offline Blob Create
        step_sql_vm_offline_blob_create(test, checks=[
            test.check("name", "{vmOfflineBlobTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlVm", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])
        '''

        #24. DB Migration Show
        step_sql_db_show(test, checks=[
            test.check("name", "{dbTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlDb", case_sensitive=False)
        ])

        #25.1. DB Migration create
        step_sql_db_offline_create(test, checks=[
            test.check("name", "{dbTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlDb", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])

        #25.2. DB Migration delete
        step_sql_db_offline_delete(test)

        #26.1. DB Migration create
        step_sql_db_offline_create(test, checks=[
            test.check("name", "{dbTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlDb", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False)
        ])

        #26.2. DB Migration cancel
        step_sql_db_offline_cancel(test)

        #27.1. DB Migration selected tables create 
        step_sql_db_offline_tablelist_create(test, checks=[
            test.check("name", "{dbTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlDb", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "InProgress", case_sensitive=False),
            test.check("properties.tableList[0]", "{tableName}", case_sensitive=False)
        ])

        #27.2. DB Migration selected tables check for completion
        step_sql_db_offline_tablelist_complete(test, checks=[
            test.check("name", "{dbTargetDb}", case_sensitive=False),
            test.check("type", "Microsoft.DataMigration/databaseMigrations", case_sensitive=False),
            test.check("properties.kind", "SqlDb", case_sensitive=False),
            test.check("properties.provisioningState", "Succeeded", case_sensitive=False),
            test.check("properties.migrationStatus", "Succeeded", case_sensitive=False),
            test.check("properties.tableList[0]", "{tableName}", case_sensitive=False)
        ])
        
    except Exception as e:
        raise e
    finally:
        cleanup_scenario(test)

