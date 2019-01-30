# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long, too-many-lines

helps['network privatedns'] = """
    type: group
    short-summary: Manage DNS domains in Azure.
"""

helps['network privatedns zone'] = """
    type: group
    short-summary: Manage DNS zones.
"""

helps['network privatedns zone create'] = """
    type: command
    short-summary: Create a DNS zone.
    parameters:
        - name: --if-none-match
          short-summary: Only create a DNS zone if one doesn't exist that matches the given name.
        - name: --tags
          short-summary: Resource tags for the DNS zone.
    examples:
        - name: Create a DNS zone using a fully qualified domain name.
          text: >
            az network dns zone create -g MyResourceGroup -n www.mysite.com
"""

helps['network privatedns zone update'] = """
    type: command
    short-summary: Update a DNS zone's properties. Does not modify DNS records within the zone.
    parameters:
        - name: --if-match
          short-summary: Update only if the resource with the same ETAG exists.
        - name: --tags
          short-summary: Resource tags for the DNS zone.
"""
