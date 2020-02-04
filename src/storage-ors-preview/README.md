# Azure CLI storage-ors-preview Extension #
This is a extension for storage-ors-preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add -s https://azurecliprod.blob.core.windows.net/cli-extensions/storage_ors_preview-0.1.0-py2.py3-none-any.whl
```

### Included Features
#### ORS Policy:
Manage data policy rules associated with a storage account: [more info](https://docs.microsoft.com/azure/storage/common/storage-lifecycle-managment-concepts)\

*Examples:*

##### Create ORS Policy on destination storage account
1. Using JSON file or JSON string
```
az storage account ors-policy create \
    --account-name accountName \
    --resource-group groupName \
    --properties @{path}
```
2. Using command parameters
```
az storage account ors-policy create \
    --account-name accountName \
    --resource-group groupName \
    --source-account srcAccountName \
    --destination-account destAccountName \
    --source-container srcContainer \
    --destination-container destContainer
```
3. Create Object Replication Service Policy to source storage account through policy associated with destination storage account.
```
az storage account ors-policy show -g ResourceGroupName -n destAccountName --policy-id "3496e652-4cea-4581-b2f7-c86b3971ba92" | az storage account ors-policy create -g ResourceGroupName -n srcAccountName -p "@-"
```

To save the policyId/ruleId in Powershell Scripts, you can use:
`$policyId = (az storage account ors-policy create --account-name accountName --resource-group groupName --properties @{path}) --query policyId)`
`$ruleId = (az storage account ors-policy create --account-name accountName --resource-group groupName --properties @{path}) --query rules.ruleId)`

##### List ORS Policies on storage account
```
az storage account ors-policy list --account-name accountName --resource-group groupName
```

##### Show ORS Policy on storage account
```
az storage account ors-policy show --policy-id policyId --account-name accountName --resource-group groupName
```

##### Update ORS Policy on storage account
```
az storage account ors-policy update --policy-id policyId --account-name accountName --resource-group groupName -s newSourceAccount
```

##### Add rule to ORS Policy
```
az storage account ors-policy rule add --destination-account destAccountName \
    --source-container srcContainer --policy-id $policyId --account-name accountName --resource-group groupName
```

##### List rules for ORS Policy
```
az storage account ors-policy rule list --policy-id $policyId --account-name accountName --resource-group groupName
```

##### Show rule for ORS Policy
```
az storage account ors-policy rule show --rule-id $ruleId --policy-id $policyId --account-name accountName --resource-group groupName
```

##### Update properties for ORS Policy Rule
```
az storage account ors-policy rule remove --rule-id $ruleId --policy-id $policyId --account-name accountName --resource-group groupName --prefix-match blobA
```

##### Remove rule for ORS Policy
```
az storage account ors-policy rule remove --rule-id $ruleId --policy-id $policyId --account-name accountName --resource-group groupName
```

##### Remove ORS Policy on storage account
```
az storage account ors-policy remove --policy-id policyId --account-name accountName --resource-group groupName
```


If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.
