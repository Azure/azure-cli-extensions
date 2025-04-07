# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az purview|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az purview` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az purview account|Accounts|[commands](#CommandsInAccounts)|
|az purview default-account|DefaultAccounts|[commands](#CommandsInDefaultAccounts)|

## COMMANDS
### <a name="CommandsInAccounts">Commands in `az purview account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az purview account list](#AccountsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersAccountsListByResourceGroup)|[Example](#ExamplesAccountsListByResourceGroup)|
|[az purview account list](#AccountsListBySubscription)|ListBySubscription|[Parameters](#ParametersAccountsListBySubscription)|[Example](#ExamplesAccountsListBySubscription)|
|[az purview account show](#AccountsGet)|Get|[Parameters](#ParametersAccountsGet)|[Example](#ExamplesAccountsGet)|
|[az purview account create](#AccountsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAccountsCreateOrUpdate#Create)|[Example](#ExamplesAccountsCreateOrUpdate#Create)|
|[az purview account update](#AccountsUpdate)|Update|[Parameters](#ParametersAccountsUpdate)|[Example](#ExamplesAccountsUpdate)|
|[az purview account delete](#AccountsDelete)|Delete|[Parameters](#ParametersAccountsDelete)|[Example](#ExamplesAccountsDelete)|
|[az purview account add-root-collection-admin](#AccountsAddRootCollectionAdmin)|AddRootCollectionAdmin|[Parameters](#ParametersAccountsAddRootCollectionAdmin)|[Example](#ExamplesAccountsAddRootCollectionAdmin)|
|[az purview account list-key](#AccountsListKeys)|ListKeys|[Parameters](#ParametersAccountsListKeys)|[Example](#ExamplesAccountsListKeys)|

### <a name="CommandsInDefaultAccounts">Commands in `az purview default-account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az purview default-account show](#DefaultAccountsGet)|Get|[Parameters](#ParametersDefaultAccountsGet)|[Example](#ExamplesDefaultAccountsGet)|
|[az purview default-account remove](#DefaultAccountsRemove)|Remove|[Parameters](#ParametersDefaultAccountsRemove)|[Example](#ExamplesDefaultAccountsRemove)|
|[az purview default-account set](#DefaultAccountsSet)|Set|[Parameters](#ParametersDefaultAccountsSet)|[Example](#ExamplesDefaultAccountsSet)|


## COMMAND DETAILS
### group `az purview account`
#### <a name="AccountsListByResourceGroup">Command `az purview account list`</a>

##### <a name="ExamplesAccountsListByResourceGroup">Example</a>
```
az purview account list --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--skip-token**|string|The skip token.|skip_token|$skipToken|

#### <a name="AccountsListBySubscription">Command `az purview account list`</a>

##### <a name="ExamplesAccountsListBySubscription">Example</a>
```
az purview account list
```
##### <a name="ParametersAccountsListBySubscription">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--skip-token**|string|The skip token.|skip_token|$skipToken|

#### <a name="AccountsGet">Command `az purview account show`</a>

##### <a name="ExamplesAccountsGet">Example</a>
```
az purview account show --name "account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the account.|account_name|accountName|

#### <a name="AccountsCreateOrUpdate#Create">Command `az purview account create`</a>

##### <a name="ExamplesAccountsCreateOrUpdate#Create">Example</a>
```
az purview account create --location "West US 2" --managed-resource-group-name "custom-rgname" --sku name="Standard" \
capacity=4 --name "account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the account.|account_name|accountName|
|**--location**|string|Gets or sets the location.|location|location|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|
|**--sku**|object|Gets or sets the Sku.|sku|sku|
|**--managed-resource-group-name**|string|Gets or sets the managed resource group name|managed_resource_group_name|managedResourceGroupName|
|**--public-network-access**|choice|Gets or sets the public network access.|public_network_access|publicNetworkAccess|

#### <a name="AccountsUpdate">Command `az purview account update`</a>

##### <a name="ExamplesAccountsUpdate">Example</a>
```
az purview account update --name "account1" --tags newTag="New tag value." --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the account.|account_name|accountName|
|**--tags**|dictionary|Tags on the azure resource.|tags|tags|
|**--managed-resource-group-name**|string|Gets or sets the managed resource group name|managed_resource_group_name|managedResourceGroupName|
|**--public-network-access**|choice|Gets or sets the public network access.|public_network_access|publicNetworkAccess|

#### <a name="AccountsDelete">Command `az purview account delete`</a>

##### <a name="ExamplesAccountsDelete">Example</a>
```
az purview account delete --name "account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the account.|account_name|accountName|

#### <a name="AccountsAddRootCollectionAdmin">Command `az purview account add-root-collection-admin`</a>

##### <a name="ExamplesAccountsAddRootCollectionAdmin">Example</a>
```
az purview account add-root-collection-admin --name "account1" --object-id "7e8de0e7-2bfc-4e1f-9659-2a5785e4356f" \
--resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsAddRootCollectionAdmin">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the account.|account_name|accountName|
|**--object-id**|string|Gets or sets the object identifier of the admin.|object_id|objectId|

#### <a name="AccountsListKeys">Command `az purview account list-key`</a>

##### <a name="ExamplesAccountsListKeys">Example</a>
```
az purview account list-key --name "account1" --resource-group "SampleResourceGroup"
```
##### <a name="ParametersAccountsListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The resource group name.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the account.|account_name|accountName|

### group `az purview default-account`
#### <a name="DefaultAccountsGet">Command `az purview default-account show`</a>

##### <a name="ExamplesDefaultAccountsGet">Example</a>
```
az purview default-account show --scope "12345678-1234-1234-12345678abc" --scope-tenant-id \
"12345678-1234-1234-12345678abc" --scope-type "Tenant"
```
##### <a name="ParametersDefaultAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope-tenant-id**|uuid|The tenant ID.|scope_tenant_id|scopeTenantId|
|**--scope-type**|choice|The scope for the default account.|scope_type|scopeType|
|**--scope**|string|The Id of the scope object, for example if the scope is "Subscription" then it is the ID of that subscription.|scope|scope|

#### <a name="DefaultAccountsRemove">Command `az purview default-account remove`</a>

##### <a name="ExamplesDefaultAccountsRemove">Example</a>
```
az purview default-account remove --scope "12345678-1234-1234-12345678abc" --scope-tenant-id \
"12345678-1234-1234-12345678abc" --scope-type "Tenant"
```
##### <a name="ParametersDefaultAccountsRemove">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--scope-tenant-id**|uuid|The tenant ID.|scope_tenant_id|scopeTenantId|
|**--scope-type**|choice|The scope for the default account.|scope_type|scopeType|
|**--scope**|string|The Id of the scope object, for example if the scope is "Subscription" then it is the ID of that subscription.|scope|scope|

#### <a name="DefaultAccountsSet">Command `az purview default-account set`</a>

##### <a name="ExamplesDefaultAccountsSet">Example</a>
```
az purview default-account set --account-name "myDefaultAccount" --resource-group "rg-1" --scope \
"12345678-1234-1234-12345678abc" --scope-tenant-id "12345678-1234-1234-12345678abc" --scope-type "Tenant" \
--subscription-id "12345678-1234-1234-12345678aaa"
```
##### <a name="ParametersDefaultAccountsSet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--account-name**|string|The name of the account that is set as the default.|account_name|accountName|
|**--resource-group-name**|string|The resource group name of the account that is set as the default.|resource_group_name|resourceGroupName|
|**--scope**|string|The scope object ID. For example, sub ID or tenant ID.|scope|scope|
|**--scope-tenant-id**|string|The scope tenant in which the default account is set.|scope_tenant_id|scopeTenantId|
|**--scope-type**|choice|The scope where the default account is set.|scope_type|scopeType|
|**--subscription-id**|string|The subscription ID of the account that is set as the default.|subscription_id|subscriptionId|
