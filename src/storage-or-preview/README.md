# Azure CLI storage-or-preview Extension #
This is an extension for storage-or-preview features.

### How to use ###
Install this extension using the below CLI command after release:
```
az extension add -n storage-or-preview
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
- `--enable-versioning` is supported in [azure cli 2.3.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest#install), which will be officially release at 2020/03/31.
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
az storage account or-policy create \
    --account-name destAccountName \
    --resource-group groupName \
    --properties @{path}
```
2. Using command parameters.
```
az storage account or-policy create \
    --account-name destAccountName \
    --resource-group groupName \
    --source-account srcAccountName \
    --destination-account destAccountName \
    --source-container srcContainer \
    --destination-container destContainer \
```
```
az storage account or-policy create \
    --account-name destAccountName \
    --resource-group groupName \
    --source-account srcAccountName \
    --destination-account destAccountName \
    --source-container srcContainer \
    --min-creation-time '2020-02-19T16:05:00Z' \
    --prefix-match blobA blobB
```

3. Create Object Replication Policy to source storage account through policy associated with destination storage account.
```
az storage account or-policy show -g groupName -n destAccountName --policy-id "3496e652-4cea-4581-b2f7-c86b3971ba92" | az storage account or-policy create -g ResourceGroupName -n srcAccountName -p "@-"
```

To save the policyId/ruleId in PowerShell Scripts, you can use:

`$policyId = (az storage account or-policy create --account-name accountName --resource-group groupName --properties @{path}) --query policyId)`

`$ruleId = (az storage account or-policy create --account-name accountName --resource-group groupName --properties @{path}) --query rules.ruleId)`

##### List OR Policies on storage account
```
az storage account or-policy list \
    --account-name accountName \
    --resource-group groupName
```

##### Show OR Policy on storage account
```
az storage account or-policy show \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Update OR Policy on storage account
Change source storage account name of existing OR policy.
```
az storage account or-policy update \
    --policy-id $policyId \
    --account-name destAccountName \
    --resource-group groupName \
    -s newSourceAccount
```

Update existing OR policy through json file.
```
az storage account or-policy update \
    --policy @policy.json \
    --account-name destAccountName \
    --resource-group groupName \
```
##### Add rule to existing OR Policy
```
az storage account or-policy rule add \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName \
    --destination-container destContainer \
    --source-container srcContainer  \
    --prefix-match blobA blobB  \
    --min-creation-time '2020-02-19T16:05:00Z' 
```

##### List rules for OR Policy
```
az storage account or-policy rule list \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Show properties of specific rule in OR Policy
```
az storage account or-policy rule show \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Update properties for specific OR Policy Rule
Change prefix match filter properties.
```
az storage account or-policy rule update \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName \
    --prefix-match blobA
```

Change min creation time in filter properties.
```
az storage account or-policy rule update \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName \
    --min-creation-time '2020-02-19T16:05:00Z'
```
##### Remove the specified rule in existing OR Policy
```
az storage account or-policy rule remove \
    --rule-id $ruleId \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```

##### Delete the specified OR Policy for storage account
```
az storage account or-policy delete \
    --policy-id $policyId \
    --account-name accountName \
    --resource-group groupName
```


If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
