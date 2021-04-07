# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['cosmosdb create'] = """
type: command
short-summary: Create a new Azure Cosmos DB database account.
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
examples:
  - name: Create a new Azure Cosmos DB database account.
    text: az cosmosdb create --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup --subscription MySubscription
  - name: Create a new Azure Cosmos DB database account with two regions. UK South is zone redundant.
    text: az cosmosdb create -n myaccount -g mygroup --locations regionName=eastus failoverPriority=0 isZoneRedundant=False --locations regionName=uksouth failoverPriority=1 isZoneRedundant=True --enable-multiple-write-locations
  - name: Create a new Azure Cosmos DB database account by restoring from an existing account in the given location
    text: az cosmosdb create -n restoredaccount -g mygroup --is-restore-request true --restore-source /subscriptions/2296c272-5d55-40d9-bc05-4d56dc2d7588/providers/Microsoft.DocumentDB/locations/westus/restorableDatabaseAccounts/d056a4f8-044a-436f-80c8-cd3edbc94c68 --restore-timestamp 2020-07-13T16:03:41+0000 --locations regionName=westus failoverPriority=0 isZoneRedundant=False
"""

helps['cosmosdb restore'] = """
type: command
short-summary: Create a new Azure Cosmos DB database account by restoring from an existing database account.
parameters:
  - name: --databases-to-restore
    short-summary: Add a database and its collection names to restore
    long-summary: |
        Usage:          --databases-to-restore name=DatabaseName collections=collection1 [collection2 ...]
        Multiple databases can be specified by using more than one `--databases-to-restore` argument.
examples:
  - name: Create a new Azure Cosmos DB database account by restoring from an existing database account.
    text: az cosmosdb restore --target-database-account-name MyRestoredCosmosDBDatabaseAccount --account-name MySourceAccount --restore-timestamp 2020-07-13T16:03:41+0000 -g MyResourceGroup --location westus
  - name: Create a new Azure Cosmos DB database account by restoring only the selected databases and collections from an existing database account.
    text: az cosmosdb restore -g MyResourceGroup --target-database-account-name MyRestoredCosmosDBDatabaseAccount --account-name MySourceAccount --restore-timestamp 2020-07-13T16:03:41+0000 --location westus --databases-to-restore name=MyDB1 collections=collection1 collection2 --databases-to-restore name=MyDB2 collections=collection3 collection4
"""

helps['cosmosdb update'] = """
type: command
short-summary: Update an Azure Cosmos DB database account.
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
  - name: Update an Azure Cosmos DB database account.
    text: az cosmosdb update --capabilities EnableGremlin --name MyCosmosDBDatabaseAccount --resource-group MyResourceGroup
  - name: Update an new Azure Cosmos DB database account with two regions. UK South is zone redundant.
    text: az cosmosdb update -n myaccount -g mygroup --locations regionName=eastus failoverPriority=0 isZoneRedundant=False --locations regionName=uksouth failoverPriority=1 isZoneRedundant=True --enable-multiple-write-locations
  - name: Update the backup policy parameters of a database account with Periodic backup type.
    text: az cosmosdb update -n myaccount -g mygroup --backup-interval 240 --backup-retention 24
"""

helps['cosmosdb restorable-database-account'] = """
type: group
short-summary: Manage restorable Azure Cosmos DB accounts.
"""

helps['cosmosdb restorable-database-account list'] = """
type: command
short-summary: List all the database accounts that can be restored.
"""

helps['cosmosdb restorable-database-account show'] = """
type: command
short-summary: Show the details of a database account that can be restored.
"""

helps['cosmosdb sql restorable-database'] = """
type: group
short-summary: Manage different versions of sql databases that are restorable in a Azure Cosmos DB account.
"""

helps['cosmosdb sql restorable-database list'] = """
type: command
short-summary: List all the versions of all the sql databases that were created / modified / deleted in the given restorable account.
"""

helps['cosmosdb sql restorable-container'] = """
type: group
short-summary: Manage different versions of sql containers that are restorable in a database of a Azure Cosmos DB account.
"""

helps['cosmosdb sql restorable-container list'] = """
type: command
short-summary: List all the versions of all the sql containers that were created / modified / deleted in the given database and restorable account.
"""

helps['cosmosdb sql restorable-resource'] = """
type: group
short-summary: Manage the databases and its containers that can be restored in the given account at the given timesamp and region.
"""

helps['cosmosdb sql restorable-resource list'] = """
type: command
short-summary: List all the databases and its containers that can be restored in the given account at the given timesamp and region.
"""

helps['cosmosdb mongodb restorable-database'] = """
type: group
short-summary: Manage different versions of mongodb databases that are restorable in a Azure Cosmos DB account.
"""

helps['cosmosdb mongodb restorable-database list'] = """
type: command
short-summary: List all the versions of all the mongodb databases that were created / modified / deleted in the given restorable account.
"""

helps['cosmosdb mongodb restorable-collection'] = """
type: group
short-summary: Manage different versions of mongodb collections that are restorable in a database of a Azure Cosmos DB account.
"""

helps['cosmosdb mongodb restorable-collection list'] = """
type: command
short-summary: List all the versions of all the mongodb collections that were created / modified / deleted in the given database and restorable account.
"""

helps['cosmosdb mongodb restorable-resource'] = """
type: group
short-summary: Manage the databases and its collections that can be restored in the given account at the given timesamp and region.
"""

helps['cosmosdb mongodb restorable-resource list'] = """
type: command
short-summary: List all the databases and its collections that can be restored in the given account at the given timesamp and region.
"""

helps['cosmosdb sql role'] = """
type: group
short-summary: Manage Azure Cosmos DB SQL role resources.
"""

helps['cosmosdb sql role definition'] = """
type: group
short-summary: Manage Azure Cosmos DB SQL role definitions.
"""

helps['cosmosdb sql role definition create'] = """
type: command
short-summary: Create a SQL role definition under an Azure Cosmos DB account.
examples:
  - name: Create a SQL role definition under an Azure Cosmos DB account using a JSON string.
    text: |
      az cosmosdb sql role definition create --account-name MyAccount --resource-group MyResourceGroup --body '{
        "Id": "be79875a-2cc4-40d5-8958-566017875b39",
        "RoleName": "My Read Only Role",
        "Type": "CustomRole",
        "AssignableScopes": ["/dbs/mydb/colls/mycontainer"],
        "Permissions": [{
          "DataActions": [
            "Microsoft.DocumentDB/databaseAccounts/readMetadata",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/executeQuery",
            "Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/readChangeFeed"
          ]
        }]
      }'
  - name: Create a SQL role definition under an Azure Cosmos DB account using a JSON file.
    text: az cosmosdb sql role definition create --account-name MyAccount --resource-group MyResourceGroup --body @role-definition.json
"""

helps['cosmosdb sql role definition delete'] = """
type: command
short-summary: Delete a SQL role definition under an Azure Cosmos DB account.
examples:
  - name: Create a SQL role definition under an Azure Cosmos DB account.
    text: az cosmosdb sql role definition delete --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb sql role definition exists'] = """
type: command
short-summary: Check if an Azure Cosmos DB role definition exists.
examples:
  - name: Check if an Azure Cosmos DB role definition exists.
    text: az cosmosdb sql role definition exists --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb sql role definition list'] = """
type: command
short-summary: List all SQL role definitions under an Azure Cosmos DB account.
examples:
  - name: List all SQL role definitions under an Azure Cosmos DB account.
    text: az cosmosdb sql role definition list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['cosmosdb sql role definition show'] = """
type: command
short-summary: Show the properties of a SQL role definition under an Azure Cosmos DB account.
examples:
  - name: Show the properties of a SQL role definition under an Azure Cosmos DB account.
    text: az cosmosdb sql role definition show --account-name MyAccount --resource-group MyResourceGroup --id be79875a-2cc4-40d5-8958-566017875b39
"""

helps['cosmosdb sql role definition update'] = """
type: command
short-summary: Update a SQL role definition under an Azure Cosmos DB account.
examples:
  - name: Update a SQL role definition under an Azure Cosmos DB account.
    text: az cosmosdb sql role definition update --account-name MyAccount --resource-group MyResourceGroup --body @role-definition.json
"""

helps['cosmosdb sql role assignment'] = """
type: group
short-summary: Manage Azure Cosmos DB SQL role assignments.
"""

helps['cosmosdb sql role assignment create'] = """
type: command
short-summary: Create a SQL role assignment under an Azure Cosmos DB account.
examples:
  - name: Create a SQL role assignment under an Azure Cosmos DB account using Role Definition Name.
    text: |
      az cosmosdb sql role assignment create --account-name MyAccount --resource-group MyResourceGroup \\
        --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 \\
        --role-definition-name "My Read Only Role" \\
        --scope "/dbs/mydb/colls/mycontainer" \\
        --principal-id 6328f5f7-dbf7-4244-bba8-fbb9d8066506
  - name: Create a SQL role assignment under an Azure Cosmos DB account using Role Definition ID.
    text: |
      az cosmosdb sql role assignment create --account-name MyAccount --resource-group MyResourceGroup \\
        --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 \\
        --role-definition-id be79875a-2cc4-40d5-8958-566017875b39 \\
        --scope "/dbs/mydb/colls/mycontainer" \\
        --principal-id 6328f5f7-dbf7-4244-bba8-fbb9d8066506
"""

helps['cosmosdb sql role assignment delete'] = """
type: command
short-summary: Delete a SQL role assignment under an Azure Cosmos DB account.
examples:
  - name: Delete a SQL role assignment under an Azure Cosmos DB account.
    text: az cosmosdb sql role assignment delete --account-name MyAccount --resource-group MyResourceGroup --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8
"""

helps['cosmosdb sql role assignment exists'] = """
type: command
short-summary: Check if an Azure Cosmos DB role assignment exists.
examples:
  - name: Check if an Azure Cosmos DB role assignment exists.
    text: az cosmosdb sql role assignment exists --account-name MyAccount --resource-group MyResourceGroup --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8
"""

helps['cosmosdb sql role assignment list'] = """
type: command
short-summary: List all SQL role assignments under an Azure Cosmos DB account.
examples:
  - name: List all SQL role assignments under an Azure Cosmos DB account.
    text: az cosmosdb sql role assignment list --account-name MyAccount --resource-group MyResourceGroup
"""

helps['cosmosdb sql role assignment show'] = """
type: command
short-summary: Show the properties of a SQL role assignment under an Azure Cosmos DB account.
examples:
  - name: Show the properties of a SQL role assignment under an Azure Cosmos DB account.
    text: az cosmosdb sql role assignment show --account-name MyAccount --resource-group MyResourceGroup --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8
"""

helps['cosmosdb sql role assignment update'] = """
type: command
short-summary: Update a SQL role assignment under an Azure Cosmos DB account.
examples:
  - name: Update a SQL role assignment under an Azure Cosmos DB account.
    text: |
      az cosmosdb sql role assignment update --account-name MyAccount --resource-group MyResourceGroup \\
        --role-assignment-id cb8ed2d7-2371-4e3c-bd31-6cc1560e84f8 \\
        --role-definition-id updated-role-definition-id
"""

helps['managed-cassandra cluster'] = """
type: group
short-summary: Azure Managed Cassandra Cluster.
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

helps['managed-cassandra cluster node-status'] = """
type: command
short-summary: Gets Status of all the nodes in all the datacenters in a given Cluster.
examples:
  - name: This command gets the status of all the nodes in this cluster. By default a json is returned.
    text: |
      az managed-cassandra cluster node-status --resource-group MyResourceGroup --cluster-name MyCluster
  - name: This command gets the status of all the nodes in this cluster. When a table output is specified only one token is displayed. Use json output to get all the tokens.
    text: |
      az managed-cassandra cluster node-status --resource-group MyResourceGroup --cluster-name MyCluster --output table
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
