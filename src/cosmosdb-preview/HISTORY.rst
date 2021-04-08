.. :changelog:

Release History
===============

0.6.0
++++++
* Addressing CLI bugs for Managed Cassandra Service and updating to python sdk 4.0.

0.5.0
++++++
* Create and Manage Azure Managed Cassandra Clusters and Cassandra Datacenters.

0.4.0
++++++
* Fix error propagation for failures in case of data plane RBAC and Restore related requests.
* Allow customer to specify associated Role Definition using name when creating or updating Role Assignments.

0.3.0
++++++
* Create and manage Role Definitions and Role Assignments for enforcing data plane RBAC on Cosmos DB SQL accounts

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
