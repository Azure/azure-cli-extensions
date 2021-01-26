# Microsoft Azure CLI 'cosmosdb-preview' Extension #

This package is for the 'cosmosdb-preview' extension.
This package provides commands to

- Create Azure CosmosDB continuous backup accounts
- List the different versions of databases and collections that were modified
- Trigger a point in time restore on the Azure CosmosDB continuous mode backup accounts
- Update the backup interval and backup retention of periodic mode backup accounts

## How to use ##

Install this extension using the below CLI command

```sh
az extension add --name cosmodb-preview
```

### Included Features ###

#### Create a new CosmosDB continuous backup Account ####

```sh
az cosmosdb create \
    --resource-group "my-rg" \
    --name "my-continuous-backup-account" \
    --backup-policy-type "Continuous"
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

#### Restore from an existing(live or deleted) database account to a new account ####

```sh
az cosmosdb restore --resource-group "my-rg" \
    --target-database-account-name "restored-account" \
    --source-database-account-name "mysourceaccount" \
    --restore-timestamp "2020-07-20T16:09:53+0000" \
    --location "westus" \
    --databases-to-restore name="MyDB1" collections="collection1" "collection2" \
    --databases-to-restore name="MyDB2" collections="collection3" "collection4"
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

#### List all the resources of a database account that are avaiable to restore at a given timestamp and region ####

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

#### List all the resources of a mongodb database account that are avaiable to restore at a given timestamp and region ####

```sh
az cosmosdb mongodb restorable-resource list \
    --instance-id "d056a4f8-044a-436f-80c8-cd3edbc94c68" \
    --location "westus" \
    --restore-location "westus" \
    --restore-timestamp "2020-07-20T16:09:53+0000"
```
