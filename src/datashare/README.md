# Azure CLI datashare Extension #
This package is for the 'datashare' extension, i.e. 'az datashare'. More info on what is [Data Share](https://docs.microsoft.com/azure/data-share/).

### How to use ###
Install this extension using the below CLI command
```
az extension add --name datashare
```

Register DataShare Resource Provider for your default susbcription.
```
az provider register -n "Microsoft.DataShare"
```

### Included Features
#### Datashare Account Management
*Examples:*

##### Create a Datashare Account

```
az datashare account create \
--location "West US 2" \
--tags tag1=Red tag2=White \
--name "cli_test_account" \
--resource-group "datashare_provider_rg"
```

##### Wait for the Datashare Account to be provisioned
```
az datashare account wait \
--name "cli_test_account" \
--resource-group "datashare_provider_rg" \
--created
```

#### Datashare Resource Management for a Provider
*Examples:*

##### Create a Datashare
```
az datashare create \
--account-name "cli_test_account" \
--resource-group "datashare_provider_rg" \
--description "share description" \
--share-kind "CopyBased" \
--terms "Confidential" \
--name "cli_test_share"
```

##### Create a Data Set
```
az datashare dataset create \
--account-name "cli_test_account" \
--name "cli_test_data_set" \
--resource-group "datashare_provider_rg" \
--share-name "cli_test_share" \
--dataset "{\"container_name\":\"mycontainer\",\"storage_account_name\":\"mysa\",\"kind\":\"Container\"}"
```

Please make sure the datashare account has the right permission of the data source when creating a data set upon it.
For instance, you can use `az datashare account show` to get 'identity.principalId' of the account, then assign the right role to it.
```
az role assignment create \
--role "Storage Blob Data Reader" \
--assignee-object-id {DatashareAccountPrincipalId} \
--assignee-principal-type ServicePrincipal \
--scope {StorageAccountId}
```

##### Create a Synchronization Setting
```
az datashare synchronization-setting create \
--account-name cli_test_account \
--resource-group datashare_provider_rg \
--share-name cli_test_share \
--name cli_test_synchronization_setting \
--recurrence-interval Day \
--synchronization-time "2020-04-05 10:50:00 +00:00" \
--kind ScheduleBased
```

##### List Synchronization History
```
az datashare synchronization list \
--account-name "cli_test_account" \
--resource-group "datashare_provider_rg" \
--share-name "cli_test_share"
```

##### Create a Datashare Invitation
```
az datashare invitation create \
--account-name "cli_test_account" \
--target-email "myname@microsoft.com" \
--name "cli_test_invitation" \
--resource-group "datashare_provider_rg" \
--share-name "cli_test_share"
```

##### List Share Subscriptions
```
az datashare provider-share-subscription list \
--account-name "cli_test_account" \
--resource-group "datashare_provider_rg" \
--share-name "cli_test_share"
```
Share subscriptions are created by Datashare consumers when they accept invitations.

##### Revoke Datashare for a Share Subscription
```
az datashare provider-share-subscription revoke \
--account-name "cli_test_account" \
--share-subscription "{ProviderShareSubscriptionObjectId}" \
--resource-group "datashare_provider_rg" \
--share-name "cli_test_share"
```

##### Reinstate Datashare for a Share Subscription
```
az datashare provider-share-subscription reinstate \
--account-name "cli_test_account" \
--share-subscription "{ProviderShareSubscriptionObjectId}" \
--resource-group "datashare_provider_rg" \
--share-name "cli_test_share"
```

#### Datashare Resource Management for a Consumer
*Examples:*

##### List received Invitations
```
az datashare consumer invitation list
```

##### Create a Share Subscription from an Invitation
```
az datashare consumer share-subscription create \
--account-name "cli_test_consumer_account" \
--resource-group "datashare_consumer_rg" \
--invitation-id "{InvitationId1}" \
--source-share-location "sourceShareLocation" \
--name "cli_test_share_subscription"
```

##### List Source Data Sets in the Share Subscription
```
az datashare consumer share-subscription list-source-dataset \
--account-name "cli_test_consumer_account" \
--resource-group "datashare_consumer_rg" \
--share-subscription-name "cli_test_share_subscription"
```

##### Create a Data Set Mapping of the Source Data Set
```
az datashare consumer dataset-mapping create \
--account-name "cli_test_consumer_account" \
--name "cli_test_data_set_mapping" \
--resource-group "datashare_consumer_rg" \
--share-subscription-name "cli_test_share_subscription" \
--mapping "{\"data_set_id\":\"2036a39f-add6-4347-9c82-a424dfaf4e8d\", \
\"container_name\":\"newcontainer\", \"storage_account_name\":\"consumersa\", \
\"kind\":\"BlobFolder\",\"prefix\":\"myprefix\"}"
```
Please make sure the datashare consumer account has the right permission of the data target when creating a data set mapping on it. For instance, you can use `az datashare account show` to get 'identity.principalId' of the account, then assign the right role to it.
```
az role assignment create \
--role "Storage Blob Data Contributor" \
--assignee-object-id "{ConsumerDatashareAccountPrincipalId}" \
--assignee-principal-type ServicePrincipal \
--scope "{ConsumerStorageAccountId}"
```

##### List the synchronization settings of the Source Datashare
```
az datashare consumer share-subscription list-source-share-synchronization-setting \
--account-name "cli_test_consumer_account" \
--resource-group "datashare_consumer_rg" \
--share-subscription-name "cli_test_share_subscription"
```

##### Create a trigger for the Share Subsciption
```
az datashare consumer trigger create \
--account-name "cli_test_consumer_account" \
--resource-group "datashare_consumer_rg" \
--share-subscription-name "cli_test_share_subscription" \
--name "cli_test_trigger" \
--recurrence-interval Day \
--synchronization-time "2020-04-05 10:50:00 +00:00" \
--kind ScheduleBased
```

##### Start a synchronization for the Share Subscription
```
az datashare consumer share-subscription synchronization start \
--account-name "cli_test_consumer_account" \
--resource-group "datashare_consumer_rg" \
--share-subscription-name "cli_test_share_subscription" \
--synchronization-mode "Incremental"
```
