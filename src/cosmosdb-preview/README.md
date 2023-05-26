# Microsoft Azure CLI 'cosmosdb-preview' Extension #

This package is for the 'cosmosdb-preview' extension.
This package provides commands to

- Create Azure CosmosDB continuous backup accounts
- List the different versions of databases and collections that were modified
- Trigger a point in time restore on the Azure CosmosDB continuous mode backup accounts
- Update the backup interval and backup retention of periodic mode backup accounts
- Create a new Azure Cosmos DB database account with materialized views
- Update an Azure Cosmos DB database account to enable materialized views
- Create/Delete a cosmosdb materialized views builder service resource
- Provision and update database account with Continuous 7 days backup mode
- Retrieve and redistribute throughput at physical partition level.
- Create a new Azure Cosmos DB database account with burst capacity.
- Update an Azure Cosmos DB database account to enable/disable burst capacity.

## How to use ##

Install this extension using the below CLI command

```sh
az extension add --name cosmosdb-preview
```

### Included Features ###

#### Create a new CosmosDB continuous backup Account ####

```sh
az cosmosdb create \
    --resource-group "my-rg" \
    --name "my-continuous-backup-account" \
    --backup-policy-type "Continuous"
```

#### Create a new CosmosDB continuous backup Account with 7 days retention ####

```sh
az cosmosdb create \
    --resource-group "my-rg" \
    --name "my-continuous-backup-account" \
    --backup-policy-type "Continuous"
    --continuous-tier "Continuous7Days"
```

#### Convert a periodic backup policy CosmosDB account to continuous backup Account ####

```sh
az cosmosdb update \
    --resource-group "my-rg" \
    --name "my-continuous-backup-account" \
    --backup-policy-type "Continuous"
```

#### Convert a periodic backup policy CosmosDB account to continuous backup Account with 7 days retention ####

```sh
az cosmosdb update \
    --resource-group "my-rg" \
    --name "my-continuous-backup-account" \
    --backup-policy-type "Continuous" \
    --continuous-tier "Continuous7Days"
```

#### List all the CosmosDB accounts that can be restored (live and deleted) ####

This command returns all the continuous mode backup accounts that can be restored.

```sh
az cosmosdb restorable-database-account list
```

#### List all the CosmosDB accounts with the given name that can be restored (live and deleted) ####

This command returns all the continuous mode backup accounts with the given name that can be restored.

```sh
az cosmosdb restorable-database-account list --name "account-name"
```

#### Restore from an existing(live or deleted) Sql/MongoDB database account to a new account ####

```sh
az cosmosdb restore --resource-group "my-rg" \
    --target-database-account-name "restored-account" \
    --source-database-account-name "mysourceaccount" \
    --restore-timestamp "2020-07-20T16:09:53+0000" \
    --location "westus" \
    --databases-to-restore name="MyDB1" collections="collection1" "collection2" \
    --databases-to-restore name="MyDB2" collections="collection3" "collection4"
```

#### Restore from an existing(live or deleted) Gremlin database account to a new account ####

```sh
az cosmosdb restore --resource-group "my-rg" \
    --target-database-account-name "restored-account" \
    --source-database-account-name "mysourceaccount" \
    --restore-timestamp "2020-07-20T16:09:53+0000" \
    --location "westus" \
    --gremlin-databases-to-restore name="MyDB1" graphs="collection1" "collection2" \
    --gremlin-databases-to-restore name="MyDB2" graphs="collection3" "collection4"
```

#### Restore from an existing(live or deleted) Table database account to a new account ####

```sh
az cosmosdb restore --resource-group "my-rg" \
    --target-database-account-name "restored-account" \
    --source-database-account-name "mysourceaccount" \
    --restore-timestamp "2020-07-20T16:09:53+0000" \
    --location "westus" \
    --tables-to-restore "table1" "table2" \
    --tables-to-restore "table3" "table4"
```

#### List all the versions of sql databases in a live database account ####

```sh
az cosmosdb sql restorable-database list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus"
```

#### List all the versions of sql containers of a database in a live database account ####

```sh
az cosmosdb sql restorable-container list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --database-rid "AoQ13r=="
    --location "westus"
```

#### List all the resources of a sql database account that are available to restore at a given timestamp and region ####

```sh
az cosmosdb sql restorable-resource list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus" \
    --restore-location "eastus" \
    --restore-timestamp "2020-07-20T16:09:53+0000"
```

#### List all the versions of mongodb databases in a live database account ####

```sh
az cosmosdb mongodb restorable-database list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus"
```

#### List all the versions of mongodb collections of a database in a live database account ####

```sh
az cosmosdb mongodb restorable-collection list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --database-rid "AoQ13r=="
    --location "westus"
```

#### List all the resources of a mongodb database account that are available to restore at a given timestamp and region ####

```sh
az cosmosdb mongodb restorable-resource list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus" \
    --restore-location "westus" \
    --restore-timestamp "2020-07-20T16:09:53+0000"
```

#### List all the versions of Gremlin databases in a live database account ####

```sh
az cosmosdb gremlin restorable-database list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus"
```

#### List all the versions of Gremlin graphs of a database in a live database account ####

```sh
az cosmosdb gremlin restorable-graph list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --database-rid "AoQ13r=="
    --location "westus"
```

#### List all the resources of a Gremlin database account that are available to restore at a given timestamp and region ####

```sh
az cosmosdb gremlin restorable-resource list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus" \
    --restore-location "eastus" \
    --restore-timestamp "2020-07-20T16:09:53+0000"
```

#### List all the versions of tables in a live database account ####

```sh
az cosmosdb table restorable-table list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus"
```

#### List all the resources of a table database account that are available to restore at a given timestamp and region ####

```sh
az cosmosdb table restorable-resource list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus" \
    --restore-location "eastus" \
    --restore-timestamp "2020-07-20T16:09:53+0000"
```

#### Create a new CosmosDB materialized views enabled Account ####

```sh
az cosmosdb create \
    --resource-group "my-rg" \
    --name "my-db-account" \
    --enable-materialized-views true \
    --capabilities "EnableCassandra" "CassandraEnableMaterializedViews"
```

#### Enable materialized views on a existing CosmosDB Account ####

```sh
az cosmosdb update \
    --resource-group "my-rg" \
    --name "my-db-account" \
    --enable-materialized-views true
```

#### Create a cosmosdb materialized views builder service resource ####

```sh
az cosmosdb service create \
    --resource-group "MyResourceGroup" \
    --account-name "MyAccount" \
    --name "MaterializedViewsBuilder" \
    --kind "MaterializedViewsBuilder" \
    --count 3 \
    --size "Cosmos.D4s"
```

#### Update a cosmosdb materialized views builder service resource ####

```sh
az cosmosdb service update \
    --resource-group "MyResourceGroup" \
    --account-name "MyAccount" \
    --name "MaterializedViewsBuilder" \
    --kind "MaterializedViewsBuilder" \
    --count 3
```

#### Delete the cosmosdb materialized views builder service resource ####

```sh
az cosmosdb service delete \
    --resource-group "MyResourceGroup" \
    --account-name "MyAccount" 
    --name "MaterializedViewsBuilder" \
```

#### Create a new CosmosDB burst capacity enabled Account ####

```sh
az cosmosdb create \
    --resource-group "my-rg" \
    --name "my-db-account" \
    --enable-burst-capacity true
```

#### Enable burst capacity on an existing CosmosDB Account ####

```sh
az cosmosdb update \
    --resource-group "my-rg" \
    --name "my-db-account" \
    --enable-burst-capacity true
```

#### Restore a deleted database within same account for a Sql database account ####

```sh
az cosmosdb sql database restore --account-name "account-name" \
    --name "database-name"
    --restore-timestamp "2020-07-20T16:09:53+0000" \
```

#### Restore a deleted container within same account for a Sql database account ####

```sh
az cosmosdb sql container restore --account-name "account-name" \
    --database-name "database-name"
    --name "container-name"
    --restore-timestamp "2020-07-20T16:09:53+0000" \
```

#### Restore a deleted database within same account for a MongoDB database account ####

```sh
az cosmosdb mongodb database restore --account-name "account-name" \
    --name "database-name"
    --restore-timestamp "2020-07-20T16:09:53+0000" \
```

#### Restore a deleted collection within same account for a MongoDB database account ####

```sh
az cosmosdb mongodb collection restore --account-name "account-name" \
    --database-name "database-name"
    --collection-name "collection-name"
    --restore-timestamp "2020-07-20T16:09:53+0000" \
```

#### Restore a deleted container within same account for a Gremlin database account ####

```sh
az cosmosdb gremlin graph restore --account-name "account-name" \
    --database-name "database-name"
    --name "graph-name"
    --restore-timestamp "2022-07-20T16:09:53+0000" \
```

#### Restore a deleted database within same account for a Gremlin database account ####

```sh
az cosmosdb gremlin database restore --account-name "account-name" \
    --name "database-name"
    --restore-timestamp "2022-07-20T16:09:53+0000" \
```

#### Restore a deleted collection within same account for a Table account ####

```sh
az cosmosdb table restore --account-name "account-name" \
    --table-name "table-name"
    --restore-timestamp "2022-07-20T16:09:53+0000" \
```