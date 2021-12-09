# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['managed-cassandra'] = """
type: group
short-summary: Azure Managed Cassandra.
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
      az cosmosdb service create --resource-group MyResourceGroup --account-name MyAccount --name "graphApiCompute" --kind "GraphApiCompute" --count 1 --size "Cosmos.D4s"
      az cosmosdb service create --resource-group MyResourceGroup --account-name MyAccount --name "sqlDedicatedGateway" --kind "SqlDedicatedGateway" --count 3 --size "Cosmos.D4s"
"""

helps['cosmosdb service update'] = """
type: command
short-summary: Update a cosmosdb service resource.
examples:
  - name: Update a cosmosdb service resource.
    text: |
      az cosmosdb service update --resource-group MyResourceGroup --account-name MyAccount --name "graphApiCompute" --kind "GraphApiCompute" --count 1
      az cosmosdb service update --resource-group MyResourceGroup --account-name MyAccount --name "sqlDedicatedGateway" --kind "SqlDedicatedGateway" --count 3
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
"""

helps['cosmosdb graph'] = """
type: group
short-summary: Commands to perform operations on Graph resources.
"""

helps['cosmosdb graph create'] = """
type: command
short-summary: Create a cosmosdb graph resource.
"""

helps['cosmosdb graph list'] = """
type: command
short-summary: List all cosmosdb graph resource under an account.
"""

helps['cosmosdb graph delete'] = """
type: command
short-summary: Delete the given cosmosdb graph resource.
"""

helps['cosmosdb graph exists'] = """
type: command
short-summary: Return if the given cosmosdb graph resource exist.
"""
