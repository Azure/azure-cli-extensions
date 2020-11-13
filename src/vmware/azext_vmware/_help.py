# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['vmware'] = """
    type: group
    short-summary: Commands to manage Azure VMware Solution.
"""

helps['vmware private-cloud'] = """
    type: group
    short-summary: Commands to manage private clouds.
"""

helps['vmware cluster'] = """
    type: group
    short-summary: Commands to manage clusters in a private cloud.
"""

helps['vmware authorization'] = """
    type: group
    short-summary: Commands to manage the authorizations of an ExpressRoute Circuit for a private cloud.
"""

helps['vmware hcx-enterprise-site'] = """
    type: group
    short-summary: Commands to manage HCX Enterprise Sites in a private cloud.
"""

helps['vmware location'] = """
    type: group
    short-summary: Commands to check availability by location.
"""

helps['vmware cluster create'] = """
    type: command
    short-summary: Create a cluster in a private cloud. The maximum number of clusters is 4.
"""

helps['vmware cluster delete'] = """
    type: command
    short-summary: Delete a cluster in a private cloud.
"""

helps['vmware cluster list'] = """
    type: command
    short-summary: List clusters in a private cloud.
"""

helps['vmware cluster show'] = """
    type: command
    short-summary: Show details of a cluster in a private cloud.
"""

helps['vmware cluster update'] = """
    type: command
    short-summary: Update a cluster in a private cloud.
"""

helps['vmware private-cloud addidentitysource'] = """
    type: command
    short-summary: Add a vCenter Single Sign On Identity Source to a private cloud.
"""

helps['vmware private-cloud create'] = """
    type: command
    short-summary: Create a private cloud.
"""

helps['vmware private-cloud delete'] = """
    type: command
    short-summary: Delete a private cloud.
"""

helps['vmware private-cloud deleteidentitysource'] = """
    type: command
    short-summary: Delete a vCenter Single Sign On Identity Source for a private cloud.
"""

helps['vmware private-cloud list'] = """
    type: command
    short-summary: List the private clouds.
"""

helps['vmware private-cloud listadmincredentials'] = """
    type: command
    short-summary: List the admin credentials for the private cloud.
"""

helps['vmware private-cloud show'] = """
    type: command
    short-summary: Show details of a private cloud.
"""

helps['vmware private-cloud update'] = """
    type: command
    short-summary: Update a private cloud.
"""

helps['vmware authorization create'] = """
    type: command
    short-summary: Create an authorization for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware authorization list'] = """
    type: command
    short-summary: List authorizations for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware authorization show'] = """
    type: command
    short-summary: Show details of an authorization for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware authorization delete'] = """
    type: command
    short-summary: Delete an authorization for an ExpressRoute Circuit in a private cloud.
"""

helps['vmware hcx-enterprise-site create'] = """
    type: command
    short-summary: Create an HCX Enterprise Site in a private cloud.
"""

helps['vmware hcx-enterprise-site list'] = """
    type: command
    short-summary: List HCX Enterprise Sites in a private cloud.
"""

helps['vmware hcx-enterprise-site show'] = """
    type: command
    short-summary: Show details of an HCX Enterprise Site in a private cloud.
"""

helps['vmware hcx-enterprise-site delete'] = """
    type: command
    short-summary: Delete an HCX Enterprise Site in a private cloud.
"""

helps['vmware location checkquotaavailability'] = """
    type: command
    short-summary: Return quota for subscription by region.
"""

helps['vmware location checktrialavailability'] = """
    type: command
    short-summary: Return trial status for subscription by region.
"""
