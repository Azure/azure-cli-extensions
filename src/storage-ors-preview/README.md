# Azure CLI storage-ors-preview Extension #
This is a extension for storage-ors-preview features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name storage-ors-preview
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

##### Remove rule for ORS Policy
```
az storage account ors-policy rule remove --rule-id $ruleId --policy-id $policyId --account-name accountName --resource-group groupName
```


If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.