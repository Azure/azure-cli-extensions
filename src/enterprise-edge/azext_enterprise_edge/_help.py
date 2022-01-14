# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['staticwebapp enterprise-edge'] = """
    type: group
    short-summary: Manage the Azure Front Door CDN for static webapps. For optimal experience and availability please check our documentation https://aka.ms/swaedge
"""

helps['staticwebapp enterprise-edge enable'] = """
    type: command
    short-summary: Enable the Azure Front Door CDN for a static webapp. Enabling enterprise-grade edge requires reregistration for the Azure Front Door Microsoft.CDN resource provider. For more details, please review the documentation available at https://go.microsoft.com/fwlink/?linkid=2184995 . For optimal experience and availability please check our documentation https://aka.ms/swaedge
"""

helps['staticwebapp enterprise-edge disable'] = """
    type: command
    short-summary: Disable the Azure Front Door CDN for a static webapp. For optimal experience and availability please check our documentation https://aka.ms/swaedge
"""

helps['staticwebapp enterprise-edge show'] = """
    type: command
    short-summary: Show the status (Enabled, Disabled, Enabling, Disabling) of the Azure Front Door CDN for a webapp. For optimal experience and availability please check our documentation https://aka.ms/swaedge
"""
