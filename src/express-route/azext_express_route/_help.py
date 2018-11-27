# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


# region Express Route Gateway
helps['network express-route gateway'] = """
    type: group
    short-summary: Manage ExpressRoute gateways.
"""

helps['network express-route gateway create'] = """
    type: command
    short-summary: Create an ExpressRoute gateway.
"""

helps['network express-route gateway delete'] = """
    type: command
    short-summary: Delete an ExpressRoute gateway.
"""

helps['network express-route gateway list'] = """
    type: command
    short-summary: List ExpressRoute gateways.
"""

helps['network express-route gateway show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute gateway.
"""

helps['network express-route gateway update'] = """
    type: command
    short-summary: Update settings of an ExpressRoute gateway.
"""
# endregion

# region Express Route gateway connection
helps['network express-route gateway connection'] = """
    type: group
    short-summary: Manage ExpressRoute gateway connections.
"""

helps['network express-route gateway connection create'] = """
    type: command
    short-summary: Create an ExpressRoute gateway connection.
"""

helps['network express-route gateway connection delete'] = """
    type: command
    short-summary: Delete an ExpressRoute gateway connection.
"""

helps['network express-route gateway connection list'] = """
    type: command
    short-summary: List ExpressRoute gateway connections.
"""

helps['network express-route gateway connection show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute gateway connection.
"""

helps['network express-route gateway connection update'] = """
    type: command
    short-summary: Update an ExpressRoute gateway connection.
"""
# endregion

# region Express Route Port
helps['network express-route port'] = """
    type: group
    short-summary: Manage ExpressRoute ports.
"""

helps['network express-route port create'] = """
    type: command
    short-summary: Create an ExpressRoute port.
"""

helps['network express-route port delete'] = """
    type: command
    short-summary: Delete an ExpressRoute port.
"""

helps['network express-route port list'] = """
    type: command
    short-summary: List ExpressRoute ports.
"""

helps['network express-route port show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute port.
"""

helps['network express-route port update'] = """
    type: command
    short-summary: Update settings of an ExpressRoute port.
"""
# endregion

# region Express Route Link
helps['network express-route port link'] = """
    type: group
    short-summary: View ExpressRoute links.
"""

helps['network express-route port link list'] = """
    type: command
    short-summary: List ExpressRoute links.
"""

helps['network express-route port link show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute link.
"""
# endregion

# region Express Route Port Locations
helps['network express-route port location'] = """
    type: group
    short-summary: View ExpressRoute port location information.
"""

helps['network express-route port location list'] = """
    type: command
    short-summary: List ExpressRoute port locations.
"""

helps['network express-route port location show'] = """
    type: command
    short-summary: Get the details of an ExpressRoute port location.
"""
# endregion
