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


helps['horizondb parameter-group'] = """
type: group
short-summary: Manage Azure HorizonDB parameter groups.
"""


helps['horizondb parameter-group create'] = """
type: command
short-summary: Create a new Azure HorizonDB parameter group.
examples:
  - name: Create an Azure HorizonDB parameter group with custom parameter values. Unspecified parameters inherit the default PostgreSQL values.
    text: az horizondb parameter-group create --name exampleparametergroup --resource-group exampleresourcegroup --location westus2 --version 17 --parameters max_connections=200 log_min_error_statement=error shared_buffers=2000
  - name: Create an Azure HorizonDB parameter group that applies parameters immediately and includes a description.
    text: az horizondb parameter-group create --name exampleparametergroup --resource-group exampleresourcegroup --location westus2 --version 17 --parameters max_connections=200 log_min_error_statement=error shared_buffers=2000 --apply-immediately true --description "Parameter group for high-throughput workloads"
"""


helps['horizondb parameter-group delete'] = """
type: command
short-summary: Delete an Azure HorizonDB parameter group.
examples:
  - name: Delete an Azure HorizonDB parameter group.
    text: az horizondb parameter-group delete --name exampleparametergroup --resource-group exampleresourcegroup
"""


helps['horizondb parameter-group show'] = """
type: command
short-summary: Show details of an Azure HorizonDB parameter group.
examples:
  - name: Show details of an Azure HorizonDB parameter group.
    text: az horizondb parameter-group show --name exampleparametergroup --resource-group exampleresourcegroup
"""


helps['horizondb parameter-group list'] = """
type: command
short-summary: List Azure HorizonDB parameter groups.
examples:
  - name: List all Azure HorizonDB parameter groups in the current subscription.
    text: az horizondb parameter-group list
  - name: List Azure HorizonDB parameter groups in a resource group.
    text: az horizondb parameter-group list --resource-group exampleresourcegroup
"""


helps['horizondb parameter-group list-connections'] = """
type: command
short-summary: List Azure HorizonDB clusters connected to a parameter group.
examples:
  - name: List Azure HorizonDB clusters connected to a parameter group.
    text: az horizondb parameter-group list-connections --resource-group exampleresourcegroup --name exampleparametergroup
"""
