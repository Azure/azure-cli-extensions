# Azure CLI dataprotection Extension #
This is the extension for dataprotection

### How to use ###
Install this extension using the below CLI command
```
az extension add --name dataprotection
```

### Included Features ###
#### Configure backup ####
##### Initialize configure backup request #####
```
az dataprotection backup-instance initialize --datasource-type AzureDisk -l southeastasia \
    --policy-id {disk_policy_id} --datasource-id {disk_id}
```

Please copy paste the output of the above command and save it in a json file. e.g. backup_instance.json.
Based on datasource type, you might have to edit the json file and add some parameters.

##### Validate configure backup request #####
```
az dataprotection backup-instance validate-for-backup -g sarath-rg --vault-name sarath-vault --backup-instance backup_instance.json
```

If validation fails then please fix the error by following the recommendations.
##### Configure backup #####
```
az dataprotection backup-instance create -g MyResourceGroup --vault-name MyVault --backup-instance backup_instance.json
```
#### Create Policy ####
##### Get default policy template #####
```
az dataprotection backup-policy get-default-policy-template --datasource-type AzureDisk
```
Save the output of above command in a json file. e.g. defaultpolicy.json
##### Add retention rule to default policy #####
```
az dataprotection backup-policy retention-rule create-lifecycle --retention-duration-count 12 \
    --retention-duration-type Days --source-datastore OperationalStore
```
Save the output of above command in a json file e.g. lifecycle.json
```
az dataprotection backup-policy retention-rule set --lifecycles lifecycle.json --name Daily --policy defaultpolicy.json
```
Save the output of above command in a json file e.g. editedpolicy.json
##### Add tag rule to policy #####
```
az dataprotection backup-policy tag create-absolute-criteria --absolute-criteria FirstOfDay
```
Save the output of above command in a json file e.g. criteria.json
```
az dataprotection backup-policy tag set --criteria criteria.json --name Daily --policy editedpolicy.json
```
##### Create backup policy #####
```
az dataprotection backup-policy create -g sarath-rg --vault-name sarath-vault -n mypolicy --policy policy.json
```
#### Restore a backup instance ####
##### Initialize restore request for item recovery #####
```
az dataprotection backup-instance restore initialize-for-data-recovery --datasource-type AzureBlob \
    --restore-location centraluseuap --source-datastore OperationalStore --backup-instance-id {backup_instance_id} \
    --point-in-time 2021-05-26T15:00:00 --container-list container1 container2
```
##### Initialize restore request for data recovery #####
```
az dataprotection backup-instance restore initialize-for-data-recovery --datasource-type AzureDisk \
    --restore-location centraluseuap --source-datastore OperationalStore --target-resource-id {restore_disk_id} \
    --recovery-point-id b7e6f082-b310-11eb-8f55-9cfce85d4fae
```
##### Validate restore request #####
```
az dataprotection backup-instance validate-for-restore --name "testInstance1" --resource-group "000pikumar" \
    --vault-name "PratikPrivatePreviewVault1" --restore-request-object restore_request.json
```
##### Trigger restore #####
```
az dataprotection backup-instance restore trigger -g sarath-rg --vault-name sarath-vault \
    --backup-instance-name {backup_instance_name} --restore=request-object restore_request.json
```
#### dataprotection backup-vault ####
##### Create #####
```
az dataprotection backup-vault create --type "None" --location "WestUS" \
    --storage-settings type="LocallyRedundant" datastore-type="VaultStore" --tags key1="val1" \
    --resource-group "SampleResourceGroup" --vault-name "swaggerExample" 
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
##### Delete #####
```
az dataprotection backup-vault delete --resource-group "SampleResourceGroup" --vault-name "swaggerExample"
```
#### dataprotection backup-policy ####
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