# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az datashare|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az datashare` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az datashare|Shares|[commands](#CommandsInShares)|
|az datashare account|Accounts|[commands](#CommandsInAccounts)|
|az datashare consumer-invitation|ConsumerInvitations|[commands](#CommandsInConsumerInvitations)|
|az datashare consumer-source-data-set|ConsumerSourceDataSets|[commands](#CommandsInConsumerSourceDataSets)|
|az datashare data-set|DataSets|[commands](#CommandsInDataSets)|
|az datashare data-set-mapping|DataSetMappings|[commands](#CommandsInDataSetMappings)|
|az datashare email-registration|EmailRegistrations|[commands](#CommandsInEmailRegistrations)|
|az datashare invitation|Invitations|[commands](#CommandsInInvitations)|
|az datashare provider-share-subscription|ProviderShareSubscriptions|[commands](#CommandsInProviderShareSubscriptions)|
|az datashare share-subscription|ShareSubscriptions|[commands](#CommandsInShareSubscriptions)|
|az datashare synchronization-setting|SynchronizationSettings|[commands](#CommandsInSynchronizationSettings)|
|az datashare trigger|Triggers|[commands](#CommandsInTriggers)|

## COMMANDS
### <a name="CommandsInShares">Commands in `az datashare` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare list](#SharesListByAccount)|ListByAccount|[Parameters](#ParametersSharesListByAccount)|[Example](#ExamplesSharesListByAccount)|
|[az datashare show](#SharesGet)|Get|[Parameters](#ParametersSharesGet)|[Example](#ExamplesSharesGet)|
|[az datashare create](#SharesCreate)|Create|[Parameters](#ParametersSharesCreate)|[Example](#ExamplesSharesCreate)|
|[az datashare delete](#SharesDelete)|Delete|[Parameters](#ParametersSharesDelete)|[Example](#ExamplesSharesDelete)|
|[az datashare list-synchronization](#SharesListSynchronizations)|ListSynchronizations|[Parameters](#ParametersSharesListSynchronizations)|[Example](#ExamplesSharesListSynchronizations)|
|[az datashare list-synchronization-detail](#SharesListSynchronizationDetails)|ListSynchronizationDetails|[Parameters](#ParametersSharesListSynchronizationDetails)|[Example](#ExamplesSharesListSynchronizationDetails)|

### <a name="CommandsInAccounts">Commands in `az datashare account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare account list](#AccountsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersAccountsListByResourceGroup)|[Example](#ExamplesAccountsListByResourceGroup)|
|[az datashare account list](#AccountsListBySubscription)|ListBySubscription|[Parameters](#ParametersAccountsListBySubscription)|[Example](#ExamplesAccountsListBySubscription)|
|[az datashare account show](#AccountsGet)|Get|[Parameters](#ParametersAccountsGet)|[Example](#ExamplesAccountsGet)|
|[az datashare account create](#AccountsCreate)|Create|[Parameters](#ParametersAccountsCreate)|[Example](#ExamplesAccountsCreate)|
|[az datashare account update](#AccountsUpdate)|Update|[Parameters](#ParametersAccountsUpdate)|[Example](#ExamplesAccountsUpdate)|
|[az datashare account delete](#AccountsDelete)|Delete|[Parameters](#ParametersAccountsDelete)|[Example](#ExamplesAccountsDelete)|

### <a name="CommandsInConsumerInvitations">Commands in `az datashare consumer-invitation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare consumer-invitation show](#ConsumerInvitationsGet)|Get|[Parameters](#ParametersConsumerInvitationsGet)|[Example](#ExamplesConsumerInvitationsGet)|
|[az datashare consumer-invitation list-invitation](#ConsumerInvitationsListInvitations)|ListInvitations|[Parameters](#ParametersConsumerInvitationsListInvitations)|[Example](#ExamplesConsumerInvitationsListInvitations)|
|[az datashare consumer-invitation reject-invitation](#ConsumerInvitationsRejectInvitation)|RejectInvitation|[Parameters](#ParametersConsumerInvitationsRejectInvitation)|[Example](#ExamplesConsumerInvitationsRejectInvitation)|

### <a name="CommandsInConsumerSourceDataSets">Commands in `az datashare consumer-source-data-set` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare consumer-source-data-set list](#ConsumerSourceDataSetsListByShareSubscription)|ListByShareSubscription|[Parameters](#ParametersConsumerSourceDataSetsListByShareSubscription)|[Example](#ExamplesConsumerSourceDataSetsListByShareSubscription)|

### <a name="CommandsInDataSets">Commands in `az datashare data-set` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare data-set list](#DataSetsListByShare)|ListByShare|[Parameters](#ParametersDataSetsListByShare)|[Example](#ExamplesDataSetsListByShare)|
|[az datashare data-set show](#DataSetsGet)|Get|[Parameters](#ParametersDataSetsGet)|[Example](#ExamplesDataSetsGet)|
|[az datashare data-set create](#DataSetsCreate)|Create|[Parameters](#ParametersDataSetsCreate)|[Example](#ExamplesDataSetsCreate)|
|[az datashare data-set delete](#DataSetsDelete)|Delete|[Parameters](#ParametersDataSetsDelete)|[Example](#ExamplesDataSetsDelete)|

### <a name="CommandsInDataSetMappings">Commands in `az datashare data-set-mapping` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare data-set-mapping list](#DataSetMappingsListByShareSubscription)|ListByShareSubscription|[Parameters](#ParametersDataSetMappingsListByShareSubscription)|[Example](#ExamplesDataSetMappingsListByShareSubscription)|
|[az datashare data-set-mapping show](#DataSetMappingsGet)|Get|[Parameters](#ParametersDataSetMappingsGet)|[Example](#ExamplesDataSetMappingsGet)|
|[az datashare data-set-mapping create](#DataSetMappingsCreate)|Create|[Parameters](#ParametersDataSetMappingsCreate)|[Example](#ExamplesDataSetMappingsCreate)|
|[az datashare data-set-mapping delete](#DataSetMappingsDelete)|Delete|[Parameters](#ParametersDataSetMappingsDelete)|[Example](#ExamplesDataSetMappingsDelete)|

### <a name="CommandsInEmailRegistrations">Commands in `az datashare email-registration` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare email-registration activate-email](#EmailRegistrationsActivateEmail)|ActivateEmail|[Parameters](#ParametersEmailRegistrationsActivateEmail)|[Example](#ExamplesEmailRegistrationsActivateEmail)|
|[az datashare email-registration register-email](#EmailRegistrationsRegisterEmail)|RegisterEmail|[Parameters](#ParametersEmailRegistrationsRegisterEmail)|[Example](#ExamplesEmailRegistrationsRegisterEmail)|

### <a name="CommandsInInvitations">Commands in `az datashare invitation` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare invitation list](#InvitationsListByShare)|ListByShare|[Parameters](#ParametersInvitationsListByShare)|[Example](#ExamplesInvitationsListByShare)|
|[az datashare invitation show](#InvitationsGet)|Get|[Parameters](#ParametersInvitationsGet)|[Example](#ExamplesInvitationsGet)|
|[az datashare invitation create](#InvitationsCreate)|Create|[Parameters](#ParametersInvitationsCreate)|[Example](#ExamplesInvitationsCreate)|
|[az datashare invitation delete](#InvitationsDelete)|Delete|[Parameters](#ParametersInvitationsDelete)|[Example](#ExamplesInvitationsDelete)|

### <a name="CommandsInProviderShareSubscriptions">Commands in `az datashare provider-share-subscription` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare provider-share-subscription list](#ProviderShareSubscriptionsListByShare)|ListByShare|[Parameters](#ParametersProviderShareSubscriptionsListByShare)|[Example](#ExamplesProviderShareSubscriptionsListByShare)|
|[az datashare provider-share-subscription show](#ProviderShareSubscriptionsGetByShare)|GetByShare|[Parameters](#ParametersProviderShareSubscriptionsGetByShare)|[Example](#ExamplesProviderShareSubscriptionsGetByShare)|
|[az datashare provider-share-subscription adjust](#ProviderShareSubscriptionsAdjust)|Adjust|[Parameters](#ParametersProviderShareSubscriptionsAdjust)|[Example](#ExamplesProviderShareSubscriptionsAdjust)|
|[az datashare provider-share-subscription reinstate](#ProviderShareSubscriptionsReinstate)|Reinstate|[Parameters](#ParametersProviderShareSubscriptionsReinstate)|[Example](#ExamplesProviderShareSubscriptionsReinstate)|
|[az datashare provider-share-subscription revoke](#ProviderShareSubscriptionsRevoke)|Revoke|[Parameters](#ParametersProviderShareSubscriptionsRevoke)|[Example](#ExamplesProviderShareSubscriptionsRevoke)|

### <a name="CommandsInShareSubscriptions">Commands in `az datashare share-subscription` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare share-subscription list](#ShareSubscriptionsListByAccount)|ListByAccount|[Parameters](#ParametersShareSubscriptionsListByAccount)|[Example](#ExamplesShareSubscriptionsListByAccount)|
|[az datashare share-subscription show](#ShareSubscriptionsGet)|Get|[Parameters](#ParametersShareSubscriptionsGet)|[Example](#ExamplesShareSubscriptionsGet)|
|[az datashare share-subscription create](#ShareSubscriptionsCreate)|Create|[Parameters](#ParametersShareSubscriptionsCreate)|[Example](#ExamplesShareSubscriptionsCreate)|
|[az datashare share-subscription delete](#ShareSubscriptionsDelete)|Delete|[Parameters](#ParametersShareSubscriptionsDelete)|[Example](#ExamplesShareSubscriptionsDelete)|
|[az datashare share-subscription cancel-synchronization](#ShareSubscriptionsCancelSynchronization)|CancelSynchronization|[Parameters](#ParametersShareSubscriptionsCancelSynchronization)|[Example](#ExamplesShareSubscriptionsCancelSynchronization)|
|[az datashare share-subscription list-source-share-synchronization-setting](#ShareSubscriptionsListSourceShareSynchronizationSettings)|ListSourceShareSynchronizationSettings|[Parameters](#ParametersShareSubscriptionsListSourceShareSynchronizationSettings)|[Example](#ExamplesShareSubscriptionsListSourceShareSynchronizationSettings)|
|[az datashare share-subscription list-synchronization](#ShareSubscriptionsListSynchronizations)|ListSynchronizations|[Parameters](#ParametersShareSubscriptionsListSynchronizations)|[Example](#ExamplesShareSubscriptionsListSynchronizations)|
|[az datashare share-subscription list-synchronization-detail](#ShareSubscriptionsListSynchronizationDetails)|ListSynchronizationDetails|[Parameters](#ParametersShareSubscriptionsListSynchronizationDetails)|[Example](#ExamplesShareSubscriptionsListSynchronizationDetails)|
|[az datashare share-subscription synchronize](#ShareSubscriptionsSynchronize)|Synchronize|[Parameters](#ParametersShareSubscriptionsSynchronize)|[Example](#ExamplesShareSubscriptionsSynchronize)|

### <a name="CommandsInSynchronizationSettings">Commands in `az datashare synchronization-setting` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare synchronization-setting list](#SynchronizationSettingsListByShare)|ListByShare|[Parameters](#ParametersSynchronizationSettingsListByShare)|[Example](#ExamplesSynchronizationSettingsListByShare)|
|[az datashare synchronization-setting show](#SynchronizationSettingsGet)|Get|[Parameters](#ParametersSynchronizationSettingsGet)|[Example](#ExamplesSynchronizationSettingsGet)|
|[az datashare synchronization-setting create](#SynchronizationSettingsCreate)|Create|[Parameters](#ParametersSynchronizationSettingsCreate)|[Example](#ExamplesSynchronizationSettingsCreate)|
|[az datashare synchronization-setting delete](#SynchronizationSettingsDelete)|Delete|[Parameters](#ParametersSynchronizationSettingsDelete)|[Example](#ExamplesSynchronizationSettingsDelete)|

### <a name="CommandsInTriggers">Commands in `az datashare trigger` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az datashare trigger list](#TriggersListByShareSubscription)|ListByShareSubscription|[Parameters](#ParametersTriggersListByShareSubscription)|[Example](#ExamplesTriggersListByShareSubscription)|
|[az datashare trigger show](#TriggersGet)|Get|[Parameters](#ParametersTriggersGet)|[Example](#ExamplesTriggersGet)|
|[az datashare trigger create](#TriggersCreate)|Create|[Parameters](#ParametersTriggersCreate)|[Example](#ExamplesTriggersCreate)|
|[az datashare trigger delete](#TriggersDelete)|Delete|[Parameters](#ParametersTriggersDelete)|[Example](#ExamplesTriggersDelete)|


## COMMAND DETAILS
### group `az datashare`
#### <a name="SharesListByAccount">Command `az datashare list`</a>

##### <a name="ExamplesSharesListByAccount">Example</a>
```
az datashare list --account-name "Account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersSharesListByAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--skip-token**|string|Continuation Token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="SharesGet">Command `az datashare show`</a>

##### <a name="ExamplesSharesGet">Example</a>
```
az datashare show --account-name "Account1" --resource-group "SampleResourceGroup" --name "Share1"
```
##### <a name="ParametersSharesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to retrieve.|share_name|shareName|

#### <a name="SharesCreate">Command `az datashare create`</a>

##### <a name="ExamplesSharesCreate">Example</a>
```
az datashare create --account-name "Account1" --resource-group "SampleResourceGroup" --description "share description" \
--share-kind "CopyBased" --terms "Confidential" --name "Share1"
```
##### <a name="ParametersSharesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--description**|string|Share description.|description|description|
|**--share-kind**|choice|Share kind.|share_kind|shareKind|
|**--terms**|string|Share terms.|terms|terms|

#### <a name="SharesDelete">Command `az datashare delete`</a>

##### <a name="ExamplesSharesDelete">Example</a>
```
az datashare delete --account-name "Account1" --resource-group "SampleResourceGroup" --name "Share1"
```
##### <a name="ParametersSharesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|

#### <a name="SharesListSynchronizations">Command `az datashare list-synchronization`</a>

##### <a name="ExamplesSharesListSynchronizations">Example</a>
```
az datashare list-synchronization --account-name "Account1" --resource-group "SampleResourceGroup" --name "Share1"
```
##### <a name="ParametersSharesListSynchronizations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="SharesListSynchronizationDetails">Command `az datashare list-synchronization-detail`</a>

##### <a name="ExamplesSharesListSynchronizationDetails">Example</a>
```
az datashare list-synchronization-detail --account-name "Account1" --resource-group "SampleResourceGroup" --name \
"Share1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
```
##### <a name="ParametersSharesListSynchronizationDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|
|**--consumer-email**|string|Email of the user who created the synchronization|consumer_email|consumerEmail|
|**--consumer-name**|string|Name of the user who created the synchronization|consumer_name|consumerName|
|**--consumer-tenant-name**|string|Tenant name of the consumer who created the synchronization|consumer_tenant_name|consumerTenantName|
|**--duration-ms**|integer|synchronization duration|duration_ms|durationMs|
|**--end-time**|date-time|End time of synchronization|end_time|endTime|
|**--message**|string|message of synchronization|message|message|
|**--start-time**|date-time|start time of synchronization|start_time|startTime|
|**--status**|string|Raw Status|status|status|
|**--synchronization-id**|string|Synchronization id|synchronization_id|synchronizationId|

### group `az datashare account`
#### <a name="AccountsListByResourceGroup">Command `az datashare account list`</a>

##### <a name="ExamplesAccountsListByResourceGroup">Example</a>
```
az datashare account list --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

#### <a name="AccountsListBySubscription">Command `az datashare account list`</a>

##### <a name="ExamplesAccountsListBySubscription">Example</a>
```
az datashare account list
```
##### <a name="ParametersAccountsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

#### <a name="AccountsGet">Command `az datashare account show`</a>

##### <a name="ExamplesAccountsGet">Example</a>
```
az datashare account show --name "Account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|

#### <a name="AccountsCreate">Command `az datashare account create`</a>

##### <a name="ExamplesAccountsCreate">Example</a>
```
az datashare account create --location "West US 2" --tags tag1="Red" tag2="White" --name "Account1" --resource-group \
"SampleResourceGroup"
```
##### <a name="ParametersAccountsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--location**|string|Location of the azure resource.|location|location|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|

#### <a name="AccountsUpdate">Command `az datashare account update`</a>

##### <a name="ExamplesAccountsUpdate">Example</a>
```
az datashare account update --name "Account1" --tags tag1="Red" tag2="White" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|

#### <a name="AccountsDelete">Command `az datashare account delete`</a>

##### <a name="ExamplesAccountsDelete">Example</a>
```
az datashare account delete --name "Account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|

### group `az datashare consumer-invitation`
#### <a name="ConsumerInvitationsGet">Command `az datashare consumer-invitation show`</a>

##### <a name="ExamplesConsumerInvitationsGet">Example</a>
```
az datashare consumer-invitation show --invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location "East US 2"
```
##### <a name="ParametersConsumerInvitationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|Location of the invitation|location|location|
|**--invitation-id**|string|An invitation id|invitation_id|invitationId|

#### <a name="ConsumerInvitationsListInvitations">Command `az datashare consumer-invitation list-invitation`</a>

##### <a name="ExamplesConsumerInvitationsListInvitations">Example</a>
```
az datashare consumer-invitation list-invitation
```
##### <a name="ParametersConsumerInvitationsListInvitations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|The continuation token|skip_token|$skipToken|

#### <a name="ConsumerInvitationsRejectInvitation">Command `az datashare consumer-invitation reject-invitation`</a>

##### <a name="ExamplesConsumerInvitationsRejectInvitation">Example</a>
```
az datashare consumer-invitation reject-invitation --invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" --location \
"East US 2"
```
##### <a name="ParametersConsumerInvitationsRejectInvitation">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|Location of the invitation|location|location|
|**--invitation-id**|string|Unique id of the invitation.|invitation_id|invitationId|

### group `az datashare consumer-source-data-set`
#### <a name="ConsumerSourceDataSetsListByShareSubscription">Command `az datashare consumer-source-data-set list`</a>

##### <a name="ExamplesConsumerSourceDataSetsListByShareSubscription">Example</a>
```
az datashare consumer-source-data-set list --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-subscription-name "Share1"
```
##### <a name="ParametersConsumerSourceDataSetsListByShareSubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

### group `az datashare data-set`
#### <a name="DataSetsListByShare">Command `az datashare data-set list`</a>

##### <a name="ExamplesDataSetsListByShare">Example</a>
```
az datashare data-set list --account-name "Account1" --resource-group "SampleResourceGroup" --share-name "Share1"
```
##### <a name="ParametersDataSetsListByShare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="DataSetsGet">Command `az datashare data-set show`</a>

##### <a name="ExamplesDataSetsGet">Example</a>
```
az datashare data-set show --account-name "Account1" --name "Dataset1" --resource-group "SampleResourceGroup" \
--share-name "Share1"
```
##### <a name="ParametersDataSetsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|dataSetName|

#### <a name="DataSetsCreate">Command `az datashare data-set create`</a>

##### <a name="ExamplesDataSetsCreate">Example</a>
```
az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"Blob\\",\\"properties\\":{\\"containe\
rName\\":\\"C1\\",\\"filePath\\":\\"file21\\",\\"resourceGroup\\":\\"SampleResourceGroup\\",\\"storageAccountName\\":\\\
"storage2\\",\\"subscriptionId\\":\\"433a8dfd-e5d5-4e77-ad86-90acdc75eb1a\\"}}" --name "Dataset1" --resource-group \
"SampleResourceGroup" --share-name "Share1"
az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"KustoCluster\\",\\"properties\\":{\\"\
kustoClusterResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/pro\
viders/Microsoft.Kusto/clusters/Cluster1\\"}}" --name "Dataset1" --resource-group "SampleResourceGroup" --share-name \
"Share1"
az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"KustoDatabase\\",\\"properties\\":{\\\
"kustoDatabaseResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/p\
roviders/Microsoft.Kusto/clusters/Cluster1/databases/Database1\\"}}" --name "Dataset1" --resource-group \
"SampleResourceGroup" --share-name "Share1"
az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"KustoTable\\",\\"properties\\":{\\"ku\
stoDatabaseResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/prov\
iders/Microsoft.Kusto/clusters/Cluster1/databases/Database1\\",\\"tableLevelSharingProperties\\":{\\"externalTablesToEx\
clude\\":[\\"test11\\",\\"test12\\"],\\"externalTablesToInclude\\":[\\"test9\\",\\"test10\\"],\\"materializedViewsToExc\
lude\\":[\\"test7\\",\\"test8\\"],\\"materializedViewsToInclude\\":[\\"test5\\",\\"test6\\"],\\"tablesToExclude\\":[\\"\
test3\\",\\"test4\\"],\\"tablesToInclude\\":[\\"test1\\",\\"test2\\"]}}}" --name "Dataset1" --resource-group \
"SampleResourceGroup" --share-name "Share1"
az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"SqlDBTable\\",\\"properties\\":{\\"da\
tabaseName\\":\\"SqlDB1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd-e5d5-4e77-ad\
86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\\":\\"Table1\
\\"}}" --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1"
az datashare data-set create --account-name "Account1" --data-set "{\\"kind\\":\\"SqlDWTable\\",\\"properties\\":{\\"da\
taWarehouseName\\":\\"DataWarehouse1\\",\\"schemaName\\":\\"dbo\\",\\"sqlServerResourceId\\":\\"/subscriptions/433a8dfd\
-e5d5-4e77-ad86-90acdc75eb1a/resourceGroups/SampleResourceGroup/providers/Microsoft.Sql/servers/Server1\\",\\"tableName\
\\":\\"Table1\\"}}" --name "Dataset1" --resource-group "SampleResourceGroup" --share-name "Share1"
az datashare data-set create --account-name "sourceAccount" --data-set "{\\"kind\\":\\"SynapseWorkspaceSqlPoolTable\\",\
\\"properties\\":{\\"synapseWorkspaceSqlPoolTableResourceId\\":\\"/subscriptions/0f3dcfc3-18f8-4099-b381-8353e19d43a7/r\
esourceGroups/SampleResourceGroup/providers/Microsoft.Synapse/workspaces/ExampleWorkspace/sqlPools/ExampleSqlPool/schem\
as/dbo/tables/table1\\"}}" --name "dataset1" --resource-group "SampleResourceGroup" --share-name "share1"
```
##### <a name="ParametersDataSetsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to add the data set to.|share_name|shareName|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|dataSetName|
|**--data-set**|object|The new data set information.|data_set|dataSet|

#### <a name="DataSetsDelete">Command `az datashare data-set delete`</a>

##### <a name="ExamplesDataSetsDelete">Example</a>
```
az datashare data-set delete --account-name "Account1" --name "Dataset1" --resource-group "SampleResourceGroup" \
--share-name "Share1"
```
##### <a name="ParametersDataSetsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--data-set-name**|string|The name of the dataSet.|data_set_name|dataSetName|

### group `az datashare data-set-mapping`
#### <a name="DataSetMappingsListByShareSubscription">Command `az datashare data-set-mapping list`</a>

##### <a name="ExamplesDataSetMappingsListByShareSubscription">Example</a>
```
az datashare data-set-mapping list --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-subscription-name "ShareSubscription1"
```
##### <a name="ParametersDataSetMappingsListByShareSubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="DataSetMappingsGet">Command `az datashare data-set-mapping show`</a>

##### <a name="ExamplesDataSetMappingsGet">Example</a>
```
az datashare data-set-mapping show --account-name "Account1" --name "DatasetMapping1" --resource-group \
"SampleResourceGroup" --share-subscription-name "ShareSubscription1"
```
##### <a name="ParametersDataSetMappingsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--data-set-mapping-name**|string|The name of the dataSetMapping.|data_set_mapping_name|dataSetMappingName|

#### <a name="DataSetMappingsCreate">Command `az datashare data-set-mapping create`</a>

##### <a name="ExamplesDataSetMappingsCreate">Example</a>
```
az datashare data-set-mapping create --account-name "Account1" --adls-gen2-file-data-set-mapping \
data-set-id="a08f184b-0567-4b11-ba22-a1199336d226" file-path="file21" file-system="fileSystem" output-type="Csv" \
resource-group="SampleResourceGroup" storage-account-name="storage2" subscription-id="433a8dfd-e5d5-4e77-ad86-90acdc75e\
b1a" --name "DatasetMapping1" --resource-group "SampleResourceGroup" --share-subscription-name "ShareSubscription1"
```
##### <a name="ParametersDataSetMappingsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription which will hold the data set sink.|share_subscription_name|shareSubscriptionName|
|**--data-set-mapping-name**|string|The name of the data set mapping to be created.|data_set_mapping_name|dataSetMappingName|
|**--adls-gen2-file-data-set-mapping**|object|An ADLS Gen2 file data set mapping.|adls_gen2_file_data_set_mapping|ADLSGen2FileDataSetMapping|
|**--adls-gen2-file-system-data-set-mapping**|object|An ADLS Gen2 file system data set mapping.|adls_gen2_file_system_data_set_mapping|ADLSGen2FileSystemDataSetMapping|
|**--adls-gen2-folder-data-set-mapping**|object|An ADLS Gen2 folder data set mapping.|adls_gen2_folder_data_set_mapping|ADLSGen2FolderDataSetMapping|
|**--blob-container-data-set-mapping**|object|A Blob container data set mapping.|blob_container_data_set_mapping|BlobContainerDataSetMapping|
|**--blob-data-set-mapping**|object|A Blob data set mapping.|blob_data_set_mapping|BlobDataSetMapping|
|**--blob-folder-data-set-mapping**|object|A Blob folder data set mapping.|blob_folder_data_set_mapping|BlobFolderDataSetMapping|
|**--kusto-cluster-data-set-mapping**|object|A Kusto cluster data set mapping|kusto_cluster_data_set_mapping|KustoClusterDataSetMapping|
|**--kusto-database-data-set-mapping**|object|A Kusto database data set mapping|kusto_database_data_set_mapping|KustoDatabaseDataSetMapping|
|**--kusto-table-data-set-mapping**|object|A Kusto database data set mapping|kusto_table_data_set_mapping|KustoTableDataSetMapping|
|**--sqldb-table-data-set-mapping**|object|A SQL DB Table data set mapping.|sqldb_table_data_set_mapping|SqlDBTableDataSetMapping|
|**--sqldw-table-data-set-mapping**|object|A SQL DW Table data set mapping.|sqldw_table_data_set_mapping|SqlDWTableDataSetMapping|
|**--synapse-workspace-sql-pool-table-data-set-mapping**|object|A Synapse Workspace Sql Pool Table data set mapping|synapse_workspace_sql_pool_table_data_set_mapping|SynapseWorkspaceSqlPoolTableDataSetMapping|

#### <a name="DataSetMappingsDelete">Command `az datashare data-set-mapping delete`</a>

##### <a name="ExamplesDataSetMappingsDelete">Example</a>
```
az datashare data-set-mapping delete --account-name "Account1" --name "DatasetMapping1" --resource-group \
"SampleResourceGroup" --share-subscription-name "ShareSubscription1"
```
##### <a name="ParametersDataSetMappingsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--data-set-mapping-name**|string|The name of the dataSetMapping.|data_set_mapping_name|dataSetMappingName|

### group `az datashare email-registration`
#### <a name="EmailRegistrationsActivateEmail">Command `az datashare email-registration activate-email`</a>

##### <a name="ExamplesEmailRegistrationsActivateEmail">Example</a>
```
az datashare email-registration activate-email --activation-code "djsfhakj2lekowd3wepfklpwe9lpflcd" --location "East \
US 2"
```
##### <a name="ParametersEmailRegistrationsActivateEmail">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|Location of the activation.|location|location|
|**--activation-code**|string|Activation code for the registration|activation_code|activationCode|

#### <a name="EmailRegistrationsRegisterEmail">Command `az datashare email-registration register-email`</a>

##### <a name="ExamplesEmailRegistrationsRegisterEmail">Example</a>
```
az datashare email-registration register-email --location "East US 2"
```
##### <a name="ParametersEmailRegistrationsRegisterEmail">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|Location of the registration|location|location|

### group `az datashare invitation`
#### <a name="InvitationsListByShare">Command `az datashare invitation list`</a>

##### <a name="ExamplesInvitationsListByShare">Example</a>
```
az datashare invitation list --account-name "Account1" --resource-group "SampleResourceGroup" --share-name "Share1"
```
##### <a name="ParametersInvitationsListByShare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|The continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="InvitationsGet">Command `az datashare invitation show`</a>

##### <a name="ExamplesInvitationsGet">Example</a>
```
az datashare invitation show --account-name "Account1" --name "Invitation1" --resource-group "SampleResourceGroup" \
--share-name "Share1"
```
##### <a name="ParametersInvitationsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--invitation-name**|string|The name of the invitation.|invitation_name|invitationName|

#### <a name="InvitationsCreate">Command `az datashare invitation create`</a>

##### <a name="ExamplesInvitationsCreate">Example</a>
```
az datashare invitation create --account-name "Account1" --expiration-date "2020-08-26T22:33:24.5785265Z" \
--target-email "receiver@microsoft.com" --name "Invitation1" --resource-group "SampleResourceGroup" --share-name \
"Share1"
```
##### <a name="ParametersInvitationsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to send the invitation for.|share_name|shareName|
|**--invitation-name**|string|The name of the invitation.|invitation_name|invitationName|
|**--expiration-date**|date-time|The expiration date for the invitation and share subscription.|expiration_date|expirationDate|
|**--target-active-directory-id**|string|The target Azure AD Id. Can't be combined with email.|target_active_directory_id|targetActiveDirectoryId|
|**--target-email**|string|The email the invitation is directed to.|target_email|targetEmail|
|**--target-object-id**|string|The target user or application Id that invitation is being sent to. Must be specified along TargetActiveDirectoryId. This enables sending invitations to specific users or applications in an AD tenant.|target_object_id|targetObjectId|

#### <a name="InvitationsDelete">Command `az datashare invitation delete`</a>

##### <a name="ExamplesInvitationsDelete">Example</a>
```
az datashare invitation delete --account-name "Account1" --name "Invitation1" --resource-group "SampleResourceGroup" \
--share-name "Share1"
```
##### <a name="ParametersInvitationsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--invitation-name**|string|The name of the invitation.|invitation_name|invitationName|

### group `az datashare provider-share-subscription`
#### <a name="ProviderShareSubscriptionsListByShare">Command `az datashare provider-share-subscription list`</a>

##### <a name="ExamplesProviderShareSubscriptionsListByShare">Example</a>
```
az datashare provider-share-subscription list --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-name "Share1"
```
##### <a name="ParametersProviderShareSubscriptionsListByShare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|Continuation Token|skip_token|$skipToken|

#### <a name="ProviderShareSubscriptionsGetByShare">Command `az datashare provider-share-subscription show`</a>

##### <a name="ExamplesProviderShareSubscriptionsGetByShare">Example</a>
```
az datashare provider-share-subscription show --account-name "Account1" --provider-share-subscription-id \
"4256e2cf-0f82-4865-961b-12f83333f487" --resource-group "SampleResourceGroup" --share-name "Share1"
```
##### <a name="ParametersProviderShareSubscriptionsGetByShare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|

#### <a name="ProviderShareSubscriptionsAdjust">Command `az datashare provider-share-subscription adjust`</a>

##### <a name="ExamplesProviderShareSubscriptionsAdjust">Example</a>
```
az datashare provider-share-subscription adjust --account-name "Account1" --expiration-date \
"2020-12-26T22:33:24.5785265Z" --provider-share-subscription-id "4256e2cf-0f82-4865-961b-12f83333f487" \
--resource-group "SampleResourceGroup" --share-name "Share1"
```
##### <a name="ParametersProviderShareSubscriptionsAdjust">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|
|**--expiration-date**|date-time|Expiration date of the share subscription in UTC format|expiration_date|expirationDate|

#### <a name="ProviderShareSubscriptionsReinstate">Command `az datashare provider-share-subscription reinstate`</a>

##### <a name="ExamplesProviderShareSubscriptionsReinstate">Example</a>
```
az datashare provider-share-subscription reinstate --account-name "Account1" --expiration-date \
"2020-12-26T22:33:24.5785265Z" --provider-share-subscription-id "4256e2cf-0f82-4865-961b-12f83333f487" \
--resource-group "SampleResourceGroup" --share-name "Share1"
```
##### <a name="ParametersProviderShareSubscriptionsReinstate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|
|**--expiration-date**|date-time|Expiration date of the share subscription in UTC format|expiration_date|expirationDate|

#### <a name="ProviderShareSubscriptionsRevoke">Command `az datashare provider-share-subscription revoke`</a>

##### <a name="ExamplesProviderShareSubscriptionsRevoke">Example</a>
```
az datashare provider-share-subscription revoke --account-name "Account1" --provider-share-subscription-id \
"4256e2cf-0f82-4865-961b-12f83333f487" --resource-group "SampleResourceGroup" --share-name "Share1"
```
##### <a name="ParametersProviderShareSubscriptionsRevoke">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--provider-share-subscription-id**|string|To locate shareSubscription|provider_share_subscription_id|providerShareSubscriptionId|

### group `az datashare share-subscription`
#### <a name="ShareSubscriptionsListByAccount">Command `az datashare share-subscription list`</a>

##### <a name="ExamplesShareSubscriptionsListByAccount">Example</a>
```
az datashare share-subscription list --account-name "Account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersShareSubscriptionsListByAccount">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--skip-token**|string|Continuation Token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="ShareSubscriptionsGet">Command `az datashare share-subscription show`</a>

##### <a name="ExamplesShareSubscriptionsGet">Example</a>
```
az datashare share-subscription show --account-name "Account1" --resource-group "SampleResourceGroup" --name \
"ShareSubscription1"
```
##### <a name="ParametersShareSubscriptionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|

#### <a name="ShareSubscriptionsCreate">Command `az datashare share-subscription create`</a>

##### <a name="ExamplesShareSubscriptionsCreate">Example</a>
```
az datashare share-subscription create --account-name "Account1" --resource-group "SampleResourceGroup" \
--expiration-date "2020-08-26T22:33:24.5785265Z" --invitation-id "12345678-1234-1234-12345678abd" \
--source-share-location "eastus2" --name "ShareSubscription1"
```
##### <a name="ParametersShareSubscriptionsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--invitation-id**|string|The invitation id.|invitation_id|invitationId|
|**--source-share-location**|string|Source share location.|source_share_location|sourceShareLocation|
|**--expiration-date**|date-time|The expiration date of the share subscription.|expiration_date|expirationDate|

#### <a name="ShareSubscriptionsDelete">Command `az datashare share-subscription delete`</a>

##### <a name="ExamplesShareSubscriptionsDelete">Example</a>
```
az datashare share-subscription delete --account-name "Account1" --resource-group "SampleResourceGroup" --name \
"ShareSubscription1"
```
##### <a name="ParametersShareSubscriptionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|

#### <a name="ShareSubscriptionsCancelSynchronization">Command `az datashare share-subscription cancel-synchronization`</a>

##### <a name="ExamplesShareSubscriptionsCancelSynchronization">Example</a>
```
az datashare share-subscription cancel-synchronization --account-name "Account1" --resource-group \
"SampleResourceGroup" --name "ShareSubscription1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
```
##### <a name="ParametersShareSubscriptionsCancelSynchronization">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--synchronization-id**|string|Synchronization id|synchronization_id|synchronizationId|

#### <a name="ShareSubscriptionsListSourceShareSynchronizationSettings">Command `az datashare share-subscription list-source-share-synchronization-setting`</a>

##### <a name="ExamplesShareSubscriptionsListSourceShareSynchronizationSettings">Example</a>
```
az datashare share-subscription list-source-share-synchronization-setting --account-name "Account1" --resource-group \
"SampleResourceGroup" --name "ShareSub1"
```
##### <a name="ParametersShareSubscriptionsListSourceShareSynchronizationSettings">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

#### <a name="ShareSubscriptionsListSynchronizations">Command `az datashare share-subscription list-synchronization`</a>

##### <a name="ExamplesShareSubscriptionsListSynchronizations">Example</a>
```
az datashare share-subscription list-synchronization --account-name "Account1" --resource-group "SampleResourceGroup" \
--name "ShareSub1"
```
##### <a name="ParametersShareSubscriptionsListSynchronizations">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|

#### <a name="ShareSubscriptionsListSynchronizationDetails">Command `az datashare share-subscription list-synchronization-detail`</a>

##### <a name="ExamplesShareSubscriptionsListSynchronizationDetails">Example</a>
```
az datashare share-subscription list-synchronization-detail --account-name "Account1" --resource-group \
"SampleResourceGroup" --name "ShareSub1" --synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"
```
##### <a name="ParametersShareSubscriptionsListSynchronizationDetails">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|
|**--filter**|string|Filters the results using OData syntax.|filter|$filter|
|**--orderby**|string|Sorts the results using OData syntax.|orderby|$orderby|
|**--synchronization-id**|string|Synchronization id|synchronization_id|synchronizationId|

#### <a name="ShareSubscriptionsSynchronize">Command `az datashare share-subscription synchronize`</a>

##### <a name="ExamplesShareSubscriptionsSynchronize">Example</a>
```
az datashare share-subscription synchronize --account-name "Account1" --resource-group "SampleResourceGroup" --name \
"ShareSubscription1" --synchronization-mode "Incremental"
```
##### <a name="ParametersShareSubscriptionsSynchronize">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of share subscription|share_subscription_name|shareSubscriptionName|
|**--synchronization-mode**|choice|Mode of synchronization used in triggers and snapshot sync. Incremental by default|synchronization_mode|synchronizationMode|

### group `az datashare synchronization-setting`
#### <a name="SynchronizationSettingsListByShare">Command `az datashare synchronization-setting list`</a>

##### <a name="ExamplesSynchronizationSettingsListByShare">Example</a>
```
az datashare synchronization-setting list --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-name "Share1"
```
##### <a name="ParametersSynchronizationSettingsListByShare">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--skip-token**|string|continuation token|skip_token|$skipToken|

#### <a name="SynchronizationSettingsGet">Command `az datashare synchronization-setting show`</a>

##### <a name="ExamplesSynchronizationSettingsGet">Example</a>
```
az datashare synchronization-setting show --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-name "Share1" --name "SynchronizationSetting1"
```
##### <a name="ParametersSynchronizationSettingsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronizationSettingName|

#### <a name="SynchronizationSettingsCreate">Command `az datashare synchronization-setting create`</a>

##### <a name="ExamplesSynchronizationSettingsCreate">Example</a>
```
az datashare synchronization-setting create --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-name "Share1" --scheduled-synchronization-setting recurrence-interval="Day" synchronization-time="2018-11-14T04\
:47:52.9614956Z" --name "Dataset1"
```
##### <a name="ParametersSynchronizationSettingsCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share to add the synchronization setting to.|share_name|shareName|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting.|synchronization_setting_name|synchronizationSettingName|
|**--scheduled-synchronization-setting**|object|A type of synchronization setting based on schedule|scheduled_synchronization_setting|ScheduledSynchronizationSetting|

#### <a name="SynchronizationSettingsDelete">Command `az datashare synchronization-setting delete`</a>

##### <a name="ExamplesSynchronizationSettingsDelete">Example</a>
```
az datashare synchronization-setting delete --account-name "Account1" --resource-group "SampleResourceGroup" \
--share-name "Share1" --name "SynchronizationSetting1"
```
##### <a name="ParametersSynchronizationSettingsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-name**|string|The name of the share.|share_name|shareName|
|**--synchronization-setting-name**|string|The name of the synchronizationSetting .|synchronization_setting_name|synchronizationSettingName|

### group `az datashare trigger`
#### <a name="TriggersListByShareSubscription">Command `az datashare trigger list`</a>

##### <a name="ExamplesTriggersListByShareSubscription">Example</a>
```
az datashare trigger list --account-name "Account1" --resource-group "SampleResourceGroup" --share-subscription-name \
"ShareSubscription1"
```
##### <a name="ParametersTriggersListByShareSubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription.|share_subscription_name|shareSubscriptionName|
|**--skip-token**|string|Continuation token|skip_token|$skipToken|

#### <a name="TriggersGet">Command `az datashare trigger show`</a>

##### <a name="ExamplesTriggersGet">Example</a>
```
az datashare trigger show --account-name "Account1" --resource-group "SampleResourceGroup" --share-subscription-name \
"ShareSubscription1" --name "Trigger1"
```
##### <a name="ParametersTriggersGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--trigger-name**|string|The name of the trigger.|trigger_name|triggerName|

#### <a name="TriggersCreate">Command `az datashare trigger create`</a>

##### <a name="ExamplesTriggersCreate">Example</a>
```
az datashare trigger create --account-name "Account1" --resource-group "SampleResourceGroup" --share-subscription-name \
"ShareSubscription1" --scheduled-trigger recurrence-interval="Day" synchronization-mode="Incremental" \
synchronization-time="2018-11-14T04:47:52.9614956Z" --name "Trigger1"
```
##### <a name="ParametersTriggersCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the share subscription which will hold the data set sink.|share_subscription_name|shareSubscriptionName|
|**--trigger-name**|string|The name of the trigger.|trigger_name|triggerName|
|**--scheduled-trigger**|object|A type of trigger based on schedule|scheduled_trigger|ScheduledTrigger|

#### <a name="TriggersDelete">Command `az datashare trigger delete`</a>

##### <a name="ExamplesTriggersDelete">Example</a>
```
az datashare trigger delete --account-name "Account1" --resource-group "SampleResourceGroup" --share-subscription-name \
"ShareSubscription1" --name "Trigger1"
```
##### <a name="ParametersTriggersDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the share account.|account_name|accountName|
|**--share-subscription-name**|string|The name of the shareSubscription.|share_subscription_name|shareSubscriptionName|
|**--trigger-name**|string|The name of the trigger.|trigger_name|triggerName|
