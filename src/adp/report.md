# Azure CLI Module Creation Report

### adp account create

create a adp account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--tags**|dictionary|Resource tags.|tags|tags|

### adp account delete

delete a adp account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|

### adp account list

list a adp account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|ListByResourceGroup|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

### adp account show

show a adp account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|

### adp account update

update a adp account.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp account|Accounts|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--tags**|dictionary|Resource tags.|tags|tags|

### adp data-pool create

create a adp data-pool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp data-pool|DataPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|create|CreateOrUpdate#Create|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|
|**--locations**|array|Gets or sets the collection of locations where Data Pool resources should be created.|locations|locations|

### adp data-pool delete

delete a adp data-pool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp data-pool|DataPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|delete|Delete|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|

### adp data-pool list

list a adp data-pool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp data-pool|DataPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|list|List|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|

### adp data-pool show

show a adp data-pool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp data-pool|DataPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|show|Get|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|

### adp data-pool update

update a adp data-pool.

#### Command group
|Name (az)|Swagger name|
|---------|------------|
|adp data-pool|DataPools|

#### Methods
|Name (az)|Swagger name|
|---------|------------|
|update|Update|

#### Parameters
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--account-name**|string|The name of the ADP account.|account_name|accountName|
|**--data-pool-name**|string|The name of the Data Pool.|data_pool_name|dataPoolName|
|**--locations**|array|Gets or sets the collection of locations where Data Pool resources should be created.|locations|locations|
