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


helps['horizondb firewall-rule'] = """
type: group
short-summary: Manage firewall rules for Azure HorizonDB clusters.
"""


helps['horizondb firewall-rule create'] = """
type: command
short-summary: Create a new firewall rule for a HorizonDB cluster.
examples:
  - name: Create a firewall rule.
    text: az horizondb firewall-rule create --name examplecluster --resource-group exampleresourcegroup --rule-name allowall --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
  - name: Create a firewall rule with a description.
    text: az horizondb firewall-rule create --name examplecluster --resource-group exampleresourcegroup --rule-name office --start-ip-address 10.0.0.1 --end-ip-address 10.0.0.255 --rule-description "Office IP range"
"""


helps['horizondb firewall-rule delete'] = """
type: command
short-summary: Delete an existing firewall rule.
examples:
  - name: Delete a firewall rule.
    text: az horizondb firewall-rule delete --name examplecluster --resource-group exampleresourcegroup --rule-name allowall
  - name: Delete a firewall rule without confirmation.
    text: az horizondb firewall-rule delete --name examplecluster --resource-group exampleresourcegroup --rule-name allowall --yes
"""


helps['horizondb firewall-rule show'] = """
type: command
short-summary: Get the details of a specific firewall rule.
examples:
  - name: Show a firewall rule.
    text: az horizondb firewall-rule show --name examplecluster --resource-group exampleresourcegroup --rule-name allowall
"""


helps['horizondb firewall-rule update'] = """
type: command
short-summary: Update an existing firewall rule.
examples:
  - name: Update a firewall rule's IP range.
    text: az horizondb firewall-rule update --name examplecluster --resource-group exampleresourcegroup --rule-name allowall --start-ip-address 10.0.0.0 --end-ip-address 10.0.0.255
"""


helps['horizondb firewall-rule list'] = """
type: command
short-summary: List firewall rules for a HorizonDB cluster.
examples:
  - name: List all firewall rules.
    text: az horizondb firewall-rule list --name examplecluster --resource-group exampleresourcegroup
"""
