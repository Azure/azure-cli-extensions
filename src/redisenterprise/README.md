# Azure CLI RedisEnterprise Extension #
This Azure CLI extension manages Azure Managed Redis and Azure Cache for Redis Enterprise resources.

This preview extension uses management API version `2026-10-01-preview` for Azure Managed Redis and Azure Cache for Redis Enterprise.

### How to use ###
Use Azure CLI version 2.75.0 or later. Once this preview is available in the extension index, install it:
```
az extension add --name redisenterprise --allow-preview true --version 1.6.0b1
```

The examples use Bash and assume you are signed in, have selected the intended subscription, and have an existing resource group named `rg1`. Choose unique cache names and a supported region with capacity for your chosen SKU; the create example uses `eastus2`.

Examples are not a script to run from top to bottom. Run delete examples only when you have finished using the resource. Migration, operation-status, import, and export examples have additional prerequisites described below.

### Included Features ###
#### redisenterprise operation-status ####
##### Show #####
This command requires the operation ID and region from the `Azure-AsyncOperation` response header of an asynchronous management operation. For migration undo, `Location` identifies the migration resource, not the operation-status endpoint. An invented operation ID will not work.

```
read -r -p "Operation ID from the Azure-AsyncOperation response header: " operation_id
read -r -p "Operation region from the Azure-AsyncOperation response header: " operation_location
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
##### Firewall rules (Azure Managed Redis only) #####
Set the complete rule set with `--firewall-rules`. Rules accept IPv4 addresses, IPv4 CIDR ranges, and supported Azure service tags, not IPv6. At most 250 rules are supported. Non-empty rules require public network access to be enabled.

```
az redisenterprise create --cluster-name "restrictedcache" --resource-group "rg1" \
    --location "eastus2" --sku "Balanced_B1" --no-database --public-network-access Enabled \
    --firewall-rules '[{"name":"office","source-address-prefix":"203.0.113.0/24"}]'
az redisenterprise update --cluster-name "restrictedcache" --resource-group "rg1" \
    --firewall-rules '[{"name":"office","source-address-prefix":"198.51.100.0/24"}]'
```

Update replaces all rules with the supplied array; omitting `--firewall-rules` preserves them. Create uses PUT: omitting rules or supplying `[]` clears them, including when recreating an existing cluster. When disabling public network access, explicitly clear existing rules with `--public-network-access Disabled --firewall-rules '[]'`. **With public network access enabled, clearing rules allows all public traffic; it does not deny all traffic.** Do not combine firewall changes with scaling or encryption changes in one update.

##### Custom Redis ACL assignments #####
Assign custom permissions to a Microsoft Entra object on an existing default database:

```
az redisenterprise database access-policy-assignment create --cluster-name "cache1" \
    --resource-group "rg1" --database-name default --access-policy-assignment-name reader \
    --object-id "<Microsoft Entra object ID>" --access-string '+@read ~cache:*'
az redisenterprise database access-policy-assignment update --cluster-name "cache1" \
    --resource-group "rg1" --database-name default --access-policy-assignment-name reader \
    --access-string '+get ~cache:*'
```

If omitted on create, `accessString` defaults to `+@all ~*`. `--access-policy-name` remains available for compatibility but is deprecated in this preview; responses always report `default`. Show and list responses include read-only `provisioningError` details when applying an ACL fails.

##### Unlink an endpoint migrated from Azure Cache for Redis Enterprise #####
Use this cluster-level command after an Azure Cache for Redis Enterprise cluster has been migrated to Azure Managed Redis. Verify that applications use the current Azure Managed Redis endpoint before removing the legacy migrated endpoint.

```
az redisenterprise unlink-migrated-endpoint --cluster-name "cache1" --resource-group "rg1"
```
#### redisenterprise migration ####
Migrate Azure Cache for Redis instances (**Basic, Standard, or Premium only**) to Azure Managed Redis. The examples use an existing source cache named `sourcecache` in `rg1`.

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
Use this migration-level command, not the cluster-level command above, for an Azure Cache for Redis source in the Basic, Standard, or Premium tier.

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