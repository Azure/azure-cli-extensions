# Azure CLI DataBox Extension #
This is a extension for DataBox features.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name databox
```

### Included Features
#### Manage DataBox jobs:


##### Create a DataBox job.

```
az databox job create \
    --resource-group rg \
    --name job_name \ 
    --location westus \
    --sku DataBox \
    --contact-name contact_name \
    --phone phone \
    --email-list email_list \
    --street-address1 street_address1 \
    --city Redmond \
    --state-or-province state_or_province \
    --country US \
    --postal-code postal_code \
    --company-name company_name \
    --storage-account storage_account_1 storage_account_2 \
    --staging-storage-account staging_storage_account \
    --resource-group-for-managed-disk rg-for-managed-disk
```

##### Update a DataBox job.
```
az databox job update \
    --resource-group rg \
    --name job_name \
    --contact-name contact_name \
    --email-list email_list
```

##### Get the information for a given job.
```
az databox job show \
    --resource-group rg \
    --name job_name
```

##### List all the jobs under the given resource group or the given subscription
```
az databox job list
```
```
az databox job list \
    --resource-group rg
```

##### List the credentials for a given job.
```
az databox job list-credentials \
    --resource-group rg \
    --name job_name
```

##### Cancel a job.
```
az databox job cancel \
    --resource-group rg \
    --name job_name \
    --reason reason
```

##### Delete a job.
```
az databox job delete \
    --resource-group rg \
    --name job_name
```

If you have issues, please give feedback by opening an issue at https://github.com/Azure/azure-cli-extensions/issues.