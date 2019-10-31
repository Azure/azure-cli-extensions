# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['network cross-connection'] = """
    type: group
    short-summary: Manage customers' ExpressRoute circuits.
    long-summary: >
        To learn more about ExpressRoute circuits visit
        https://docs.microsoft.com/azure/expressroute/howto-circuit-cli
"""

helps['network cross-connection list'] = """
    type: command
    short-summary: List all ExpressRoute cross-connections for the current subscription.
    examples:
        - name: List all ExpressRoute cross-connections for the current subscription.
          text: >
            az network cross-connection list -g MyResourceGroup
"""

helps['network cross-connection list-arp-tables'] = """
    type: command
    short-summary: Show the current Address Resolution Protocol (ARP) table of an ExpressRoute cross-connection peering.
    examples:
        - name: Show the current Address Resolution Protocol (ARP) table of an ExpressRoute cross-connection.
          text: |
            az network cross-connection list-arp-tables -g MyResourceGroup -n MyCircuit \\
                --path primary --peering-name AzurePrivatePeering
"""

helps['network cross-connection list-route-tables'] = """
    type: command
    short-summary: Show the current routing table of an ExpressRoute cross-connection peering.
    examples:
        - name: Show the current routing table of an ExpressRoute cross-connection peering.
          text: |
            az network cross-connection list-route-tables -g MyResourceGroup -n MyCircuit \\
                --path primary --peering-name AzurePrivatePeering
"""

helps['network cross-connection show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute cross-connection.
    examples:
        - name: Get the details of an ExpressRoute cross-connection.
          text: >
            az network cross-connection show -n MyCircuit -g MyResourceGroup
"""

helps['network cross-connection update'] = """
    type: command
    short-summary: Update settings of an ExpressRoute cross-connection.
"""

helps['network cross-connection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the ExpressRoute is met.
    examples:
        - name: Pause executing next line of CLI script until the ExpressRoute cross-connection is successfully provisioned.
          text: az network cross-connection wait -n MyCircuit -g MyResourceGroup --created
"""

helps['network cross-connection peering'] = """
    type: group
    short-summary: Manage ExpressRoute peering of an ExpressRoute cross-connection.
"""

helps['network cross-connection peering create'] = """
    type: command
    short-summary: Create peering settings for an ExpressRoute cross-connection.
    examples:
        - name: Create Microsoft Peering settings with IPv4 configuration.
          text: |
            az network cross-connection peering create -g MyResourceGroup --cross-connection-name MyCircuit \\
                --peering-type MicrosoftPeering --peer-asn 10002 --vlan-id 103 \\
                --primary-peer-subnet 101.0.0.0/30 --secondary-peer-subnet 102.0.0.0/30 \\
                --advertised-public-prefixes 101.0.0.0/30
"""

helps['network cross-connection peering update'] = """
    type: command
    short-summary: Update peering settings for an ExpressRoute cross-connection.
"""

helps['network cross-connection peering delete'] = """
    type: command
    short-summary: Delete peering settings.
    examples:
    - name: Delete private peering.
      text: >
        az network cross-connection peering delete -g MyResourceGroup --cross-connection-name MyCircuit -n AzurePrivatePeering
"""

helps['network cross-connection peering list'] = """
    type: command
    short-summary: List peering settings of an ExpressRoute cross-connection.
    examples:
    - name: List peering settings of an ExpressRoute cross-connection.
      text: >
        az network cross-connection peering list -g MyResourceGroup --cross-connection-name MyCircuit
"""

helps['network cross-connection peering show'] = """
    type: command
    short-summary: Get the details of an express route peering.
    examples:
    - name: Get private peering details of an ExpressRoute cross-connection.
      text: >
        az network cross-connection peering show -g MyResourceGroup --cross-connection-name MyCircuit -n AzurePrivatePeering
"""
