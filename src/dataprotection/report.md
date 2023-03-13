# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az dataprotection|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az dataprotection` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az dataprotection backup-vault|BackupVaults|[commands](#CommandsInBackupVaults)|
|az dataprotection backup-policy|BackupPolicies|[commands](#CommandsInBackupPolicies)|
|az dataprotection backup-instance|BackupInstances|[commands](#CommandsInBackupInstances)|
|az dataprotection recovery-point|RecoveryPoints|[commands](#CommandsInRecoveryPoints)|
|az dataprotection job|Jobs|[commands](#CommandsInJobs)|
|az dataprotection restorable-time-range|RestorableTimeRanges|[commands](#CommandsInRestorableTimeRanges)|
|az dataprotection resource-guard|ResourceGuards|[commands](#CommandsInResourceGuards)|

## COMMANDS
### <a name="CommandsInBackupInstances">Commands in `az dataprotection backup-instance` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection backup-instance list](#BackupInstancesList)|List|[Parameters](#ParametersBackupInstancesList)|[Example](#ExamplesBackupInstancesList)|
|[az dataprotection backup-instance show](#BackupInstancesGet)|Get|[Parameters](#ParametersBackupInstancesGet)|[Example](#ExamplesBackupInstancesGet)|
|[az dataprotection backup-instance create](#BackupInstancesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBackupInstancesCreateOrUpdate#Create)|[Example](#ExamplesBackupInstancesCreateOrUpdate#Create)|
|[az dataprotection backup-instance delete](#BackupInstancesDelete)|Delete|[Parameters](#ParametersBackupInstancesDelete)|[Example](#ExamplesBackupInstancesDelete)|
|[az dataprotection backup-instance adhoc-backup](#BackupInstancesAdhocBackup)|AdhocBackup|[Parameters](#ParametersBackupInstancesAdhocBackup)|[Example](#ExamplesBackupInstancesAdhocBackup)|
|[az dataprotection backup-instance restore trigger](#BackupInstancesTriggerRestore)|TriggerRestore|[Parameters](#ParametersBackupInstancesTriggerRestore)|[Example](#ExamplesBackupInstancesTriggerRestore)|
|[az dataprotection backup-instance resume-protection](#BackupInstancesResumeProtection)|ResumeProtection|[Parameters](#ParametersBackupInstancesResumeProtection)|[Example](#ExamplesBackupInstancesResumeProtection)|
|[az dataprotection backup-instance stop-protection](#BackupInstancesStopProtection)|StopProtection|[Parameters](#ParametersBackupInstancesStopProtection)|[Example](#ExamplesBackupInstancesStopProtection)|
|[az dataprotection backup-instance suspend-backup](#BackupInstancesSuspendBackups)|SuspendBackups|[Parameters](#ParametersBackupInstancesSuspendBackups)|[Example](#ExamplesBackupInstancesSuspendBackups)|
|[az dataprotection backup-instance validate-for-backup](#BackupInstancesValidateForBackup)|ValidateForBackup|[Parameters](#ParametersBackupInstancesValidateForBackup)|[Example](#ExamplesBackupInstancesValidateForBackup)|
|[az dataprotection backup-instance validate-for-restore](#BackupInstancesValidateForRestore)|ValidateForRestore|[Parameters](#ParametersBackupInstancesValidateForRestore)|[Example](#ExamplesBackupInstancesValidateForRestore)|

### <a name="CommandsInBackupPolicies">Commands in `az dataprotection backup-policy` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection backup-policy list](#BackupPoliciesList)|List|[Parameters](#ParametersBackupPoliciesList)|[Example](#ExamplesBackupPoliciesList)|
|[az dataprotection backup-policy show](#BackupPoliciesGet)|Get|[Parameters](#ParametersBackupPoliciesGet)|[Example](#ExamplesBackupPoliciesGet)|
|[az dataprotection backup-policy create](#BackupPoliciesCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBackupPoliciesCreateOrUpdate#Create)|[Example](#ExamplesBackupPoliciesCreateOrUpdate#Create)|
|[az dataprotection backup-policy delete](#BackupPoliciesDelete)|Delete|[Parameters](#ParametersBackupPoliciesDelete)|[Example](#ExamplesBackupPoliciesDelete)|

### <a name="CommandsInBackupVaults">Commands in `az dataprotection backup-vault` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection backup-vault show](#BackupVaultsGet)|Get|[Parameters](#ParametersBackupVaultsGet)|[Example](#ExamplesBackupVaultsGet)|
|[az dataprotection backup-vault create](#BackupVaultsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersBackupVaultsCreateOrUpdate#Create)|[Example](#ExamplesBackupVaultsCreateOrUpdate#Create)|
|[az dataprotection backup-vault update](#BackupVaultsUpdate)|Update|[Parameters](#ParametersBackupVaultsUpdate)|[Example](#ExamplesBackupVaultsUpdate)|
|[az dataprotection backup-vault delete](#BackupVaultsDelete)|Delete|[Parameters](#ParametersBackupVaultsDelete)|[Example](#ExamplesBackupVaultsDelete)|

### <a name="CommandsInJobs">Commands in `az dataprotection job` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection job list](#JobsList)|List|[Parameters](#ParametersJobsList)|[Example](#ExamplesJobsList)|
|[az dataprotection job show](#JobsGet)|Get|[Parameters](#ParametersJobsGet)|[Example](#ExamplesJobsGet)|

### <a name="CommandsInRecoveryPoints">Commands in `az dataprotection recovery-point` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection recovery-point list](#RecoveryPointsList)|List|[Parameters](#ParametersRecoveryPointsList)|[Example](#ExamplesRecoveryPointsList)|
|[az dataprotection recovery-point show](#RecoveryPointsGet)|Get|[Parameters](#ParametersRecoveryPointsGet)|[Example](#ExamplesRecoveryPointsGet)|

### <a name="CommandsInResourceGuards">Commands in `az dataprotection resource-guard` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection resource-guard show](#ResourceGuardsGet)|Get|[Parameters](#ParametersResourceGuardsGet)|[Example](#ExamplesResourceGuardsGet)|
|[az dataprotection resource-guard create](#ResourceGuardsPut)|Put|[Parameters](#ParametersResourceGuardsPut)|[Example](#ExamplesResourceGuardsPut)|
|[az dataprotection resource-guard delete](#ResourceGuardsDelete)|Delete|[Parameters](#ParametersResourceGuardsDelete)|[Example](#ExamplesResourceGuardsDelete)|

### <a name="CommandsInRestorableTimeRanges">Commands in `az dataprotection restorable-time-range` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az dataprotection restorable-time-range find](#RestorableTimeRangesFind)|Find|[Parameters](#ParametersRestorableTimeRangesFind)|[Example](#ExamplesRestorableTimeRangesFind)|


## COMMAND DETAILS

### group `az dataprotection backup-instance`
#### <a name="BackupInstancesList">Command `az dataprotection backup-instance list`</a>

##### <a name="ExamplesBackupInstancesList">Example</a>
```
az dataprotection backup-instance list --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|

#### <a name="BackupInstancesGet">Command `az dataprotection backup-instance show`</a>

##### <a name="ExamplesBackupInstancesGet">Example</a>
```
az dataprotection backup-instance show --name "testInstance1" --resource-group "000pikumar" --vault-name \
"PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|

#### <a name="BackupInstancesCreateOrUpdate#Create">Command `az dataprotection backup-instance create`</a>

##### <a name="ExamplesBackupInstancesCreateOrUpdate#Create">Example</a>
```
az dataprotection backup-instance create --name "testInstance1" --data-source-info datasource-type="Microsoft.DBforPost\
greSQL/servers/databases" object-type="Datasource" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/res\
ourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb" \
resource-location="" resource-name="testdb" resource-type="Microsoft.DBforPostgreSQL/servers/databases" \
resource-uri="" --data-source-set-info datasource-type="Microsoft.DBforPostgreSQL/servers/databases" \
object-type="DatasourceSet" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgte\
st/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest" resource-location="" resource-name="viveksipgtest" \
resource-type="Microsoft.DBforPostgreSQL/servers" resource-uri="" --policy-parameters objectType="SecretStoreBasedAuthC\
redentials" secretStoreResource={"secretStoreType":"AzureKeyVault","uri":"https://samplevault.vault.azure.net/secrets/c\
redentials"} --friendly-name "harshitbi2" --object-type "BackupInstance" --policy-id "/subscriptions/04cf684a-d41f-4550\
-9f70-7708a3a2283b/resourceGroups/000pikumar/providers/Microsoft.DataProtection/Backupvaults/PratikPrivatePreviewVault1\
/backupPolicies/PratikPolicy1" --policy-parameters data-store-parameters-list={"dataStoreType":"OperationalStore","obje\
ctType":"AzureOperationalStoreParameters","resourceGroupId":"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resour\
ceGroups/viveksipgtest"} --validation-type "ShallowValidation" --tags key1="val1" --resource-group "000pikumar" \
--vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--tags**|dictionary|Proxy Resource tags.|tags|tags|
|**--friendly-name**|string|Gets or sets the Backup Instance friendly name.|friendly_name|friendlyName|
|**--data-source-info**|object|Gets or sets the data source information.|data_source_info|dataSourceInfo|
|**--data-source-set-info**|object|Gets or sets the data source set information.|data_source_set_info|dataSourceSetInfo|
|**--secret-store-based-auth-credentials**|object|Secret store based authentication credentials.|secret_store_based_auth_credentials|SecretStoreBasedAuthCredentials|
|**--validation-type**|choice|Specifies the type of validation. In case of DeepValidation, all validations from /validateForBackup API will run again.|validation_type|validationType|
|**--object-type**|string||object_type|objectType|
|**--policy-id**|string||policy_id|policyId|
|**--policy-parameters**|object|Policy parameters for the backup instance|policy_parameters|policyParameters|

#### <a name="BackupInstancesDelete">Command `az dataprotection backup-instance delete`</a>

##### <a name="ExamplesBackupInstancesDelete">Example</a>
```
az dataprotection backup-instance delete --name "testInstance1" --resource-group "000pikumar" --vault-name \
"PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|

#### <a name="BackupInstancesAdhocBackup">Command `az dataprotection backup-instance adhoc-backup`</a>

##### <a name="ExamplesBackupInstancesAdhocBackup">Example</a>
```
az dataprotection backup-instance adhoc-backup --name "testInstance1" --rule-name "BackupWeekly" \
--retention-tag-override "yearly" --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesAdhocBackup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--rule-name**|string||rule_name|ruleName|
|**--retention-tag-override**|string||retention_tag_override|retentionTagOverride|

#### <a name="BackupInstancesTriggerRestore">Command `az dataprotection backup-instance restore trigger`</a>

##### <a name="ExamplesBackupInstancesTriggerRestore">Example</a>
```
az dataprotection backup-instance restore trigger --name "testInstance1" --restore-request-object \
"{\\"objectType\\":\\"AzureBackupRecoveryPointBasedRestoreRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"restore\
TargetInfo\\":{\\"datasourceAuthCredentials\\":{\\"objectType\\":\\"SecretStoreBasedAuthCredentials\\",\\"secretStoreRe\
source\\":{\\"secretStoreType\\":\\"AzureKeyVault\\",\\"uri\\":\\"https://samplevault.vault.azure.net/secrets/credentia\
ls\\"}},\\"datasourceInfo\\":{\\"datasourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"objectType\\":\
\\"Datasource\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/p\
roviders/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/targetdb\\",\\"resourceLocation\\":\\"\\",\\"resourc\
eName\\":\\"targetdb\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"resourceUri\\":\\"\\"},\
\\"datasourceSetInfo\\":{\\"datasourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"objectType\\":\\"Dat\
asourceSet\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/prov\
iders/Microsoft.DBforPostgreSQL/servers/viveksipgtest\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"viveksipgt\
est\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers\\",\\"resourceUri\\":\\"\\"},\\"objectType\\":\\"Restore\
TargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\"},\\"sourceDataStoreType\
\\":\\"VaultStore\\",\\"sourceResourceId\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/vivek\
sipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\"}" --resource-group "000pikumar" \
--vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ExamplesBackupInstancesTriggerRestore">Example</a>
```
az dataprotection backup-instance restore trigger --name "testInstance1" --restore-request-object \
"{\\"objectType\\":\\"AzureBackupRecoveryPointBasedRestoreRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"restore\
TargetInfo\\":{\\"objectType\\":\\"RestoreFilesTargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\
\\":\\"southeastasia\\",\\"targetDetails\\":{\\"filePrefix\\":\\"restoredblob\\",\\"restoreTargetLocationType\\":\\"Azu\
reBlobs\\",\\"url\\":\\"https://teststorage.blob.core.windows.net/restoretest\\"}},\\"sourceDataStoreType\\":\\"VaultSt\
ore\\",\\"sourceResourceId\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/provi\
ders/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\"}" --resource-group "000pikumar" --vault-name \
"PrivatePreviewVault1"
```
##### <a name="ExamplesBackupInstancesTriggerRestore">Example</a>
```
az dataprotection backup-instance restore trigger --name "testInstance1" --restore-request-object \
"{\\"objectType\\":\\"AzureBackupRestoreWithRehydrationRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"rehydratio\
nPriority\\":\\"High\\",\\"rehydrationRetentionDuration\\":\\"7D\\",\\"restoreTargetInfo\\":{\\"datasourceInfo\\":{\\"d\
atasourceType\\":\\"OssDB\\",\\"objectType\\":\\"Datasource\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82\
e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\
\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"testdb\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/serve\
rs/databases\\",\\"resourceUri\\":\\"\\"},\\"datasourceSetInfo\\":{\\"datasourceType\\":\\"OssDB\\",\\"objectType\\":\\\
"DatasourceSet\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/\
providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"viveks\
ipgtest\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers\\",\\"resourceUri\\":\\"\\"},\\"objectType\\":\\"Res\
toreTargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\"},\\"sourceDataStore\
Type\\":\\"VaultStore\\",\\"sourceResourceId\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/v\
iveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\"}" --resource-group \
"000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesTriggerRestore">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--parameters**|object|Request body for operation|parameters|parameters|

#### <a name="BackupInstancesResumeProtection">Command `az dataprotection backup-instance resume-protection`</a>

##### <a name="ExamplesBackupInstancesResumeProtection">Example</a>
```
az dataprotection backup-instance resume-protection --name "testbi" --resource-group "testrg" --vault-name "testvault"
```
##### <a name="ParametersBackupInstancesResumeProtection">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string||backup_instance_name|backupInstanceName|

#### <a name="BackupInstancesStopProtection">Command `az dataprotection backup-instance stop-protection`</a>

##### <a name="ExamplesBackupInstancesStopProtection">Example</a>
```
az dataprotection backup-instance stop-protection --name "testbi" --resource-group "testrg" --vault-name "testvault"
```
##### <a name="ParametersBackupInstancesStopProtection">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string||backup_instance_name|backupInstanceName|

#### <a name="BackupInstancesSuspendBackups">Command `az dataprotection backup-instance suspend-backup`</a>

##### <a name="ExamplesBackupInstancesSuspendBackups">Example</a>
```
az dataprotection backup-instance suspend-backup --name "testbi" --resource-group "testrg" --vault-name "testvault"
```
##### <a name="ParametersBackupInstancesSuspendBackups">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string||backup_instance_name|backupInstanceName|

#### <a name="BackupInstancesValidateForBackup">Command `az dataprotection backup-instance validate-for-backup`</a>

##### <a name="ExamplesBackupInstancesValidateForBackup">Example</a>
```
az dataprotection backup-instance validate-for-backup --data-source-info datasource-type="OssDB" \
object-type="Datasource" resource-id="/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/\
providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb" resource-location="" \
resource-name="testdb" resource-type="Microsoft.DBforPostgreSQL/servers/databases" resource-uri="" \
--data-source-set-info datasource-type="OssDB" object-type="DatasourceSet" resource-id="/subscriptions/f75d8d8b-6735-46\
97-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest" \
resource-location="" resource-name="viveksipgtest" resource-type="Microsoft.DBforPostgreSQL/servers" resource-uri="" \
--policy-parameters objectType="SecretStoreBasedAuthCredentials" secretStoreResource={"secretStoreType":"AzureKeyVault"\
,"uri":"https://samplevault.vault.azure.net/secrets/credentials"} --friendly-name "harshitbi2" --object-type \
"BackupInstance" --policy-id "/subscriptions/04cf684a-d41f-4550-9f70-7708a3a2283b/resourceGroups/000pikumar/providers/M\
icrosoft.DataProtection/Backupvaults/PratikPrivatePreviewVault1/backupPolicies/PratikPolicy1" --resource-group \
"000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesValidateForBackup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--data-source-info**|object|Gets or sets the data source information.|data_source_info|dataSourceInfo|
|**--object-type**|string||object_type|objectType|
|**--policy-id**|string||policy_id|policyId|
|**--friendly-name**|string|Gets or sets the Backup Instance friendly name.|friendly_name|friendlyName|
|**--data-source-set-info**|object|Gets or sets the data source set information.|data_source_set_info|dataSourceSetInfo|
|**--secret-store-based-auth-credentials**|object|Secret store based authentication credentials.|secret_store_based_auth_credentials|SecretStoreBasedAuthCredentials|
|**--validation-type**|choice|Specifies the type of validation. In case of DeepValidation, all validations from /validateForBackup API will run again.|validation_type|validationType|
|**--policy-parameters**|object|Policy parameters for the backup instance|policy_parameters|policyParameters|

#### <a name="BackupInstancesValidateForRestore">Command `az dataprotection backup-instance validate-for-restore`</a>

##### <a name="ExamplesBackupInstancesValidateForRestore">Example</a>
```
az dataprotection backup-instance validate-for-restore --name "testInstance1" --restore-request-object \
"{\\"objectType\\":\\"AzureBackupRecoveryPointBasedRestoreRequest\\",\\"recoveryPointId\\":\\"hardcodedRP\\",\\"restore\
TargetInfo\\":{\\"datasourceAuthCredentials\\":{\\"objectType\\":\\"SecretStoreBasedAuthCredentials\\",\\"secretStoreRe\
source\\":{\\"secretStoreType\\":\\"AzureKeyVault\\",\\"uri\\":\\"https://samplevault.vault.azure.net/secrets/credentia\
ls\\"}},\\"datasourceInfo\\":{\\"datasourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"objectType\\":\
\\"Datasource\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/p\
roviders/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/targetdb\\",\\"resourceLocation\\":\\"\\",\\"resourc\
eName\\":\\"targetdb\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"resourceUri\\":\\"\\"},\
\\"datasourceSetInfo\\":{\\"datasourceType\\":\\"Microsoft.DBforPostgreSQL/servers/databases\\",\\"objectType\\":\\"Dat\
asourceSet\\",\\"resourceID\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/viveksipgtest/prov\
iders/Microsoft.DBforPostgreSQL/servers/viveksipgtest\\",\\"resourceLocation\\":\\"\\",\\"resourceName\\":\\"viveksipgt\
est\\",\\"resourceType\\":\\"Microsoft.DBforPostgreSQL/servers\\",\\"resourceUri\\":\\"\\"},\\"objectType\\":\\"Restore\
TargetInfo\\",\\"recoveryOption\\":\\"FailIfExists\\",\\"restoreLocation\\":\\"southeastasia\\"},\\"sourceDataStoreType\
\\":\\"VaultStore\\",\\"sourceResourceId\\":\\"/subscriptions/f75d8d8b-6735-4697-82e1-1a7a3ff0d5d4/resourceGroups/vivek\
sipgtest/providers/Microsoft.DBforPostgreSQL/servers/viveksipgtest/databases/testdb\\"}" --resource-group "000pikumar" \
--vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersBackupInstancesValidateForRestore">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--restore-request-object**|object|Gets or sets the restore request object.|restore_request_object|restoreRequestObject|

### group `az dataprotection backup-policy`
#### <a name="BackupPoliciesList">Command `az dataprotection backup-policy list`</a>

##### <a name="ExamplesBackupPoliciesList">Example</a>
```
az dataprotection backup-policy list --resource-group "000pikumar" --vault-name "PrivatePreviewVault"
```
##### <a name="ParametersBackupPoliciesList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|

#### <a name="BackupPoliciesGet">Command `az dataprotection backup-policy show`</a>

##### <a name="ExamplesBackupPoliciesGet">Example</a>
```
az dataprotection backup-policy show --name "OSSDBPolicy" --resource-group "000pikumar" --vault-name \
"PrivatePreviewVault"
```
##### <a name="ParametersBackupPoliciesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-policy-name**|string||backup_policy_name|backupPolicyName|

#### <a name="BackupPoliciesCreateOrUpdate#Create">Command `az dataprotection backup-policy create`</a>

##### <a name="ExamplesBackupPoliciesCreateOrUpdate#Create">Example</a>
```
az dataprotection backup-policy create --name "OSSDBPolicy" --properties "{\\"datasourceTypes\\":[\\"OssDB\\"],\\"objec\
tType\\":\\"BackupPolicy\\",\\"policyRules\\":[{\\"name\\":\\"BackupWeekly\\",\\"backupParameters\\":{\\"backupType\\":\
\\"Full\\",\\"objectType\\":\\"AzureBackupParams\\"},\\"dataStore\\":{\\"dataStoreType\\":\\"VaultStore\\",\\"objectTyp\
e\\":\\"DataStoreInfoBase\\"},\\"objectType\\":\\"AzureBackupRule\\",\\"trigger\\":{\\"objectType\\":\\"ScheduleBasedTr\
iggerContext\\",\\"schedule\\":{\\"repeatingTimeIntervals\\":[\\"R/2019-11-20T08:00:00-08:00/P1W\\"]},\\"taggingCriteri\
a\\":[{\\"isDefault\\":true,\\"tagInfo\\":{\\"tagName\\":\\"Default\\"},\\"taggingPriority\\":99},{\\"criteria\\":[{\\"\
daysOfTheWeek\\":[\\"Sunday\\"],\\"objectType\\":\\"ScheduleBasedBackupCriteria\\",\\"scheduleTimes\\":[\\"2019-03-01T1\
3:00:00Z\\"]}],\\"isDefault\\":false,\\"tagInfo\\":{\\"tagName\\":\\"Weekly\\"},\\"taggingPriority\\":20}]}},{\\"name\\\
":\\"Default\\",\\"isDefault\\":true,\\"lifecycles\\":[{\\"deleteAfter\\":{\\"duration\\":\\"P1W\\",\\"objectType\\":\\\
"AbsoluteDeleteOption\\"},\\"sourceDataStore\\":{\\"dataStoreType\\":\\"VaultStore\\",\\"objectType\\":\\"DataStoreInfo\
Base\\"}}],\\"objectType\\":\\"AzureRetentionRule\\"},{\\"name\\":\\"Weekly\\",\\"isDefault\\":false,\\"lifecycles\\":[\
{\\"deleteAfter\\":{\\"duration\\":\\"P12W\\",\\"objectType\\":\\"AbsoluteDeleteOption\\"},\\"sourceDataStore\\":{\\"da\
taStoreType\\":\\"VaultStore\\",\\"objectType\\":\\"DataStoreInfoBase\\"}}],\\"objectType\\":\\"AzureRetentionRule\\"}]\
}" --resource-group "000pikumar" --vault-name "PrivatePreviewVault"
```
##### <a name="ParametersBackupPoliciesCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-policy-name**|string|Name of the policy|backup_policy_name|backupPolicyName|
|**--backup-policy**|object|Rule based backup policy|backup_policy|BackupPolicy|

#### <a name="BackupPoliciesDelete">Command `az dataprotection backup-policy delete`</a>

##### <a name="ExamplesBackupPoliciesDelete">Example</a>
```
az dataprotection backup-policy delete --name "OSSDBPolicy" --resource-group "000pikumar" --vault-name \
"PrivatePreviewVault"
```
##### <a name="ParametersBackupPoliciesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-policy-name**|string||backup_policy_name|backupPolicyName|

### group `az dataprotection backup-vault`
#### <a name="BackupVaultsGet">Command `az dataprotection backup-vault show`</a>

##### <a name="ExamplesBackupVaultsGet">Example</a>
```
az dataprotection backup-vault show --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### <a name="ExamplesBackupVaultsGet">Example</a>
```
az dataprotection backup-vault show --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### <a name="ParametersBackupVaultsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|

#### <a name="BackupVaultsCreateOrUpdate#Create">Command `az dataprotection backup-vault create`</a>

##### <a name="ExamplesBackupVaultsCreateOrUpdate#Create">Example</a>
```
az dataprotection backup-vault create --type "None" --location "WestUS" --azure-monitor-alerts-for-job-failures \
"Enabled" --storage-settings type="LocallyRedundant" datastore-type="VaultStore" --tags key1="val1" --resource-group \
"SampleResourceGroup" --vault-name "swaggerExample"
```
##### <a name="ExamplesBackupVaultsCreateOrUpdate#Create">Example</a>
```
az dataprotection backup-vault create --type "systemAssigned" --location "WestUS" --azure-monitor-alerts-for-job-failur\
es "Enabled" --storage-settings type="LocallyRedundant" datastore-type="VaultStore" --tags key1="val1" \
--resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### <a name="ParametersBackupVaultsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--storage-settings**|array|Storage Settings|storage_settings|storageSettings|
|**--e-tag**|string|Optional ETag.|e_tag|eTag|
|**--location**|string|Resource location.|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--type**|string|The identityType which can be either SystemAssigned or None|type|type|
|**--alerts-for-all-job-failures**|choice||alerts_for_all_job_failures|alertsForAllJobFailures|

#### <a name="BackupVaultsUpdate">Command `az dataprotection backup-vault update`</a>

##### <a name="ExamplesBackupVaultsUpdate">Example</a>
```
az dataprotection backup-vault update --azure-monitor-alerts-for-job-failures "Enabled" --tags newKey="newVal" \
--resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### <a name="ParametersBackupVaultsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--alerts-for-all-job-failures**|choice||alerts_for_all_job_failures|alertsForAllJobFailures|
|**--type**|string|The identityType which can be either SystemAssigned or None|type|type|

#### <a name="BackupVaultsDelete">Command `az dataprotection backup-vault delete`</a>

##### <a name="ExamplesBackupVaultsDelete">Example</a>
```
az dataprotection backup-vault delete --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
##### <a name="ParametersBackupVaultsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|

### group `az dataprotection job`
#### <a name="JobsList">Command `az dataprotection job list`</a>

##### <a name="ExamplesJobsList">Example</a>
```
az dataprotection job list --resource-group "BugBash1" --vault-name "BugBashVaultForCCYv11"
```
##### <a name="ParametersJobsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|

#### <a name="JobsGet">Command `az dataprotection job show`</a>

##### <a name="ExamplesJobsGet">Example</a>
```
az dataprotection job show --job-id "3c60cb49-63e8-4b21-b9bd-26277b3fdfae" --resource-group "BugBash1" --vault-name \
"BugBashVaultForCCYv11"
```
##### <a name="ParametersJobsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--job-id**|string|The Job ID. This is a GUID-formatted string (e.g. 00000000-0000-0000-0000-000000000000).|job_id|jobId|

### group `az dataprotection recovery-point`
#### <a name="RecoveryPointsList">Command `az dataprotection recovery-point list`</a>

##### <a name="ExamplesRecoveryPointsList">Example</a>
```
az dataprotection recovery-point list --backup-instance-name "testInstance1" --resource-group "000pikumar" \
--vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersRecoveryPointsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--filter**|string|OData filter options.|filter|$filter|
|**--skip-token**|string|skipToken Filter.|skip_token|$skipToken|

#### <a name="RecoveryPointsGet">Command `az dataprotection recovery-point show`</a>

##### <a name="ExamplesRecoveryPointsGet">Example</a>
```
az dataprotection recovery-point show --backup-instance-name "testInstance1" --recovery-point-id \
"7fb2cddd-c5b3-44f6-a0d9-db3c4f9d5f25" --resource-group "000pikumar" --vault-name "PratikPrivatePreviewVault1"
```
##### <a name="ParametersRecoveryPointsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--recovery-point-id**|string||recovery_point_id|recoveryPointId|

### group `az dataprotection resource-guard`
#### <a name="ResourceGuardsGet">Command `az dataprotection resource-guard show`</a>

##### <a name="ExamplesResourceGuardsGet">Example</a>
```
az dataprotection resource-guard show --resource-group "SampleResourceGroup" --resource-guard-name "swaggerExample"
```
##### <a name="ParametersResourceGuardsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--resource-guards-name**|string|The name of ResourceGuard|resource_guards_name|resourceGuardsName|

#### <a name="ResourceGuardsPut">Command `az dataprotection resource-guard create`</a>

##### <a name="ExamplesResourceGuardsPut">Example</a>
```
az dataprotection resource-guard create --location "WestUS" --tags key1="val1" --resource-group "SampleResourceGroup" \
--resource-guard-name "swaggerExample"
```
##### <a name="ParametersResourceGuardsPut">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--resource-guards-name**|string|The name of ResourceGuard|resource_guards_name|resourceGuardsName|
|**--e-tag**|string|Optional ETag.|e_tag|eTag|
|**--location**|string|Resource location.|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--type**|string|The identityType which can be either SystemAssigned or None|type|type|
|**--vault-critical-operation-exclusion-list**|array|List of critical operations which are not protected by this resourceGuard|vault_critical_operation_exclusion_list|vaultCriticalOperationExclusionList|

#### <a name="ResourceGuardsDelete">Command `az dataprotection resource-guard delete`</a>

##### <a name="ExamplesResourceGuardsDelete">Example</a>
```
az dataprotection resource-guard delete --resource-group "SampleResourceGroup" --resource-guard-name "swaggerExample"
```
##### <a name="ParametersResourceGuardsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--resource-guards-name**|string|The name of ResourceGuard|resource_guards_name|resourceGuardsName|

### group `az dataprotection restorable-time-range`
#### <a name="RestorableTimeRangesFind">Command `az dataprotection restorable-time-range find`</a>

##### <a name="ExamplesRestorableTimeRangesFind">Example</a>
```
az dataprotection restorable-time-range find --backup-instance-name "zblobbackuptestsa58" --end-time \
"2021-02-24T00:35:17.6829685Z" --source-data-store-type "OperationalStore" --start-time "2020-10-17T23:28:17.6829685Z" \
--resource-group "Blob-Backup" --vault-name "ZBlobBackupVaultBVTD3"
```
##### <a name="ParametersRestorableTimeRangesFind">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group where the backup vault is present.|resource_group_name|resourceGroupName|
|**--vault-name**|string|The name of the backup vault.|vault_name|vaultName|
|**--backup-instance-name**|string|The name of the backup instance|backup_instance_name|backupInstanceName|
|**--source-data-store-type**|choice|Gets or sets the type of the source data store.|source_data_store_type|sourceDataStoreType|
|**--start-time**|string|Start time for the List Restore Ranges request. ISO 8601 format.|start_time|startTime|
|**--end-time**|string|End time for the List Restore Ranges request. ISO 8601 format.|end_time|endTime|
