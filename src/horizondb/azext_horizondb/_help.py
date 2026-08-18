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
  - name: Create a HorizonDB cluster and allow public access from a single IP address (creates a firewall rule).
    text: az horizondb create --name examplecluster --resource-group exampleresourcegroup --location centralus --administrator-login myadmin --administrator-login-password examplepassword --version 17 --v-cores 4 --public-access 12.12.12.12
  - name: Create a HorizonDB cluster and allow public access from a range of IP addresses.
    text: az horizondb create --name examplecluster --resource-group exampleresourcegroup --location centralus --administrator-login myadmin --administrator-login-password examplepassword --version 17 --v-cores 4 --public-access 12.12.12.0-12.12.12.255
  - name: Create a HorizonDB cluster and allow public access from all IP addresses.
    text: az horizondb create --name examplecluster --resource-group exampleresourcegroup --location centralus --administrator-login myadmin --administrator-login-password examplepassword --version 17 --v-cores 4 --public-access All
"""


helps['horizondb update'] = """
type: command
short-summary: Update an existing Azure HorizonDB cluster.
examples:
  - name: Update an existing HorizonDB cluster to have 6 vCores.
    text: az horizondb update --name examplecluster --resource-group exampleresourcegroup --v-cores 6
  - name: Assign a parameter group to an existing HorizonDB cluster.
    text: az horizondb update --name examplecluster --resource-group exampleresourcegroup --parameter-group /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.HorizonDb/parameterGroups/{parameterGroup}
  - name: Enable public access on an existing HorizonDB cluster (detects your client IP and prompts to create a firewall rule).
    text: az horizondb update --name examplecluster --resource-group exampleresourcegroup --public-access Enabled
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


helps['horizondb firewall-rule'] = """
type: group
short-summary: Manage firewall rules for an Azure HorizonDB cluster.
long-summary: >
  Firewall rules control public access to a HorizonDB cluster and are applied to the cluster's
  default pool. Use these commands to allow inbound connections from specific IP addresses or ranges.
"""


helps['horizondb firewall-rule create'] = """
type: command
short-summary: Create a firewall rule for an Azure HorizonDB cluster.
examples:
  - name: Create a firewall rule allowing a single IP address.
    text: az horizondb firewall-rule create --resource-group exampleresourcegroup --cluster-name examplecluster --name allowclientip --start-ip-address 12.12.12.12
  - name: Create a firewall rule allowing a range of IP addresses.
    text: az horizondb firewall-rule create --resource-group exampleresourcegroup --cluster-name examplecluster --name allowrange --start-ip-address 12.12.12.0 --end-ip-address 12.12.12.255
  - name: Create a firewall rule allowing access from all Azure-internal IP addresses.
    text: az horizondb firewall-rule create --resource-group exampleresourcegroup --cluster-name examplecluster --name allowazure --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
"""


helps['horizondb firewall-rule update'] = """
type: command
short-summary: Update a firewall rule for an Azure HorizonDB cluster.
examples:
  - name: Update the IP range of an existing firewall rule.
    text: az horizondb firewall-rule update --resource-group exampleresourcegroup --cluster-name examplecluster --name allowrange --start-ip-address 12.12.12.0 --end-ip-address 12.12.12.128
"""


helps['horizondb firewall-rule show'] = """
type: command
short-summary: Show the details of a firewall rule for an Azure HorizonDB cluster.
examples:
  - name: Show a firewall rule.
    text: az horizondb firewall-rule show --resource-group exampleresourcegroup --cluster-name examplecluster --name allowclientip
"""


helps['horizondb firewall-rule list'] = """
type: command
short-summary: List the firewall rules for an Azure HorizonDB cluster.
examples:
  - name: List all firewall rules for a cluster.
    text: az horizondb firewall-rule list --resource-group exampleresourcegroup --cluster-name examplecluster
"""


helps['horizondb firewall-rule delete'] = """
type: command
short-summary: Delete a firewall rule for an Azure HorizonDB cluster.
examples:
  - name: Delete a firewall rule.
    text: az horizondb firewall-rule delete --resource-group exampleresourcegroup --cluster-name examplecluster --name allowclientip
"""


helps['horizondb private-endpoint-connection'] = """
type: group
short-summary: Manage HorizonDB private endpoint connections.
"""


helps['horizondb private-endpoint-connection list'] = """
type: command
short-summary: List private endpoint connections for a HorizonDB cluster.
examples:
  - name: List private endpoint connections for a HorizonDB cluster.
    text: az horizondb private-endpoint-connection list --resource-group exampleresourcegroup --cluster-name examplecluster
"""


helps['horizondb private-endpoint-connection show'] = """
type: command
short-summary: Show details of a HorizonDB private endpoint connection.
examples:
  - name: Show a private endpoint connection by cluster and connection name.
    text: az horizondb private-endpoint-connection show --resource-group exampleresourcegroup --cluster-name examplecluster --name exampleconnection
  - name: Show a private endpoint connection by resource ID.
    text: az horizondb private-endpoint-connection show --id /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.HorizonDb/clusters/{clusterName}/privateEndpointConnections/{connectionName}
"""


helps['horizondb private-endpoint-connection approve'] = """
type: command
short-summary: Approve a HorizonDB private endpoint connection.
examples:
  - name: Approve a private endpoint connection by cluster and connection name.
    text: az horizondb private-endpoint-connection approve --resource-group exampleresourcegroup --cluster-name examplecluster --name exampleconnection --description "Approved"
  - name: Approve a private endpoint connection by resource ID.
    text: az horizondb private-endpoint-connection approve --id /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.HorizonDb/clusters/{clusterName}/privateEndpointConnections/{connectionName} --description "Approved"
"""


helps['horizondb private-endpoint-connection reject'] = """
type: command
short-summary: Reject a HorizonDB private endpoint connection.
examples:
  - name: Reject a private endpoint connection by cluster and connection name.
    text: az horizondb private-endpoint-connection reject --resource-group exampleresourcegroup --cluster-name examplecluster --name exampleconnection --description "Rejected"
  - name: Reject a private endpoint connection by resource ID.
    text: az horizondb private-endpoint-connection reject --id /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.HorizonDb/clusters/{clusterName}/privateEndpointConnections/{connectionName} --description "Rejected"
"""


helps['horizondb private-endpoint-connection delete'] = """
type: command
short-summary: Delete a HorizonDB private endpoint connection.
examples:
  - name: Delete a private endpoint connection by cluster and connection name.
    text: az horizondb private-endpoint-connection delete --resource-group exampleresourcegroup --cluster-name examplecluster --name exampleconnection
  - name: Delete a private endpoint connection by resource ID.
    text: az horizondb private-endpoint-connection delete --id /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.HorizonDb/clusters/{clusterName}/privateEndpointConnections/{connectionName}
"""


helps['horizondb private-link-resource'] = """
type: group
short-summary: Manage HorizonDB private link resources.
"""


helps['horizondb private-link-resource list'] = """
type: command
short-summary: List private link resources for a HorizonDB cluster.
examples:
  - name: List private link resources for a HorizonDB cluster.
    text: az horizondb private-link-resource list --resource-group exampleresourcegroup --cluster-name examplecluster
"""


helps['horizondb private-link-resource show'] = """
type: command
short-summary: Show details of a HorizonDB private link resource.
examples:
  - name: Show a private link resource by group name.
    text: az horizondb private-link-resource show --resource-group exampleresourcegroup --cluster-name examplecluster --group-name DefaultPool
"""
