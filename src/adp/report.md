# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az adp|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az adp` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az adp account|Accounts|[commands](#CommandsInAccounts)|
|az adp data-pool|DataPools|[commands](#CommandsInDataPools)|

## COMMANDS
### <a name="CommandsInAccounts">Commands in `az adp account` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az adp account list](#AccountsListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersAccountsListByResourceGroup)|[Example](#ExamplesAccountsListByResourceGroup)|
|[az adp account list](#AccountsList)|List|[Parameters](#ParametersAccountsList)|[Example](#ExamplesAccountsList)|
|[az adp account show](#AccountsGet)|Get|[Parameters](#ParametersAccountsGet)|[Example](#ExamplesAccountsGet)|
|[az adp account create](#AccountsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersAccountsCreateOrUpdate#Create)|[Example](#ExamplesAccountsCreateOrUpdate#Create)|
|[az adp account update](#AccountsUpdate)|Update|[Parameters](#ParametersAccountsUpdate)|[Example](#ExamplesAccountsUpdate)|
|[az adp account delete](#AccountsDelete)|Delete|[Parameters](#ParametersAccountsDelete)|[Example](#ExamplesAccountsDelete)|

### <a name="CommandsInDataPools">Commands in `az adp data-pool` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az adp data-pool list](#DataPoolsList)|List|[Parameters](#ParametersDataPoolsList)|[Example](#ExamplesDataPoolsList)|
|[az adp data-pool show](#DataPoolsGet)|Get|[Parameters](#ParametersDataPoolsGet)|[Example](#ExamplesDataPoolsGet)|
|[az adp data-pool create](#DataPoolsCreateOrUpdate#Create)|CreateOrUpdate#Create|[Parameters](#ParametersDataPoolsCreateOrUpdate#Create)|[Example](#ExamplesDataPoolsCreateOrUpdate#Create)|
|[az adp data-pool update](#DataPoolsUpdate)|Update|[Parameters](#ParametersDataPoolsUpdate)|[Example](#ExamplesDataPoolsUpdate)|
|[az adp data-pool delete](#DataPoolsDelete)|Delete|[Parameters](#ParametersDataPoolsDelete)|[Example](#ExamplesDataPoolsDelete)|


## COMMAND DETAILS

### group `az adp account`
#### <a name="AccountsListByResourceGroup">Command `az adp account list`</a>

##### <a name="ExamplesAccountsListByResourceGroup">Example</a>
```
az adp account list --resource-group "adpClient"
```
##### <a name="ParametersAccountsListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="AccountsList">Command `az adp account list`</a>

##### <a name="ExamplesAccountsList">Example</a>
```
az adp account list
```
##### <a name="ParametersAccountsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="AccountsGet">Command `az adp account show`</a>

##### <a name="ExamplesAccountsGet">Example</a>
```
az adp account show --name "sampleacct" --resource-group "adpClient"
```
##### <a name="ParametersAccountsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|

#### <a name="AccountsCreateOrUpdate#Create">Command `az adp account create`</a>

##### <a name="ExamplesAccountsCreateOrUpdate#Create">Example</a>
```
az adp account create --name "sampleacct" --location "Global" --resource-group "adpClient"
```
##### <a name="ParametersAccountsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--location**|string|The geo-location where the resource lives|location|location|

#### <a name="AccountsUpdate">Command `az adp account update`</a>

##### <a name="ExamplesAccountsUpdate">Example</a>
```
az adp account update --name "sampleacct" --resource-group "adpClient"
```
##### <a name="ParametersAccountsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|

#### <a name="AccountsDelete">Command `az adp account delete`</a>

##### <a name="ExamplesAccountsDelete">Example</a>
```
az adp account delete --name "sampleacct" --resource-group "adpClient"
```
##### <a name="ParametersAccountsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|

### group `az adp data-pool`
#### <a name="DataPoolsList">Command `az adp data-pool list`</a>

##### <a name="ExamplesDataPoolsList">Example</a>
```
az adp data-pool list --account-name "sampleacct" --resource-group "adpClient"
```
##### <a name="ParametersDataPoolsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|

#### <a name="DataPoolsGet">Command `az adp data-pool show`</a>

##### <a name="ExamplesDataPoolsGet">Example</a>
```
az adp data-pool show --account-name "sampleacct" --name "sampledp" --resource-group "adpClient"
```
##### <a name="ParametersDataPoolsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|

#### <a name="DataPoolsCreateOrUpdate#Create">Command `az adp data-pool create`</a>

##### <a name="ExamplesDataPoolsCreateOrUpdate#Create">Example</a>
```
az adp data-pool create --account-name "sampleacct" --name "sampledp" --locations name="westus" --resource-group \
"adpClient"
```
##### <a name="ParametersDataPoolsCreateOrUpdate#Create">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|
|**--locations**|array|Gets or sets the collection of locations where Data Pool resources should be created.|locations|locations|

#### <a name="DataPoolsUpdate">Command `az adp data-pool update`</a>

##### <a name="ExamplesDataPoolsUpdate">Example</a>
```
az adp data-pool update --account-name "sampleacct" --name "sampledp" --locations name="westus" --resource-group \
"adpClient"
```
##### <a name="ParametersDataPoolsUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|
|**--locations**|array|Gets or sets the collection of locations where Data Pool resources should be created.|locations|locations|

#### <a name="DataPoolsDelete">Command `az adp data-pool delete`</a>

##### <a name="ExamplesDataPoolsDelete">Example</a>
```
az adp data-pool delete --account-name "sampleacct" --name "sampledp" --resource-group "adpClient"
```
##### <a name="ParametersDataPoolsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|
