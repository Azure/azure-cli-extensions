# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long, too-many-lines

helps['network privatedns'] = """
    type: group
    short-summary: Manage Private DNS domains in Azure.
"""

helps['network privatedns zone'] = """
    type: group
    short-summary: Manage Private DNS zones.
"""

helps['network privatedns zone create'] = """
    type: command
    short-summary: Create a Private DNS zone.
    parameters:
        - name: --tags
          short-summary: Resource tags for the Private DNS zone.
    examples:
        - name: Create a Private DNS zone using a fully qualified domain name.
          text: >
            az network privatedns zone create -g MyResourceGroup -n www.mysite.com
"""

helps['network privatedns zone update'] = """
    type: command
    short-summary: Update a Private DNS zone's properties. Does not modify Private DNS records or virtual network links within the zone.
    parameters:
        - name: --tags
          short-summary: Resource tags for the Private DNS zone.
    examples:
        - name: Update a Private DNS zone properties to change the user-defined value of a previously set tag.
          text: >
            az network privatedns zone update -g MyResourceGroup -n www.mysite.com --tags CostCenter=Marketing
"""

helps['network privatedns zone list'] = """
    type: command
    short-summary: List Private DNS zones.
    examples:
        - name: List Private DNS zones in a resource group.
          text: >
            az network privatedns zone list -g MyResourceGroup
"""

helps['network privatedns zone delete'] = """
    type: command
    short-summary: Delete a Private DNS zone.
    long-summary: All DNS records in the zone will
        also be deleted. This operation cannot be undone. Private DNS zone
        cannot be deleted unless all virtual network links to it are removed.
    examples:
        - name: Delete a Private DNS zone using a fully qualified domain name.
          text: >
            az network privatedns zone delete -g MyResourceGroup -n www.mysite.com
"""

helps['network privatedns zone show'] = """
    type: command
    short-summary: Get a Private DNS zone.
    examples:
        - name: Get a Private DNS zone using a fully qualified domain name.
          text: >
            az network privatedns zone show -g MyResourceGroup -n www.mysite.com
"""

helps['network privatedns link'] = """
    type: group
    short-summary: Manage virtual network links to the specified Private DNS zone.
"""

helps['network privatedns link create'] = """
    type: command
    short-summary: Create a virtual network link to the specified Private DNS zone.
    parameters:
        - name: --tags
          short-summary: Resource tags for the virtual network link.
    examples:
        - name: Create a virtual network link to the specified Private DNS zone.
          text: >
            az network privatedns link create -g MyResourceGroup -n MyLinkName -z www.mysite.com -v MyVirtualNetworkId -e False
"""

helps['network privatedns link update'] = """
    type: command
    short-summary: Update a virtual network link's properties. Does not modify virtual network within the link.
    parameters:
        - name: --tags
          short-summary: Resource tags for the virtual network link.
    examples:
        - name: Update a virtual network link properties to enable registration.
          text: >
            az network privatedns link update -g MyResourceGroup -n MyLinkName -z www.mysite.com -e True
"""

helps['network privatedns link list'] = """
    type: command
    short-summary: List the virtual network links to the specified Private DNS zone.
    examples:
        - name: List virtual network links to the specified Private DNS zone in a resource group.
          text: >
            az network privatedns link list -g MyResourceGroup -z www.mysite.com
"""

helps['network privatedns link delete'] = """
    type: command
    short-summary: Delete a virtual network link to the specified Private DNS zone.
    long-summary: In case of a registration virtual network, all auto-registered DNS records in the
        zone for the virtual network will also be deleted. This operation cannot be undone.
    examples:
        - name: Delete a virtual network link to the specified Private DNS zone.
          text: >
            az network privatedns link delete -g MyResourceGroup -z www.mysite.com -n MyLinkName
"""

helps['network privatedns link show'] = """
    type: command
    short-summary: Get a virtual network link to the specified Private DNS zone.
    examples:
        - name: Get a virtual network link to the specified Private DNS zone..
          text: >
            az network privatedns link show -g MyResourceGroup -n MyLinkName -z www.mysite.com
"""
