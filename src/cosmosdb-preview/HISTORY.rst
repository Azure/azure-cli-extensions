.. :changelog:

Release History
===============
1.0.0
* Add support for Per-Region Per-Partition Autoscale. '--enable-prpp-autoscale' parameter can be used during account create/update.
* Add support for Restore with Time-To-Live Disabled. '--disable-ttl' parameter can be used during restore.
* Add support for online mode in container copy job.
* Add support for minimum allowed TLS version configuration
* BREAKING CHANGE: az cosmosdb create/update: Rename --enable-public-network true/false to --public-network-access ENABLED/DISABLED/SECUREDBYPERIMETER
* BREAKING CHANGE: az cosmosdb restore: Rename --enable-public-network true/false to --public-network-access ENABLED/DISABLED

++++++
0.26.0
* Add '--enable-priority-based-execution' and '--default-priority-level' parameter for create/update database account.
* Add support for cross account container copy
* Add Non-CMK to CMK support
* Removed preview tag from CMK related properties

++++++
0.25.0
* Add support for performing database merge for Sql and MongoDB database account.

++++++
0.24.0
* Create and manage mongo clusters.
* Add 'source_backup_location' parameter to 'cosmosdb restore' command
* Add support for performing in-account restore of deleted databases and graphs in a Gremlin account.
* Add support for performing in-account restore of deleted tables in a Table account.
* Add `--enable-burst-capacity` parameter for create/update database account.

++++++
0.23.0
* Add 'enable_public_network' param to 'cosmosdb restore' command

++++++
0.22.0
* Add fix for restorable resources APIs.

++++++
0.21.0
* Add support for mongo data transfer jobs.

++++++
0.20.0
* Add support for Continuous mode restore with user provided identity.

0.19.0
++++++
* Add support for performing in-account restore of deleted databases and containers for a Sql database account.
* Add support for performing in-account restore of deleted databases and collections for a MongoDB database account.

0.18.1
++++++
* Modify parameter for Managed Identity name.

0.18.0
++++++
* Add support for retrieving and redistributing throughput at physical partition level.

0.17.0
++++++
* Add support for new Continuous 7 Days backup mode
* Add oldest restorable timestamp to indicate when the accounts can be restored to

0.16.0
++++++
* Create and manage data transfer jobs.

0.15.0
++++++
* Add `--enable-materialized-views` parameter for create/update database account.

0.14.0
++++++
* List the different versions of databases and graphs that were modified for a gremlin database account.
* List the different versions of tables that were modified for a table database account.
* Trigger a point in time restore on the Azure CosmosDB continuous mode backup accounts for gremlin and table database account.
* Retrieve latest restorable timestamp for graphs and tables in gremlin and table database account respectively.
* Filter restorable collections, graphs and tables event feed by start and end time.

0.13.0
++++++
* Create and manage Role Definitions and User Definitions for enforcing data plane RBAC on Cosmos DB MongoDB accounts

0.12.0
++++++
* Modify parameter names for Ldap support in Managed Instance for Apache Cassandra.

0.11.0
++++++
* Add Ldap support for Managed Instance for Apache Cassandra.

0.10.0
++++++
* Adding support for Services APIs and Graph Resources.

0.9.0
++++++
* Fixing Managed Cassandra issues that were introduced due to updating to python sdk 4.0.

0.8.0
++++++
* Adding the support for conversion of accounts from periodic to continuous backup policy and updating to python sdk 4.0.

0.7.0
++++++
* Removing APIs to create and manage Role Definitions and Role Assignments since they are now GA.

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
