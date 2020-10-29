# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az account|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az account` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az account subscription|Subscriptions|[commands](#CommandsInSubscriptions)|
|az account tenant|Tenants|[commands](#CommandsInTenants)|
|az account subscription|Subscription|[commands](#CommandsInSubscription)|
|az account alias|Alias|[commands](#CommandsInAlias)|

## COMMANDS
### <a name="CommandsInAlias">Commands in `az account alias` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az account alias list](#AliasList)|List|[Parameters](#ParametersAliasList)|[Example](#ExamplesAliasList)|
|[az account alias show](#AliasGet)|Get|[Parameters](#ParametersAliasGet)|[Example](#ExamplesAliasGet)|
|[az account alias create](#AliasCreate)|Create|[Parameters](#ParametersAliasCreate)|[Example](#ExamplesAliasCreate)|
|[az account alias delete](#AliasDelete)|Delete|[Parameters](#ParametersAliasDelete)|[Example](#ExamplesAliasDelete)|

### <a name="CommandsInSubscription">Commands in `az account subscription` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az account subscription cancel](#SubscriptionCancel)|Cancel|[Parameters](#ParametersSubscriptionCancel)|[Example](#ExamplesSubscriptionCancel)|
|[az account subscription enable](#SubscriptionEnable)|Enable|[Parameters](#ParametersSubscriptionEnable)|[Example](#ExamplesSubscriptionEnable)|
|[az account subscription rename](#SubscriptionRename)|Rename|[Parameters](#ParametersSubscriptionRename)|[Example](#ExamplesSubscriptionRename)|

### <a name="CommandsInTenants">Commands in `az account tenant` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az account tenant list](#TenantsList)|List|[Parameters](#ParametersTenantsList)|[Example](#ExamplesTenantsList)|


## COMMAND DETAILS

### group `az account alias`
#### <a name="AliasList">Command `az account alias list`</a>

##### <a name="ExamplesAliasList">Example</a>
```
az account alias list
```
##### <a name="ParametersAliasList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="AliasGet">Command `az account alias show`</a>

##### <a name="ExamplesAliasGet">Example</a>
```
az account alias show --name "aliasForNewSub"
```
##### <a name="ParametersAliasGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--alias-name**|string|Alias Name|alias_name|aliasName|

#### <a name="AliasCreate">Command `az account alias create`</a>

##### <a name="ExamplesAliasCreate">Example</a>
```
az account alias create --name "aliasForNewSub" --properties billing-scope="/providers/Microsoft.Billing/billingAccount\
s/e879cf0f-2b4d-5431-109a-f72fc9868693:024cabf4-7321-4cf9-be59-df0c77ca51de_2019-05-31/billingProfiles/PE2Q-NOIT-BG7-TG\
B/invoiceSections/MTT4-OBS7-PJA-TGB" display-name="Contoso MCA subscription" workload="Production"
```
##### <a name="ParametersAliasCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--alias-name**|string|Alias Name|alias_name|aliasName|
|**--properties**|object|Put alias request properties.|properties|properties|

#### <a name="AliasDelete">Command `az account alias delete`</a>

##### <a name="ExamplesAliasDelete">Example</a>
```
az account alias delete --name "aliasForNewSub"
```
##### <a name="ParametersAliasDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--alias-name**|string|Alias Name|alias_name|aliasName|

### group `az account subscription`
#### <a name="SubscriptionCancel">Command `az account subscription cancel`</a>

##### <a name="ExamplesSubscriptionCancel">Example</a>
```
az account subscription cancel --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
```
##### <a name="ParametersSubscriptionCancel">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Subscription Id.|subscription_id|subscriptionId|

#### <a name="SubscriptionEnable">Command `az account subscription enable`</a>

##### <a name="ExamplesSubscriptionEnable">Example</a>
```
az account subscription enable --subscription-id "7948bcee-488c-47ce-941c-38e20ede803d"
```
##### <a name="ParametersSubscriptionEnable">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Subscription Id.|subscription_id|subscriptionId|

#### <a name="SubscriptionRename">Command `az account subscription rename`</a>

##### <a name="ExamplesSubscriptionRename">Example</a>
```
az account subscription rename --name "Test Sub" --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
```
##### <a name="ParametersSubscriptionRename">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--subscription-id**|string|Subscription Id.|subscription_id|subscriptionId|
|**--subscription-name**|string|New subscription name|subscription_name|subscriptionName|

### group `az account tenant`
#### <a name="TenantsList">Command `az account tenant list`</a>

##### <a name="ExamplesTenantsList">Example</a>
```
az account tenant list
```
##### <a name="ParametersTenantsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|