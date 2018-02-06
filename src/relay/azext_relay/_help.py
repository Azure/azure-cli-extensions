# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['relay'] = """
    type: group
    short-summary: Manage Azure Relay Namespace, WCF Relays and Hybrid Connections
"""

helps['relay namespace'] = """
    type: group
    short-summary: Manage Azure Relay Namespace and AuthorizationRule
"""

helps['relay namespace authorizationrule'] = """
    type: group
    short-summary: Manage Azure Relay AuthorizationRule for Namespace
"""

helps['relay namespace authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure Relay AuthorizationRule connection strings for Namespace
"""

helps['relay wcfrelay'] = """
    type: group
    short-summary: Manage Azure Relay's WCF Relays and AuthorizationRule
"""

helps['relay wcfrelay authorizationrule'] = """
    type: group
    short-summary: Manage Azure Relay AuthorizationRule for WCF Relay
"""

helps['relay wcfrelay authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for WCF Relay
"""

helps['relay hybrid-connections'] = """
    type: group
    short-summary: Manage Azure Relay's Hybrid Connections and AuthorizationRule
"""

helps['relay hybrid-connections authorizationrule'] = """
    type: group
    short-summary: Manage Azure Relay AuthorizationRule for Hybrid Connections
"""

helps['relay hybrid-connections authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for Hybrid Connections
"""

helps['relay namespace exists'] = """
    type: command
    short-summary: check for the availability of the given name for the Namespace
    examples:
        - name: check for the availability of the given name for the Namespace.
          text: az relay namespace exists --name mynamespace
"""

helps['relay namespace create'] = """
    type: command
    short-summary: Creates the Relay Namespace
    examples:
        - name: Create a new namespace.
          text: az relay namespace create --resource-group myresourcegroup --name mynamespace --location westus --tags tag1=value1 tag2=value2 --sku-name Standard --sku-tier
"""

helps['relay namespace show'] = """
    type: command
    short-summary: shows the Relay Namespace Details
    examples:
        - name: shows the Namespace details.
          text: az relay namespace show --resource-group myresourcegroup --name mynamespace
"""

helps['relay namespace list'] = """
    type: command
    short-summary: Lists the Relay Namespaces
    examples:
        - name: List the Relay Namespaces by resource group.
          text: az relay namespace list --resource-group myresourcegroup
        - name: Get the Namespaces by Subscription.
          text: az relay namespace list
"""

helps['relay namespace delete'] = """
    type: command
    short-summary: Deletes the Namespaces
    examples:
        - name: Deletes the Namespace
          text: az relay namespace delete --resource-group myresourcegroup --name mynamespace
"""

helps['relay namespace authorizationrule create'] = """
    type: command
    short-summary: Creates AuthorizationRule for the given Namespace
    examples:
        - name: Creates Authorization rules
          text: az relay namespace authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule --access-rights Send Listen
"""

helps['relay namespace authorizationrule show'] = """
    type: command
    short-summary: Shows the details of AuthorizationRule
    examples:
        - name: Shows the details of AuthorizationRule
          text: az relay namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['relay namespace authorizationrule list'] = """
    type: command
    short-summary: Shows the list of AuthorizationRule by Namespace
    examples:
        - name: Shows the list of AuthorizationRule by Namespace
          text: az relay namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['relay namespace authorizationrule keys list'] = """
    type: command
    short-summary: Shows the connection strings for namespace
    examples:
        - name: Shows the connectionstrings of AuthorizationRule for the namespace.
          text: az relay namespace authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['relay namespace authorizationrule keys renew'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizationRule for the namespace.
    examples:
        - name: Regenerate the connectionstrings of AuthorizationRule for the namespace.
          text: az relay namespace authorizationrule regenerate-keys --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule --key PrimaryKey
"""

helps['relay namespace authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the namespace.
    examples:
        - name: Deletes the AuthorizationRule of the namespace.
          text: az relay namespace authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['relay wcfrelay create'] = """
    type: command
    short-summary: Creates the Relay's WCF Relays
    examples:
        - name: Create a new WCF Relays.
          text: az relay wcfrelay create --resource-group myresourcegroup --namespace-name mynamespace --name mywcfrelay --relay-type NetTcp --requires-client-authorization true --requires-transport-security true --user-metadata 'User Metadata'
"""

helps['relay wcfrelay show'] = """
    type: command
    short-summary: shows the WCF Relays Details
    examples:
        - name: Shows the WCF Relays details.
          text: az relay wcfrelay show --resource-group myresourcegroup --namespace-name mynamespace --name mywcfrelay
"""

helps['relay wcfrelay list'] = """
    type: command
    short-summary: List the WCF Relays by Namepsace
    examples:
        - name: Get the WCF Relays by Namespace.
          text: az relay wcfrelay list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['relay wcfrelay delete'] = """
    type: command
    short-summary: Deletes the WCF Relays
    examples:
        - name: Deletes the WCF Relays
          text: az relay wcfrelay delete --resource-group myresourcegroup --namespace-name mynamespace --name mywcfrelay
"""

helps['relay wcfrelay authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given WCF Relays
    examples:
        - name: Creates Authorization rules
          text: az relay wcfrelay authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace --wcfrelay-name mywcfrelay --name myauthorule --access-rights Listen
"""

helps['relay wcfrelay authorizationrule show'] = """
    type: command
    short-summary: shows the details of AuthorizationRule
    examples:
        - name: shows the details of AuthorizationRule
          text: az relay wcfrelay authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --wcfrelay-name mywcfrelay --name myauthorule
"""

helps['relay wcfrelay authorizationrule list'] = """
    type: command
    short-summary: shows the list of AuthorizationRule by WCF Relays
    examples:
        - name: shows the list of AuthorizationRule by WCF Relays
          text: az relay wcfrelay authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --wcfrelay-name mywcfrelay
"""

helps['relay wcfrelay authorizationrule  keys list'] = """
    type: command
    short-summary: Shows the connection strings of AuthorizationRule for the WCF Relays.
    examples:
        - name: Shows the connection strings of AuthorizationRule for the WCF Relays.
          text: az relay wcfrelay authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace --wcfrelay-name mywcfrelay --name myauthorule
"""

helps['relay wcfrelay authorizationrule  keys renew'] = """
    type: command
    short-summary: Regenerate the connection strings of AuthorizationRule for the namespace.
    examples:
        - name: Regenerate the connection strings of AuthorizationRule for the namespace.
          text: az relay wcfrelay authorizationrule regenerate-keys --resource-group myresourcegroup --namespace-name mynamespace --wcfrelay-name mywcfrelay --name myauthorule --key PrimaryKey
"""

helps['relay wcfrelay authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the WCF Relays
    examples:
        - name: Deletes the AuthorizationRule of the WCF Relays
          text: az relay wcfrelay authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace --wcfrelay-name mywcfrelay --name myauthorule
"""

helps['relay hybrid-connections create'] = """
    type: command
    short-summary: Creates the Realy's Hybrid Connections
    examples:
        - name: Create a new Realy's Hybrid Connections.
          text: az relay hybrid-connections create --resource-group myresourcegroup --namespace-name mynamespace --name myhybridconnection --requires-client-authorization true --user-metadata 'User Metadata'
"""

helps['relay hybrid-connections show'] = """
    type: command
    short-summary: shows the Hybrid Connections Details
    examples:
        - name: Shows the Hybrid Connections details.
          text: az relay hybrid-connections show --resource-group myresourcegroup --namespace-name mynamespace --name myhybridconnection
"""

helps['relay hybrid-connections list'] = """
    type: command
    short-summary: List the Hybrid Connections by Namepsace
    examples:
        - name: Get the Hybrid Connections by Namespace.
          text: az relay hybrid-connections list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['relay hybrid-connections delete'] = """
    type: command
    short-summary: Deletes the Hybrid Connections
    examples:
        - name: Deletes the Hybrid Connections
          text: az relay hybrid-connections delete --resource-group myresourcegroup --namespace-name mynamespace --name myhybridconnection
"""

helps['relay hybrid-connections authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given Hybrid Connections
    examples:
        - name: Creates Authorization rules
          text: az relay hybrid-connections authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace --hybrid-connection-name myhybridconnection --name myauthorule --access-rights Listen
"""

helps['relay hybrid-connections authorizationrule show'] = """
    type: command
    short-summary: shows the details of AuthorizationRule
    examples:
        - name: shows the details of AuthorizationRule
          text: az relay hybrid-connection authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --hybrid-connection-name myhybridconnection --name myauthorule
"""

helps['relay hybrid-connection authorizationrule list'] = """
    type: command
    short-summary: shows the list of AuthorizationRule by Hybrid Connections
    examples:
        - name: shows the list of AuthorizationRule by Hybrid Connections
          text: az relay hybrid-connections authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --hybrid-connection-name myhybridconnection
"""

helps['relay hybrid-connections authorizationrule  keys list'] = """
    type: command
    short-summary: Shows the connection strings of AuthorizationRule for the Hybrid Connections.
    examples:
        - name: Shows the connection strings of AuthorizationRule for the Hybrid Connections.
          text: az relay hybrid-connections authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace --hybrid-connection-name myhybridconnection --name myauthorule
"""

helps['relay hybrid-connections authorizationrule  keys renew'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizationRule for the namespace.
    examples:
        - name: Regenerate the connectionstrings of AuthorizationRule for the namespace.
          text: az relay hybrid-connections authorizationrule regenerate-keys --resource-group myresourcegroup --namespace-name mynamespace --hybrid-connection-name myhybridconnection --name myauthorule --key PrimaryKey
"""

helps['relay hybrid-connections authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the Hybrid Connections.
    examples:
        - name: Deletes the AuthorizationRule of the Hybrid Connections.
          text: az relay hybrid-connections authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace --hybrid-connection-name myhybridconnection --name myauthorule
"""
