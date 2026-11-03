# Azure CLI RedisEnterprise Extension #
This Azure CLI extension manages Azure Managed Redis and Azure Cache for Redis Enterprise resources.

The extension uses stable management API version `2026-09-01` for Azure Managed Redis and Azure Cache for Redis Enterprise.

### How to use ###
Use Azure CLI version 2.75.0 or later. Install the extension:
```
az extension add --name redisenterprise
```

The examples use Bash and assume you are signed in, have selected the intended subscription, and have an existing resource group named `rg1`. Choose unique cache names and a supported region with capacity for your chosen SKU; the create example uses `eastus2`.

Examples are not a script to run from top to bottom. Run delete examples only when you have finished using the resource. Migration, operation-status, import, and export examples have additional prerequisites described below.

### Included Features ###
#### redisenterprise operation-status ####
##### Show #####
This command requires the operation ID and region from the `Location` response header of an asynchronous management operation. An invented operation ID will not work.

```
read -r -p "Operation ID from the Location response header: " operation_id
read -r -p "Operation region: " operation_location
az redisenterprise operation-status show --operation-id "$operation_id" --location "$operation_location"
```
#### redisenterprise ####
##### Create #####
Create an Azure Managed Redis cluster without a database. Use the database create example below to add its default database.

```
az redisenterprise create --cluster-name "cache1" --location "eastus2" --minimum-tls-version "1.2" \
    --sku "Balanced_B1" --high-availability "Disabled" --public-network-access "Enabled" \
    --tags tag1="value1" --no-database --resource-group "rg1"
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
az redisenterprise update --cluster-name "cache1" --minimum-tls-version "1.2" \
    --tags tag1="value1" tag2="value2" --resource-group "rg1"
```
##### Delete #####
```
az redisenterprise delete --cluster-name "cache1" --resource-group "rg1"
```
##### Unlink an endpoint migrated from Azure Cache for Redis Enterprise #####
Use this cluster-level command after an Azure Cache for Redis Enterprise cluster has been migrated to Azure Managed Redis. Verify that applications use the current Azure Managed Redis endpoint before removing the legacy migrated endpoint.

```
az redisenterprise unlink-migrated-endpoint --cluster-name "cache1" --resource-group "rg1"
```
#### redisenterprise migration ####
These commands migrate an existing Azure Cache for Redis instance to a compatible Azure Managed Redis target cluster. The example assumes an existing source named `sourcecache` in `rg1`. Retrieve its actual resource ID rather than typing a sample subscription ID.

Prepare a separate target with the nonclustered configuration used for an OSS migration. The source region must support the target SKU and have available capacity.

```
source_cache_resource_id=$(az redis show --name "sourcecache" --resource-group "rg1" --query id -o tsv)
source_cache_location=$(az redis show --name "sourcecache" --resource-group "rg1" --query location -o tsv)
az redisenterprise create --cluster-name "migrationcache" --resource-group "rg1" \
    --location "$source_cache_location" --sku "Balanced_B1" --high-availability "Disabled" \
    --clustering-policy "NoCluster" --eviction-policy "NoEviction" \
    --minimum-tls-version "1.2" --access-keys-auth "Enabled" --public-network-access "Enabled"
```

##### Validate a migration with data transfer #####
```
az redisenterprise migration validate --cluster-name "migrationcache" --resource-group "rg1" \
    --source-resource-id "$source_cache_resource_id" --skip-data-migration false
```
Resolve validation errors and review warnings before starting. Proceed only when `isValid` is `true`.

##### Start a migration with data transfer #####
This example includes data transfer and requests automatic DNS switching:
```
az redisenterprise migration start --cluster-name "migrationcache" --resource-group "rg1" \
    --source-resource-id "$source_cache_resource_id" --skip-data-migration false --switch-dns true
```
To deliberately omit data transfer, use `--skip-data-migration true` on both commands. **That setting does not copy the source cache's data.**

##### Check migration status #####
```
az redisenterprise migration show --cluster-name "migrationcache" --resource-group "rg1"
az redisenterprise migration list --cluster-name "migrationcache" --resource-group "rg1"
```
##### Undo a migration #####
For a successful migration, `properties.rollbackEligibleUntil` gives the rollback deadline. Keep the source cache available until you no longer need rollback.

```
az redisenterprise migration undo --cluster-name "migrationcache" --resource-group "rg1" --rollback-reason performance
```
##### Unlink an endpoint migrated from Azure Cache for Redis #####
Use this migration-level command, not the cluster-level command above, for an Azure Cache for Redis source.

The source cache must be deleted before its migrated endpoint can be unlinked. Before deleting it, verify the target data and application connectivity and confirm you no longer need rollback.
```
az redisenterprise migration unlink-migrated-endpoint --cluster-name "migrationcache" --resource-group "rg1"
```
#### redisenterprise database ####
##### Create #####
The cluster must not already have a default database. The cluster create example above uses `--no-database` for this reason.

```
az redisenterprise database create --cluster-name "cache1" --client-protocol "Encrypted" \
    --clustering-policy "EnterpriseCluster" --eviction-policy "NoEviction" \
    --port 10000 --resource-group "rg1"
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
    --eviction-policy "AllKeysLRU" --resource-group "rg1"
```
##### Export #####
Use an existing blob container and a valid, unexpired container SAS granting read, add, create, and write permissions. The storage account must allow the service's network access. Enter the real SAS URI at the prompt; treat it as a secret.

```
read -r -s -p "Blob container SAS URI: " container_sas_uri
printf '\n'
az redisenterprise database export --cluster-name "cache1" \
    --sas-uri "$container_sas_uri" --resource-group "rg1"
unset container_sas_uri
```
##### Import #####
Use the URI of an existing compatible Redis export blob, with a valid, unexpired SAS granting read permission. The storage account must allow the service's network access. Import replaces the target database's data; use a disposable target or back up data first.

```
read -r -s -p "Export blob SAS URI: " blob_sas_uri
printf '\n'
az redisenterprise database import --cluster-name "cache1" \
    --sas-uris "$blob_sas_uri" --resource-group "rg1"
unset blob_sas_uri
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