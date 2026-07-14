# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

# pylint: disable=line-too-long, too-many-lines


helps['horizondb'] = """
type: group
short-summary: Manage Azure HorizonDB.
"""


helps['horizondb create'] = """
type: command
short-summary: Create a new Azure HorizonDB cluster.
examples:
  - name: Create a new HorizonDB cluster.
    text: az horizondb create --name examplecluster --resource-group exampleresourcegroup --location centralus --administrator-login myadmin --administrator-login-password examplepassword --version 17 --v-cores 4 --replica-count 3
  - name: Create a HorizonDB cluster with zone placement policy.
    text: az horizondb create --name examplecluster --resource-group exampleresourcegroup --location centralus --administrator-login myadmin --administrator-login-password examplepassword --version 17 --v-cores 4 --replica-count 3 --zone-placement-policy Strict
"""


helps['horizondb update'] = """
type: command
short-summary: Update an existing Azure HorizonDB cluster.
examples:
  - name: Update an existing HorizonDB cluster to have 6 vCores.
    text: az horizondb update --name examplecluster --resource-group exampleresourcegroup --v-cores 6
  - name: Assign a parameter group to an existing HorizonDB cluster.
    text: az horizondb update --name examplecluster --resource-group exampleresourcegroup --parameter-group /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.HorizonDb/parameterGroups/{parameterGroup}
"""


helps['horizondb restore'] = """
type: command
short-summary: Restore an Azure HorizonDB cluster from backups of an existing source cluster.
examples:
  - name: Restore an Azure HorizonDB cluster from most recent backup of an existing source cluster in the same subscription and resource group.
    text: az horizondb restore --name restoredcluster --resource-group exampleresourcegroup --source-cluster sourcecluster
  - name: Restore an Azure HorizonDB cluster from most recent backup of an existing source cluster, given its identifier, to a specific resource group.
    text: az horizondb restore --name restoredcluster --resource-group exampleresourcegroup --source-cluster /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/examplerg/providers/Microsoft.HorizonDB/clusters/sourcecluster
  - name: Restore an Azure HorizonDB cluster from a specific point in time in the backup chain of an existing source cluster in the same subscription and resource group.
    text: az horizondb restore --name restoredcluster --resource-group exampleresourcegroup --source-cluster sourcecluster --restore-time "2026-07-15T02:10:00+00:00"
"""


helps['horizondb delete'] = """
type: command
short-summary: Delete an Azure HorizonDB cluster.
examples:
  - name: Delete an Azure HorizonDB cluster.
    text: az horizondb delete --name examplecluster --resource-group exampleresourcegroup
"""


helps['horizondb show'] = """
type: command
short-summary: Show details of an Azure HorizonDB cluster.
examples:
  - name: Show details of an Azure HorizonDB cluster.
    text: az horizondb show --name examplecluster --resource-group exampleresourcegroup
"""


helps['horizondb list'] = """
type: command
short-summary: List Azure HorizonDB clusters.
examples:
  - name: List all Azure HorizonDB clusters in the current subscription.
    text: az horizondb list
  - name: List Azure HorizonDB clusters in a resource group.
    text: az horizondb list --resource-group exampleresourcegroup
"""
