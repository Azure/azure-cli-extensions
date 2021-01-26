.. :changelog:

Release History
===============

0.2.0
++++++
* Utc is taken as the default timezone when the timezone is not specified in the restore timestamp
* Added the `--name` parameter to `az cosmosdb restorable-database-account list` to return all the restorable database accounts with the given name

0.1.0
++++++
* Create Azure CosmosDB continuous backup accounts
* List the different versions of databases and collections that were modified
* Trigger a point in time restore on the Azure CosmosDB continuous mode backup accounts
* Update the backup interval and backup retention of periodic mode backup accounts
