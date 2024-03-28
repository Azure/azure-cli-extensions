# pylint: disable=too-many-lines
# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, missing-function-docstring

from knack.help_files import helps  # pylint: disable=unused-import

helps['cosmosdb mongocluster firewall'] = """
type: group
short-summary: Mongo cluster firewall.
"""

helps['cosmosdb mongocluster firewall rule'] = """
type: group
short-summary: Mongo cluster firewall rule.
"""

helps['cosmosdb mongocluster firewall rule create'] = """
type: command
short-summary: Create a Mongo cluster firewall rule.
examples:
  - name: Create a Mongo cluster firewall rule.
    text: |
      az cosmosdb mongocluster firewall rule create \\
      --cluster-name MyCluster \\
      --resource-group MyResourceGroup \\
      --rule-name MyRule \\
      --start-ip-address MyStartIpAddress \\
      --end-ip-address MyEndIpAddress \\
"""

helps['cosmosdb mongocluster firewall rule update'] = """
type: command
short-summary: Create a Mongo cluster firewall rule.
examples:
  - name: Update a Mongo cluster firewall rule.
    text: |
      az cosmosdb mongocluster firewall rule update \\
      --cluster-name MyCluster \\
      --resource-group MyResourceGroup \\
      --rule-name MyRule \\
      --start-ip-address MyStartIpAddress \\
      --end-ip-address MyEndIpAddress \\
"""

helps['cosmosdb mongocluster firewall rule list'] = """
type: command
short-summary: Lists firewall rule on a Mongo cluster.
examples:
  - name: Lists a Mongo cluster firewall rule in a resource group.
    text: |
      az cosmosdb mongocluster firewall rule list --cluster-name MyCluster --resource-group MyResourceGroup
"""

helps['cosmosdb mongocluster firewall rule show'] = """
type: command
short-summary: Get a Mongo cluster firewall rule.
examples:
  - name: Gets a Mongo cluster firewall rule. If the firewall rule does not exist a NotFound response is returned.
    text: |
      az cosmosdb mongocluster firewall rule show --cluster-name MyCluster --resource-group MyResourceGroup --rule-name MyRuleName
"""

helps['cosmosdb mongocluster firewall rule delete'] = """
type: command
short-summary: Delete a Mongo cluster firewall rule.
examples:
  - name: Delete a Mongo Cluster firewall rule. If the firewall rule does not exist a NoContent response is returned.
    text: |
      az cosmosdb mongocluster firewall rule delete --cluster-name MyCluster --resource-group MyResourceGroup --rule-name MyRuleName
"""

helps['cosmosdb mongocluster'] = """
type: group
short-summary: Mongo cluster.
"""

helps['cosmosdb mongocluster create'] = """
type: command
short-summary: Create a Mongo cluster.
examples:
  - name: Create a Mongo cluster.
    text: |
      az cosmosdb mongocluster create \\
      --cluster-name MyCluster \\
      --resource-group MyResourceGroup \\
      --location MyLocation \\
      --administrator-login MyAdminUser \\
      --administrator-login-password MyAdminPassword \\
      --server-version 5.0 \\
      --shard-node-tier "M30" \\
      --shard-node-ha true \\
      --shard-node-disk-size-gb 128 \\
      --shard-node-count 2
"""

helps['cosmosdb mongocluster update'] = """
type: command
short-summary: Update a Mongo cluster.
examples:
  - name: Update a Mongo cluster.
    text: |
      az cosmosdb mongocluster update \\
      --cluster-name MyCluster \\
      --resource-group MyResourceGroup \\
      --administrator-login MyAdminUser \\
      --administrator-login-password MyAdminPassword \\
      --server-version 5.0 \\
      --shard-node-tier "M30" \\
      --shard-node-ha true \\
      --shard-node-disk-size-gb 128
"""

helps['cosmosdb mongocluster list'] = """
type: command
short-summary: List a Mongo Cluster Resource.
examples:
  - name: Lists Mongo Cluster Resource list in a resource group.
    text: |
      az cosmosdb mongocluster list --resource-group MyResourceGroup
  - name: Lists a Mongo Cluster Resource list in the subscription.
    text: |
      az cosmosdb mongocluster list
"""

helps['cosmosdb mongocluster show'] = """
type: command
short-summary: Get a Mongo Cluster Resource.
examples:
  - name: Gets a Mongo Cluster Resource. ProvisioningState tells the state of this cluster. If the cluster does not exist a NotFound response is returned.
    text: |
      az cosmosdb mongocluster show --cluster-name MyCluster --resource-group MyResourceGroup
"""

helps['cosmosdb mongocluster delete'] = """
type: command
short-summary: Delete a Mongo Cluster Resource.
examples:
  - name: Deletes a Mongo Cluster Resource. If the cluster does not exist a NoContent response is returned.
    text: |
      az cosmosdb mongocluster delete --cluster-name MyCluster --resource-group MyResourceGroup
"""

helps['managed-cassandra'] = """
type: group
short-summary: Azure Managed Cassandra.
long-summary: See https://docs.microsoft.com/en-us/azure/managed-instance-apache-cassandra/manage-resources-cli for Cassandra API samples.
"""

helps['managed-cassandra cluster'] = """
type: group
short-summary: Azure Managed Cassandra Cluster.
long-summary: See https://docs.microsoft.com/en-us/azure/managed-instance-apache-cassandra/manage-resources-cli for Cassandra API samples.
"""

helps['managed-cassandra cluster create'] = """
type: command
short-summary: Create a Managed Cassandra Cluster.
examples:
  - name: Create a Managed Cassandra Cluster in a given Subscription and ResourceGroup. Either a cassandra admin password or external seed needs are required.
    text: |
      az managed-cassandra cluster create \\
      --resource-group MyResourceGroup \\
      --cluster-name MyCluster \\
      --location MyLocation \\
      --initial-cassandra-admin-password password \\
      --delegated-management-subnet-id /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/My-vnet/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/test-subnet
"""

helps['managed-cassandra cluster update'] = """
type: command
short-summary: Update a Managed Cassandra Cluster.
examples:
  - name: Update External Seed Nodes of a given cluster.
    text: |
      az managed-cassandra cluster update --resource-group MyResourceGroup --cluster-name MyCluster --external-seed-nodes 127.0.0.1 127.0.0.2
  - name: Update External Gossip Certificates of a given cluster. Certs can be passed in as strings or the file locations.
    text: |
      az managed-cassandra cluster update --resource-group MyResourceGroup --cluster-name MyCluster --external-gossip-certificates C:/MyFolder/test.pem BeginCert-MLXCF-EndCert
"""

helps['managed-cassandra cluster delete'] = """
type: command
short-summary: Deletes a Managed Cassandra Cluster.
examples:
  - name: Deletes a Managed Cassandra Cluster in the given Subscription and ResourceGroup.
    text: |
      az managed-cassandra cluster delete --resource-group MyResourceGroup --cluster-name MyCluster
"""

helps['managed-cassandra cluster show'] = """
type: command
short-summary: Get a Managed Cassandra Cluster Resource.
examples:
  - name: Gets a Managed Cassandra Cluster Resource. ProvisioningState tells the state of this cluster. If the cluster doesnot exist a NotFound response is returned.
    text: |
      az managed-cassandra cluster show --resource-group MyResourceGroup --cluster-name MyCluster
"""

helps['managed-cassandra cluster list'] = """
type: command
short-summary: List the Managed Cassandra Clusters in a ResourceGroup and Subscription. If the ResourceGroup is not specified all the clusters in this Subscription are returned.
examples:
  - name: List all Managed Cassandra Clusters in a given Subscription and ResourceGroup.
    text: |
      az managed-cassandra cluster list --resource-group MyResourceGroup
  - name: List all Managed Cassandra Clusters in a given Subscription.
    text: |
      az managed-cassandra cluster list
"""

helps['managed-cassandra cluster backup list'] = """
type: command
short-summary: List the backups of this cluster that are available to restore.
examples:
  - name: This command lists the backups of this cluster that are available to restore.
    text: |
      az managed-cassandra cluster backup list --resource-group MyResourceGroup --cluster-name MyCluster
"""

helps['managed-cassandra cluster backup show'] = """
type: command
short-summary: Get a managed cassandra backup resource of this cluster
examples:
  - name: Gets a managed cassandra backup resource.
    text: |
      az managed-cassandra cluster backup show --resource-group MyResourceGroup --cluster-name MyCluster --backup-id BackUpId
"""

helps['managed-cassandra cluster backup'] = """
type: group
short-summary: Azure Managed Cassandra cluster Backup.
"""

helps['managed-cassandra cluster invoke-command'] = """
type: command
short-summary: Invoke a command like nodetool for cassandra maintenance.
examples:
  - name: This command runs nodetool with these arguments in a host node of the cluster.
    text: |
      az managed-cassandra cluster invoke-command --resource-group MyResourceGroup --cluster-name MyCluster --host "10.0.1.12" --command-name "nodetool" --arguments arg1="value1" arg2="value2" arg3="value3"
"""

helps['managed-cassandra datacenter'] = """
type: group
short-summary: Azure Managed Cassandra DataCenter.
"""

helps['managed-cassandra datacenter create'] = """
type: command
short-summary: Create a Datacenter in an Azure Managed Cassandra Cluster.
examples:
  - name: Create a Managed Cassandra Datacenter in a Cassandra Cluster. Each datacenter should atleast have 3 nodes.
    text: |
      az managed-cassandra datacenter create \\
      --resource-group MyResourceGroup \\
      --cluster-name MyCluster \\
      --data-center-name MyDataCenter \\
      --data-center-location westus2 \\
      --node-count 3 \\
      --delegated-subnet-id /subscriptions/94d9b402-77b4-4049-b4c1-947bc6b7729b/resourceGroups/My-vnet/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/test-subnet
"""

helps['managed-cassandra datacenter update'] = """
type: command
short-summary: Update a Datacenter in an Azure Managed Cassandra Cluster.
examples:
  - name: Scale the number of nodes in a datacenter. This is a scale up operation assuming that the create datacenter was done with 3 nodes. Each datacenter should atleast have 3 nodes.
    text: |
      az managed-cassandra datacenter update --resource-group MyResourceGroup --cluster-name MyCluster --data-center-name MyDataCenter --node-count 6
  - name: Scale the number of nodes in a datacenter. This is a scale down operation assuming that the create datacenter was done with 3 nodes, followed by a scale up to 6 nodes. Each datacenter should atleast have 3 nodes.
    text: |
      az managed-cassandra datacenter update --resource-group MyResourceGroup --cluster-name MyCluster --data-center-name MyDataCenter --node-count 4
"""

helps['managed-cassandra datacenter delete'] = """
type: command
short-summary: Deletes a Managed Cassandra Datacenter.
examples:
  - name: Deletes a Managed Cassandra Datacenter in the given Cluster.
    text: |
      az managed-cassandra datacenter delete --resource-group MyResourceGroup --cluster-name MyCluster --data-center-name MyDataCenter
  - name: Deletes a Managed Cassandra Datacenter in the given Cluster without waiting for the long-running operation to finish.
    text: |
      az managed-cassandra datacenter delete --resource-group MyResourceGroup --cluster-name MyCluster --data-center-name MyDataCenter --no-wait
"""

helps['managed-cassandra datacenter show'] = """
type: command
short-summary: Get a Managed Cassandra DataCenter Resource.
examples:
  - name: Gets a Managed Cassandra Datacenter Resource. ProvisioningState tells the state of this datacenter. If the datacenter does not exist a NotFound response is returned.
    text: |
      az managed-cassandra datacenter show --resource-group MyResourceGroup --cluster-name MyCluster --data-center-name MyDataCenter
"""

helps['managed-cassandra datacenter list'] = """
type: command
short-summary: List the Managed Cassandra Datacenters in a given Cluster.
examples:
  - name: List all Managed Cassandra DataCenters in a given Cluster.
    text: |
      az managed-cassandra datacenter list --resource-group MyResourceGroup --cluster-name MyCluster
"""

helps['cosmosdb service'] = """
type: group
short-summary: Commands to perform operations on Service.
"""

helps['cosmosdb service create'] = """
type: command
short-summary: Create a cosmosdb service resource.
examples:
  - name: Create a cosmosdb service resource.
    text: |
      az cosmosdb service create --resource-group MyResourceGroup --account-name MyAccount --name "sqlDedicatedGateway" --kind "SqlDedicatedGateway" --count 3 --size "Cosmos.D4s"
  - name: Create a cosmosdb materialized views builder service resource.
    text: |
      az cosmosdb service create --resource-group MyResourceGroup --account-name MyAccount --name "MaterializedViewsBuilder" --kind "MaterializedViewsBuilder" --count 3 --size "Cosmos.D4s"
"""

helps['cosmosdb service update'] = """
type: command
short-summary: Update a cosmosdb service resource.
examples:
  - name: Update a cosmosdb service resource.
    text: |
      az cosmosdb service update --resource-group MyResourceGroup --account-name MyAccount --name "sqlDedicatedGateway" --kind "SqlDedicatedGateway" --count 3
  - name: Update a cosmosdb materialized views builder service resource.
    text: |
      az cosmosdb service update --resource-group MyResourceGroup --account-name MyAccount --name "MaterializedViewsBuilder" --kind "MaterializedViewsBuilder" --count 3
"""

helps['cosmosdb service list'] = """
type: command
short-summary: List all cosmosdb service resource under an account.
examples:
  - name: List all cosmosdb service resource under an account.
    text: |
      az cosmosdb service list --resource-group MyResourceGroup --account-name MyAccount
"""

helps['cosmosdb service delete'] = """
type: command
short-summary: Delete the given cosmosdb service resource.
examples:
  - name: Delete the given cosmosdb service resource.
    text: |
      az cosmosdb service delete --resource-group MyResourceGroup --account-name MyAccount --name "sqlDedicatedGateway"
  - name: Delete the cosmosdb materialized views builder service resource.
    text: |
      az cosmosdb service delete --resource-group MyResourceGroup --account-name MyAccount --name "MaterializedViewsBuilder"
"""

helps['cosmosdb mongodb role'] = """
type: group
short-summary: Manage Azure Cosmos DB Mongo role resources.
"""

helps['cosmosdb mongodb role definition'] = """
type: group
short-summary: Manage Azure Cosmos DB Mongo role definitions.
"""

helps['cosmosdb mongodb role definition create'] = """
type: command
short-summary: Create a Mongo DB role definition under an Azure Cosmos DB account.
examples:
  - name: Create a Mongo DB role definition under an Azure Cosmos DB account using a JSON string.
    text: |
      az cosmosdb mongodb role definition create --account-name MyAccount --resource-group MyResourceGroup --body '{
        "Id": "MyDB.My_Read_Only_Role",
        "RoleName": "My_Read_Only_Role",
        "Type": "CustomRole",
        "DatabaseName": "MyDB",
        "Privileges": [{
          "Resource": {
              "Db": "MyDB",
              "Collection": "MyCol"
            },
            "Actions": [
              "insert",
              "find"
            ]
        }],
        "Roles": [
          {
            "Role": "myInheritedRole",
            "Db": "MyTestDb"
          }
        ]
      }'
  - name: Create a Mongo DB role definition under an Azure Cosmos DB account using a JSON file.
    text: az cosmosdb mongodb role definition create --account-name MyAccount --resource-group MyResourceGroup --body @mongo-role-definition.json
"""

helps['cosmosdb mongodb role definition delete'] = """
type: command
short-summary: Delete a CosmosDb MongoDb role definition under an Azure Cosmos DB account.
examples:
  - name: Delete a Mongo role definition under an Azure Cosmos DB account.
    text: az cosmosdb mongodb role definition delete --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb mongodb role definition exists'] = """
type: command
short-summary: Check if an Azure Cosmos DB MongoDb role definition exists.
examples:
  - name: Check if an Azure Cosmos DB MongoDb role definition exists.
    text: az cosmosdb mongodb role definition exists --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb mongodb role definition list'] = """
type: command
short-summary: List all MongoDb role definitions under an Azure Cosmos DB account.
examples:
  - name: List all Mongodb role definitions under an Azure Cosmos DB account.
    text: az cosmosdb mongodb role definition list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['cosmosdb mongodb role definition show'] = """
type: command
short-summary: Show the properties of a MongoDb role definition under an Azure Cosmos DB account.
examples:
  - name: Show the properties of a MongoDb role definition under an Azure Cosmos DB account.
    text: az cosmosdb mongodb role definition show --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb mongodb role definition update'] = """
type: command
short-summary: Update a MongoDb role definition under an Azure Cosmos DB account.
examples:
  - name: Update a MongoDb role definition under an Azure Cosmos DB account.
    text: az cosmosdb mongodb role definition update --account-name MyAccount --resource-group MyResourceGroup --body @mongo-role-definition.json
"""

helps['cosmosdb mongodb user'] = """
type: group
short-summary: Manage Azure Cosmos DB Mongo user resources.
"""

helps['cosmosdb mongodb user definition'] = """
type: group
short-summary: Manage Azure Cosmos DB Mongo user definitions.
"""

helps['cosmosdb mongodb user definition create'] = """
type: command
short-summary: Create a Mongo DB user definition under an Azure Cosmos DB account.
examples:
  - name: Create a Mongo DB user definition under an Azure Cosmos DB account using a JSON string.
    text: |
      az cosmosdb mongodb user definition create --account-name MyAccount --resource-group MyResourceGroup --body '{
        "Id": "MyDB.MyUName",
        "UserName": "MyUName",
        "Password": "MyPass",
        "DatabaseName": "MyDB",
        "CustomData": "TestCustomData",
        "Mechanisms": "SCRAM-SHA-256",
        "Roles": [
          {
            "Role": "myReadRole",
            "Db": "MyDB"
          }
        ]
      }'
  - name: Create a Mongo DB user definition under an Azure Cosmos DB account using a JSON file.
    text: az cosmosdb mongodb user definition create --account-name MyAccount --resource-group MyResourceGroup --body @mongo-user-definition.json
"""

helps['cosmosdb mongodb user definition delete'] = """
type: command
short-summary: Delete a CosmosDb MongoDb user definition under an Azure Cosmos DB account.
examples:
  - name: Delete a Mongo user definition under an Azure Cosmos DB account.
    text: az cosmosdb mongodb user definition delete --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb mongodb user definition exists'] = """
type: command
short-summary: Check if an Azure Cosmos DB MongoDb user definition exists.
examples:
  - name: Check if an Azure Cosmos DB MongoDb user definition exists.
    text: az cosmosdb mongodb user definition exists --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb mongodb user definition list'] = """
type: command
short-summary: List all MongoDb user definitions under an Azure Cosmos DB account.
examples:
  - name: List all Mongodb user definitions under an Azure Cosmos DB account.
    text: az cosmosdb mongodb user definition list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['cosmosdb mongodb user definition show'] = """
type: command
short-summary: Show the properties of a MongoDb user definition under an Azure Cosmos DB account.
examples:
  - name: Show the properties of a MongoDb user definition under an Azure Cosmos DB account.
    text: az cosmosdb mongodb user definition show --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb mongodb user definition update'] = """
type: command
short-summary: Update a MongoDb user definition under an Azure Cosmos DB account.
examples:
  - name: Update a MongoDb user definition under an Azure Cosmos DB account.
    text: az cosmosdb mongodb user definition update --account-name MyAccount --resource-group MyResourceGroup --body @mongo-user-definition.json
"""


# create new account by restoring from a different account
helps['cosmosdb create'] = """
type: command
short-summary: Creates a new Azure Cosmos DB database account.
parameters:
  - name: --locations
    short-summary: Add a location to the Cosmos DB database account
    long-summary: |
        Usage:          --locations KEY=VALUE [KEY=VALUE ...]
        Required Keys:  regionName, failoverPriority
        Optional Key:   isZoneRedundant
        Default:        single region account in the location of the specified resource group.
        Failover priority values are 0 for write regions and greater than 0 for read regions. A failover priority value must be unique and less than the total number of regions.
        Multiple locations can be specified by using more than one `--locations` argument.
  - name: --databases-to-restore
    short-summary: Add a database and its collection names to restore
    long-summary: |
        Usage:          --databases-to-restore name=DatabaseName collections=collection1 [collection2 ...]
  - name: --gremlin-databases-to-restore
    short-summary: Add a gremlin database and its graph names to restore
    long-summary: |
        Usage:          --gremlin-databases-to-restore name=DatabaseName graphs=graph1 [graph2 ...]
  - name: --tables-to-restore
    short-summary: Add table names to restore
    long-summary: |
        Usage:          --tables-to-restore tables=table1 [table2 ...]
examples:
  - name:  DB database account. (autogenerated)
    text: az cosmosdb create --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup --subscription MySubscription
    crafted: true
  - name: Creates a new Azure Cosmos DB database account with two regions. UK South is zone redundant.
    text: az cosmosdb create -n myaccount -g mygroup --locations regionName=eastus failoverPriority=0 isZoneRedundant=False --locations regionName=uksouth failoverPriority=1 isZoneRedundant=True --enable-multiple-write-locations --network-acl-bypass AzureServices --network-acl-bypass-resource-ids /subscriptions/subId/resourceGroups/rgName/providers/Microsoft.Synapse/workspaces/wsName
  - name: Create a new Azure Cosmos DB database account by restoring from an existing account in the given location
    text: az cosmosdb create -n restoredaccount -g mygroup --is-restore-request true --restore-source /subscriptions/2296c272-5d55-40d9-bc05-4d56dc2d7588/providers/Microsoft.DocumentDB/locations/westus/restorableDatabaseAccounts/d056a4f8-044a-436f-80c8-cd3edbc94c68 --restore-timestamp 2020-07-13T16:03:41+0000 --locations regionName=westus failoverPriority=0 isZoneRedundant=False
  - name: Creates a new Azure Cosmos DB database account with materialized views and cassandra capability enabled.
    text: az cosmosdb create --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup --enable-materialized-views true --capabilities EnableCassandra CassandraEnableMaterializedViews
"""

helps['cosmosdb update'] = """
type: command
short-summary:  Update an Azure Cosmos DB database account.
parameters:
  - name: --locations
    short-summary: Add a location to the Cosmos DB database account
    long-summary: |
        Usage:          --locations KEY=VALUE [KEY=VALUE ...]
        Required Keys:  regionName, failoverPriority
        Optional Key:   isZoneRedundant
        Default:        single region account in the location of the specified resource group.
        Failover priority values are 0 for write regions and greater than 0 for read regions. A failover priority value must be unique and less than the total number of regions.
        Multiple locations can be specified by using more than one `--locations` argument.
examples:
  - name: Update an Azure Cosmos DB database account. (autogenerated)
    text: az cosmosdb update --capabilities EnableGremlin --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup
  - name: Update an Azure Cosmos DB database account to enable materialized views.
    text: az cosmosdb update --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup --enable-materialized-views true
"""

# restore account
helps['cosmosdb restore'] = """
type: command
short-summary: Create a new Azure Cosmos DB database account by restoring from an existing database account.
parameters:
  - name: --databases-to-restore
    short-summary: Add a database and its collection names to restore
    long-summary: |
        Usage:          --databases-to-restore name=DatabaseName collections=collection1 [collection2 ...]
        Multiple databases can be specified by using more than one `--databases-to-restore` argument.
  - name: --gremlin-databases-to-restore
    short-summary: Add a gremlin database and its graph names to restore
    long-summary: |
        Usage:          --gremlin-databases-to-restore name=DatabaseName graphs=graph1 [graph2 ...]
  - name: --tables-to-restore
    short-summary: Add table names to restore
    long-summary: |
        Usage:          --tables-to-restore table1 [table2 ...]
examples:
  - name: Create a new Azure Cosmos DB database account by restoring from an existing database account.
    text: az cosmosdb restore --target-database-account-name MyRestoredCosmosDBDatabaseAccount --account-name MySourceAccount --restore-timestamp 2020-07-13T16:03:41+0000 -g MyResourceGroup --location westus
  - name: Create a new Azure Cosmos DB Sql or MongoDB database account by restoring only the selected databases and collections from an existing database account.
    text: az cosmosdb restore -g MyResourceGroup --target-database-account-name MyRestoredCosmosDBDatabaseAccount --account-name MySourceAccount --restore-timestamp 2020-07-13T16:03:41+0000 --location westus --databases-to-restore name=MyDB1 collections=collection1 collection2 --databases-to-restore name=MyDB2 collections=collection3 collection4
  - name: Create a new Azure Cosmos DB Gremlin database account by restoring only the selected databases or graphs from an existing database account.
    text: az cosmosdb restore -g MyResourceGroup --target-database-account-name MyRestoredCosmosDBDatabaseAccount --account-name MySourceAccount --restore-timestamp 2020-07-13T16:03:41+0000 --location westus --gremlin-databases-to-restore name=graphdb1 graphs=graph1 graph2
  - name: Create a new Azure Cosmos DB Table database account by restoring only the selected tables from an existing database account.
    text: az cosmosdb restore -g MyResourceGroup --target-database-account-name MyRestoredCosmosDBDatabaseAccount --account-name MySourceAccount --restore-timestamp 2020-07-13T16:03:41+0000 --location westus --tables-to-restore table1,table2
"""

# sql restorable containers
helps['cosmosdb sql restorable-container list'] = """
type: command
short-summary: List all the versions of all the sql containers that were created / modified / deleted in the given database and restorable account.
"""

# mongodb restorable collections
helps['cosmosdb mongodb restorable-collection list'] = """
type: command
short-summary: List all the versions of all the mongodb collections that were created / modified / deleted in the given database and restorable account.
"""

# gremlin restorable resources
helps['cosmosdb gremlin restorable-database'] = """
type: group
short-summary: Manage different versions of gremlin databases that are restorable in a Azure Cosmos DB account.
"""

helps['cosmosdb gremlin restorable-database list'] = """
type: command
short-summary: List all the versions of all the gremlin databases that were created / modified / deleted in the given restorable account.
"""

helps['cosmosdb gremlin restorable-graph'] = """
type: group
short-summary: Manage different versions of gremlin graphs that are restorable in a database of a Azure Cosmos DB account.
"""

helps['cosmosdb gremlin restorable-graph list'] = """
type: command
short-summary: List all the versions of all the gremlin graphs that were created / modified / deleted in the given database and restorable account.
"""

helps['cosmosdb gremlin restorable-resource'] = """
type: group
short-summary: Manage the databases and its graphs that can be restored in the given account at the given timestamp and region.
"""

helps['cosmosdb gremlin restorable-resource list'] = """
type: command
short-summary: List all the databases and its graphs that can be restored in the given account at the given timestamp and region.
"""

# table restorable resources
helps['cosmosdb table restorable-table'] = """
type: group
short-summary: Manage different versions of tables that are restorable in Azure Cosmos DB account.
"""

helps['cosmosdb table restorable-table list'] = """
type: command
short-summary: List all the versions of all the tables that were created / modified / deleted in the given restorable account.
"""

helps['cosmosdb table restorable-resource'] = """
type: group
short-summary: Manage the tables that can be restored in the given account at the given timestamp and region.
"""

helps['cosmosdb table restorable-resource list'] = """
type: command
short-summary: List all the tables that can be restored in the given account at the given timestamp and region.
"""

# gremlin graph latest backup time.
helps['cosmosdb gremlin retrieve-latest-backup-time'] = """
type: command
short-summary: Retrieves latest restorable timestamp for the given gremlin graph in given region.
"""

# table latest backup time.
helps['cosmosdb table retrieve-latest-backup-time'] = """
type: command
short-summary: Retrieves latest restorable timestamp for the given table in given region.
"""

helps['cosmosdb dts copy'] = """
    type: command
    short-summary: "Creates a Data Transfer Copy Job."
    parameters:
      - name: --source-cassandra-table
        short-summary: "Source cassandra table"
        long-summary: |
            Usage: --source-cassandra-table keyspace=XX table=XX'
            keyspace: Keyspace name of CosmosDB Cassandra.
            table: Table name of CosmosDB Cassandra.
      - name: --dest-cassandra-table
        short-summary: "Destination cassandra table"
        long-summary: |
            Usage: --dest-cassandra-table keyspace=XX table=XX'
            keyspace: Keyspace name of CosmosDB Cassandra.
            table: Table name of CosmosDB Cassandra.
      - name: --source-sql-container
        short-summary: "Source sql container"
        long-summary: |
            Usage: --source-sql-container database=XX container=XX'
            database: Database name of CosmosDB Sql.
            container: Container name of CosmosDB Sql.
      - name: --dest-sql-container
        short-summary: "Destination sql container"
        long-summary: |
            Usage: --dest-sql-container database=XX container=XX'
            database: Database name of CosmosDB Sql.
            container: Container name of CosmosDB Sql.
      - name: --source-mongo
        short-summary: "Source mongo collection"
        long-summary: |
            Usage: --source-mongo database=XX collection=XX'
            database: Database name of CosmosDB Mongo.
            collection: Collection name of CosmosDB Mongo.
      - name: --dest-mongo
        short-summary: "Destination mongo collection"
        long-summary: |
            Usage: --dest-mongo database=XX collection=XX'
            database: Database name of CosmosDB Mongo.
            collection: Collection name of CosmosDB Mongo.

    examples:
      - name: Copy sql container
        text: |-
          az cosmosdb dts copy -g "rg1" --job-name "j1" --account-name "db1" --source-sql-container database=db1 container=c1 --dest-sql-container database=db2 container=c2
      - name: Copy cassandra table
        text: |-
          az cosmosdb dts copy -g "rg1" --job-name "j1" --account-name "db1" --source-cassandra-table keyspace=k1 table=t1 --dest-cassandra-table keyspace=k2 table=t2
      - name: Copy mongo collection
        text: |-
          az cosmosdb dts copy -g "rg1" --job-name "j1" --account-name "db1" --source-mongo database=d1 collection=c1 --dest-mongo database=d2 collection=c2
"""

helps['cosmosdb dts'] = """
    type: group
    short-summary: Manage data transfer job with cosmosdb
"""

helps['cosmosdb dts list'] = """
    type: command
    short-summary: "Get a list of Data Transfer Jobs."
    examples:
      - name: List all jobs
        text: |-
               az cosmosdb dts list --account-name "ddb1" -g "rg1"
"""

helps['cosmosdb dts show'] = """
    type: command
    short-summary: "Get a Data Transfer Job."
    examples:
      - name: Show details of job j1
        text: |-
               az cosmosdb dts show --account-name "ddb1" --job-name "j1" -g "rg1"
"""

helps['cosmosdb dts pause'] = """
    type: command
    short-summary: "Pause a Data Transfer Job."
    examples:
      - name: Pause job j1
        text: |-
               az cosmosdb dts pause --account-name "ddb1" --job-name "j1" -g "rg1"
"""

helps['cosmosdb dts resume'] = """
    type: command
    short-summary: "Resumes a Data Transfer Job."
    examples:
      - name: Resume job j1
        text: |-
               az cosmosdb dts resume --account-name "ddb1" --job-name "j1" -g "rg1"
"""

helps['cosmosdb dts cancel'] = """
    type: command
    short-summary: "Cancels a Data Transfer Job."
    examples:
      - name: Cancel job j1
        text: |-
               az cosmosdb dts cancel --account-name "ddb1" --job-name "j1" -g "rg1"
"""

helps['cosmosdb copy'] = """
    type: group
    short-summary: Manage container copy job
"""

helps['cosmosdb copy create'] = """
    type: command
    short-summary: "Creates a container copy job."
    parameters:
      - name: --src-cassandra
        short-summary: "Source table"
        long-summary: |
            Usage: --src-cassandra keyspace=XX table=XX'
            keyspace: Keyspace name.
            table: Table name.
      - name: --dest-cassandra
        short-summary: "Destination table"
        long-summary: |
            Usage: --dest-cassandra keyspace=XX table=XX'
            keyspace: Keyspace name.
            table: Table name.
      - name: --src-nosql
        short-summary: "Source container"
        long-summary: |
            Usage: --src-nosql database=XX container=XX'
            database: Database name.
            container: Container name.
      - name: --dest-nosql
        short-summary: "Destination container"
        long-summary: |
            Usage: --dest-nosql database=XX container=XX'
            database: Database name.
            container: Container name.
      - name: --src-mongo
        short-summary: "Source collection"
        long-summary: |
            Usage: --src-mongo database=XX collection=XX'
            database: Database name.
            collection: Collection name.
      - name: --dest-mongo
        short-summary: "Destination collection"
        long-summary: |
            Usage: --dest-mongo database=XX collection=XX'
            database: Database name.
            collection: Collection name.

    examples:
      - name: Copy Azure Cosmos DB API for NoSQL container in same account
        text: |-
          az cosmosdb copy create -g "rg1" --job-name "j1" --src-account "acc1" --dest-account "acc1" --src-nosql database=db1 container=c1 --dest-nosql database=db2 container=c2
      - name: Copy Azure Cosmos DB API for NoSQL container in different account
        text: |-
          az cosmosdb copy create -g "rg1" --job-name "j1" --src-account "acc1" --dest-account "acc2" --src-nosql database=db1 container=c1 --dest-nosql database=db2 container=c2
      - name: Copy Azure Cosmos DB API for Apache Cassandra table
        text: |-
          az cosmosdb copy create -g "rg1" --job-name "j1" --src-account "acc1" --dest-account "acc1" --src-cassandra keyspace=k1 table=t1 --dest-cassandra keyspace=k2 table=t2
      - name: Copy Azure Cosmos DB API for MongoDB collection
        text: |-
          az cosmosdb copy create -g "rg1" --job-name "j1" --src-account "acc1" --dest-account "acc1" --src-mongo database=d1 collection=c1 --dest-mongo database=d2 collection=c2
"""

helps['cosmosdb copy list'] = """
    type: command
    short-summary: "Get a container copy job."
    examples:
      - name: List all jobs
        text: |-
               az cosmosdb copy list -g "rg1" --account-name "acc1"
"""

helps['cosmosdb copy show'] = """
    type: command
    short-summary: "Get a container copy job."
    examples:
      - name: Show details of job j1
        text: |-
               az cosmosdb copy show -g "rg1" --account-name "acc1" --job-name "j1"
"""

helps['cosmosdb copy pause'] = """
    type: command
    short-summary: "Pause a container copy job."
    examples:
      - name: Pause job j1
        text: |-
               az cosmosdb copy pause -g "rg1" --account-name "acc1" --job-name "j1"
"""

helps['cosmosdb copy resume'] = """
    type: command
    short-summary: "Resume a container copy job."
    examples:
      - name: Resume job j1
        text: |-
               az cosmosdb copy resume -g "rg1" --account-name "acc1" --job-name "j1"
"""

helps['cosmosdb copy cancel'] = """
    type: command
    short-summary: "Cancel a container copy job."
    examples:
      - name: Cancel job j1
        text: |-
               az cosmosdb copy cancel -g "rg1" --account-name "acc1" --job-name "j1"
"""

helps['cosmosdb copy complete'] = """
    type: command
    short-summary: "Completes an online container copy job."
    examples:
      - name: Complete job j1
        text: |-
               az cosmosdb copy complete -g "rg1" --account-name "acc1" --job-name "j1"
"""

helps['cosmosdb sql container merge'] = """
    type: command
    short-summary: "Merges the partitions of a sql container."
    examples:
      - name: merge partitions of container my-container
        text: |-
               az cosmosdb sql container merge -g my-resource-group -a my-account -d my-db --name my-container
"""

helps['cosmosdb mongodb collection merge'] = """
    type: command
    short-summary: "Merges the partitions of a mongodb collection."
    examples:
      - name: merge partitions of collection my-mongodb-collection
        text: |-
               az cosmosdb mongodb collection merge -g my-resource-group -a my-account -d my-db --name my-mongodb-collection
"""

helps['cosmosdb sql database merge'] = """
    type: command
    short-summary: "Merge the partitions of a sql database."
    examples:
      - name: Merge partitions of database my-database
        text: |-
               az cosmosdb sql database merge -g my-resource-group -a my-account --name my-database
"""

helps['cosmosdb mongodb database merge'] = """
    type: command
    short-summary: "Merges the partitions of a mongodb database."
    examples:
      - name: merge partitions of database my-mongodb-database
        text: |-
               az cosmosdb mongodb database merge -g my-resource-group -a my-account --name my-mongodb-collection
"""

helps['cosmosdb sql container retrieve-partition-throughput'] = """
    type: command
    short-summary: "Retrieve  the partition throughput of a sql container."
    examples:
      - name: Retrieve container container_name's throughput for specific physical partitions
        text: |-
               az cosmosdb sql container retrieve-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --physical-partition-ids 8 9
      - name: Retrieve container container_name's throughput for all physical partitions
        text: |-
               az cosmosdb sql container retrieve-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --all-partitions
"""

helps['cosmosdb sql container redistribute-partition-throughput'] = """
    type: command
    short-summary: "Redistributes the partition throughput of a sql container."
    examples:
      - name: Evenly distributes the partition throughput for a sql container among all physical partitions
        text: |-
               az cosmosdb sql container redistribute-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --evenly-distribute
      - name: Redistributes the partition throughput for a sql container from source partitions to target partitions
        text: |-
               az cosmosdb sql container redistribute-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --target-partition-info 8=1200 6=1200]' --source-partition-info 9]'
"""

helps['cosmosdb mongodb collection retrieve-partition-throughput'] = """
    type: command
    short-summary: "Retrieve the partition throughput of a mongodb collection."
    examples:
      - name: Retrieve container container_name's throughput for specific physical partitions
        text: |-
               az cosmosdb mongodb collection retrieve-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --physical-partition-ids 8 9
      - name: Retrieve container container_name's throughput for all physical partitions
        text: |-
               az cosmosdb mongodb collection retrieve-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --all-partitions
"""

helps['cosmosdb mongodb collection redistribute-partition-throughput'] = """
    type: command
    short-summary: "Redistributes the partition throughput of a mongodb collection."
    examples:
      - name: Evenly distributes the partition throughput for a mongodb collection among all physical partitions
        text: |-
               az cosmosdb mongodb collection redistribute-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --evenly-distribute
      - name: Redistributes the partition throughput for a mongodb collection from source partitions to target partitions
        text: |-
               az cosmosdb mongodb collection redistribute-partition-throughput --account-name account_name --database-name db_name --name container_name  --resource-group rg_name --target-partition-info 8=1200 6=1200' --source-partition-info 9'
"""

# in-account restore of a deleted sql database
helps['cosmosdb sql database restore'] = """
    type: command
    short-summary: "Restore a deleted sql database within the same account."
    examples:
      - name: Restore a deleted sql database within the same account.
        text: |-
               az cosmosdb sql database restore --resource-group resource_group --account-name database_account_name --name name_of_database_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""

# in-account restore of a deleted sql container
helps['cosmosdb sql container restore'] = """
    type: command
    short-summary: "Restore a deleted sql container within the same account."
    examples:
      - name: Restore a deleted sql container within the same account.
        text: |-
               az cosmosdb sql container restore --resource-group resource_group --account-name database_account_name --database-name parent_database_name --name name_of_container_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""

# in-account restore of a deleted mongodb database
helps['cosmosdb mongodb database restore'] = """
    type: command
    short-summary: "Restore a deleted mongodb database within the same account."
    examples:
      - name: Restore a deleted mongodb database within the same account.
        text: |-
               az cosmosdb mongodb database restore --resource-group resource_group --account-name database_account_name --name name_of_database_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""

# in-account restore of a deleted mongodb collection
helps['cosmosdb mongodb collection restore'] = """
    type: command
    short-summary: "Restore a deleted mongodb collection within the same account."
    examples:
      - name: Restore a deleted mongodb collection within the same account.
        text: |-
               az cosmosdb mongodb collection restore --resource-group resource_group --account-name database_account_name --database-name parent_database_name --name name_of_collection_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""

# in-account restore of a deleted gremlin database
helps['cosmosdb gremlin database restore'] = """
    type: command
    short-summary: "Restore a deleted gremlin database within the same account."
    examples:
      - name: Restore a deleted gremlin database within the same account.
        text: |-
               az cosmosdb gremlin database restore --resource-group resource_group --account-name database_account_name --name name_of_database_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""

# in-account restore of a deleted gremlin graph
helps['cosmosdb gremlin graph restore'] = """
    type: command
    short-summary: "Restore a deleted gremlin graph within the same account."
    examples:
      - name: Restore a deleted gremlin graph within the same account.
        text: |-
               az cosmosdb gremlin graph restore --resource-group resource_group --account-name database_account_name --database-name parent_database_name --name name_of_graph_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""

# in-account restore of a deleted table
helps['cosmosdb table restore'] = """
    type: command
    short-summary: "Restore a deleted table within the same account."
    examples:
      - name: Restore a deleted table within the same account.
        text: |-
               az cosmosdb table restore --resource-group resource_group --account-name database_account_name --table-name name_of_table_needs_to_be_restored --restore-timestamp 2020-07-13T16:03:41+0000
"""
