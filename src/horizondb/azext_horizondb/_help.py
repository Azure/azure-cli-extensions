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


helps['horizondb identity'] = """
type: group
short-summary: Manage user assigned managed identities for an Azure HorizonDB cluster.
"""


helps['horizondb identity assign'] = """
type: command
short-summary: Add user assigned managed identities to an Azure HorizonDB cluster.
examples:
  - name: Assign a user assigned managed identity to a HorizonDB cluster.
    text: az horizondb identity assign --name examplecluster --resource-group exampleresourcegroup --identity /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/exampleresourcegroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/exampleidentity
"""


helps['horizondb identity list'] = """
type: command
short-summary: List all user assigned managed identities from an Azure HorizonDB cluster.
examples:
  - name: List identities for a HorizonDB cluster.
    text: az horizondb identity list --name examplecluster --resource-group exampleresourcegroup
"""


helps['horizondb identity remove'] = """
type: command
short-summary: Remove user assigned managed identities from an Azure HorizonDB cluster.
examples:
  - name: Remove a user assigned managed identity from a HorizonDB cluster.
    text: az horizondb identity remove --name examplecluster --resource-group exampleresourcegroup --identity /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/exampleresourcegroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/exampleidentity
"""


helps['horizondb identity show'] = """
type: command
short-summary: Get a user assigned managed identity from an Azure HorizonDB cluster.
examples:
  - name: Show a specific identity from a HorizonDB cluster.
    text: az horizondb identity show --name examplecluster --resource-group exampleresourcegroup --identity /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/exampleresourcegroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/exampleidentity
"""
