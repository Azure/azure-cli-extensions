# Azure CLI RedisEnterprise Extension #
This is an extension to Azure CLI to manage redisenterprise resources.

### How to use ###
Install this extension using the below CLI command
```
az extension add --name redisenterprise
```

### Included Features ###
#### redisenterprise operation-status ####
##### Show #####
```
az redisenterprise operation-status show --operation-id "testoperationid" --location "West US"
```
#### redisenterprise ####
##### Create #####
```
az redisenterprise create --cluster-name "cache1" --location "West US" --minimum-tls-version "1.2" \
    --sku "EnterpriseFlash_F300" --capacity 3 --tags tag1="value1" --zones "1" "2" "3" --resource-group "rg1" 
```
##### Show #####
```
az redisenterprise show --cluster-name "cache1" --resource-group "rg1"
```
##### List #####
```
az redisenterprise list --resource-group "rg1"
```
##### Update #####
```
az redisenterprise update --cluster-name "cache1" --minimum-tls-version "1.2" --sku "EnterpriseFlash_F300" \
    --capacity 9 --tags tag1="value1" --resource-group "rg1" 
```
##### Delete #####
```
az redisenterprise delete --cluster-name "cache1" --resource-group "rg1"
```
#### redisenterprise database ####
##### Create #####
```
az redisenterprise database create --cluster-name "cache1" --client-protocol "Encrypted" \
    --clustering-policy "EnterpriseCluster" --eviction-policy "AllKeysLRU" \
    --modules name="RedisBloom" args="ERROR_RATE 0.00 INITIAL_SIZE 400" \
    --modules name="RedisTimeSeries" args="RETENTION_POLICY 20" --modules name="RediSearch" \
    --persistence aof-enabled=true aof-frequency="1s" --port 10000 --resource-group "rg1" 
```
##### Show #####
```
az redisenterprise database show --cluster-name "cache1" --resource-group "rg1"
```
##### List #####
```
az redisenterprise database list --cluster-name "cache1" --resource-group "rg1"
```
##### Update #####
```
az redisenterprise database update --cluster-name "cache1" --client-protocol "Encrypted" \
    --eviction-policy "AllKeysLRU" --persistence rdb-enabled=true rdb-frequency="12h" --resource-group "rg1" 
```
##### Export #####
```
az redisenterprise database export --cluster-name "cache1" \
    --sas-uri "https://contosostorage.blob.core.window.net/urlToBlobContainer?sasKeyParameters" --resource-group "rg1" 
```
##### Import #####
```
az redisenterprise database import --cluster-name "cache1" \
    --sas-uri "https://contosostorage.blob.core.window.net/urltoBlobFile?sasKeyParameters" --resource-group "rg1" 
```
##### List-keys #####
```
az redisenterprise database list-keys --cluster-name "cache1" --resource-group "rg1"
```
##### Regenerate-key #####
```
az redisenterprise database regenerate-key --cluster-name "cache1" --key-type "Primary" --resource-group "rg1"
```
##### Delete #####
```
az redisenterprise database delete --cluster-name "cache1" --resource-group "rg1"
```