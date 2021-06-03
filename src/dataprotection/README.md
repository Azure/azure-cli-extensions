# Azure CLI dataprotection Extension #
This is the extension for dataprotection

### How to use ###
Install this extension using the below CLI command
```
az extension add --name dataprotection
```

### Included Features ###
#### dataprotection backup-vault ####
##### Create #####
```
az dataprotection backup-vault create --type "None" --location "WestUS" \
    --storage-settings type="LocallyRedundant" datastore-type="VaultStore" --tags key1="val1" \
    --resource-group "SampleResourceGroup" --vault-name "swaggerExample" 
```
##### Create #####
```
az dataprotection backup-vault create --type "systemAssigned" --location "WestUS" \
    --storage-settings type="LocallyRedundant" datastore-type="VaultStore" --tags key1="val1" \
    --resource-group "SampleResourceGroup" --vault-name "swaggerExample" 
```
##### Show #####
```
az dataprotection backup-vault show --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### Show #####
```
az dataprotection backup-vault show --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### Update #####
```
az dataprotection backup-vault update --tags newKey="newVal" --resource-group "SampleResourceGroup" \
    --vault-name "swaggerExample" 
```
##### Show-in-resource-group #####
```
az dataprotection backup-vault show-in-resource-group --resource-group "SampleResourceGroup"
```
##### Show-in-subscription #####
```
az dataprotection backup-vault show-in-subscription
```
##### Delete #####
```
az dataprotection backup-vault delete --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
#### dataprotection operation-status ####
##### Show #####
```
az dataprotection operation-status show \
    --operation-id "MjkxOTMyODMtYTE3My00YzJjLTg5NjctN2E4MDIxNDA3NjA2OzdjNGE2ZWRjLWJjMmItNDRkYi1hYzMzLWY1YzEwNzk5Y2EyOA==" \
    --location "WestUS" 
```
#### dataprotection backup-vault-operation-result ####
##### Show #####
```
az dataprotection backup-vault-operation-result show \
    --operation-id "YWUzNDFkMzQtZmM5OS00MmUyLWEzNDMtZGJkMDIxZjlmZjgzOzdmYzBiMzhmLTc2NmItNDM5NS05OWQ1LTVmOGEzNzg4MWQzNA==" \
    --resource-group "SampleResourceGroup" --vault-name "swaggerExample" 
```
#### dataprotection data-protection ####
##### Check-feature-support #####
```
az dataprotection data-protection check-feature-support --location "WestUS" \
    --parameters "{\\"featureType\\":\\"DataSourceType\\",\\"objectType\\":\\"FeatureValidationRequest\\"}" 
```
#### dataprotection data-protection-operation ####
#### dataprotection backup-policy ####
##### Create #####
```
az dataprotection backup-policy create --name "OSSDBPolicy" \
    --properties "{\\"datasourceTypes\\":[\\"OssDB\\"],\\"objectType\\":\\"BackupPolicy\\",\\"policyRules\\":[{\\"name\\":\\"BackupWeekly\\",\\"backupParameters\\":{\\"backupType\\":\\"Full\\",\\"objectType\\":\\"AzureBackupParams\\"},\\"dataStore\\":{\\"dataStoreType\\":\\"VaultStore\\",\\"objectType\\":\\"DataStoreInfoBase\\"},\\"objectType\\":\\"AzureBackupRule\\",\\"trigger\\":{\\"objectType\\":\\"ScheduleBasedTriggerContext\\",\\"schedule\\":{\\"repeatingTimeIntervals\\":[\\"R/2019-11-20T08:00:00-08:00/P1W\\"]},\\"taggingCriteria\\":[{\\"isDefault\\":true,\\"tagInfo\\":{\\"tagName\\":\\"Default\\"},\\"taggingPriority\\":99},{\\"criteria\\":[{\\"daysOfTheWeek\\":[\\"Sunday\\"],\\"objectType\\":\\"ScheduleBasedBackupCriteria\\",\\"scheduleTimes\\":[\\"2019-03-01T13:00:00Z\\"]}],\\"isDefault\\":false,\\"tagInfo\\":{\\"tagName\\":\\"Weekly\\"},\\"taggingPriority\\":20}]}},{\\"name\\":\\"Default\\",\\"isDefault\\":true,\\"lifecycles\\":[{\\"deleteAfter\\":{\\"duration\\":\\"P1W\\",\\"objectType\\":\\"AbsoluteDeleteOption\\"},\\"sourceDataStore\\":{\\"dataStoreType\\":\\"VaultStore\\",\\"objectType\\":\\"DataStoreInfoBase\\"}}],\\"objectType\\":\\"AzureRetentionRule\\"},{\\"name\\":\\"Weekly\\",\\"isDefault\\":false,\\"lifecycles\\":[{\\"deleteAfter\\":{\\"duration\\":\\"P12W\\",\\"objectType\\":\\"AbsoluteDeleteOption\\"},\\"sourceDataStore\\":{\\"dataStoreType\\":\\"VaultStore\\",\\"objectType\\":\\"DataStoreInfoBase\\"}}],\\"objectType\\":\\"AzureRetentionRule\\"}]}" \
    --resource-group "000pikumar" --vault-name "PrivatePreviewVault" 
```
##### Show #####
```
az dataprotection backup-policy show --name "OSSDBPolicy" --resource-group "000pikumar" \
    --vault-name "PrivatePreviewVault" 
```
##### List #####
```
az dataprotection backup-policy list --resource-group "000pikumar" --vault-name "PrivatePreviewVault"
```
##### Delete #####
```
az dataprotection backup-policy delete --name "OSSDBPolicy" --resource-group "000pikumar" \
    --vault-name "PrivatePreviewVault" 
```
#### dataprotection backup-instance ####
##### Create #####
```
az dataprotection backup-instance create --name "testInstance1" \
    --data-source-info datasource-type="OssDB" object-type="Datasource" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb" resource-location="" resource-name="testdb" resource-type="Microsoft.DBforPostgreSQL/servers/databases" resource-uri="" \
    --data-source-set-info datasource-type="OssDB" object-type="DatasourceSet" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest" resource-location="" resource-name="viveksipgtest" resource-type="Microsoft.DBforPostgreSQL/servers" resource-uri="" \
    --friendly-name "harshitbi2" --object-type "BackupInstance" \
    --policy-id "/subscriptions/04cf684a-d41f-4550-9f70-7708a3a2283b/resourceGroups/000pikumar/providers/Microsoft.DataProtection/Backupvaults/PratikPrivatePreviewVault1/backupPolicies/PratikPolicy1" \
    --policy-parameters data-store-parameters-list={"dataStoreType":"OperationalStore","objectType":"AzureOperationalStoreParameters","resourceGroupId":"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest"} \
    --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 

az dataprotection backup-instance wait --created --name "{myBackupInstance}" --resource-group "{rg_2}"
```
##### Show #####
```
az dataprotection backup-instance show --name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
##### List #####
```
az dataprotection backup-instance list --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### Adhoc-backup #####
```
az dataprotection backup-instance adhoc-backup --name "testInstance1" --rule-name "BackupWeekly" \
    --retention-tag-override "yearly" --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 
```
##### Trigger-rehydrate #####
```
az dataprotection backup-instance trigger-rehydrate --name "testInstance1" --recovery-point-id "hardcodedRP" \
    --rehydration-priority "High" --rehydration-retention-duration "7D" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
##### Trigger-restore #####
```
az dataprotection backup-instance trigger-restore --name "testInstance1" \
    --parameters "{\\"objectType\\":\\"AzureBackupRecoveryPointBasedRestoreRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"restoreTargetInfo\\":{\\"datasourceInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\"Datasource\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"testdb\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"resourceUri\\":\\"\\"},\\"datasourceSetInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\"DatasourceSet\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"viveksipgtest\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers\\",\\"resourceUri\\":\\"\\"},\\"objectType\\":\\"RestoreTargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\"},\\"sourceDataStoreType\\":\\"VaultStore\\"}" \
    --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 
```
##### Trigger-restore #####
```
az dataprotection backup-instance trigger-restore --name "testInstance1" \
    --parameters "{\\"objectType\\":\\"AzureBackupRecoveryPointBasedRestoreRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"restoreTargetInfo\\":{\\"objectType\\":\\"RestoreFilesTargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\",\\"targetDetails\\":{\\"filePrefix\\":\\"restoredblob\\",\\"restoreTargetLocationType\\":\\"AzureBlobs\\",\\"url\\":\\"https://teststorage.blob.core.windows.net/restoretest\\"}},\\"sourceDataStoreType\\":\\"VaultStore\\"}" \
    --resource-group "000pikumar" --vault-name "PrivatePreviewVault1" 
```
##### Trigger-restore #####
```
az dataprotection backup-instance trigger-restore --name "testInstance1" \
    --parameters "{\\"objectType\\":\\"AzureBackupRestoreWithRehydrationRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"rehydrationPriority\\":\\"High\\",\\"rehydrationRetentionDuration\\":\\"7D\\",\\"restoreTargetInfo\\":{\\"datasourceInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\"Datasource\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"testdb\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"resourceUri\\":\\"\\"},\\"datasourceSetInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\"DatasourceSet\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"viveksipgtest\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers\\",\\"resourceUri\\":\\"\\"},\\"objectType\\":\\"RestoreTargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\"},\\"sourceDataStoreType\\":\\"VaultStore\\"}" \
    --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 
```
##### Validate-for-backup #####
```
az dataprotection backup-instance validate-for-backup \
    --data-source-info datasource-type="OssDB" object-type="Datasource" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb" resource-location="" resource-name="testdb" resource-type="Microsoft.DBforPostgreSQL/servers/databases" resource-uri="" \
    --data-source-set-info datasource-type="OssDB" object-type="DatasourceSet" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest" resource-location="" resource-name="viveksipgtest" resource-type="Microsoft.DBforPostgreSQL/servers" resource-uri="" \
    --friendly-name "harshitbi2" --object-type "BackupInstance" \
    --policy-id "/subscriptions/04cf684a-d41f-4550-9f70-7708a3a2283b/resourceGroups/000pikumar/providers/Microsoft.DataProtection/Backupvaults/PratikPrivatePreviewVault1/backupPolicies/PratikPolicy1" \
    --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 
```
##### Validate-for-restore #####
```
az dataprotection backup-instance validate-for-restore --name "testInstance1" \
    --restore-request-object "{\\"objectType\\":\\"AzureBackupRecoveryPointBasedRestoreRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"restoreTargetInfo\\":{\\"datasourceInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\"Datasource\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"testdb\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"resourceUri\\":\\"\\"},\\"datasourceSetInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\"DatasourceSet\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"viveksipgtest\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers\\",\\"resourceUri\\":\\"\\"},\\"objectType\\":\\"RestoreTargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\"},\\"sourceDataStoreType\\":\\"VaultStore\\"}" \
    --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1" 
```
##### Delete #####
```
az dataprotection backup-instance delete --name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
#### dataprotection recovery-point ####
##### List #####
```
az dataprotection recovery-point list --backup-instance-name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
##### Show #####
```
az dataprotection recovery-point show --backup-instance-name "testInstance1" \
    --recovery-point-id "7fb2cddd-c5b3-44f6-a0d9-db3c4f9d5f25" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" 
```
#### dataprotection job ####
##### List #####
```
az dataprotection job list --resource-group "BugBash1" --vault-name "BugBashVaultForCCYv11"
```
##### Show #####
```
az dataprotection job show --job-id "3c60cb49-63e8-4b21-b9bd-26277b3fdfae" --resource-group "BugBash1" \
    --vault-name "BugBashVaultForCCYv11" 
```
#### dataprotection restorable-time-range ####
##### Find #####
```
az dataprotection restorable-time-range find --backup-instances "zblobbackuptestsa58" \
    --end-time "2021-02-24T00:35:17.6829685Z" --source-data-store-type "OperationalStore" \
    --start-time "2020-10-17T23:28:17.6829685Z" --resource-group "Blob-Backup" --vault-name "ZBlobBackupVaultBVTD3" 
```
#### dataprotection export-job ####
##### Trigger #####
```
az dataprotection export-job trigger --resource-group "SwaggerTestRg" --vault-name "NetSDKTestRsVault"
```
#### dataprotection export-job-operation-result ####
##### Show #####
```
az dataprotection export-job-operation-result show --operation-id "00000000-0000-0000-0000-000000000000" \
    --resource-group "SwaggerTestRg" --vault-name "NetSDKTestRsVault" 
```