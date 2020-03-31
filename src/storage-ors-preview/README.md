# Azure CLI storage-ors-preview Extension #
This is an extension for storage-ors-preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add -s https://azurecliprod.blob.core.windows.net/cli-extensions/storage_ors_preview-0.1.0-py2.py3-none-any.whl
```

### Prepare
1. Prepare general purpose v2 storage account 
```
az storage account create -n storageaccount -g groupName --kind StorageV2
```

2. Enable Versioning for both source and destination storage accounts
```
az storage account blob-service-properties update --enable-versioning --account-name srcAccountName
```
Note:
- `--enable-versioning` is supported in azure cli 2.3.0, which will be officially release at 2020/03/31.
- Another option to enable Versioning in azure cli is as follows:
```
az storage account blob-service-properties update --account-name srcAccountName --set is_versioning_enabled=True
```
 
3. Enable ChangeFeed for source storage account
```
az storage account blob-service-properties update --enable-change-feed --account-name srcAccountName
```

### Included Features
#### ORS Policy:
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/azure/storage/common/storage-lifecycle-managment-concepts)\

*Examples:*

##### Create ORS Policy on destination storage account
1. Using JSON file or JSON string.
```
az storage account ors-policy create \
    --account-name destAccountName \
    --resource-group groupName \
    --properties @{path}
```
2. Using command parameters.
```
az storage account ors-policy create \
    --account-name destAccountName \
    --resource-group groupName \
    --source-account srcAccountName \
    --destination-account destAccountName \
    --source-container srcContainer \
    --destination-container destContainer \
```
```
az storage account ors-policy create \
    --account-name destAccountName \
    --resource-group groupName \
    --source-account srcAccountName \
    --destination-account destAccountName \
    --source-container srcContainer \
    --min-creation-time '2020-02-19T16:05:00Z' \
    --prefix-match blobA blobB
```

3. Create Object Replication Service Policy to source storage account through policy associated with destination storage account.
```
az storage account ors-policy show -g groupName -n destAccountName --policy-id "3496e652-4cea-4581-b2f7-c86b3971ba92" | az storage account ors-policy create -g ResourceGroupName -n srcAccountName -p "@-"
```

To save the policyId/ruleId in Powershell Scripts, you can use:

`$policyId = (az storage account ors-policy create --account-name accountName --resource-group groupName --properties @{path}) --query policyId)`

`$ruleId = (az storage account ors-policy create --account-name accountName --resource-group groupName --properties @{path}) --query rules.ruleId)`

##### List ORS Policies on storage account
```
az storage account ors-policy list \
    --account-name accountName \
    --resource-group groupName
```

##### Show ORS Policy on storage account
```
az storage account ors-policy show \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Update ORS Policy on storage account
Change source storage account name of existing ORS policy.
```
az storage account ors-policy update \
    --policy-id $policyId \
    --account-name destAccountName \
    --resource-group groupName \
    -s newSourceAccount
```

Update existing ORS policy through json file.
```
az storage account ors-policy update \
    --policy @policy.json \
    --account-name destAccountName \
    --resource-group groupName \
```
##### Add rule to existing ORS Policy
```
az storage account ors-policy rule add \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName \
    --destination-container destContainer \
    --source-container srcContainer  \
    --prefix-match blobA blobB  \
    --min-creation-time '2020-02-19T16:05:00Z' 
```

##### List rules for ORS Policy
```
az storage account ors-policy rule list \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Show properties of specific rule in ORS Policy
```
az storage account ors-policy rule show \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Update properties for secific ORS Policy Rule
Change prefix match filter properties.
```
az storage account ors-policy rule update \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName \
    --prefix-match blobA
```

Change min creation time in filter properties.
```
az storage account ors-policy rule update \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName \
    --min-creation-time '2020-02-19T16:05:00Z'
```
##### Remove the specified rule in existing ORS Policy
```
az storage account ors-policy rule remove \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Delete the specified ORS Policy for storage account
```
az storage account ors-policy delete \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```


If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
