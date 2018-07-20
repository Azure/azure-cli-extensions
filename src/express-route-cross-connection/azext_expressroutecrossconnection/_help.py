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
        https://docs.microsoft.com/en-us/azure/expressroute/howto-circuit-cli
"""

helps['network cross-connection list'] = """
    type: command
    short-summary: List all ExpressRoute circuits for the current subscription.
    examples:
        - name: List all ExpressRoute circuits for the current subscription.
          text: >
            az network cross-connection list -g MyResourceGroup
"""

helps['network cross-connection list-arp-tables'] = """
    type: command
    short-summary: Show the current Address Resolution Protocol (ARP) table of an ExpressRoute circuit peering.
    examples:
        - name: Show the current Address Resolution Protocol (ARP) table of an ExpressRoute circuit.
          text: |
            az network cross-connection list-arp-tables -g MyResourceGroup -n MyCircuit \\
                --path primary --peering-name AzurePrivatePeering
"""

helps['network cross-connection list-route-tables'] = """
    type: command
    short-summary: Show the current routing table of an ExpressRoute circuit peering.
    examples:
        - name: Show the current routing table of an ExpressRoute circuit peering.
          text: |
            az network cross-connection list-route-tables -g MyResourceGroup -n MyCircuit \\
                --path primary --peering-name AzurePrivatePeering
"""

helps['network cross-connection show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute circuit.
    examples:
        - name: Get the details of an ExpressRoute circuit.
          text: >
            az network cross-connection show -n MyCircuit -g MyResourceGroup
"""

helps['network cross-connection update'] = """
    type: command
    short-summary: Update settings of an ExpressRoute circuit.
    examples:
        - name: Change the SKU of an ExpressRoute circuit from Standard to Premium.
          text: >
            az network cross-connection update -n MyCircuit -g MyResourceGroup --sku-tier Premium
"""

helps['network cross-connection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the ExpressRoute is met.
    examples:
        - name: Pause executing next line of CLI script until the ExpressRoute circuit is successfully provisioned.
          text: az network cross-connection wait -n MyCircuit --g MyResourceGroup --created
"""

helps['network cross-connection peering'] = """
    type: group
    short-summary: Manage ExpressRoute peering of an ExpressRoute circuit.
"""

helps['network cross-connection peering create'] = """
    type: command
    short-summary: Create peering settings for an ExpressRoute circuit.
    examples:
        - name: Create Microsoft Peering settings with IPv4 configuration.
          text: |
            az network cross-connection peering create -g MyResourceGroup --circuit-name MyCircuit \\
                --peering-type MicrosoftPeering --peer-asn 10002 --vlan-id 103 \\
                --primary-peer-subnet 101.0.0.0/30 --secondary-peer-subnet 102.0.0.0/30 \\
                --advertised-public-prefixes 101.0.0.0/30
        - name: Add IPv6 settings to existing IPv4 config for Microsoft peering.
          text: |
            az network cross-connection peering update -g MyResourceGroup --circuit-name MyCircuit \\
                --peering-type MicrosoftPeering --ip-version ipv6 --primary-peer-subnet 2002:db00::/126 \\
                --secondary-peer-subnet 2003:db00::/126 --advertised-public-prefixes 2002:db00::/126
"""

helps['network cross-connection peering delete'] = """
    type: command
    short-summary: Delete peering settings.
    examples:
    - name: Delete private peering.
      text: >
        az network cross-connection peering delete -g MyResourceGroup --circuit-name MyCircuit -n AzurePrivatePeering
"""

helps['network cross-connection peering list'] = """
    type: command
    short-summary: List peering settings of an ExpressRoute circuit.
    examples:
    - name: List peering settings of an ExpressRoute circuit.
      text: >
        az network cross-connection peering list -g MyResourceGroup --circuit-name MyCircuit
"""

helps['network cross-connection peering show'] = """
    type: command
    short-summary: Get the details of an express route peering.
    examples:
    - name: Get private peering details of an ExpressRoute circuit.
      text: >
        az network cross-connection peering show -g MyResourceGroup --circuit-name MyCircuit -n AzurePrivatePeering
"""

helps['network cross-connection peering update'] = """
    type: command
    short-summary: Update peering settings of an ExpressRoute circuit.
    examples:
        - name: Add IPv6 Microsoft Peering settings to existing IPv4 config.
          text: |
            az network cross-connection peering update -g MyResourceGroup \\
                --circuit-name MyCircuit --peering-type MicrosoftPeering --ip-version ipv6 \\
                --primary-peer-subnet 2002:db00::/126 --secondary-peer-subnet 2003:db00::/126 \\
                --advertised-public-prefixes 2002:db00::/126
          min_profile: latest
"""
