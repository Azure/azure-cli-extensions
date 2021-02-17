# Azure CLI Module Creation Report

## EXTENSION
|CLI Extension|Command Groups|
|---------|------------|
|az redisenterprise|[groups](#CommandGroups)

## GROUPS
### <a name="CommandGroups">Command groups in `az redisenterprise` extension </a>
|CLI Command Group|Group Swagger name|Commands|
|---------|------------|--------|
|az redisenterprise operation-status|OperationsStatus|[commands](#CommandsInOperationsStatus)|
|az redisenterprise|RedisEnterprise|[commands](#CommandsInRedisEnterprise)|
|az redisenterprise database|Databases|[commands](#CommandsInDatabases)|
|az redisenterprise private-endpoint-connection|PrivateEndpointConnections|[commands](#CommandsInPrivateEndpointConnections)|
|az redisenterprise private-link-resource|PrivateLinkResources|[commands](#CommandsInPrivateLinkResources)|

## COMMANDS
### <a name="CommandsInRedisEnterprise">Commands in `az redisenterprise` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az redisenterprise list](#RedisEnterpriseListByResourceGroup)|ListByResourceGroup|[Parameters](#ParametersRedisEnterpriseListByResourceGroup)|[Example](#ExamplesRedisEnterpriseListByResourceGroup)|
|[az redisenterprise list](#RedisEnterpriseList)|List|[Parameters](#ParametersRedisEnterpriseList)|[Example](#ExamplesRedisEnterpriseList)|
|[az redisenterprise show](#RedisEnterpriseGet)|Get|[Parameters](#ParametersRedisEnterpriseGet)|[Example](#ExamplesRedisEnterpriseGet)|
|[az redisenterprise create](#RedisEnterpriseCreate)|Create|[Parameters](#ParametersRedisEnterpriseCreate)|[Example](#ExamplesRedisEnterpriseCreate)|
|[az redisenterprise update](#RedisEnterpriseUpdate)|Update|[Parameters](#ParametersRedisEnterpriseUpdate)|[Example](#ExamplesRedisEnterpriseUpdate)|
|[az redisenterprise delete](#RedisEnterpriseDelete)|Delete|[Parameters](#ParametersRedisEnterpriseDelete)|[Example](#ExamplesRedisEnterpriseDelete)|

### <a name="CommandsInDatabases">Commands in `az redisenterprise database` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az redisenterprise database list](#DatabasesListByCluster)|ListByCluster|[Parameters](#ParametersDatabasesListByCluster)|[Example](#ExamplesDatabasesListByCluster)|
|[az redisenterprise database show](#DatabasesGet)|Get|[Parameters](#ParametersDatabasesGet)|[Example](#ExamplesDatabasesGet)|
|[az redisenterprise database create](#DatabasesCreate)|Create|[Parameters](#ParametersDatabasesCreate)|[Example](#ExamplesDatabasesCreate)|
|[az redisenterprise database update](#DatabasesUpdate)|Update|[Parameters](#ParametersDatabasesUpdate)|[Example](#ExamplesDatabasesUpdate)|
|[az redisenterprise database delete](#DatabasesDelete)|Delete|[Parameters](#ParametersDatabasesDelete)|[Example](#ExamplesDatabasesDelete)|
|[az redisenterprise database export](#DatabasesExport)|Export|[Parameters](#ParametersDatabasesExport)|[Example](#ExamplesDatabasesExport)|
|[az redisenterprise database import](#DatabasesImport)|Import|[Parameters](#ParametersDatabasesImport)|[Example](#ExamplesDatabasesImport)|
|[az redisenterprise database list-key](#DatabasesListKeys)|ListKeys|[Parameters](#ParametersDatabasesListKeys)|[Example](#ExamplesDatabasesListKeys)|
|[az redisenterprise database regenerate-key](#DatabasesRegenerateKey)|RegenerateKey|[Parameters](#ParametersDatabasesRegenerateKey)|[Example](#ExamplesDatabasesRegenerateKey)|

### <a name="CommandsInOperationsStatus">Commands in `az redisenterprise operation-status` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az redisenterprise operation-status show](#OperationsStatusGet)|Get|[Parameters](#ParametersOperationsStatusGet)|[Example](#ExamplesOperationsStatusGet)|

### <a name="CommandsInPrivateEndpointConnections">Commands in `az redisenterprise private-endpoint-connection` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az redisenterprise private-endpoint-connection list](#PrivateEndpointConnectionsList)|List|[Parameters](#ParametersPrivateEndpointConnectionsList)|[Example](#ExamplesPrivateEndpointConnectionsList)|
|[az redisenterprise private-endpoint-connection show](#PrivateEndpointConnectionsGet)|Get|[Parameters](#ParametersPrivateEndpointConnectionsGet)|[Example](#ExamplesPrivateEndpointConnectionsGet)|
|[az redisenterprise private-endpoint-connection delete](#PrivateEndpointConnectionsDelete)|Delete|[Parameters](#ParametersPrivateEndpointConnectionsDelete)|[Example](#ExamplesPrivateEndpointConnectionsDelete)|
|[az redisenterprise private-endpoint-connection put](#PrivateEndpointConnectionsPut)|Put|[Parameters](#ParametersPrivateEndpointConnectionsPut)|[Example](#ExamplesPrivateEndpointConnectionsPut)|

### <a name="CommandsInPrivateLinkResources">Commands in `az redisenterprise private-link-resource` group</a>
|CLI Command|Operation Swagger name|Parameters|Examples|
|---------|------------|--------|-----------|
|[az redisenterprise private-link-resource list](#PrivateLinkResourcesListByCluster)|ListByCluster|[Parameters](#ParametersPrivateLinkResourcesListByCluster)|[Example](#ExamplesPrivateLinkResourcesListByCluster)|


## COMMAND DETAILS

### group `az redisenterprise`
#### <a name="RedisEnterpriseListByResourceGroup">Command `az redisenterprise list`</a>

##### <a name="ExamplesRedisEnterpriseListByResourceGroup">Example</a>
```
az redisenterprise list --resource-group "rg1"
```
##### <a name="ParametersRedisEnterpriseListByResourceGroup">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|

#### <a name="RedisEnterpriseList">Command `az redisenterprise list`</a>

##### <a name="ExamplesRedisEnterpriseList">Example</a>
```
az redisenterprise list
```
##### <a name="ParametersRedisEnterpriseList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
#### <a name="RedisEnterpriseGet">Command `az redisenterprise show`</a>

##### <a name="ExamplesRedisEnterpriseGet">Example</a>
```
az redisenterprise show --cluster-name "cache1" --resource-group "rg1"
```
##### <a name="ParametersRedisEnterpriseGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|

#### <a name="RedisEnterpriseCreate">Command `az redisenterprise create`</a>

##### <a name="ExamplesRedisEnterpriseCreate">Example</a>
```
az redisenterprise create --cluster-name "cache1" --location "West US" --minimum-tls-version "1.2" --sku \
name="EnterpriseFlash_F300" capacity=3 --tags tag1="value1" --zones "1" "2" "3" --resource-group "rg1"
```
##### <a name="ParametersRedisEnterpriseCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--location**|string|The geo-location where the resource lives|location|location|
|**--sku**|object|The SKU to create, which affects price, performance, and features.|sku|sku|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--zones**|array|The Availability Zones where this cluster will be deployed.|zones|zones|
|**--minimum-tls-version**|choice|The minimum TLS version for the cluster to support, e.g. '1.2'|minimum_tls_version|minimumTlsVersion|

#### <a name="RedisEnterpriseUpdate">Command `az redisenterprise update`</a>

##### <a name="ExamplesRedisEnterpriseUpdate">Example</a>
```
az redisenterprise update --cluster-name "cache1" --minimum-tls-version "1.2" --sku name="EnterpriseFlash_F300" \
capacity=9 --tags tag1="value1" --resource-group "rg1"
```
##### <a name="ParametersRedisEnterpriseUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--sku**|object|The SKU to create, which affects price, performance, and features.|sku|sku|
|**--tags**|dictionary|Resource tags.|tags|tags|
|**--minimum-tls-version**|choice|The minimum TLS version for the cluster to support, e.g. '1.2'|minimum_tls_version|minimumTlsVersion|

#### <a name="RedisEnterpriseDelete">Command `az redisenterprise delete`</a>

##### <a name="ExamplesRedisEnterpriseDelete">Example</a>
```
az redisenterprise delete --cluster-name "cache1" --resource-group "rg1"
```
##### <a name="ParametersRedisEnterpriseDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|

### group `az redisenterprise database`
#### <a name="DatabasesListByCluster">Command `az redisenterprise database list`</a>

##### <a name="ExamplesDatabasesListByCluster">Example</a>
```
az redisenterprise database list --cluster-name "cache1" --resource-group "rg1"
```
##### <a name="ParametersDatabasesListByCluster">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|

#### <a name="DatabasesGet">Command `az redisenterprise database show`</a>

##### <a name="ExamplesDatabasesGet">Example</a>
```
az redisenterprise database show --cluster-name "cache1" --database-name "default" --resource-group "rg1"
```
##### <a name="ParametersDatabasesGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|

#### <a name="DatabasesCreate">Command `az redisenterprise database create`</a>

##### <a name="ExamplesDatabasesCreate">Example</a>
```
az redisenterprise database create --cluster-name "cache1" --database-name "default" --client-protocol "Encrypted" \
--clustering-policy "EnterpriseCluster" --eviction-policy "AllKeysLRU" --modules name="RedisBloom" args="ERROR_RATE \
0.00 INITIAL_SIZE 400" --modules name="RedisTimeSeries" args="RETENTION_POLICY 20" --modules name="RediSearch" \
--persistence aof-enabled=true aof-frequency="1s" --port 10000 --resource-group "rg1"
```
##### <a name="ParametersDatabasesCreate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|
|**--client-protocol**|choice|Specifies whether redis clients can connect using TLS-encrypted or plaintext redis protocols. Default is TLS-encrypted.|client_protocol|clientProtocol|
|**--port**|integer|TCP port of the database endpoint. Specified at create time. Defaults to an available port.|port|port|
|**--clustering-policy**|choice|Clustering policy - default is OSSCluster. Specified at create time.|clustering_policy|clusteringPolicy|
|**--eviction-policy**|choice|Redis eviction policy - default is VolatileLRU|eviction_policy|evictionPolicy|
|**--persistence**|object|Persistence settings|persistence|persistence|
|**--modules**|array|Optional set of redis modules to enable in this database - modules can only be added at creation time.|modules|modules|

#### <a name="DatabasesUpdate">Command `az redisenterprise database update`</a>

##### <a name="ExamplesDatabasesUpdate">Example</a>
```
az redisenterprise database update --cluster-name "cache1" --database-name "default" --client-protocol "Encrypted" \
--eviction-policy "AllKeysLRU" --persistence rdb-enabled=true rdb-frequency="12h" --resource-group "rg1"
```
##### <a name="ParametersDatabasesUpdate">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|
|**--client-protocol**|choice|Specifies whether redis clients can connect using TLS-encrypted or plaintext redis protocols. Default is TLS-encrypted.|client_protocol|clientProtocol|
|**--port**|integer|TCP port of the database endpoint. Specified at create time. Defaults to an available port.|port|port|
|**--clustering-policy**|choice|Clustering policy - default is OSSCluster. Specified at create time.|clustering_policy|clusteringPolicy|
|**--eviction-policy**|choice|Redis eviction policy - default is VolatileLRU|eviction_policy|evictionPolicy|
|**--persistence**|object|Persistence settings|persistence|persistence|
|**--modules**|array|Optional set of redis modules to enable in this database - modules can only be added at creation time.|modules|modules|

#### <a name="DatabasesDelete">Command `az redisenterprise database delete`</a>

##### <a name="ExamplesDatabasesDelete">Example</a>
```
az redisenterprise database delete --cluster-name "cache1" --database-name "db1" --resource-group "rg1"
```
##### <a name="ParametersDatabasesDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|

#### <a name="DatabasesExport">Command `az redisenterprise database export`</a>

##### <a name="ExamplesDatabasesExport">Example</a>
```
az redisenterprise database export --cluster-name "cache1" --database-name "default" --sas-uri \
"https://contosostorage.blob.core.window.net/urlToBlobContainer?sasKeyParameters" --resource-group "rg1"
```
##### <a name="ParametersDatabasesExport">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|
|**--sas-uri**|string|SAS URI for the target directory to export to|sas_uri|sasUri|

#### <a name="DatabasesImport">Command `az redisenterprise database import`</a>

##### <a name="ExamplesDatabasesImport">Example</a>
```
az redisenterprise database import --cluster-name "cache1" --database-name "default" --sas-uri \
"https://contosostorage.blob.core.window.net/urltoBlobFile?sasKeyParameters" --resource-group "rg1"
```
##### <a name="ParametersDatabasesImport">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|
|**--sas-uri**|string|SAS URI for the target blob to import from|sas_uri|sasUri|

#### <a name="DatabasesListKeys">Command `az redisenterprise database list-key`</a>

##### <a name="ExamplesDatabasesListKeys">Example</a>
```
az redisenterprise database list-key --cluster-name "cache1" --database-name "default" --resource-group "rg1"
```
##### <a name="ParametersDatabasesListKeys">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|

#### <a name="DatabasesRegenerateKey">Command `az redisenterprise database regenerate-key`</a>

##### <a name="ExamplesDatabasesRegenerateKey">Example</a>
```
az redisenterprise database regenerate-key --cluster-name "cache1" --database-name "default" --key-type "Primary" \
--resource-group "rg1"
```
##### <a name="ParametersDatabasesRegenerateKey">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--database-name**|string|The name of the database.|database_name|databaseName|
|**--key-type**|sealed-choice|Which access key to regenerate.|key_type|keyType|

### group `az redisenterprise operation-status`
#### <a name="OperationsStatusGet">Command `az redisenterprise operation-status show`</a>

##### <a name="ExamplesOperationsStatusGet">Example</a>
```
az redisenterprise operation-status show --operation-id "testoperationid" --location "West US"
```
##### <a name="ParametersOperationsStatusGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--location**|string|The region the operation is in.|location|location|
|**--operation-id**|string|The operation's unique identifier.|operation_id|operationId|

### group `az redisenterprise private-endpoint-connection`
#### <a name="PrivateEndpointConnectionsList">Command `az redisenterprise private-endpoint-connection list`</a>

##### <a name="ExamplesPrivateEndpointConnectionsList">Example</a>
```
az redisenterprise private-endpoint-connection list --cluster-name "cache1" --resource-group "rg1"
```
##### <a name="ParametersPrivateEndpointConnectionsList">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|

#### <a name="PrivateEndpointConnectionsGet">Command `az redisenterprise private-endpoint-connection show`</a>

##### <a name="ExamplesPrivateEndpointConnectionsGet">Example</a>
```
az redisenterprise private-endpoint-connection show --cluster-name "cache1" --name "pectest01" --resource-group "rg1"
```
##### <a name="ParametersPrivateEndpointConnectionsGet">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsDelete">Command `az redisenterprise private-endpoint-connection delete`</a>

##### <a name="ExamplesPrivateEndpointConnectionsDelete">Example</a>
```
az redisenterprise private-endpoint-connection delete --cluster-name "cache1" --name "pectest01" --resource-group \
"rg1"
```
##### <a name="ParametersPrivateEndpointConnectionsDelete">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|

#### <a name="PrivateEndpointConnectionsPut">Command `az redisenterprise private-endpoint-connection put`</a>

##### <a name="ExamplesPrivateEndpointConnectionsPut">Example</a>
```
az redisenterprise private-endpoint-connection put --cluster-name "cache1" --name "pectest01" \
--private-link-service-connection-state description="Auto-Approved" status="Approved" --resource-group "rg1"
```
##### <a name="ParametersPrivateEndpointConnectionsPut">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
|**--private-endpoint-connection-name**|string|The name of the private endpoint connection associated with the Azure resource|private_endpoint_connection_name|privateEndpointConnectionName|
|**--private-link-service-connection-state**|object|A collection of information about the state of the connection between service consumer and provider.|private_link_service_connection_state|privateLinkServiceConnectionState|

### group `az redisenterprise private-link-resource`
#### <a name="PrivateLinkResourcesListByCluster">Command `az redisenterprise private-link-resource list`</a>

##### <a name="ExamplesPrivateLinkResourcesListByCluster">Example</a>
```
az redisenterprise private-link-resource list --cluster-name "cache1" --resource-group "rg1"
```
##### <a name="ParametersPrivateLinkResourcesListByCluster">Parameters</a> 
|Option|Type|Description|Path (SDK)|Swagger name|
|------|----|-----------|----------|------------|
|**--resource-group-name**|string|The name of the resource group. The name is case insensitive.|resource_group_name|resourceGroupName|
|**--cluster-name**|string|The name of the RedisEnterprise cluster.|cluster_name|clusterName|
