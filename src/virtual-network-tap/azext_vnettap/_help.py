# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['network vnet tap'] = """
    type: group
    short-summary: Manage virtual network taps.
"""

helps['network vnet tap create'] = """
    type: command
    short-summary: Create a virtual network tap.
"""

helps['network vnet tap list'] = """
    type: command
    short-summary: List virtual network taps.
"""

helps['network vnet tap show'] = """
    type: command
    short-summary: Get the details of a virtual network tap.
"""

helps['network vnet tap update'] = """
    type: command
    short-summary: Update settings of a virtual network tap.
"""

helps['network vnet tap delete'] = """
    type: command
    short-summary: Delete a virtual network tap.
"""

helps['network nic vtap-config'] = """
    type: group
    short-summary: Manage virtual network tap configurations.
"""

helps['network nic vtap-config create'] = """
    type: command
    short-summary: Create a virtual network tap configuration.
"""

helps['network nic vtap-config delete'] = """
    type: command
    short-summary: Delete a virtual network tap configuration.
"""

helps['network nic vtap-config list'] = """
    type: command
    short-summary: List virtual network tap configurations.
"""

helps['network nic vtap-config show'] = """
    type: command
    short-summary: Get details of a virtual network tap configuration.
"""
